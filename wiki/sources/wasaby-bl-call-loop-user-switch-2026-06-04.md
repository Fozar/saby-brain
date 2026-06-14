---
type: source
address: c-000065
title: "Петля вызова при смене пользователя — SBIS Forum Thread"
source: "https://link.sbis.ru/page/forum-card/c1eea789-a574-4a9d-96ea-53bf14ddee0a"
author: "Разговоров Андрей (вопрос), Бадаев Евгений (ответ)"
published: 2025-08-05
created: 2026-06-04
tags:
  - source
  - wasaby
  - business-logic
  - endpoint
  - multitenancy
  - call-loop
status: processed
related:
  - "[[Wasaby-BL-Call-Loop-Pattern]]"
  - "[[Multitenancy-Architecture]]"
  - "[[Wasaby-BL-Advanced]]"
  - "[[Wasaby-SharedFuture]]"
updated: 2026-06-04
---

# Источник: Петля вызова при смене пользователя (SBIS Forum, 05.08.2025)

**Ссылка:** https://link.sbis.ru/page/forum-card/c1eea789-a574-4a9d-96ea-53bf14ddee0a

---

## Суть вопроса

Разговоров Андрей (команда Календарь и планировщик) описывает сценарий:

- Есть БЛ-метод, которому передаётся другой пользователь.
- Внутри метода происходит вызов с **сессией переданного пользователя** на **той же группе серверов** и в **том же аккаунте** (ClientID), что и текущий пользователь.
- Результат: **петля вызова** (call loop / циклический вызов).

**Проблема проявляется при:**
- использовании `sbis.EndPoint('online', auth_data=...)` с передачей другого пользователя;
- вызове метода в рамках того же сервиса и того же ClientID.

---

## Решение от Бадаева Евгения (Сервер приложения)

Использовать **`CreateMultitenantEndpointByClientId`**:

> Вам нужно использовать `CreateMultitenantEndpointByClientId`
> (https://wi.sbis.ru/docs/py/multitenancy/methods/CreateMultitenantEndpointByClientId?v=25.2100)

Это API специально предназначено для межпользовательских вызовов в рамках одного аккаунта без образования петли.

**Уточнение Разговорова:** поскольку клиент тот же и сервис тот же, параметр `service_name` не нужен передавать внутрь.

---

## Похожие темы из треда

Следующие форумные треды подтверждают, что петля вызовов — распространённая проблема:

| Дата | Автор | Описание |
|------|-------|---------|
| 08.07.25 | Тимошенко Александр | Вызов метода в другой схеме того же сервиса через TenantContext + EndPoint → петля |
| 11.10.24 | Киселев Алексей | Петля при проверке прав через `AuthByClientUserID` |
| 05.08.24 | Постнов Святослав | Петля при декораторе соцсети (другой ClientID через `BLObject.Invoke` + EndPoint) |

**Что НЕ решает проблему:** `TenantContext` — при использовании вместе с `EndPoint('online', auth_data)` в рамках одного ClientID петля остаётся.

---

## Извлечённые знания

- [[Wasaby-BL-Call-Loop-Pattern]] — полная концепция петли вызовов и способы её избежать
