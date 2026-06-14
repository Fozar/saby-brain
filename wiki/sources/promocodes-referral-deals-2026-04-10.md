---
type: source
title: "Промокоды + Реферальная система сделок (batch 2026-04-10)"
source_files:
  - "raw/Промокоды.md"
  - "raw/Промокоды - Описание подсистемы.md"
  - "raw/Промокоды - Информационная модель.md"
  - "raw/Промокоды - Концепт решения и архитектура.md"
  - "raw/Возможности использования промокодов.md"
  - "raw/Реферальная система сделок - Описание.md"
  - "raw/Реферальная система сделок - API подсистемы.md"
  - "raw/Реферальная система сделок - Алгоритмы и процессы.md"
  - "raw/Реферальная система сделок - База данных.md"
  - "raw/Реферальная система сделок - Интерфейс.md"
  - "raw/Реферальная система сделок - Организация кода.md"
  - "raw/Реферальная система сделок - Подсистема распределения прав.md"
status: ingested
ingested: 2026-04-10
pages_created:
  - "[[Promocode-Subsystem-Overview]]"
  - "[[Promocode-Info-Model]]"
  - "[[ReferralDeals-System]]"
pages_updated:
  - "[[ReferralProgram-Module]]"
  - "[[price-formation/_index]]"
  - "[[index]]"
tags:
  - source
  - loyalty
  - promocode
  - referral
created: 2026-04-10
updated: 2026-04-10
---

# Промокоды + Реферальная система сделок

Batch ingest of 12 source documents from `raw/` covering two loyalty subsystems.

## Промокоды (5 docs)

- **Промокоды.md** — marketing overview, 4 types used in Розница/Престо/Салон/Документы продаж
- **Описание подсистемы.md** — subsystem index page (mostly navigation)
- **Информационная модель.md** — full object hierarchy: PromoCode (abstract) → 4 subtypes; PromoCodeEmission; PromoCodeItem; condition types
- **Концепт решения и архитектура.md** — service interaction schema (Профили + ДК сервис + SabyGet); ВидКарты/Карта/ВидЦеныДокумент technical model
- **Возможности использования промокодов.md** — feature list: 4 mechanics, analytics, flexible config, promo materials

## Реферальная система сделок (7 docs)

- **Описание.md** — Owner/Partner/SabyNet/Маркетинг/Сделки subsystem decomposition; conceptual model terms
- **API подсистемы.md** — single public API: `sabyReferralProgram.CreateLead`; parameters
- **Алгоритмы и процессы.md** — two reward flows: Lead.StateChanged + daily scheduler (visits)
- **База данных.md** — ВидЦены/Карта/ВидЦеныДокумент roles; 10 typical queries with join patterns; 5 indexes
- **Интерфейс.md** — 3 SabyNet widgets: Офферы (partner), Офферы и партнёры (owner), Станьте участником; role detection via AgentContract.AccessData
- **Организация кода.md** — PriceFormation.Online / ReferralProgram.orx; git repos
- **Подсистема распределения прав.md** — access matrix Владелец vs Партнёр; BusinessGroup.GetPersonRoleInAgents

## Key connections

- Промокод технически = Дисконтная карта (те же таблицы Карта/ВидКарты)
- Реферальная система сделок использует те же таблицы ВидЦены/Карта/ВидЦеныДокумент что и бонусная программа
- Вознаграждение Партнёра реализовано как бонусные начисления — связь с [[Bonus-Programs-Architecture]]
