---
type: concept
title: "Синхронный и асинхронный вызов метода БЛ"
address: c-000073
tags:
  - wasaby
  - bl
  - async
  - endpoint
  - amqp
  - rbc
status: current
related:
  - "[[Wasaby-MQ]]"
  - "[[Wasaby-BL-Advanced]]"
  - "[[Wasaby-BL-Methods]]"
  - "[[Request-Broker-Service]]"
  - "[[File-Transfer-Service]]"
  - "[[DWC-Distributed-Workflow-Coordinator]]"
  - "[[Wasaby-BL-Objects]]"
  - "[[Sync-Broker]]"
created: 2026-06-11
updated: 2026-06-11
---

# Синхронный и асинхронный вызов метода БЛ

Программный API для вызова методов бизнес-логики в Wasaby-облаке — синхронный (`Invoke`) и асинхронный (`AsyncInvoke`).

## Типы вызовов по расположению исполнителя

### Локальный вызов

Метод выполняется в том же сервисе облака, из которого вызван. `EndPoint` не используется или передан пустой строкой.

```python
obj = BLObject('НазваниеОбъекта')

# Синхронный — текущий процесс и поток
result = obj.Invoke('НазваниеМетода', param1, param2)

# Асинхронный — произвольный процесс того же сервиса (возможно, другой сервер)
obj.AsyncInvoke('НазваниеМетода', param1, param2)
```

```cpp
bl::Object object( L"НазваниеОбъекта" );
int result = object.Invoke< int >( L"НазваниеМетода", param1, param2 );
object.AsyncInvoke( L"НазваниеМетода", param1, param2 );
```

### Удалённый вызов

Метод выполняется в **другом** сервисе облака. `EndPoint` обязателен.

```python
# Старый стиль
ep = EndPoint('telephony')
result = BLObject('Phonebook', ep).Invoke('ReadNumber', param1, param2)

# Новый стиль (dot-notation)
result = EndPoint('telephony').Phonebook.ReadNumber(param1, param2)
```

```cpp
blcore::EndPoint ep{ L"telephony" };
int result = blcore::Object{ L"Phonebook", ep }.Invoke< int >( L"ReadNumber", param1, param2 );
```

> [!warning] Вызов по абсолютному URL
> Политики аутентификации (`AuthByUserID` и др.) не работают, если вместо системного имени сервиса используется абсолютный URL.

## Аутентификация при удалённом вызове

По умолчанию используется текущая сессия. Для **персональных сервисов** необходимо явно задать пользователя/клиента через `auth_data` в EndPoint:

| Способ | Описание |
|---|---|
| `AuthByClientID` | По прямому ID клиента в облаке |
| `AuthByExtID` | По внешнему ID из биллинга |
| `AuthByUserID` | По прямому ID пользователя |
| `AuthByLogin` | По логину пользователя |

```python
ep = EndPoint(service_name='online', auth_data=AuthByUserID(myId))
response = ep.MyBLOName.MyMethodName(param1, param2)
```

Если сервис входит в online/inside/private, вызов идёт через `online-private.sbis.ru`.

## Приоритет обработки

| Приоритет | Константа | Применение |
|---|---|---|
| Нормальный | `rpNORMAL` | «Быстрые» методы, результат нужен моментально пользователю |
| Пониженный | `rpLOW` | Фоновые задачи и «долгие» методы (файлы и т.п.) |

У всех асинхронных вызовов приоритет **всегда `rpLOW`** — попадают только в служебный пул, изменить нельзя.

## Типы доставки асинхронного вызова

### Негарантированная доставка (HTTP)

- Обработан **не более одного раза** — может быть потерян при остановке сервиса-исполнителя.
- Вызов из рабочего процесса БЛ напрямую с минимальным таймаутом.
- Управление возвращается клиенту сразу после получения запроса исполнителем.

### Гарантированная доставка (AMQP / RBC)

- Обработан **не менее одного раза** — может быть повторён; число повторов задаётся `SetRepeatCnt`.
- Управление возвращается после подтверждения от брокера.
- Протоколы:
  - **AMQP** (по умолчанию) — через [[Wasaby-MQ]] / RabbitMQ.
  - **RBC** — через платформенный [[Request-Broker-Service]].

```python
ep = EndPoint('ОсновнойСервис', True, session)
# Переключить на RBC (AMQP по умолчанию)
ep.SetTransportProtocol('Async Request Broker', sbis.InteractionKind.AsyncInvokeWithGuarantee)
ep.SetRepeatCnt(10)
obj = BLObject('ЧастноеЛицо', ep)
obj.AsyncInvoke('ЗаписатьПерсональныеДанные', transData)
```

### Специализированный брокер (RBC)

Изолированный контур доставки для критичных запросов или высокого потока. Не зависит от основного брокера.

