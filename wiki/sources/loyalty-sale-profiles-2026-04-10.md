---
type: source
title: "Loyalty Sale Application + Profiles Service"
ingested: 2026-04-10
files:
  - "raw/Применение лояльности на продаже - Описание.md"
  - "raw/Применение лояльности на продаже - Алгоритмы и процессы.md"
  - "raw/Применение лояльности на продаже - Организация кода.md"
  - "raw/Сервис Профилей.md"
pages_created:
  - "[[Loyalty-Sale-Application]]"
  - "[[Profiles-Service]]"
pages_updated:
  - "[[index]]"
  - "[[hot]]"
  - "[[log]]"
tags:
  - loyalty
  - price-formation
  - platform
created: 2026-04-10
updated: 2026-04-10
status: archived
---

# Loyalty Sale Application + Profiles Service

**4 source files** ingested 2026-04-10.

## Key insights

- "Применение лояльности на продаже" is a standalone subsystem acting as a **consultant** — returns recommendations, does not modify the sale itself.
- The C++ kernel (`CalcDiscount`) is universal across Retail/Presto/СУ/SabyGet — changes to kernel propagate everywhere.
- Strict calculation order: gifts → discounts → bonus deduction → accrual → markup → rounding.
- Stamp loyalty ("штампики") is a distinct gift type: integer-only accumulation, partial stamps are lost.
- Offer mode (режим оферты): in a document chain (счёт→реализация), the consequence must strictly follow prices from the basis. New promos NOT calculated.
- `Сервис Профилей` solves cross-client user identification via the `Персона` UUID concept; uses local-first query strategy to minimize cross-service calls.

## Created pages

- [[Loyalty-Sale-Application]] — full subsystem: tasks, architecture, lifecycle, discount types, gifts, bonuses, offer mode, code org
- [[Profiles-Service]] — Персона concept, 3-contour architecture, bi-directional sync, repos
