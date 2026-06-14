---
type: concept
address: c-000054
title: "PostgreSQL CTE Cursor Pushdown"
created: 2026-05-19
updated: 2026-05-19
tags:
  - postgresql
  - performance
  - cursor-navigation
  - price-formation
status: current
related:
  - "[[JSONB-Array-Containment-Optimization]]"
  - "[[Wasaby-DB-Access-Patterns]]"
  - "[[PriceFormationOnline-Core]]"
  - "[[DiscountCard-Subsystem-Overview]]"
---

# PostgreSQL CTE Cursor Pushdown

## The Problem

PostgreSQL cannot push a cursor WHERE condition through a `GROUP BY` that sits inside a CTE. When cursor pagination is applied to the outer query, the planner materializes **all rows** from the GROUP BY CTE before filtering by the cursor condition — even if `LIMIT 31` is requested.

### Anatomy of the anti-pattern

```sql
WITH combined AS (
    TABLE cte_a   -- large: 23 669 rows
    UNION ALL
    TABLE cte_b   -- small: 359 rows
),
grouped AS (
    SELECT "RowId", MAX("Date") AS "Date", ...
    FROM combined
    GROUP BY "RowId"          -- materializes ALL 24 028 rows
)
SELECT ... FROM grouped
WHERE ("Date", "RowId") < (cursor_date, cursor_id)  -- applied AFTER full materialization
ORDER BY "Date" DESC, "RowId" DESC
LIMIT 31
```

**Result from `EXPLAIN`** (Bonus.GetClientListWithStats, Feb 2026):
- `ЧастноеЛицо` nested loop: 23 669 iterations, **142ms**, 95K buffers
- GROUP BY Sort: 24 028 rows, **299ms**, 4MB memory
- Total: ~400ms for 31 rows returned

---

## Why the Large CTE Is 1-to-1

In the Bonus client list, `personal_accounts` CTE scans "Карта" with `Эмиссия IS NULL`. A unique constraint (`UniquePersonalCard`) guarantees exactly **one personal card per client**. Therefore:
- Each row in `personal_accounts` maps to exactly one `RowId`
- `GROUP BY "RowId"` for personal_accounts rows is a no-op — no actual aggregation
- The cursor condition `(LastSaleDate, RowId) < cursor` can be applied **directly inside `personal_accounts`** without losing any rows

The second source (`cards_only`) is small (~359 rows) and is unaffected.

---

## Correctness Proof

Applying cursor pre-filter to `personal_accounts` is safe even when a client appears in both CTEs (~317 overlapping clients):

| Scenario | personal_date | cards_only_date | MAX(group) | Pre-filter result | Final result |
|---|---|---|---|---|---|
| Only in personal | `< cursor` | — | `< cursor` | included | included ✓ |
| Overlap, both before cursor | `< cursor` | `< cursor` | `< cursor` | included | included ✓ |
| Overlap, cards_only after cursor | `< cursor` | `≥ cursor` | `≥ cursor` | pre-filtered out | excluded by outer WHERE ✓ |
| personal before cursor, cards_only exact | `< cursor` | `= cursor` (same RowId excluded by `<`) | correct | included | included ✓ |

**No false negatives are possible.** The pre-filter can only exclude rows whose `MAX(LastSaleDate)` would also fail the outer cursor condition.

---

## Implementation Pattern

### 1. Define inner-CTE-equivalent nav fields

```python
# Outer query nav fields (use column aliases from the final SELECT)
_NAV_FIELDS = [
    NavField('''COALESCE(T."LastSaleDate", '-INFINITY'::DATE)''', 'NavKey', 'DATE'),
    NavField('''COALESCE('P' || T."ClientId", 'C' || T."CardId")''', 'RowId', 'TEXT'),
]

# Equivalent expressions inside the large CTE (use raw column names)
_PA_NAV_FIELDS = [
    NavField(
        "COALESCE((C.\"Атрибуты\"->'BonusStats'->>'LastBonusDate')::DATE, '-infinity'::DATE)",
        'NavKey', 'DATE',
    ),
    NavField("'P' || C.\"Лицо\"::TEXT", 'RowId', 'TEXT'),
]
```