```python
rbc_settings = sbisrequestbrokerclient.RbcTransportProtocolSettings()
rbc_settings.BrokerName = 'custom_broker_name'
rbc_settings.HighDeliveryGuarantee = True   # хранить в резервном хранилище
ep.SetTransportProtocol(rbc_settings, sbis.InteractionKind.AsyncInvokeWithGuarantee)
```

Принимающий и вызывающий сервисы должны подписаться на брокер в обработчике загрузки модуля:
```python
import sbisrequestbrokerclient
def OnEndAllLoadModules(answer):
    sbisrequestbrokerclient.AddBrokerToListen('custom_broker_name')
```

## Приоритет доставки через брокер (`SetAsyncPriority`)

0 (наименьший) — 9 (наивысший). По умолчанию **2**.

| Значение | Применение |
|---|---|
| 2 | Фоновые задачи, никто не ждёт |
| 5 | Пользователь ждёт результата (например, загрузка файлов) |

```python
ep.SetAsyncPriority(8)  # значение определяет ответственный за ресурс
```

Получить приоритет внутри вызванного метода: `Session.GetHeader("X-AsyncPriority")` (None для синхронных, строка для асинхронных).

## Ограничения на размер запроса

> [!warning] Лимит 100 КБ
> - 100 КБ–1 МБ → предупреждение в логах.
> - > 1 МБ → критическое нарушение.
> - Передача файлов асинхронным вызовом с гарантией доставки **запрещена**.

Причины: мульти-мастер (каждый запрос сохраняется на все ноды), синхронизация нод, ограниченное дисковое хранилище брокера.

## Huge Payload Protocol (> 100 КБ)

При превышении порога данные автоматически выгружаются в [[File-Transfer-Service]], в запросе передаётся только ссылка. Принимающая сторона загружает данные прозрачно до вызова метода.

Модули: `HugePayload` (C++) / `HugePayload-Py` (Python). Нужно подключить на обеих сторонах.

```python
import hugepayload
e = EndPoint('service_name')
e.SetProtocol(hugepayload.GetHugePayloadRpcProtocol())
BLObject('object', e).AsyncInvoke('method', big_data)
```

## Порядок выполнения асинхронных вызовов

Порядок не гарантирован. Для явной последовательности — использовать цепочку через callback:

```python
obj = sbis.BLObject("Объект")
# Метод2 вызывается из обработчика успеха Метод1
obj.AsyncInvoke("Метод1", callbacks=["Объект.ОбработчикНаУспех"])
```

## Обработчики результата (Callbacks / Errbacks)

```python
obj = BLObject('НазваниеОбъекта')
obj.AsyncInvoke('НазваниеМетода', param,
    callbacks=('Объект.ОбработчикУспеха', 'Объект.ОбработчикОшибки', '{"report_id":42}'))
```

- Первый аргумент — callback (успех).
- Второй — errback (ошибка); `None` или `''` если не нужен.
- Третий — `КонтекстОперации` (JSON-строка, приходит в поле `context`).

### Параметры функций-обработчиков

| Параметр | Тип | Содержимое |
|---|---|---|
| `Метод` | `sbis.Record` | НазваниеМетода, Сессия, Сервис, ГруппаСерверов, request_uuid, context |
| `Параметры` | `sbis.Record` | Входные параметры вызова (обращаться по номеру, не имени) |
| `Результат` | `sbis.Record` | Результат успешного выполнения (только в callback) |
| `Ошибка` | `sbis.Record` | Ошибка, Сообщение, ДопИнфо, Ид, Type, ErrorCode (только в errback) |

> [!note]
> Платформа гарантирует: каждый обработчик вызывается ровно один раз. Обработка результата обработчиков не предусмотрена.

Повторить сериализуемое исключение в errback: `sbis.GenerateAsyncException()`.

## Очереди брокера

- **Основная**: `<UUID_облака>.<ИдГруппыСерверов>` (параметр `Ядро.Асинхронные сообщения.НазваниеОчереди`)
- **Ошибки**: `<основная>#error`
- **Отложенные**: `<основная>#delay<ВремяПовтора>`

Подробнее о шине — [[Wasaby-MQ]].

## Модули для асинхронных вызовов

Подключить сервисный модуль **BL Async** на вызывающей и вызываемой сторонах:

| Модуль | Роль |
|---|---|
| `BL Async` | Основной модуль |
| `AMQP Client` | Работа с RabbitMQ (при AMQP) |
| `RequestBrokerClient` | Работа с request-broker (при RBC) |
| `Berkeley DB` / `Berkeley Storage` | Локальное временное хранилище вызовов |
| `MessageBroker` | Базовый модуль для произвольного брокера |

## Связанные страницы

- [[Wasaby-BL-Objects]] — BL-объекты и их типы методов (CRUD, List, File, Remote)
- [[DWC-Distributed-Workflow-Coordinator]] — граф задач для сложных async-сценариев
- [[Sync-Broker]] — офлайн-облако синхронизация: работает поверх async-вызовов
- [[Wasaby-MQ]] — шина AMQP: детали протокола и именования очередей
