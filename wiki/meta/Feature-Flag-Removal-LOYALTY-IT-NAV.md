---
type: decision
title: "Удаление фич loyalty_it_nav и bonus_it_navigation"
created: 2026-06-05
updated: 2026-06-05
decision_date: 2026-06-05
status: active
tags:
  - price-formation
  - feature-flags
  - iterative-navigation
  - refactoring
related:
  - "[[Loyalty-React-Migration-Project]]"
  - "[[ReferralBonus-GetSaleList-Iterative-Ordering-Bug]]"
  - "[[GetClientListWithStats-PA-NavCondition-Duplicate-Bug]]"
---

# Удаление фич loyalty_it_nav и bonus_it_navigation

Задача [3004dcf8](https://online.sbis.ru/opendoc.html?guid=3004dcf8-6c11-45f9-87fb-7a59b0728ec3&client=3). Обе фичи выкачены на 100% → удалены из кода.

Итеративная навигация (`it_nav`) разрабатывалась в рамках [[Loyalty-React-Migration-Project]] — проекта перехода на React, которому требовался новый механизм навигации по реестрам. Фичи были раскатаны полностью → код под флагами становится постоянным.

---

## Правила удаления

**Стандартный случай (loyalty_it_nav):**
- Ветку feature-ON (итеративная навигация) — оставить
- Ветку feature-OFF (старый курсорный путь) — удалить
- Если базовый класс больше не нужен нигде кроме одного подкласса — влить в подкласс

**Исключение — `bonus/get_client_list_with_stats.py`:**
- Функционал под фичей был **отменён** (не допилен)
- Оставить OLD path (не итеративный), удалить `BonusClientListWithStatsIterative`

**bonus_it_navigation:** «мёртвая» фича — константа определена, нигде не используется. Просто удалена.

---

## Слияние классов

`BonusSaleListWithCursor` (parent) влит в `BonusSaleListIterative` (child) — после удаления старой ветки parent нигде не использовался кроме `BonusSaleListIterative`.

`ReferralBonusSaleListWithCursorIterative(BonusSaleListIterative)` — наследует `get_result` и `_prepare_next_position_iterative` целиком; переопределяет только `_graphic_type`, `_iterative_block_size`, `_query`.

---

## Затронутые файлы

### .feature и константы
- `PriceFormation.feature` — удалены блоки `bonus_it_navigation` и `loyalty_it_nav`
- `priceformationcommon/helpers/feature.py` — удалены `BONUS_IT_NAVIGATION`, `LOYALTY_IT_NAV`

### Производственный код
| Файл | Что сделано |
|------|-------------|
| `discountcard/discountcard/get_list_with_stats.py` | Удалена `_should_use_iterative()`, всегда используется `DiscountCardListWithCursorIterative` |
| `loyaltyprograms/bonus/get_sale_list.py` | `BonusSaleListWithCursor` влит в `BonusSaleListIterative`, старый класс удалён |
| `loyaltyprograms/referralbonus/get_sale_list.py` | `ReferralBonusSaleListWithCursor` удалён, только итеративный путь |
| `loyaltyprograms/promocode/get_sale_list.py` | `PromoCodeSaleListWithCursor` удалён, только итеративный путь |
| `loyaltyprograms/bonus/get_client_list_with_stats.py` | `BonusClientListWithStatsIterative` (~360 строк) удалён, закомментированный feature-check убран; остаётся OLD path |

### Тесты (9 файлов)
Паттерн одинаковый для всех:
- `@with_feature([Feature.LOYALTY_IT_NAV])` / `@with_feature(Feature.LOYALTY_IT_NAV)` на классе → удалить декоратор (тест прогоняется один раз)
- `if not check_feature(Feature.LOYALTY_IT_NAV): return` → удалить guard целиком
- `if check_feature(Feature.LOYALTY_IT_NAV): expected[...] = ...` → раскрыть тело (всегда выполнять)

**Исключение** — `bonus/get_client_list_with_stats.py` тест: условие `if check_feature(...)` добавляло `_IsControlRecord`/`ScannedCount`/`RawResultCount` в expected; OLD path их не возвращает → строки удалены (не раскрыты).

---

## Баги, найденные при прогоне тестов

1. **`test_empty_card_type_skips_heavy_sql`** (`discountcard/get_list_with_stats.py`):
   - Мокировал `get_list_by_cursor`, которая была удалена из модуля
   - Фикс: убрать mock, оставить только `patch.object(DiscountCardListWithCursorIterative, 'get_result')`

2. **`test_4`** (`bonus/get_client_list_with_stats.py`):
   - Expected содержал три поля итеративного пути (`_IsControlRecord`, `ScannedCount`, `RawResultCount`)
   - OLD path их не возвращает → поля убраны из expected

---

## Результат

74 теста, все зелёные:
- `GetListWithStats` (37) — discountcard + bonus client list
- `GetSaleList` (18) — bonus, referralbonus, promocode
- `GetReferralSaleTotalsBase` + `BatchSetLockedTest` (5)
- `GetSaleTotals` бонусы (14)
