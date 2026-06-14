---
address: c-000105
title: "Wasaby BL Async/Sync Cloud Calls"
aliases: ["BLObject AsyncInvoke", "async bl call", "EndPoint auth", "HugePayload Protocol"]
tags: [wasaby, bl, async, cloud, rpc, python, cpp]
source: ".raw/Синхронный и асинхронный вызов метода БЛ в облаке.md"
created: 2026-06-12
---

# Wasaby BL Async/Sync Cloud Calls

Документация: https://link.sbis.ru/article/5fed7326-90f0-4bdf-8e34-af8b04dfd93e

Вызов методов БЛ в облаке бывает синхронным (ждём результат) и асинхронным (не ждём). По типу сервиса: локальный (тот же сервис) или удалённый (другой сервис). Протоколы: AMQP, RBC или HTTP/HTTPS — выбор зависит от настроек EndPoint.

## Модули

Подключить `BL Async` в состав сервисов (на обеих сторонах):
- `AMQP Client` — если протокол AMQP (RabbitMQ)
- `RequestBrokerClient` — если протокол RBC (request-broker)
- `BL Async` — основной модуль
- `Berkeley DB` + `Berkeley Storage` — временное хранилище на основе Berkeley DB
- `MessageBroker` — базовый модуль для произвольного брокера

## Типы вызовов

### Локальный вызов

`EndPoint` не используется (или передаётся пустая строка). Выполнение в том же сервисе.

```python
obj = BLObject('НазваниеОбъекта')

# Синхронный — текущий процесс и поток
result = obj.Invoke('НазваниеМетода', param1, param2)
# Альтернатива:
result = НазваниеОбъекта.НазваниеМетода(param1, param2)

# Асинхронный — любой процесс того же сервиса (возможно, другой сервер)
obj.AsyncInvoke('НазваниеМетода', param1, param2)
```

```cpp
bl::Object object(L"НазваниеОбъекта");
int result = object.Invoke<int>(L"НазваниеМетода", param1, param2);  // sync
object.AsyncInvoke(L"НазваниеМетода", param1, param2);               // async
```

### Удалённый вызов

`EndPoint` обязателен. Выполнение в другом сервисе облака.

```python
ep = EndPoint('НазваниеСервисаПриложения')
obj = BLObject('НазваниеОбъекта', ep)

result = obj.Invoke('НазваниеМетода', param1, param2)   # sync
obj.AsyncInvoke('НазваниеМетода', param1, param2)        # async

# Новый стиль (chain):
result = EndPoint('telephony').Phonebook.ReadNumber(param1, param2)
```

```cpp
blcore::EndPoint ep{L"НазваниеСервисаПриложения"};
blcore::Object obj{L"НазваниеОбъекта", ep};
int result = obj.Invoke<int>(L"НазваниеМетода", param1, param2);
obj.AsyncInvoke(L"НазваниеМетода", param1, param2);
```

**Внимание**: вызов по абсолютному URL (а не системному имени) — политики аутентификации (`AuthByUserID` и др.) не работают.

## Аутентификация при удалённом вызове

`EndPoint` принимает параметр `auth_data`:

| Политика | Смысл |
|---|---|
| `AuthByClientID` | по прямому идентификатору клиента в облаке |
| `AuthByExtID` | по внешнему идентификатору клиента из биллинга |
| `AuthByUserID` | по прямому идентификатору пользователя клиента |
| `AuthByLogin` | по логину пользователя клиента в облаке |

```python
ep = EndPoint(service_name='online', auth_data=AuthByUserID(myId))
response = BLObject('MyBLOName', ep).Invoke('MyMethodName', param1, param2)
# Новый стиль:
response = ep.MyBLOName.MyMethodName(param1, param2)
```

```cpp
#include <sbis-lib/sbis-cloud-interaction/auth/user_id_auth_policy.hpp>
bl::EndPoint ep(L"online", AuthByUserID(myId));
String response = bl::Object(L"MyBLOName", ep).Invoke<String>(L"MyMethodName", param1, param2);
```

Если сессия не установлена явно — используется текущая сессия. Для "персональных" сервисов при каждом вызове нужно явно задавать пользователя/клиента.

## Приоритеты вызовов

| Приоритет | Описание |
|---|---|
| `rpNORMAL` (по умолчанию) | нормальный приоритет, основной пул — для быстрых методов |
| `rpLOW` | пониженный, служебный пул — для фоновых / долгих методов |

**Все асинхронные вызовы** всегда имеют приоритет `rpLOW` (служебный пул). Это изменить нельзя.

### SetAsyncPriority — приоритет в очереди брокера

