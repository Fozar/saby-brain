---
type: source
title: "Discount Cards Subsystem — Batch Ingest 2026-04-10"
source_path: raw/
ingested: 2026-04-10
tags:
  - loyalty
  - discount-cards
  - sbis
  - batch-ingest
status: current
related:
  - "[[DiscountCard-Subsystem-Overview]]"
  - "[[DiscountCard-Service-API]]"
  - "[[DiscountCard-Algorithms-Processes]]"
  - "[[DiscountCard-UI-Specifics]]"
  - "[[PassUpdater-Service]]"
  - "[[DiscountCard-Diagnostic-Service]]"
  - "[[DiscountCard-Admin-Ops]]"
  - "[[Loyalty-Database-Schema]]"
  - "[[Loyalty-Cloud-Config]]"
created: 2026-04-10
updated: 2026-04-10
---

# Discount Cards Subsystem — Batch Ingest 2026-04-10

10 документов из `raw/` о подсистеме дисконтных карт (ДК) системы лояльности СБИС/Saby.

## Источники

| Файл | Статус | Wiki-страница |
|------|--------|---------------|
| `raw/Описание.md` | NEW | [[DiscountCard-Subsystem-Overview]] |
| `raw/API подсистемы.md` | NEW | [[DiscountCard-Service-API]] |
| `raw/Алгоритмы и процессы.md` | NEW | [[DiscountCard-Algorithms-Processes]] |
| `raw/Особенности работы интерфейса.md` | NEW | [[DiscountCard-UI-Specifics]] |
| `raw/Подсистема распределения прав.md` | NEW | → [[DiscountCard-Algorithms-Processes]] |
| `raw/Пользовательская документация (для смежных команд).md` | NEW | [[DiscountCard-Admin-Ops]] |
| `raw/Сервис Диагностика (discount-cards_diagnostic).md` | NEW | [[DiscountCard-Diagnostic-Service]] |
| `raw/Сервис обновления образов (pass-updater).md` | NEW | [[PassUpdater-Service]] |
| `raw/База данных.md` | CHANGED | [[Loyalty-Database-Schema]] (updated) |
| `raw/Параметры облака, задачи планировщика.md` | CHANGED | [[Loyalty-Cloud-Config]] (confirmed same) |

## Ключевые инсайты

1. **СДК — 5 частей**: CRUD-API, синхронизация с онлайном, образы (AW/GPay), push/гео-уведомления, диагностика
2. **pass-updater**: очередь-based: ProcessQueue → EntryPoint → ResultQueue → DWC. Нельзя обновлять мастер-репликой
3. **Apple vs Google образы**: AW — асинхронно через APN + REST; GPay — синхронно к Google API + доставка через TaskDeliveryProcessor
4. **inside.sbis.ru + ClickHouse**: мониторинг активности типов карт по регионам. Синхронизация через брокер с "фейковым" UUID
5. **Конфиденциальные данные**: 11 методов с шифрованием логов, ключ в интеграции `dcslogging`
6. **Права**: внешние вызовы только с `online.sbis.ru` и `api.sabyget.ru`, 14 разрешённых методов
