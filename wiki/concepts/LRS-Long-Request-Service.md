---
type: concept
title: "LRS — Long Request Service (Сервис длительных операций)"
updated: 2026-04-10
tags:
  - lrs
  - dwc
  - wasaby
  - middleware
status: current
related:
  - "[[DWC-Distributed-Workflow-Coordinator]]"
  - "[[DWC-Client-Library-v1]]"
  - "[[Wasaby-DB-Access-Patterns]]"
  - "[[price-formation/_index]]"
created: 2026-04-10
---

# LRS — Long Request Service (Сервис длительных операций)

Сервис LRS — надстройка над [[DWC-Distributed-Workflow-Coordinator]]. Запускает пользовательские операции в неблокирующем режиме: интерфейс не замерзает, пользователь видит прогресс и может управлять операциями.

---

## Термины

- **Длительная операция** — упорядоченный набор задач (Workflow kind = Long request в Genie).
- **Задача** — вызов метода бизнес-логики с параметрами, реквизитами пользователя и политикой запуска.

---

## Возможности

- Запуск сложных операций (множество подопераций-задач).
- Приостановка / удаление операций.
- Отображение статуса и прогресса пользователю.
- Результат — строка, ссылка для скачивания, ссылка для перехода.
- Разграничение прав: Администратор/Руководитель могут управлять чужими операциями.
- Панель управления: Настройки → Мониторинг → Длительные операции.
- Архив операций хранится **90 дней**.

---

## Архитектура

```
[Сервис облака] → (клиентская библиотека dwc)
    → [LRS: создаёт сценарий]
    → [DWC: вызывает задачи на целевых сервисах]
    → колбэки от сервисов → DWC → LRS (серверные события о задачах)
    → [Профиль-сервис] — данные пользователей для реестра
    → [dwc-dash] — статические настройки (WorkflowInfoStorage.GetWorkflowInfo), кэш в WorkflowClassCache
    → [БД LRS, шардированная] — хранение всех операций
```

**Жизненный цикл:**
1. Сервис получает операцию → записывает в БД, рассчитывает объём задач для прогресса → проксирует на DWC.
2. DWC исполняет задачи, LRS получает нотификации → обновляет прогресс.
3. После завершения — операция чистится на DWC, остаётся в БД LRS (90 дней).

**Модули:**
- `Long Requests Service` — зависимости: Cloud Interaction, BL Async, Db Manager, EventSubscription, Redis Client, BL Core, i18n.
- `Workflow Coordinator Client` — зависимости: Cloud Interaction, HugePayload, BL Core.
- `Workflow Coordinator Client Py` — зависимости: Python Core.

**Git:** `git.sbis.ru/sbis/middleware.git`, `git.sbis.ru/sbis/core.git`

---

## Создание длительной операции (BL)

### В Genie

1. Создать `.dwc` сценарий с `Workflow kind = Long request`.
2. При высоком приоритете выполнения, ход и результат отображаются пользователю.

**Флаги конфигурации:**
- `Lrs has result` — операция должна вернуть результат (последняя задача возвращает record).
- `Lrs result message tmpls` — шаблон строки результата, параметры через `%1%`.
- `Lrs show task log` — отображение журнала задач: Always / Task failed only / Never.
- `Lrs result action visibility` — где открывается результат: All / Popup panel / History.
- `Lrs description template` — шаблон описания операции. Без описания — задача служебная (не отображается, не считается в прогрессе).
- `Lrs is modal` — модальный режим. Панель LRS показывается только при закрытии окна.
- `Lrs modal expand enable` — открыть операцию повторно из панели.
- `Lrs modal tmpl` — шаблон для открытия модального окна (параметры через `LongRequestSettings.SetModalTmplParams`).

> [!warning] Ограничение
> Описание операции и задачи — не более 16 тыс. символов. При нарушении — исключение на сервисе-источнике.

> [!warning] Ограничение
> Длительная операция должна завершаться **одной задачей** с фиксированным форматом результата. Завершение блоком задач — недопустимо.