```python
ep.SetAsyncPriority(8)  # 0 (наименьший) — 9 (наивысший), по умолчанию 2
```

- Если вызван `SetPriority(rpNORMAL)`, то `SetAsyncPriority` автоматически = 5.
- Читать приоритет внутри вызванного метода: `Session.GetHeader("X-AsyncPriority")` (для синхронного → `None`, для асинхронного → строка с числом).
- Callback-и выполняются с тем же приоритетом, что и основной вызов.

## Типы доставки асинхронных вызовов

### Негарантированная доставка (по умолчанию)

Протокол HTTP/HTTPS. Вызов обрабатывается не более одного раза — может быть утерян при остановке сервиса. Управление возвращается после получения запроса исполнителем (до передачи в обработку).

### Гарантированная доставка

Протокол AMQP (RabbitMQ) или RBC (request-broker). Обрабатывается не менее одного раза — при сбое повторяется. Управление возвращается после подтверждения приёма от брокера.

```python
ep = EndPoint('ОсновнойСервис', True, session)

# AMQP по умолчанию. Для RBC:
ep.SetTransportProtocol('Async Request Broker', sbis.InteractionKind.AsyncInvokeWithGuarantee)

# Число повторений при ошибке:
ep.SetRepeatCnt(10)

ep.SetAsyncPriority(8)
obj = BLObject('ЧастноеЛицо', ep)
obj.AsyncInvoke('ЗаписатьПерсональныеДанные', transData)
```

```cpp
auto ep = EndPoint(L"ОсновнойСервис", true, session);
ep.SetTransportProtocol(rbc::RBC_PROTOCOL, rpc::InteractionKind::AsyncInvokeWithGuarantee);
BLObject(L"ЧастноеЛицо", ep).AsyncInvoke(L"ЗаписатьПерсональныеДанные", transData);
```

### Специализированный брокер

Изолированный контур доставки для критичных/высоконагруженных механизмов. При аварии основного брокера продолжает работать и наоборот.

```python
ep = EndPoint('ОсновнойСервис', True, session)
rbc_settings = sbisrequestbrokerclient.RbcTransportProtocolSettings()
rbc_settings.BrokerName = 'custom_broker_name'
rbc_settings.HighDeliveryGuarantee = True  # повышенная гарантия (резервное хранилище + повтор)
ep.SetTransportProtocol(rbc_settings, sbis.InteractionKind.AsyncInvokeWithGuarantee)
obj = BLObject('ЧастноеЛицо', ep)
obj.AsyncInvoke('ЗаписатьПерсональныеДанные', transData)
```

```cpp
auto rbc_settings = std::make_unique<rbc::RbcTransportProtocolSettings>();
rbc_settings->SetBrokerName(L"custom_broker_name");
ep.SetHighDeliveryGuarantee(true);
ep.SetTransportProtocol(std::move(rbc_settings), rpc::InteractionKind::AsyncInvokeWithGuarantee);
```

**Подписка на специализированный брокер** — делается в обработчике загрузки модуля (основные брокеры подписываются автоматически):

```python
import sbisrequestbrokerclient

def OnEndAllLoadModules(answer):
    sbisrequestbrokerclient.AddBrokerToListen('custom_broker_name')
```

```cpp
#include <sbis-request-broker-client/rbc_transport_protocol_settings.hpp>

struct SomeInitializer : ld::ModuleInitializerHandle {
    bool OnEndLoadModules(EndLoadEventAnswer&) const override {
        rbc::AddBrokerToListen(L"custom_broker_name"_sv);
        return true;
    }
};
```

## Ограничения на размер тела запроса (гарантированная доставка)

**Лимит: 100 КБ.** При превышении:
- 100 КБ — 1 МБ: запись `Предупреждение` в лог.
- >1 МБ: запрещено (передача файлов асинхронным вызовом с гарантией доставки запрещена).

Причины: брокер — мульти-мастер (каждый запрос сохраняется на диск на всех нодах), большие запросы замедляют синхронизацию, хранилище брокера небольшое.

## Huge Payload Protocol (для данных >100 КБ)

Данные автоматически выгружаются на Сервис временных файлов (file-transfer), в запросе передаётся ссылка. На вызываемой стороне данные загружаются до передачи в метод — прозрачно для кода.

Модули: `HugePayload` (C++) и `HugePayload-Py` (Python). Подключить в оба сервиса (вызывающий и вызываемый).

```python
import hugepayload
e = EndPoint('service_name')
e.SetProtocol(hugepayload.GetHugePayloadRpcProtocol())
BLObject('object', e).AsyncInvoke('method', big_data)
```

