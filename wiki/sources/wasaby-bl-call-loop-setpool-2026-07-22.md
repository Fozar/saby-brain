---
type: source
address: c-000201
title: "SetPool у Endpoint / петля между аккаунтами одного юнита — SBIS Forum (Лемешко, 23.06.25)"
source: "https://online.sbis.ru/page/forum-card/4a44a3a8-4747-4140-bb21-0e8d0f3fa108"
author: "Лемешко Никита (вопрос); Бадаев Евгений (ответ)"
published: 2025-06-23
created: 2026-07-22
tags:
  - source
  - wasaby
  - business-logic
  - endpoint
  - multitenancy
  - call-loop
  - service-pool
status: processed
related:
  - "[[Wasaby-BL-Call-Loop-Pattern]]"
  - "[[Multitenancy-Architecture]]"
  - "[[wasaby-bl-call-loop-setpool-ext-registration-2026-07-22]]"
updated: 2026-07-22
---

# Источник: SetPool у Endpoint / петля между аккаунтами одного юнита (SBIS Forum, 23.06.2025)

**Ссылка:** https://online.sbis.ru/page/forum-card/4a44a3a8-4747-4140-bb21-0e8d0f3fa108
**Автор вопроса:** Лемешко Никита (Прикладная криптография)
**Ответил:** Бадаев Евгений (Сервер приложения)

Это **исходный (корневой) тред**, вариациями которого являются вопросы Черемисина (10.07.25, [[wasaby-cross-client-call-2026-06-04]]) и Разговорова (05.08.25, [[wasaby-bl-call-loop-user-switch-2026-06-04]]).

---

## Суть вопроса

- Основной метод вызывается в **аккаунте 1**, подметод — в **аккаунте 2**.
- Оба аккаунта в **одном юните** → в итоге петля `"autotest-ext" => "autotest-ext"`.
- Вызовы между аккаунтами вроде бы не запрещены; посоветовали **перевести вызов через endpoint на служебный пул**.
- Вопрос: насколько корректна сама ошибка и предложенное решение (через служебный пул)?

---

## Решение от Бадаева Евгения

> Вам нужно использовать `CreateMultitenantEndpointByClientId`
> (https://wi.sbis.ru/docs/py/multitenancy/methods/CreateMultitenantEndpointByClientId?v=25.2100)

---

## Ключевой вывод

> [!key-insight] Служебный пул — не тот инструмент
> Интуитивный workaround «увести вызов на служебный пул через SetPool» здесь **не является каноничным решением**. Проблема не в пуле, а в маршрутизации: вызов в рамках одного юнита возвращается на тот же сервис. Канонический фикс — `CreateMultitenantEndpointByClientId`, который специально обходит петлю. Вызовы между аккаунтами одного юнита при этом сами по себе не запрещены.

---

## Извлечённые знания

- [[Wasaby-BL-Call-Loop-Pattern]] — полная концепция петли вызовов и способы её избежать
- [[Multitenancy-Architecture]] — маршрутизация client → service → версия приложения
