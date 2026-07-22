---
type: source
address: c-000202
title: "Вызов БЛ-метода в другой схеме того же сервиса без петли — SBIS Forum (Тимошенко, 08.07.25)"
source: "https://link.sbis.ru/page/forum-card/02f93c9d-286c-41ef-8e13-3a95c28b2155"
author: "Тимошенко Александр (вопрос); Бойцов Евгений (ответ)"
published: 2025-07-08
created: 2026-07-22
tags:
  - source
  - wasaby
  - business-logic
  - endpoint
  - multitenancy
  - call-loop
  - tenant-context
status: processed
related:
  - "[[Wasaby-BL-Call-Loop-Pattern]]"
  - "[[Multitenancy-Architecture]]"
  - "[[Тимошенко А.А.]]"
  - "[[wasaby-bl-call-loop-setpool-2026-07-22]]"
updated: 2026-07-22
---

# Источник: Вызов БЛ-метода в другой схеме того же сервиса без петли (SBIS Forum, 08.07.2025)

**Ссылка:** https://link.sbis.ru/page/forum-card/02f93c9d-286c-41ef-8e13-3a95c28b2155
**Автор вопроса:** [[Тимошенко А.А.]] (Дисконтные карты, лояльность на продаже — backend)
**Ответил:** Бойцов Евгений (Сервисный фреймворк)

---

## Суть вопроса

Есть декоратор: при обращении **участника** группы соцсети он дёргает тот же метод под **владельцем** группы.

- Вызов идёт из `ext-registration` в `ext-registration`, но под **другим ClientID**.
- Использовались **`TenantContext` + `EndPoint('online', auth_data)`** → **петля вызовов**.

```python
auth_data = sbis.AuthByClientID(access_data.Get('ClientID'))
with sbis.TenantContext(auth_data):
    end_point = sbis.EndPoint('online', auth_data=auth_data)
    return sbis.BLObject(self.bl_object, end_point).Invoke(self.bl_method, *args)
```

Ошибка ранее «исчезала», но повторилась в апреле 2025. Профилирование показало петлю на `ReferralProgram.Read/3`.

---

## Решение от Бойцова Евгения

> Используйте `CreateMultitenantEndpointByClientId`
> (https://wi.sbis.ru/docs/py/multitenancy/methods/CreateMultitenantEndpointByClientId?v=25.2100)

**Уточнение (в комментариях):** при этом `TenantContext` **не нужен** (Бойцов Е., 08.07.25).

---

## Ключевой вывод

> [!key-insight] TenantContext не предотвращает петлю
> Обёртка `TenantContext` + ручной `EndPoint('online', auth_data)` в рамках того же сервиса не спасает от петли. `CreateMultitenantEndpointByClientId` заменяет обе конструкции сразу и не требует отдельного `TenantContext`.

---

## Извлечённые знания

- [[Wasaby-BL-Call-Loop-Pattern]] — концепция петли вызовов, антипаттерн с `TenantContext`, решение через `CreateMultitenantEndpointByClientId`
- [[wasaby-bl-call-loop-setpool-2026-07-22]] — корневой тред (Лемешко, 23.06.25)
