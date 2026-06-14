---
type: source
title: "Сервис параметров (parameters)"
source_files:
  - "raw/Сервис параметров.md"
  - "raw/Декларативное описание параметров.md"
  - "raw/Как встраивать (API parameters).md"
  - "raw/Сервис parameters-constants.md"
ingested: 2026-04-12
tags:
  - source
  - wasaby
  - infrastructure
  - parameters
created: 2026-04-12
updated: 2026-04-12
status: archived
---

# Сервис параметров — источник

4 документа по сервису parameters из wasaby.Backend Knowledge Base.

## Ключевые инсайты

- Параметры имеют 6 типов scope (GLOBAL/USER/PROFILE/ACCOUNT/DEVICE/USER_DEVICE)
- TTL по умолчанию: 30 дней (бой: 180 дней); Permanent-параметры — бессрочно
- Декларативное описание (.psk в Genie) нужно только для permanent/synchronizable параметров
- Синхронизация: User/Person — двунаправленная; Account — только из облака
- parameters-constants = parameters + история + API выборки по моменту времени (без автоочистки)
- GLOBAL и ACCOUNT нельзя записывать из браузера

## Связи

- Шардированная БД — аналогично [[LRS-Long-Request-Service]] и request-broker-backup
- Используется повсеместно — истории ввода, настройки реестров, настройки устройств

## Созданные страницы

- [[Parameters-Service]] — сервис параметров, концепция, scope-типы, TTL
- [[Parameters-API]] — полное клиентское и серверное API
