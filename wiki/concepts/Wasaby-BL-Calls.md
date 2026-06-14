---
address: c-000110
created: 2026-06-14
updated: 2026-06-14
type: concept
title: "Wasaby BL Calls — синхронный и асинхронный вызов"
tags:
  - wasaby
  - backend
  - bl
  - async
  - microservices
  - architecture
status: current
related:
  - "[[Wasaby-Service-Framework]]"
  - "[[Wasaby-BL-Objects]]"
sources:
  - ".raw/wasaby.Backend/Сервисный фреймворк/Синхронный и асинхронный вызов метода БЛ в облаке.pdf"
  - ".raw/wasaby.Backend/Сервисный фреймворк/Внутриоблачные межсервисные вызовы.pdf"
---

# Wasaby BL Calls

Паттерны вызова методов бизнес-логики: локальный/удалённый, синхронный/асинхронный.

## Матрица вызовов

| | Локальный (тот же сервис) | Удалённый (другой сервис) |
|---|---|---|
| **Синхронный** | `BLObject('Obj').Invoke('Method', p)` | `BLObject('Obj', EndPoint('svc')).Invoke(...)` |
| **Асинхронный** | `BLObject('Obj').AsyncInvoke('Method', p)` | `BLObject('Obj', EndPoint('svc')).AsyncInvoke(...)` |
| **Новый стиль** | — | `EndPoint('svc').Obj.Method(p)` |

## Синхронный вызов

```python
# Локальный — объект в текущем сервисе
result = sbis.BLObject('Document').Invoke('Read', params)

# Удалённый — объект в другом сервисе
ep = sbis.EndPoint('accounting-service')
result = sbis.BLObject('Invoice', ep).Invoke('List', params)

# Новый стиль (рекомендуемый для удалённых)
result = sbis.EndPoint('accounting-service').Invoice.List(params)
```

> [!key-insight] Синхронный == блокирующий
> Синхронный вызов блокирует поток до получения ответа. Для длительных операций используйте AsyncInvoke. Синхронные методы выполняются в пуле `rpNORMAL`.

## Асинхронный вызов

```python
# Базовый — fire and forget
sbis.BLObject('Report').AsyncInvoke('Generate', params)

# С обратными вызовами
sbis.BLObject('Report').AsyncInvoke(
    'Generate',
    params,
    callbacks=('OnSuccess', 'OnError', '{"context":"json"}')
)

# Удалённый асинхронный
sbis.BLObject('Report', sbis.EndPoint('report-service')).AsyncInvoke(
    'Generate', params
)
```

Асинхронный вызов помещает сообщение в очередь и немедленно возвращает управление. Метод-обработчик выполняется в пуле `rpLOW`.

### Приоритеты пулов

| Пул | Константа | Назначение |
|-----|-----------|------------|
| Основной | `rpNORMAL` | Быстрые синхронные методы (пользовательские запросы) |
| Сервисный | `rpLOW` | Все асинхронные вызовы, фоновые задачи |

## Транспорт и гарантии доставки

| Тип доставки | Транспорт | Гарантия | Применение |
|---|---|---|---|
| **Guaranteed** | AMQP / RBC | At-least-once (по умолчанию) | Бизнес-операции, финансы |
| **Unguaranteed** | HTTP | At-most-once | Уведомления, метрики, события |

- Гарантированная доставка: сообщение сохраняется в брокере, повторяется при сбое
- Негарантированная: HTTP-запрос; потеря при недоступности получателя

## Ограничения размера сообщений

| Порог | Поведение |
|-------|-----------|
| < 100 KB | Штатная передача в теле сообщения |
| > 100 KB | Предупреждение; рекомендуется Huge Payload Protocol |
| > 1 MB | Ошибка при асинхронном вызове |

## Huge Payload Protocol

Для передачи больших данных (>100 KB) в асинхронном вызове:

1. Данные загружаются в сервис передачи файлов
2. В сообщение передаётся только ссылка (reference)
3. Получатель скачивает данные по ссылке

```python
# Автоматически активируется при превышении порога (зависит от конфигурации)
# или вызывается явно через HugePayload wrapper
sbis.BLObject('DataImport').AsyncInvoke('Process', huge_params)
```

## Политики аутентификации для межсервисных вызовов

Применяются при удалённых вызовах через `EndPoint`:

| Политика | Контекст |
|----------|---------|
| `AuthByClientID` | От имени клиента (тенанта) |
| `AuthByUserID` | От имени конкретного пользователя |
| `AuthByExtID` | По внешнему идентификатору |
| `AuthByLogin` | По логину |
| `AuthByClientUserID` | Клиент + пользователь вместе |
| `AuthByApplicationId` | От имени приложения (сервисный вызов без пользователя) |
| `AuthByApplication` | Системный сервисный вызов |

```python
ep = sbis.EndPoint('accounting-service', auth=sbis.AuthByApplicationId('myapp'))
result = ep.Invoice.List(params)
```

## Мультитенантность

При вызове между сервисами контекст тенанта (клиента) передаётся автоматически. Явное переключение:

```python
# Вызов в контексте конкретного клиента
ep = sbis.EndPoint('service', client_id=12345)
```

## Callbacks асинхронного вызова

```python
callbacks = (
    'OnSuccess',           # имя метода текущего объекта для обработки успеха
    'OnError',             # имя метода для обработки ошибки
    '{"context":"data"}'   # JSON-контекст, передаётся в callback
)
sbis.BLObject('MyObj').AsyncInvoke('LongMethod', params, callbacks=callbacks)

# Методы в том же BL-объекте:
def OnSuccess(self, result, context):
    ...

def OnError(self, error, context):
    ...
```

## Связанные страницы

- [[Wasaby-BL-Objects]] — иерархия объектов, типы методов
- [[Wasaby-Service-Framework]] — архитектурный контекст и EndPoint
