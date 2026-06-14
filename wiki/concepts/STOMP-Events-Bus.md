---
type: concept
title: "Шина доставки клиентских событий STOMP"
tags:
  - wasaby
  - infrastructure
  - messaging
  - rabbitmq
  - stomp
status: current
related:
  - "[[Wasaby-RabbitMQ]]"
  - "[[Async-Calls-Bus]]"
  - "[[Server-Events-Bus]]"
created: 2026-04-12
updated: 2026-04-12
---

# Шина доставки клиентских событий STOMP

Сервис доставки уведомлений от облака (БЛ) до внешних клиентов: браузер, СБИС Плагин, мобильные приложения.

## Архитектура

Каскадная (2 слоя), построена на RabbitMQ:

```
БЛ → AMQP → [Route Layer] → shovel → [Web Layer] → WebSocket/STOMP → Клиент
```

| Слой | Роль |
|---|---|
| **Route (маршрутизирующий)** | Принимает события от БЛ, маршрутизирует в web-слой по сегменту клиента |
| **Web (клиентский)** | Принимает подключения клиентов, финальная маршрутизация |

## Диапазоны публикации

| Тип | Routing key |
|---|---|
| `user` | Конкретный пользователь (UID hex) |
| `client` | Все пользователи аккаунта (CID hex) |
| `global` | Все пользователи облака (пустая строка) |

## Сегментирование пользователей

Клиент (CID) → групповая часть (24 бит) mod N → номер сегмента.
Каждый web-под = один сегмент. Ingress использует sliding-hash для стабильного маршрута.

## Протоколы клиентского подключения

- **Primary**: WebSocket + STOMP (порт 15674)
- **Fallback**: XHR long-polling через sockjs-xhr (http порт 8088)

## Ключевые заголовки AMQP при публикации

```
delivery    — область публикации (user/client/global)
sites       — список сайтов
event-type  — имя события
recipients  — идентификаторы получателей
timestamp   — unix time (секунды)
delivery_mode = 1  — только RAM (низкая задержка)
content_type = application/json; charset=utf-8
```

## Порты

| Слой | Порт | Назначение |
|---|---|---|
| Route | 5672 | AMQP от БЛ |
| Route | 15692 | Prometheus метрики |
| Web | 5672 | AMQP между слоями |
| Web | 15674 | WebSocket клиенты |
| Web | 8088 | HTTP (ping/whoami/info/block) |
| Web | 15692 | Prometheus метрики |

## Восстановление и масштабирование

- Состав Route-слоя запрашивается каждые **5 минут** (`RabbitMQNode.NodeListJSON`)
- Shovel соединения создаются динамически (`dynamic_shovel` плагин)
- Probe (external-probe): pod выводится из балансировки через 30с, перезагружается через 100с

## Конфигурация

Управляется из реестра "Кластеры" на `cloud.sbis.ru`. Три типа карточек: Route, Web, Гостевой Web.
