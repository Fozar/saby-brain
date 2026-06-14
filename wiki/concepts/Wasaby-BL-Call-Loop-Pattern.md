---
type: concept
address: c-000062
title: "Wasaby BL Call Loop Pattern (Петля вызовов)"
updated: 2026-06-04
tags:
  - concept
  - wasaby
  - business-logic
  - endpoint
  - multitenancy
  - anti-pattern
status: current
related:
  - "[[Multitenancy-Architecture]]"
  - "[[Wasaby-BL-Advanced]]"
  - "[[Wasaby-BL-Methods]]"
  - "[[Wasaby-SharedFuture]]"
  - "[[wasaby-bl-call-loop-user-switch-2026-06-04]]"
created: 2026-06-04
---

# Wasaby BL Call Loop Pattern (Петля вызовов)

Петля вызовов (call loop) — ошибка, при которой БЛ-метод вызывает сам себя или тот же сервис в бесконечной рекурсии через механизм `sbis.EndPoint`.

---

## Когда возникает петля

> [!warning] Основная причина
> Петля возникает, если метод вызывает другой (или тот же) метод через `sbis.EndPoint` с такими параметрами, при которых запрос маршрутизируется обратно на тот же сервис/группу серверов.

Типичные сценарии:

| Сценарий | Причина петли |
|----------|--------------|
| Вызов под другим **пользователем** того же аккаунта (`auth_data=sbis.AuthByClientUserID(...)`) | Тот же ClientID → тот же маршрут → тот же сервис |
| Декоратор соцсети: Owner вызывает метод участника группы через `BLObject.Invoke` + `EndPoint` | Тот же юнит → петля |
| Проверка прав внутри метода через `EndPoint('online', auth_data=AuthByClientUserID(..., check_rights=True))` | ClientID совпадает с текущим |
| `TenantContext` + `EndPoint('online', auth_data)` в одном ClientID | `TenantContext` не предотвращает петлю для одного аккаунта |

---

## Решение 1: CreateMultitenantEndpointByClientId

**Рекомендуемый способ** для вызова метода под другим пользователем в рамках того же аккаунта (ClientID):

```python
# Документация: https://wi.sbis.ru/docs/py/multitenancy/methods/CreateMultitenantEndpointByClientId?v=25.2100
from multitenancy import CreateMultitenantEndpointByClientId

ep = CreateMultitenantEndpointByClientId(client_id=sbis.Session.ClientID())
result = ep.SomeObject.SomeMethod(params)
```

**Когда применять:**
- Вызов метода под другим пользователем того же аккаунта
- Тот же сервис, та же группа серверов, тот же ClientID
- Не нужно передавать `service_name`, если сервис тот же

---

## Решение 2: Проверка принадлежности к одному юниту

Если нужно вызвать метод под другим **ClientID** (декоратор соцсети, франшизный сценарий):

1. Проверить, принадлежат ли оба ClientID к одному юниту.
2. Если да — использовать прямой вызов (без `EndPoint`), чтобы избежать межсервисной маршрутизации.
3. Если нет — `EndPoint` с другим `ClientID` безопасен (разные маршруты).

---

## Антипаттерн: EndPoint с auth_data в одном ClientID

```python
# ПЛОХО — образует петлю вызовов, если ClientID совпадает с текущим
ep = sbis.EndPoint(
    'online',
    auth_data=sbis.AuthByClientUserID(
        sbis.Session.ClientID(),
        other_user_id
    )
)
result = ep.SomeObject.SomeMethod(params)
```

```python
# ПЛОХО — TenantContext не спасает при одинаковом ClientID
with TenantContext(client_id=sbis.Session.ClientID()):
    ep = sbis.EndPoint('online', auth_data=...)
    ep.SomeObject.SomeMethod(params)
```

---

## Паттерн для вызова под другим пользователем того же аккаунта

```python
# ПРАВИЛЬНО — CreateMultitenantEndpointByClientId специально проектировался
# чтобы обходить петлю при вызове в том же ClientID
ep = CreateMultitenantEndpointByClientId(
    client_id=sbis.Session.ClientID()
    # service_name не нужен, если сервис тот же
)
# Сессия переданного пользователя будет взята из auth_data конструктора
result = ep.SomeObject.SomeMethod(params)
```

---

## Связанные паттерны

- [[Multitenancy-Architecture]] — 1 client = 1 PostgreSQL schema; изоляция и маршрутизация
- [[Wasaby-BL-Advanced]] — Remote Calls: Proxy-метод, HTTP-запрос, `EndPoint.SetTimeout`
- [[Wasaby-SharedFuture]] — `FutureInvoke` для параллельных вызовов (не создаёт петли, если разные сервисы)
- [[Wasaby-Cross-Client-BL-Call]] — вызов под другим **клиентом и пользователем** (другой ClientID): `AuthByClientAndUserId` как предпочтительный подход; `CreateMultitenantEndpointByClientId` только меняет схему клиента, не пользователя

> [!note] Уточнение по CreateMultitenantEndpointByClientId
> Метод `CreateMultitenantEndpointByClientId` переключает только клиент (схему), но **не подставляет конкретного пользователя** целевого аккаунта. Для вызова под конкретным пользователем другого аккаунта нужен `AuthByClientAndUserId`. Для вызова в том же аккаунте под другим пользователем того же ClientID — `CreateMultitenantEndpointByClientId` является корректным решением (избегает петли за счёт обхода маршрутизации текущего сервиса).

---

## История проблемы

Проблема системно появляется в сценариях:
- Декораторы, меняющие «точку зрения» (от имени владельца соцсети, от имени другого пользователя)
- Проверка прав через отдельный `EndPoint` внутри метода
- Межсхемные вызовы в рамках одного сервиса (`ext-registration → ext-registration` под другим ClientID)

Известна с ~2017, воспроизводилась вновь в апреле 2025 (см. [[wasaby-bl-call-loop-user-switch-2026-06-04]]).
