---
type: concept
title: "Wasaby RabbitMQ (MQ)"
tags:
  - wasaby
  - infrastructure
  - messaging
  - rabbitmq
status: current
related:
  - "[[STOMP-Events-Bus]]"
  - "[[Async-Calls-Bus]]"
  - "[[Server-Events-Bus]]"
  - "[[Request-Broker-Service]]"
created: 2026-04-12
updated: 2026-04-12
---

# Wasaby RabbitMQ (MQ)

RabbitMQ — брокер сообщений (Erlang, Pivotal), работающий по протоколу AMQP. Используется в СБИС как основа для трёх шин обмена и STOMP-сервиса.

## Основные понятия

| Термин | Описание |
|---|---|
| **Exchange (обменник)** | Маршрутизирует сообщения по очередям |
| **Queue (очередь)** | Накапливает и распределяет сообщения по consumer-ам |
| **Binding (связь)** | Правило маршрутизации exchange → queue |
| **Routing key** | Ключ для адресации сообщения |
| **Producer** | Отправитель сообщений |
| **Consumer** | Получатель/обработчик сообщений |

## Типы обменников

| Тип | Поведение |
|---|---|
| **fanout** | Рассылка во все привязанные очереди (широковещательный) |
| **direct** | Точное совпадение routing key |
| **topic** | Шаблонное совпадение routing key (`images.*.small`) |
| **headers** | Маршрутизация по заголовкам (`x-match: any/all`) |

## Durability

- **durable exchange/queue** — данные сохраняются на диск, переживают рестарт
- **transient** — только в ОЗУ, быстрее, но теряется при рестарте
- **persistent message** — сохранение тела на диск (только в durable-очередях)

## Publish Confirms

Брокер подтверждает получение сообщения после записи на диск или подтверждения consumer-ом. Используется для natural throttling при перегрузках.

## QoS (Quality of Service)

Consumer запрашивает N сообщений без подтверждения — повышает пропускную способность, сглаживает сетевую задержку.

## Persistence хранилище

- **Queue index** — мета-информация по каждому сообщению (per-queue)
- **Message store** — общее key-value хранилище тел сообщений

## Применение в СБИС

- [[STOMP-Events-Bus]] — доставка событий браузерам/мобильным клиентам
- [[Async-Calls-Bus]] — асинхронные вызовы БЛ между сервисами
- [[Server-Events-Bus]] — обмен серверными событиями между БЛ
- [[Request-Broker-Service]] — специализированный брокер с отслеживанием статуса
