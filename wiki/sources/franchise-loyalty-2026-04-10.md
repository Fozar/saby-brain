---
type: source
title: "Описание — Франшиза в системе лояльности"
source: "https://online.sbis.ru/knowledge-bases/001495c1-d301-490a-9531-0b6fe60059d7?folder=2f3526bc-8224-4fc8-8b70-41164a62deba"
raw_file: "raw/Описание.md"
ingested: 2026-04-10
tags:
  - source
  - loyalty
  - franchise
  - sbis
  - saby
status: ingested
related:
  - "[[Franchise-Loyalty-System]]"
  - "[[DiscountCard-Subsystem-Overview]]"
  - "[[Loyalty-Product-Overview]]"
  - "[[Loyalty-Database-Schema]]"
created: 2026-04-10
updated: 2026-04-10
---

# Source: Описание — Франшиза в системе лояльности

**Source URL:** https://online.sbis.ru/knowledge-bases/001495c1-d301-490a-9531-0b6fe60059d7  
**Raw file:** `raw/Описание.md`  
**Ingested:** 2026-04-10

---

## Summary

Describes the Franchise (Франшиза) loyalty system feature — a mechanism that extends SBIS loyalty programs across a franchise network of multiple sellers (Участники), managed from a single Owner (Владелец) account via SabyNet.

## Key Points

- The Owner configures shared promotions, bonus programs, discount cards, and promo codes from their SabyNet personal cabinet.
- A Franchise is technically a **SabyNet social network group** with specific properties set at the social network service level.
- Current limitation: only **one franchise network** per Owner or Participant is supported.
- Synchronization is **full-overwrite** (no per-entity sent-state tracking); entities matched by UUID.
- СДК (Discount Card Service) stores all franchise cards and bonus balances; all participants access current balance from СДК.
- Single customer base: all enrollment flows (discount card forms, SabyGet "Join" button) point to the Owner's account.

## Pages Created

- [[Franchise-Loyalty-System]] — full concept page for the franchise loyalty subsystem

## Pages Updated

- [[DiscountCard-Subsystem-Overview]] — noted franchise as a key use case for cross-account card storage
- [[domains/price-formation/_index]] — added franchise loyalty as a subsystem
