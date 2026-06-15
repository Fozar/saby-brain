---
address: c-000140
created: 2026-06-14
updated: 2026-06-14
type: concept
title: "Wasaby STOMP Bus (клиентские события)"
tags:
  - wasaby
  - stomp
  - websocket
  - amqp
  - rabbitmq
  - events
  - realtime
status: current
related:
  - "[[Wasaby-MQ]]"
  - "[[Wasaby-Service-Framework]]"
sources:
  - ".raw/wasaby.Backend/Шина доставки клиентских событии STOMP.sabydoc"
---

# Wasaby STOMP Bus

**STOMP Bus** — шина доставки облачных событий от BL к клиентам (браузер, плагин, мобильное приложение) через WebSocket. Использует протокол STOMP поверх WebSocket.

## Архитектура (2 слоя)

```
BL → AMQP → [Route Layer] → AMQP → [Web Layer] → WebSocket → Клиент
```

| Слой | Назначение |
|------|-----------|
| **Route** | Принимает сообщения от BL, маршрутизирует по веб-сегментам |
| **Web** | Управляет WebSocket-соединениями клиентов |

## Порты

| Слой | Порт | Назначение |
|------|------|-----------|
| Route | 5672 | AMQP from BL |
| Route | 15692 | Prometheus metrics |
| Web | 5672 | AMQP inter-layer |
| Web | 15692 | Prometheus metrics |
| Web | 15674 | WebSocket clients |
| Web | 8088 | HTTP clients |

## Публикация из BL

BL публикует через AMQP на exchange `!web-entrypoint` слоя Route.

### AMQP заголовки

| Заголовок | Описание |
|-----------|---------|
| `delivery` | Тип доставки (`user`, `client`, `global`) |
| `sites` | Список сайтов-получателей |
| `event-type` | Тип события |
| `app` | Приложение-источник |
| `recipients` | Список получателей |
| `timestamp` | Время события |
| `delivery_mode=1` | Non-persistent (не сохранять на диск) |
| `x-requestuuid` | UUID запроса для трассировки |

## Области доставки

| Тип | Routing key | Описание |
|-----|-------------|---------|
| `user` | hex(UID) | Конкретному пользователю |
| `client` | hex(CID) | Всем пользователям клиента (аккаунта) |
| `global` | пусто | Всем пользователям облака |

## Сегментация

Клиенты сегментируются по Client ID для масштабирования:
- **8 бит** — индивидуальная доставка
- **24 бита** — групповая доставка

## Необходимые сервисы

Для работы STOMP bus требуются:
- `user-service`
- `cloud-ctrl`
- `admin-service`
- `configuration-service`

## Связанные страницы

- [[Wasaby-MQ]] — общая архитектура очередей RabbitMQ
- [[Wasaby-Sync-Broker]] — облачный брокер синхронизации (использует STOMP для уведомлений)
