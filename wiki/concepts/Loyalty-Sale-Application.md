---
type: concept
title: "Loyalty Sale Application (Применение лояльности на продаже)"
updated: 2026-04-10
tags:
  - loyalty
  - price-formation
  - sale
status: current
related:
  - "[[Loyalty-Database-Schema]]"
  - "[[Акции-Architecture]]"
  - "[[Bonus-Deduction-Algorithm]]"
  - "[[DiscountCard-Subsystem-Overview]]"
  - "[[Promocode-Subsystem-Overview]]"
  - "[[Loyalty-In-Products]]"
created: 2026-04-10
---

# Loyalty Sale Application (Применение лояльности на продаже)

Subsystem applying discounts, bonuses, gifts, and promo codes to sale documents (Retail, Presto, Salon, СУ). Acts as a **consultant** — calculates loyalty and returns recommendations, but does not modify the sale document directly.

## Three Core Tasks

1. **Расчёт лояльности** — determine applicable promotions and return recommendations without modifying the sale.
2. **Предоставление информации** — expose current loyalty state (applied discounts, bonuses, card info) to UI and API consumers.
3. **Определение контекста** — bind loyalty objects (cards, promo codes) and load stats/balances needed for calculation.

## Calculation Architecture

### Input (Context)
- Sale document: positions, prices, payment type, date/time, point of sale
- Loyalty context: card (with purchase stats), promo codes, buyer (Лицо)
- Existing loyalty records: ВидЦеныДокумент (manual discounts, applied promo codes)
- Reference data: available ВидЦены

### Calculation Kernel (C++, module CalcDiscount)
Universal engine shared by all platforms. Fixed execution order:
1. **Подарки** (gifts)
2. **Позиционные скидки** (line-level discounts)
3. **Чековые скидки** (receipt-level discounts)
4. **Конкурс скидок** (discount contest by priority)
5. **Списание бонусов** (bonus deduction)
6. **Начисление бонусов** (bonus accrual)
7. **Наценка** (markup)
8. **Округление** (rounding via external API)

### Output (Written to DB)
- `ВидЦеныДокумент` — loyalty at document level
- `ВидЦеныНоменклатураДокумента` — loyalty per line item
- Returned synchronously by calculation method; also accessible via API.

## Key Loyalty Objects (Context)

| Object | Role |
|--------|------|
| Персональная карта | Auto-created per buyer; holds bonus balance + purchase stats |
| Дисконтная карта | Standalone; may or may not be linked to a buyer |
| Карта внешней лояльности | External system identifier (UDS, PremiumBonus, iiko) |
| Промокод | Short-lived activation mechanism (technically = Карта) |
| Ручная скидка | Explicit discount entered by operator; no buyer identification |

Both discount card and personal card can participate simultaneously in a single sale calculation.

## Sale Lifecycle

1. **Создание** — no loyalty until first change event.
2. **Динамическое применение** — every change triggers full recalculation cycle.
3. **Пользовательские действия** — operator can add/remove discounts, bind cards, apply promo codes, choose gifts, adjust bonus deduction via discount panel (`панель скидок`) or buyer window (`окно покупателя`).
4. **Закрытие** — final recalculation → activate `ВидЦеныДокумент` records → sync with external loyalty systems → update stats.

After closing, loyalty records are final and immutable.

## Discount Types

| Type | Notes |
|------|-------|
| Ручные скидки | Pass condition checks and contest like automatics |
| Позиционные | Apply to specific line; calculated globally for correct contest |
| Пороговые | Require cloud stats (purchase history) |
| Лимитированные | Capped by quantity/amount; require cloud for current limit |
| Внешние | Static values from external card; skip contest |
| Статические внешние | Passed via API params; skip contest |

## Gifts

- **Самостоятельно** — 100% discount applied to existing position in sale.
- **На кассе** — operator selects from available list (retail only).
- **Накопительные** — triggered by cumulative purchase volume; stats from cloud.
- **Штампики** — abstract unit accumulation. Only whole stamps counted (partial = lost). Works like cumulative gift: reach threshold → get gift → stamps reduced by threshold.

> [!note]
> In offline apps without cloud connection: cumulative stats = 0. Stamps still accumulate offline but trigger based on local data only.

## Bonus Deduction Mechanics

Maximum deduction = `min(` max applicable discount sum, card balance, program limits, user-entered value `)`.

Deduction amount is spread proportionally across eligible positions. Multiple deduction rules can apply per card, each with its own priority and conditions (nomenclature, point of sale, payment type, weekday, etc.).

## Offer Mode (Режим оферты)

When a document-consequence is linked to a document-basis (e.g., реализация → счёт):
- Only discounts inherited from the basis document apply.
- New promotions are NOT calculated on the consequence.
- Bonus accrual from new programs IS allowed.
- Bonus deduction: chosen on basis document only; applied immediately when selected.
- Prices per unit are fixed; quantity changes use fixed price.

## Promo Codes

Promo code = Карта (technically). Before adding: check if benefit is actually applicable. If promo code cannot produce a benefit (fails conditions or loses contest), it is NOT added. A successfully added promo code is immediately marked as used.

Auto-issue: some promo codes are issued at sale completion; user sees all eligible options, but only one enters the receipt.

## Service Architecture

No microservice split — all calculation runs inside the main service. External dependencies:
- **Сервис дисконтных карт** — provides bonus balance; accepts debit/credit operations.
- **Модуль external-discount** — external loyalty data (external discounts, external bonuses).
- **Округление API** — rounding logic owned externally; subsystem passes raw values, receives adjusted result.

## Code Organization

| Module | Purpose |
|--------|---------|
| `PriceFormation.Common` | Cloud + desktop builds of retail |
| `PriceFormation.Offline` | Desktop build only |
| `PriceFormation.Online` | Cloud only |
| `PntToolbox` | Shared tools + ВИС transport helpers |
| `CalcDiscount` | C++ calculation kernel |

**Git repos:**
- `git.sbis.ru/warehouse/price-formation`
- `git.sbis.ru/warehouse/discount-core`
- `git.sbis.ru/warehouse/pnt-toolbox`

See also: [[Акции-Architecture]] for contest algorithm details, [[Bonus-Deduction-Algorithm]] for bonus deduction rules, [[DiscountCard-Subsystem-Overview]] for card types.
