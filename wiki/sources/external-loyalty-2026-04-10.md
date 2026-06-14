---
type: source
title: "External Loyalty Integrations — Batch Ingest 2026-04-10"
date: 2026-04-10
tags:
  - loyalty
  - external
  - iiko
  - uds
  - premium-bonus
  - source
status: ingested
related:
  - "[[ExternalLoyalty-Integrations]]"
  - "[[ExternalLoyalty-iiko-Integration]]"
  - "[[ExternalLoyalty-Info-Model]]"
  - "[[Loyalty-Database-Schema]]"
created: 2026-04-10
updated: 2026-04-10
---

# External Loyalty Integrations — Source Summary

Batch ingest of 6 files from `raw/` covering external loyalty integrations (UDS, PremiumBonus, iikoCard).

## Files Ingested

| File | Status | Target Page |
|------|--------|-------------|
| `raw/Интеграции с внешними системами лояльности.md` | NEW | [[ExternalLoyalty-Integrations]] (created) |
| `raw/Интеграция с iiko.md` | NEW | [[ExternalLoyalty-iiko-Integration]] (created) |
| `raw/Информационная модель.md` | NEW | [[ExternalLoyalty-Info-Model]] (created) |
| `raw/Концепт решения и архитектура.md` | CHANGED | [[ExternalLoyalty-Integrations]] (updated) |
| `raw/API подсистемы.md` | CHANGED | [[ExternalLoyalty-iiko-Integration]] (updated) |
| `raw/База данных.md` | CHANGED | [[Loyalty-Database-Schema]] (updated) |

## Key Content

**UDS** — бонусная программа с реферальной системой. 6-значный код из приложения. 1 балл = 1 рубль. Вебхуки для уведомлений о новых клиентах.

**Premium Bonus (PB)** — SaaS-маркетинг для HoReCa и ритейла. Реферальная система, персональные акции, единый профиль клиента.

**iikoCard** — бонусно-депозитная система для ресторанов. Идентификация строго по карте (не телефон/ФИО). Реализована для УК «Алендвик». Известная проблема: задержка обновления баланса после продажи (~несколько минут).

**Информационная модель**: 4 метода ВнешняяБонуснаяСистема — FindClient, GetExternalLoyalty, ProcessSale, ProcessCancelSale.

**Общие ограничения**: внутренняя + внешняя ЛС не смешиваются; desktop работает только онлайн; 1 балл = 1 рублю.

## Pages Created

- [[ExternalLoyalty-Integrations]] — обзор UDS/PB/iikoCard; алгоритмы, архитектура, ограничения
- [[ExternalLoyalty-iiko-Integration]] — детали iiko: алгоритм продажи, API методы, отладка, DB
- [[ExternalLoyalty-Info-Model]] — объектная модель: ВнешняяБонуснаяСистема и 6 прикладных объектов

## Pages Updated

- [[Loyalty-Database-Schema]] — добавлена секция External Loyalty: КодыЛиц + ВидКарты.Тип=2