### 2. Build parallel condition via closure

`get_list_by_cursor` generates `nav_condition` from the outer nav fields. To build the inner CTE condition, use `get_navigation_params` + `get_nav_expressions` with the **same position** but different field expressions:

```python
def _get_card_list(filter_, navigation):
    nav = get_navigation_params(navigation, _NAV_FIELDS)

    def _sql_with_pa_prefilter(flt, nav_condition, order_expression, limit):
        pa_nav_condition = None
        if nav.position:
            order = 'DESC' if nav_condition and ') < (' in nav_condition else 'ASC'
            pa_nav_cond, _, _ = get_nav_expressions(_PA_NAV_FIELDS, nav.position, order)
            if pa_nav_cond and pa_nav_cond != 'TRUE':
                pa_nav_condition = pa_nav_cond
        return _sql_get_client_list_with_stats(
            flt, nav_condition, order_expression, limit, pa_nav_condition=pa_nav_condition
        )

    return get_list_by_cursor(_sql_with_pa_prefilter, filter_, navigation, _NAV_FIELDS,
                               reverse=True, with_next_position=False)
```

Key points:
- `nav.position` is captured in the closure — same for both forward and backward directions
- Operator (`<` or `>`) is inferred from the rendered `nav_condition` string
- `pa_nav_condition` is passed as an extra kwarg, not stored in `sbis.Record` (TemplateExecutor is not storable in sbis.Record via `.Put()`)

### 3. Inject into inner CTE WHERE

```sql
{% item ifdef _pa_nav_condition %}
    !_pa_nav_condition
{% enditem %}
```

Added as the last `{% item %}` inside `{% where all %}` of `personal_accounts`.

### 4. Wire into params

```python
if pa_nav_condition:
    params['_pa_nav_condition'] = sbis.TemplateExecutor(sbis.Template(pa_nav_condition))
```

---

## Performance Impact (without index)

| Node | Before | After |
|---|---|---|
| ЧастноеЛицо nested loop | 23 669 iterations, 142ms | ~31 iterations, ~1ms |
| GROUP BY Sort | 24 028 rows, 299ms | ~390 rows, ~1ms |
| Seq scan "Карта" | ~105ms (unchanged) | ~105ms |
| **Total** | **~400ms** | **~110ms** |

With an index on `COALESCE((Атрибуты->'BonusStats'->>'LastBonusDate')::DATE, '-infinity'::DATE)` + `Лицо` (partial: `Эмиссия IS NULL AND Лицо IS NOT NULL AND NOT Заблокировано`), the seq scan would also collapse to ~1ms (total ~2ms). Index not added in this implementation.

---

## Applicability Conditions

This optimization is safe when ALL of the following hold:

1. **The large CTE is 1-to-1 with the cursor key.** If rows from the large CTE can aggregate (GROUP BY produces different date than individual row date), pushdown is unsafe.
2. **The cursor key expressions in the inner CTE are deterministic.** Must map exactly to the outer query's NavField expressions.
3. **No "upward date shift"** from the small CTE can save a row that the pre-filter removed. (Proven above: if inner-pre-filter excludes a row, but the group MAX would pass, the final outer cursor will exclude it anyway.)

---

## Files

- Implementation: `priceformationonline/loyaltyprograms/bonus/get_client_list_with_stats.py`
- Test: `tests/tests_priceformationonline/loyaltyprograms/bonus/get_client_list_with_stats.py` — `test_cursor_navigation`
- Analysis doc: `docs/perf_bonus_get_client_list_with_stats.md`
- Cursor navigation utility: `priceformationcommon/core/cursor_navigation.py` — `get_navigation_params`, `get_nav_expressions`