### SetCustomData (зарезервированные атрибуты)

```python
# Python
import workflow2
h = {'id': 'b750d86e-ab1e-11ea-bb37-0242ac130002', 'type': 'some_type'}
w_builder = workflow2.WorkflowBuilder("lr")
w_builder.SetCustomData(h)
```

```cpp
// C++
sbis::HashTable h;
h.FromString(L"{ id: \"b750d86e-ab1e-11ea-bb37-0242ac130002\", type: \"some_type\"}"_sv);
dwc2::WorkflowBuilder builder("lr");
builder.SetCustomData(h);
```

Зарезервированные атрибуты:
- `id` — UUID операции (используется, например, для отмены из кода).
- `type` — тип операции (фильтрация отображения по типу).

### Пример создания (Python)

```python
import workflow2

w_builder = workflow2.WorkflowBuilder("Download")
w_builder.SetDescriptionArgs("такого то реестра")
w = w_builder.Build()

task = w.CreateTask("Excel.Download")
task.SetMethodArgs(doc_id)
task.SetDescriptionArgs("такой то страницы")
w.AddTask(task)

workflow2.Sender().AddWorkflow(w).Commit(sbis.PublicationPolicy.ppIMMEDIATELY)
```

---

## Формат результата операции

Последняя задача должна вернуть `Record` с полями:

| Поле | Тип | Описание |
| --- | --- | --- |
| `ResultLink` | String | Ссылка для скачивания файла. Использовать `sbis.PrepareGetRPCInvocationURL()`. |
| `ResultLinkCurrentTarget` | Boolean | `true` — загрузить файл, `false` — открыть в новом окне. |
| `ResultValidUntil` | DateTime | Дата истечения ссылки. После истечения — "Операция устарела. Выполните повторно". |
| `ResultTmpl` | Text | Путь до функции: `MyArea/MyComponent:myPublicMethod`. Импортируется автоматически. |
| `ResultTmplParams` | JSON | Аргументы для `ResultTmpl`. |
| `HasErrors` | Boolean | `true` — пометить операцию ошибочной при успешном завершении (красная плашка). |
| `UseResult` | Boolean | `true` — использовать `ResultTmpl`/`ResultLink` даже при ошибочном завершении. |

> [!note] Приоритет
> Если заданы `ResultTmpl` и `ResultLink` — приоритет у `ResultTmpl`. Если ничего не задано — кнопка результата не отображается.

### Пример возврата результата (Python)

```python
import datetime
params = Record()
params.AddString("id", ticket)
link = PrepareGetRPCInvocationURL("FileTransfer.Download", params, 0, "/file-transfer/service/")
valid = datetime.datetime.now() + datetime.timedelta(hours=1)
record = Record()
record.AddString("ResultLink", link)
record.AddDateTime("ResultValidUntil", valid)
return record
```

---

## Статус и прогресс

- Стандартный механизм: процент = выполненные задачи / всего задач.
- Для кастомного прогресса: `LongRequestNotify()` (вызывается только внутри задачи LRS). Прогресс отображается в текстовом формате.
- Текст в подвале диалога: аргумент `LongRequestNotify()` — текст, который будет отображён.

---

## Прерывание операции

- Кнопка "Прервать" → вызываются errback-методы с сообщением `"Manually canceled"`.
- Кнопка "Прервать все" — если запущено несколько процессов одновременно.

---

## Локализация

Локализации подлежат:
- `Task.SetDescriptionArgs`
- `Workflow.SetDescriptionArgs`
- `LongRequestSettings.SetResultLinkText`
- Уведомления через `LongRequestNotify()`

Перегрузки функций принимают шаблон + аргументы. Шаблон: `%1%` — первый аргумент (нумерация с 1). `%%` — литеральный `%`. Локализуемые строки добавляются в словарь переводов сервисного модуля.

```python
# Пример с параметром
settings.SetResultLinkText("Текст с параметром %1% %2%", "Параметр1", workflow2.Loc("Локализуемый параметр"))
```

