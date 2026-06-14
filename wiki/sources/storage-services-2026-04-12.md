---
type: source
title: "Хранение данных: SabyDisk / FileStorage / file-transfer"
source_files:
  - "raw/Saby Space.md"
  - "raw/Описание.md"
  - "raw/FileStorage (хранилище файлов).md"
  - "raw/Хранение бинарных данных.md"
  - "raw/Сервис временных файлов (file-transfer).md"
ingested: 2026-04-12
tags:
  - source
  - wasaby
  - infrastructure
  - storage
created: 2026-04-12
updated: 2026-04-12
status: archived
---

# Хранение данных — источник

5 документов по подсистемам хранения из wasaby.Backend Knowledge Base.

## Ключевые инсайты

- **3 уровня**: SabyDisk (пользовательские) → FileStorage (внутренние сервисов) → file-transfer (временные)
- Бинарные данные → SWIFT/CEPH; метаданные → СУБД (с утилизацией в объектное хранилище через 2 года)
- FileStorage: "горячий" кэш (<5 МБ, СУБД) → фоновый перенос в SWIFT; блок метаданных ~5 МБ
- file-transfer: 2 usecase: LRS-результат клиенту + Huge Payload Protocol (async bus)
- Циклическая запись SabyDisk: при превышении квоты — удаление старых файлов (Звонки)
- FileStorage шардирована по тегу `filestorage_N`; GET-кэш через nginx/varnish перед SWIFT

## Связи

- [[File-Transfer-Service]] используется в [[Async-Calls-Bus]] (Huge Payload Protocol)
- [[File-Transfer-Service]] используется в [[LRS-Long-Request-Service]] (возврат результата)
- [[SabyDisk-Platform]] зависит от right-mng, history-disk, Profiles-Service, Online

## Созданные страницы

- [[SabyDisk-Platform]] — архитектура платформы и все сервисы Диска
- [[FileStorage-Service]] — внутреннее хранилище файлов сервисов
- [[File-Transfer-Service]] — временные файлы, API, метрики
- [[Binary-Storage-Options]] — сравнительная таблица выбора хранилища
