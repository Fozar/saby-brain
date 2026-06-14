---
type: source
title: "Messaging Middleware (RabbitMQ / Шины / request-broker)"
source_files:
  - "raw/MQ.md"
  - "raw/Шина доставки клиентских событий STOMP.md"
  - "raw/Шина обмена асинхронными вызовами.md"
  - "raw/Шина обмена серверными событиями.md"
  - "raw/Сервис request-broker.md"
ingested: 2026-04-12
tags:
  - source
  - wasaby
  - messaging
  - infrastructure
created: 2026-04-12
updated: 2026-04-12
status: archived
---

# Messaging Middleware — источник

5 документов из wasaby.Backend Knowledge Base по теме обмена сообщениями.

## Ключевые инсайты

- Все шины построены на RabbitMQ (AMQP); единая кодовая база плагинов (`git.sbis.ru/mq`, `git.sbis.ru/rabbitmq`)
- **STOMP bus** — доставка до внешних клиентов (браузер/мобайл): 2 слоя (Route + Web), WebSocket/STOMP протокол
- **Async bus** — асинхронные BL-вызовы: Proxy+Main слои; Huge Payload Protocol для аргументов >100 КБ
- **Server events bus** — pub-sub между BL-сервисами: гарантия через `durable` флаг
- **request-broker** — заменитель RabbitMQ для DWC/Scheduler с отслеживанием статуса каждого запроса; 3 компонента (управляющий + node + backup); berkeley-db как хранилище

## Связи между документами

- Async bus использует [[File-Transfer-Service]] для Huge Payload
- request-broker используется [[DWC-Distributed-Workflow-Coordinator]] и Scheduler
- STOMP bus зависит от user-service, cloud-ctrl, admin-service, configuration-service
- Все шины управляются через `cloud.sbis.ru` → реестр "Кластеры"

## Созданные страницы

- [[Wasaby-RabbitMQ]] — базовые концепции RabbitMQ
- [[STOMP-Events-Bus]] — шина доставки клиентских событий
- [[Async-Calls-Bus]] — шина асинхронных вызовов
- [[Server-Events-Bus]] — шина серверных событий
- [[Request-Broker-Service]] — request-broker архитектура и алгоритмы
