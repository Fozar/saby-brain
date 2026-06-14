---
type: source
title: "Синхронный и асинхронный вызов метода БЛ в облаке"
address: c-000072
source_url: "https://link.sbis.ru/article/5fed7326-90f0-4bdf-8e34-af8b04dfd93e"
fetched: 2026-06-11
tags:
  - wasaby
  - bl
  - async
  - source
status: current
related:
  - "[[Wasaby-BL-AsyncInvoke]]"
  - "[[Async-Calls-Bus]]"
  - "[[Request-Broker-Service]]"
created: 2026-06-11
updated: 2026-06-11
---

# Источник: Синхронный и асинхронный вызов метода БЛ в облаке

**Источник:** wasaby.Backend документация (link.sbis.ru)
**Дата получения:** 2026-06-11

## Что описывает

Официальная документация Wasaby по программному API вызова методов БЛ:
- Синхронный `Invoke` vs асинхронный `AsyncInvoke`
- Локальный (тот же сервис) vs удалённый (другой сервис через `EndPoint`) вызовы
- Аутентификация при удалённых вызовах (`AuthByUserID`, `AuthByClientID` и т.д.)
- Типы доставки: негарантированная (HTTP, at-most-once) vs гарантированная (AMQP/RBC, at-least-once)
- Специализированный изолированный брокер (RBC)
- Приоритеты: `rpNORMAL`/`rpLOW` для пулов; `SetAsyncPriority` (0–9) для очереди брокера
- Ограничение 100 КБ на тело запроса; Huge Payload Protocol для больших данных
- Callbacks/Errbacks с `КонтекстОперации`
- Именование очередей брокера

## Страницы, созданные при инжесте

- [[Wasaby-BL-AsyncInvoke]] — основная концепт-страница (c-000073)

## Страницы, обновлённые при инжесте

- [[Async-Calls-Bus]] — добавлена ссылка на [[Wasaby-BL-AsyncInvoke]]
- [[index]] — добавлена запись
