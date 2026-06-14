---
type: source
title: "Подсказки Subsystem — 4 docs"
source_files:
  - "raw/Описание.md"
  - "raw/API подсистемы.md"
  - "raw/База данных.md"
  - "raw/Подсистема распределения прав.md"
ingested: 2026-04-10
tags:
  - loyalty
  - prompts
  - price-formation
status: ingested
related:
  - "[[Prompts-Cashier-Hints]]"
  - "[[Loyalty-Database-Schema]]"
created: 2026-04-10
updated: 2026-04-10
---

# Подсказки Subsystem — 4 docs (2026-04-10)

Batch of 4 updated source documents describing the **Подсказки (Cashier Hints)** subsystem within the SBIS/Saby loyalty system.

## Sources

| File | Content |
|---|---|
| `raw/Описание.md` | Full subsystem description: business value, decomposition, display flow, interaction model, information model |
| `raw/API подсистемы.md` | API: WarehouseSaleDoc.CalculateDiscount + RetailSaleDoc.CalculateDiscount Prompts output |
| `raw/База данных.md` | DB schema: ВидЦены (Тип=18) + ВидЦеныРасширение |
| `raw/Подсистема распределения прав.md` | Access rights: Presto (section «Presto») + Retail (section «Магазин») |

## Pages Created
- [[Prompts-Cashier-Hints]] — main concept page

## Pages Updated
- [[Loyalty-Database-Schema]] — added Тип=18 entry

## Key Insight
Подсказки reuse the `ВидЦены` data model (same as discounts/promotions) — Тип=18 is the only differentiator. Session storage deduplication prevents repeat display within 1 hour.
