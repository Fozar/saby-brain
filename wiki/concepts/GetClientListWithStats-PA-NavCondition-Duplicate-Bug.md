---
type: decision
address: c-000051
title: "GetClientListWithStats PA NavCondition Duplicate Bug"
created: 2026-05-25
updated: 2026-05-25
decision_date: 2026-05-25
status: fixed
tags:
  - decision
  - bugfix
  - loyalty
  - pagination
  - sql
related:
  - "[[PostgreSQL-CTE-Cursor-Pushdown]]"
  - "[[CursorNavigation-Mechanism]]"
  - "[[PriceFormationOnline-Core]]"
---

# GetClientListWithStats — Дубли CardId при скроллинге (pa_nav_condition)

**Задача-баг:** https://online.sbis.ru/opendoc.html?guid=05212281&client=3 (скроллинг реестра Бонусы/Клиенты)
**Где сломали:** https://online.sbis.ru/opendoc.html?guid=59944457-4f2c-4216-9715-2570194f6ae0&client=3

---

## Симптом

При скроллинге реестра «Бонусы/Клиенты» фронтенд падал с ошибкой:

```
Controls/list: корректная работа списка не возможна.
Сырые данные содержат дубли записей с ключом "CardId"="247".
Списочный метод: "Bonus.Bonus.GetClientListWithStats"
keyProperty: "CardId"
```

---

## Где сломали

Оптимизация [[PostgreSQL-CTE-Cursor-Pushdown]] в коммите `e6fe55ea61` добавила `pa_nav_condition` — проталкивание условия курсора внутрь CTE `personal_accounts` до `GROUP BY`. Цель: сократить nested loop scan по `ЧастноеЛицо` (~400ms → ~110ms).

---

## Root Cause

Запрос использует два CTE-источника карт:

- **`personal_accounts`** — карты без эмиссии (`EmissionId IS NULL`)
- **`cards_only`** — карты с эмиссией (`EmissionId IS NOT NULL`, INNER JOIN `ВидКарты`)

После `UNION ALL` они группируются по `RowId = COALESCE('P'||ClientId, 'C'||CardId)`.
Итоговый `NavKey` группы = `MAX(LastSaleDate)` по всем картам клиента.

**Неверное допущение оптимизации:** NavKey группы = дата персональной карты.

Это неверно, когда у клиента есть обе карты с разными датами:

| Карта | EmissionId | LastBonusDate |
|-------|-----------|---------------|
| Личная | NULL | 2024-01-10 |
| Номерная | 5 | **2024-01-15** |

Реальный NavKey группы = `MAX(2024-01-10, 2024-01-15) = 2024-01-15`.

**Сценарий дублирования (cursor < 2024-01-12):**

1. `pa_nav_condition` фильтрует личную карту: `2024-01-10 < cursor-threshold` → **исключена** из `personal_accounts`
2. Номерная карта в `cards_only` — фильтра нет → **включена**
3. `GROUP BY RowId`: MaxLastSaleDate = `2024-01-15`, CardId = 247
4. Внешний `nav_condition`: `2024-01-15 > cursor` → запись **проходит**
5. Клиент появляется на **двух страницах** → `CardId=247` дублируется

При прокрутке вверх (ndBACKWARD, оператор `>`) проблема ещё более выражена: `pa_nav_condition` фильтрует личную карту в обратном направлении, но номерная карта всё равно попадает в результат.

---

## Decision

**Убрать оптимизацию `pa_nav_condition` целиком** — ради корректности пагинации.

Производительность: регрессия ~290 мс (110 мс → 400 мс). Допустимо.

Правило на будущее: предфильтрация CTE по курсору безопасна **только если NavKey группы = NavKey единственного источника данных для этой группы**. Когда `UNION ALL` объединяет несколько CTE с одним RowId — предфильтровать надо либо все CTE сразу (симметрично), либо ни один.

---

## Changes

**`get_client_list_with_stats.py`:**
- Удалена константа `_PA_NAV_FIELDS`
- Удалены импорты `get_navigation_params`, `get_nav_expressions`
- Удалено замыкание `_sql_with_pa_prefilter` из `_get_card_list`
- Удалён параметр `pa_nav_condition` из `_sql_get_client_list_with_stats`
- Удалён `{% item ifdef _pa_nav_condition %}` блок в SQL
- Удалён `if pa_nav_condition:` в params
- `_get_card_list` теперь передаёт `_sql_get_client_list_with_stats` напрямую

**`tests/.../get_client_list_with_stats.py`:**
- Добавлен `test_cursor_no_duplicates_personal_and_emission_card` — воспроизводит точный сценарий бага

---

## Verification

28 тестов `GetListWithStats` — все OK.
