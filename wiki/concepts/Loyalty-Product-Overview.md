---
type: concept
title: "Loyalty Product Overview"
updated: 2026-04-10
tags:
  - loyalty
  - product
  - price-formation
  - sbis
status: current
related:
  - "[[Loyalty-Database-Schema]]"
  - "[[Loyalty-In-Products]]"
  - "[[Loyalty-Public-API]]"
  - "[[ReferralProgram-Module]]"
  - "[[price-formation/_index]]"
created: 2026-04-10
---

# Loyalty Product Overview

SBIS/Saby loyalty system: universal loyalty engine reused across the Saby product ecosystem.

---

## Goals

- Increase repeat purchases and average check
- Reduce churn, increase return rate (client visits > 1 time)
- Increase visit frequency
- Improve customer knowledge and make marketing measurable

---

## Core Entities

### Акция (Promotion)
Abstract customer benefit, in the moment or future, with optional trigger conditions. **One benefit per promotion.**

Benefit types:
- **Скидка** — percentage or amount discount (on whole document or specific items)
- **Подарок** — gift item
- **Бонусное начисление** — bonus points accrual
- **Спеццена** — special price

Promotion classifications:
- By benefit: percentage, amount, gift, special price
- By scope: whole check, per item (позиционная), set (комплектная)
- By stacking: summable, non-summable, prioritized, non-prioritized

Special promotion subtypes:
- **Наценки** — negative discounts (service surcharges)
- **Подсказки** — tip/hint promotions that display info to cashier without applying a benefit

### Дисконтная карта (Discount Card)
Customer identifier in the loyalty system. Each card belongs to a **Тип карт** (card emission type) — a container defining the rules.

Card acquisition:
1. Online registration form (self-fill, phone confirmation, e-card download link)
2. Connect via venue page in Saby Get (simplified registration)
3. Receive at POS

**Персональная карта** — technical card with no number, no emission type. Auto-created for every loyalty client to store accumulations and referral bonuses.

### Промокод (Promo Code)
Hybrid of Акция + Дисконтная карта. Stored in same tables as discount cards. Each promo code instance is a Карта record.

### Клиент лояльности (Loyalty Client)
Not yet formalized as a distinct entity. Closest analog: персональная карта. The "loyalty client" is a broader concept not yet explicitly represented in the system.

---

## Product Integrations

| Product | Role |
|---|---|
| Saby Retail | POS sales, offline support |
| Saby Presto | Restaurant POS |
| Saby Hotel | Hotel checkout |
| SabyTrade | Procurement/trading |
| Saby Target | Targeted mailing and ad campaigns |
| Saby Clients | Client identification, buyer profile |
| Saby Get | Customer-facing: active cards, bonus balances, promo codes, referral link |
| Saby CRM | Sales efficiency analytics, cashier stats, dashboards |
| Saby Net | Franchise network: shared loyalty, bonus balances across accounts |

---

## Subsystem Decomposition

| Subsystem | Description |
|---|---|
| **Акции** | Discount/promotion registry, cards, sync to offline |
| **Бонусы** | Global bonus settings, bonus programs, holiday accruals, balance management |
| **Дисконтные карты** | Card types, card instances, e-card images (Apple Wallet, Google Pay), SDC microservice |
| **Реферальная бонусная программа** | Referral link generation, registration reaction, bonus accrual |
| **Промокоды** | Promo code emission types, instance issuance, client display |
| **Статистика** | Widgets and reports for loyalty effectiveness |
| **Лояльность в Retail/Presto/Salon** | Specialized UI registries; houses the core discount calculation engine |
| **Подсказки на кассе** | Cashier hint actions: text, product lists, discount card offers |
| **Наценки** | Negative discounts (service fees); no separate trigger logic |
| **Внешние бонусные системы** | Integration with UDS, Premium Bonus, Iiko via public API |
| **Реферальная система сделок** | SabyNet partner deal accounting and billing |

---

## Statistics Architecture

All loyalty application events write to **ВидЦеныДокумент** — a single unified table. This enables:
- Uniform storage across all loyalty types
- Widgets for quick KPI overview
- Reports for detailed analysis (filters, breakdowns, multiple metrics)

> [!note] Franchise support
> Almost all loyalty mechanisms support franchise networks (SabyNet). Exception: накопительные подарочные акции (cumulative gift promotions) and пороговые акции (threshold promotions) — in progress.
