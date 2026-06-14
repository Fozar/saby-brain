---
type: concept
title: "Loyalty in Saby Products"
updated: 2026-04-10
tags:
  - loyalty
  - products
  - compatibility
  - retail
  - presto
  - price-formation
status: current
related:
  - "[[Loyalty-Product-Overview]]"
  - "[[Loyalty-Database-Schema]]"
  - "[[price-formation/_index]]"
  - "[[Saby-Product-Lineup]]"
  - "[[Saby-Naming-Guide]]"
created: 2026-04-10
---

# Loyalty in Saby Products

Compatibility matrix and usage details for loyalty features across Saby products.

---

## Feature Support by Product

| Product | Discounts | Bonuses | Referral | Discount Cards | Promo Codes |
|---|---|---|---|---|---|
| Складские документы (СУ) | ✅ | ✅ | ❌ | ✅ | ✅ |
| SabyDocs | ✅ | ✅ | ❌ | ✅ | ✅ |
| Розница (Retail) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Presto | ✅ | ✅ | ✅ | ✅ | ✅ |

Settings location: `Бизнес/Каталог/Скидки и Акции` in personal account (and back-office for Retail).

---

## Warehouse Documents (СУ)

**Owner:** Морозов А.

**Limitations:**
- "Доставка" condition: only fires if set to "Не применяется"
- "Продажа" condition: only fires if set to "Только оптом"
- Conditions that don't work: День рождения, За первый заказ, Оплата, Вид оплаты, Зал/стол, Число покупок
- Promo codes: scanning not supported; manual entry via "Без скидки" button
- Discount cards and bonuses: not available on deals (сделки)
- Credit/advance: discounts apply only at document creation; no new promotions on subsequent payments

---

## SabyDocs

**Owner:** Морозов А. | Supported docs: Реализация, Счет исходящий, Заказ от покупателя.

**Limitations:**
- No cumulative discounts, stamps, hall/table, first-order, payment type, source, birthday conditions
- No manual discounts with client restrictions
- iOS: cannot apply manual discounts; Android can
- Gifts: auto and manual (appear after web sync)

---

## Retail (Online)

**Owner:** Гатауллина Г. / Спиридонова О.

**Key behaviors:**
- Client not required in sale if using SabyGet (auto-match by authenticated user)
- Credit/prepayment: discounts from advance fixation carry through to the advance sale automatically
- Bonuses: accrue on first check closure for full amount; can be spent partially; cannot pay advance; credit recalculation on close for "payment type" programs

---

## Retail (Offline)

**Limitations vs online:**
- Gifts: don't pass through to SabyGet payments; limited discounts + gifts don't work without internet
- Personal cards/discount cards: only after client specified (must have prior purchases at this point)
- Promo codes without internet: only available if in offline DB (partner promo codes and general without apply limit)
- Bonuses: cannot spend without internet; accrual queued until internet restored

---

## Presto (Online/Offline)

**Owner:** Пирогов С. / Теплухин А.

Similar to Retail behavior. See product documentation for Presto-specific details.

---

## Offline Development / Debug Setup

> [!key-insight] Подмена BL-модулей для отладки
> С версии 25.6218 ресурсы офлайн-приложений предкомпилируются. Для отладки собственных изменений нужно явно отключить скомпилированный модуль и переключить конфиг.
> Полный алгоритм: [[RetailPresto-Offline-Debug-Setup]]

---

## Discount Stacking Rules

All products follow the same discount priority/stacking logic:
- **Суммируемые** (summable) — fire alongside the best discount
- **Приоритетные** (priority) — override all other discounts even if less favorable
- **ApplyWithPromotions** — fire simultaneously with selected specific promotions

---

## Notes

> [!key-insight] Referral system
> Referral bonus system is only supported in Retail and Presto. Warehouse documents and SabyDocs do not support it.

> [!note] Franchise
> Franchise (SabyNet) loyalty: shared discounts and promotions between accounts, unified bonus balances, threshold accumulations. Owner can view franchise application statistics.
> See [[Franchise-SabyNet-Subsystem]] for full subsystem details: custom regulation (reduced fields), operator workflow, no KPI settings, statistics fixation. Most loyalty mechanisms support franchise networks; exceptions: накопительные подарочные акции and пороговые акции (in progress).