---

## Поиск в логах (UUID-цепочка)

При работе с LRS UUID вызывающего метода **не сохраняется** в сценарии. Схема поиска:

1. Найдите логи цепи, которая сгенерировала сценарий.
2. Скопируйте UUID сценария от метода, который **инициирует** сценарий.
3. В "Управление облаком" → поле **ID запроса / ID стека** → вставьте UUID, в поле **Текст** → `log_id:`.
4. Результат — логи исполнения сценария.

При обычных вызовах (без LRS) UUID пробрасывается транзитивно независимо от типа вызова.

---

## Бесшовное обновление

Механизм обеспечивает работу LRS при обновлении мастер-реплики или обслуживании БД.

**3 режима:**

1. **Нормальный** — БД основная, redis не используется, асинхронная очередь разбирается.
2. **Обновления** — БД только на чтение, асинхронные запросы накапливаются, новые задачи → redis.
3. **Синхронизации** — после обновления, фоновый разбор redis, незасинхронизированные сценарии читаются из redis.

**Критерии перехода в режим обновления:**
- `dbi::GetConnectedDataDB()->IsReadOnly()` = true (мастер-реплика).
- Параметр `Distributed Workflow Coordinator.Config.ReadOnlyMode` = true.

**Методы, использующие redis при обновлении:**
`LongRequests.Create`, `AddTasks`, `Commit`, `FastCreate`, `Cancel`, `Notify`

**Ручная активация (для обслуживания БД, не более ~5 минут):**
1. `Long Requests Service.Config.ReadOnlyMode` → Да → зафиксировать.
2. Перезапустить БЛ сервиса последовательно.
3. Производим необходимые работы.
4. `ReadOnlyMode` → Нет → зафиксировать.
5. Перезапустить БЛ последовательно.

---

## Шардирование БД

Сервис работает с несколькими БД, таблицы поделены на секции.

**Правило распределения по client ID:**
- Правые 6 бит → индекс виртуального шарда (0–63).
- Левые 4 бита из правых 10 бит → индекс секции.

64 виртуальных шарда, несколько виртуальных могут указывать на один физический (для масштабирования). Маршруты задаются в `Long Requests Service.Config.DBRoutes` (JSON):

```json
{
  "0": "0-15",
  "1": "16-30,31",
  "2": "32-61",
  "3": "62,63"
}
```

Именование узлов: `{name}{i}` где `i` — индекс шарда от 0 без пропусков.

**Добавление новой БД:**
1. Перевести в режим бесшовного обновления.
2. Отредактировать `DBRoutes`, применить конфиг.
3. Вывести из режима обновления.

---

## Схема БД и типовые выборки

**Таблицы:**
- `LongRequests` — операции (Workflow, Client, User, State, StartTime, ExecuteTime, IsModal, FinishTime).
- `OperationHistory` — задачи операции (LongRequests FK, Time).
- `WorkflowClassCache` — кэш метаданных по Name и HashName.
- `ShardingRoutes` — история маршрутов шардов.

**Ключевые выборки:**
1. Операции по Workflow (для интерфейса): фильтр `LongRequests.Workflow`.
2. Задачи операции: `OperationHistory.LongRequests`.
3. Операции клиента по State + User + StartTime DESC.
4. Очистка устаревших: `FinishTime` старше 90 дней.
5. Операции по State > 0, StartTime + ExecutedTime DESC (модальные/немодальные).
6. Удаление данных пользователя при его удалении.
7. Удаление операций > 90 дней.
8. Подвисшие операции (запущены, но не завершены).
9. Метаданные по имени (карточка интерфейса).
10. Метаданные конкретной операции.

---

## Публичное API

- Серверное: `https://wi.sbis.ru/doc/platform/developmentapl/middleware/long-request-service/`
- Клиентское (UI-часть): `https://wi.sbis.ru/doc/platform/developmentapl/middleware/long-request-service/#visual`
