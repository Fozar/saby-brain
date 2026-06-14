---
type: source
title: "Markup Subsystem (Наценка) — Batch Ingest 2026-04-10"
source_files:
  - "raw/Описание.md"
  - "raw/База данных.md"
  - "raw/API подсистемы Наценка.md"
  - "raw/Подсистема распределения прав.md"
ingested: 2026-04-10
tags:
  - source
  - loyalty
  - markup
  - price-formation
status: current
created: 2026-04-10
updated: 2026-04-10
---

# Markup Subsystem — Ingest Summary

4 documents describing the Наценка (Markup) subsystem in the SBIS/Saby loyalty and price formation system.

## Pages Created
- [[Markup-Subsystem]] — full subsystem description, info model, DB schema, API, rights

## Pages Updated
- [[Loyalty-Database-Schema]] — added ВидЦены.Тип=32 (Наценка)

## Key Insights
- Наценка = ВидЦены.Тип=32, unified data model with [[Акции-Subsystem-Overview|Акции]] (MARKUP_* type)
- Two modes: automatic (on first nomenclature add) vs manual (cashier dialog)
- Special nomenclature «Сервисный сбор» auto-created when block enabled
- Calculated AFTER discounts/bonuses, BEFORE rounding; max markup wins if multiple match
- API: `RetailSaleDoc.CalculateDiscount(WithMarkup=true)` → `Markup: Money`