```cpp
#include <sbis-huge-payload-protocol/protocol_traits.hpp>
#include <sbis-bl-core/object.hpp>

blcore::EndPoint e(L"service_name");
e.SetProtocol<rpc::HugePayloadRpcProtocol>();
blcore::Object(L"object", e).AsyncInvoke(L"method", big_data);
// cmake: sbis_add_sdk_dependencies(sbis-huge-payload-protocol)
```

## Callbacks — обработка результатов асинхронного вызова

Порядок выполнения нескольких `AsyncInvoke` не гарантирован. Для цепочки: первый вызов → callback → второй вызов.

```python
obj = BLObject('НазваниеОбъекта')

# callback + errback
obj.AsyncInvoke('Метод', param, callbacks=('Объект.ОбработчикУспеха', 'Объект.ОбработчикОшибки'))

# только callback
obj.AsyncInvoke('Метод', param, callbacks=('Объект.ОбработчикУспеха',))

# без callback, с errback и контекстом операции
obj.AsyncInvoke('Метод', param, callbacks=('', 'Объект.ОбработчикОшибки', '{"report_id":42, "attachment_id":12}'))

# без errback, с контекстом
obj.AsyncInvoke('Метод', param, callbacks=('Объект.ОбработчикУспеха', '', '{"report_id":42}'))
```

```cpp
bl::Object obj(L"НазваниеОбъекта");
// первый аргумент — callback, второй — errback (nullptr если не нужен)
obj.AsyncInvoke(L"НазваниеМетода", param,
    bl::Callbacks(L"Объект.ОбработчикУспеха", L"Объект.ОбработчикОшибки"));
```

**Контекст операции** (3-й параметр) — произвольная строка (JSON), приходит в поле `context` обработчика. Используется, чтобы понять, к какой операции относится callback.

### Параметры функций-обработчиков

| Параметр | Тип | Поля |
|---|---|---|
| 1. Метод | `sbis.Record` | `НазваниеМетода`, `Сессия`, `Сервис`, `ГруппаСерверов`, `request_uuid`, `context` |
| 2. Параметры | `sbis.Record` | обращаться по номерам (`r[0]`), т.к. имена могут отсутствовать |
| 3. Результат | `sbis.Record` | результат выполнения метода |
| 4. Ошибка (errback) | `sbis.Record` | `Ошибка` (details), `Сообщение` (message), `ДопИнфо`, `Ид`, `Type`, `ErrorCode` |

Платформа гарантирует вызов обработчика ровно один раз. Повторить исключение из errback: `GenerateAsyncException()`.

### Пример errback (запись в лог планировщика)

```python
@staticmethod
def MyHandlr(Метод, Параметры, Ошибка):
    SqlQuery(
        """update scheduler_log set reply_date = now(),
           reply_stage = 2,
           reply_status = $1 where task_uuid = $2::uuid""",
        'Выполнение завершилось с ошибкой: ' + Ошибка.Ошибка,
        Метод.request_uuid
    )
```

## Очереди брокера

### Основная очередь

Формат: `<UUID_Облака>.<ИдГруппыСерверов>` (всё в нижнем регистре).

- `UUID_Облака` — таблица `ServiceGuid` в БД управления облаком; в конфигурации: `Ядро.Асинхронные сообщения.ИдентификаторОблака`
- `ИдГруппыСерверов` — шестнадцатеричный ID группы серверов; в конфигурации: `__sbis__group_id`

Пример: `Ядро.Асинхронные сообщения.НазваниеОчереди=4704ea8e-22b9-40e0-96c9-c18a4ec6ceb2.00000008`

### Прочие очереди

- Очередь ошибок: `<ИмяОсновнойОчереди>#error`
- Отложенные: `<ИмяОсновнойОчереди>#delay<ВремяПовтора>`

При критической ошибке (падение процесса с дампом) задача помещается в `#error`. Повторная обработка не автоматическая — разработчик вручную перемещает задачи обратно после исправления.

## Сценарии обработки результата

| Сценарий | Описание |
|---|---|
| Без обработки | Штатно для негарантированной доставки |
| Критическая ошибка без errback | Аварийный сценарий: запись в лог + задача в `#error` |
| Только errback | Срабатывает при ошибке выполнения |
| Только callback | Срабатывает при успехе |

При заданном числе повторов (`SetRepeatCnt(N)`) — errback вызывается только после исчерпания всех попыток.

## Связанные страницы

- [[Wasaby-BL-Methods]] — базовые методы БЛ
- [[Wasaby-BL-Objects]] — BLObject, объекты БЛ
- [[DWC-Distributed-Workflow-Coordinator]] — DWC как альтернатива для сложных workflow
- [[Sync-Broker]] — синхронный брокер Tensor
