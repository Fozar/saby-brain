---
type: synthesis
title: "GetClientListWithStatsTotals — Franchise Welcome Bonus Double-Count Bug"
created: 2026-06-05
updated: 2026-06-05
tags:
  - bug
  - franchise
  - bonus
  - loyaltyprograms
status: fixed
related:
  - "[[Bonus-GetTotalBalance]]"
  - "[[Loyalty-Franchise-Mechanics]]"
  - "[[GetClientListWithStats-PA-NavCondition-Duplicate-Bug]]"
  - "[[Loyalty-Database-Schema]]"
---

# GetClientListWithStatsTotals — Franchise Welcome Bonus Double-Count Bug

## Symptom

In **Бизнес → Скидки и акции → Бонусы → Клиенты**, the total balance (footer) doubles welcome bonuses charged to a franchise discount card issued to a physical person (e.g. via a questionnaire). Example: base 3949 → after 100-bonus welcome accrual on one franchise card → shown as 4149 (+200 instead of +100). Non-franchise cards are unaffected.

Method: `Bonus.GetClientListWithStatsTotals`  
File: `priceformationonline/loyaltyprograms/bonus/get_client_list_with_stats.py`

## Root Cause

The totals balance flows through two steps:

1. `_sql_get_client_list_with_stats(filter_, is_totals=True)` builds a `_precomputed` record with two UUID lists:
   - `FranchiseCardTypeUUIDList` — UUIDs of franchise card types
   - `ClientCardUUIDList` — UUIDs of franchise cards belonging to physical persons (`IsFranchise = TRUE`)

2. This record is passed as `_precomputed` to `get_total_balance(filter_, _precomputed=result)`, which calls `_sum_franchise_balances`. That function sums **both sources**:
   - `Card.GetBonusBalanceByCardType(...)` — for each card type UUID
   - `Card.GetBonusBalanceByCards(...)` — for each card UUID

A franchise card issued to a physical person (`IsFranchise = TRUE`) has **both** a `CardTypeUUID` and a `ClientCardUUID`. The is_totals SQL path placed it in **both** lists simultaneously → its balance (including welcome bonuses) was summed twice.

### Why the previous fix didn't cover this

Commit `2fd6bbff` (branch `26.3200/bugfix/aatimoshenko/041511305`) fixed the same doubling in `_SQL_GET_BALANCE_COMPONENTS` — the SQL used when `_precomputed` is **not** passed (standalone `Bonus.GetTotalBalance` path). That SQL got `AND "CardTypeUUID" IS NULL` added to the `ClientCardUUIDList` aggregation.

But `GetClientListWithStatsTotals` **always** passes `_precomputed`, so `_SQL_GET_BALANCE_COMPONENTS` is never executed in that path. The is_totals SELECT in `_sql_get_client_list_with_stats` (line 919) did not receive the same fix → bug survived.

### Log confirmation

In a single `GetClientListWithStatsTotals` trace (`logs20260605174556703460.csv`):
- ~21 calls to `Card.GetBonusBalanceByCardType` (one per franchise card type)
- 1 call to `Card.GetBonusBalanceByCards` with 12 935-byte payload (full card UUID list)

The franchise card with a type is present in both → double-count confirmed.

### Why existing tests didn't catch it

`test_franchise_card_type_balance_in_totals` created a franchise card **without** linking it to a physical person. In the SQL, `IsFranchise = (FranchiseRole IS NOT NULL) AND ИдентификаторФизЛица IS NOT NULL`. Without a person, `IsFranchise = FALSE` → the card went into local balance, never into `ClientCardUUIDList` → the franchise double-path was not exercised.

In production the card is issued via questionnaire → physical person is attached → `IsFranchise = TRUE` → both lists populated → double-count.

## Fix

**One-line change** in `_sql_get_client_list_with_stats`, `{% iftrue is_totals %}` branch, line 919:

```sql
-- Before (buggy)
ARRAY_AGG("ClientCardUUID") FILTER (
    WHERE !has_franchise AND T."IsFranchise" AND "ClientCardUUID" IS NOT NULL
) AS "ClientCardUUIDList",

-- After (fixed)
ARRAY_AGG("ClientCardUUID") FILTER (
    WHERE !has_franchise AND T."IsFranchise" AND "ClientCardUUID" IS NOT NULL AND "CardTypeUUID" IS NULL
) AS "ClientCardUUIDList",
```

Cards with a `CardTypeUUID` are accounted for exclusively via `FranchiseCardTypeUUIDList` (by type). Franchise personal accounts (no type, `CardTypeUUID IS NULL`) continue to be accounted for by UUID. No doubling.

### What was NOT changed

The `{% iffalse is_totals %}` branch (row-level `cards` CTE, line 879) and the iterative `BonusClientListWithStatsIterative` class (line 560) were left untouched. Those paths call `GetBonusBalanceByCards` only — not `GetBonusBalanceByCardType` — so a card must remain in `ClientCardUUIDList` for its balance to be retrieved. Applying the same filter there would break row-level balances.

## Regression Test Added

Class `GetListWithStatsTotalsCardTypeTests`, method `test_franchise_card_issued_to_person_welcome_bonus_not_doubled`:

- Creates franchise emission (`FranchiseUUIDList`, `FranchiseRole.OWNER`)
- Creates `person = Individual.create()` → attaches card to person → forces `IsFranchise = TRUE`
- SDK mock: `GetBonusBalanceByCardType` → 100; `GetBonusBalanceByCards` → returns the card UUID with bonus=100 (same amount, so without the fix total would be 200)
- Asserts: `AvailableBonusBalance == 100`; `GetBonusBalanceByCards.assert_not_called()` (UUID with a type must not be sent there)

All 29 tests in `get_client_list_with_stats.py` green; 10 tests in `get_total_balance.py` green.
