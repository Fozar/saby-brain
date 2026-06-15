---
type: concept
title: "DWC - Distributed Workflow Coordinator (v2)"
updated: 2026-04-10
tags:
  - concept
  - wasaby
  - dwc
  - async
  - middleware
  - api
status: current
related:
  - "[[Wasaby-Framework]]"
  - "[[DWC-Client-Library-v1]]"
  - "[[DWC-Migration-SDK]]"
  - "[[price-formation/_index]]"
  - "[[Wasaby-DWC]]"
created: 2026-04-10
---

# DWC - Distributed Workflow Coordinator (v2)

Navigation: [[price-formation/_index]] | [[DWC-Migration-SDK]] | [[DWC-Client-Library-v1]] | [[Wasaby-DWC]]

**DWC (Distributed Workflow Coordinator)** — сервис для описания и выполнения сложных асинхронных бизнес-сценариев в кластерах сервисов СБИС.

**Python module:** `workflow2` | **C++ namespace:** `dwc2::` | **Headers:** `v2/workflow_builder.hpp`, `v2/sender.hpp`, `v2/task.hpp`

> [!note] v1 deprecated
> Старая версия (`workflow` / `dwc::`) устарела. Документация: [[DWC-Client-Library-v1]].

---

## Возможности

- Ограничение нагрузки на узлы кластера для класса задач
- Слияние одинаковых сценариев по ключу
- Отложенный запуск с задержкой (max 62 дня)
- Приоритеты выполнения (0–9 для сценариев, 0–100 для задач)
- Сценарии из вызовов методов БЛ на разных узлах кластера
- Отчёты о состоянии выполнения задач

---

## Ключевые понятия

**Сценарий** — упорядоченный набор задач с правилами передачи данных между ними.

**Задача** — вызов метода БЛ с параметрами, реквизитами пользователя и политикой запуска на одном из сервисов кластера.

**Метаданные (.dwc)** — ресурсный файл, описывающий сценарий и его задачи. Создаётся через контекстное меню сервисных модулей в IDE. После создания .dwc требуется редеплой стенда.

---

## Подключение API

```python
import workflow2
```

```cpp
#include <sbis-workflow-coordinator-client/v2/workflow_builder.hpp>
#include <sbis-workflow-coordinator-client/v2/sender.hpp>
#include <sbis-workflow-coordinator-client/v2/task.hpp>
```

Модули: `Workflow Coordinator Client` (C++) и `Workflow Coordinator Client Py` (Python) — оба в SBIS SDK.

---

## Сценарии

### Создание и отправка

```python
# Python
builder = workflow2.WorkflowBuilder(workflow_name)
# ... конфигурация через builder ...
w = builder.Build()
# ... создание задач ...
workflow2.Sender().AddWorkflow(w).Commit(sbis.PublicationPolicy.ppIMMEDIATELY)
```

```cpp
// C++
dwc2::WorkflowBuilder builder(workflow_name);
// ... конфигурация ...
dwc2::Workflow w = builder.Build();
// ... создание задач ...
dwc2::Sender::Commit(w);  // shortcut для одного сценария с ppIMMEDIATELY
// или
dwc2::Sender().AddWorkflow(w).Commit(PublicationPolicy::ppIMMEDIATELY);
```

`workflow_name` — макс. 128 символов, без кавычек и спецсимволов.

Политики запуска (`Sender::Commit`):
- `ppIMMEDIATELY` — немедленно
- `ppON_TRANSACTION_COMMIT` — после завершения транзакции
- `ppON_REQUEST_FINISH` — после завершения метода БЛ

### Метаданные сценария (.dwc)

Поля `.dwc` файла:

| Поле | Описание |
|------|----------|
| Name | Имя сценария (идентичен `workflow_name`) |
| Responsible | Ответственный разработчик |
| Application area | Прикладная зона (согласовать с Бойцовым Е.А.) |
| Workflow kind | `Background` / `Long request` / `User` |
| Merge policy | Политика слияния (см. ниже) |
| Merge key template | Шаблон ключа с плейсхолдерами `%1%`, `%2%` |
| Priority | 0–9, по умолчанию 5 |
| Error policy | `Abort` / `Continue` |
| Using errback | Флаг + имя метода + аргументы |
| Using extended errback | Расширенная ошибка через `sbis.Record` |
| Using cancellation errback | Обработчик отмены пользователем |
| Using immediate cancellation errback | Немедленный обработчик отмены |
| Is single task workflow | Оптимизация для сценариев с 1 задачей |
| Is using parallel blocks | Параллельное выполнение задач |
| Is using conditional blocks | Условные блоки |
| Is dynamic tasks enabled | Белый список, согласовать с Бойцовым Е.А. |
| Task infos | Реестр шаблонных задач |

### Политика слияния

Слияние основано на тройке: **имя сценария + ключ слияния + политика слияния**.

| Политика | Описание |
|----------|----------|
| No Merge (default) | Выполняются все копии |
| Merge any state | Слить с любым (ожидающим или выполняемым) |
| Merge not running | Слить только с ожидающим |
| Merge array | Объединить массивы первых аргументов |
| Merge with minimal delay | Слить с ожидающим, выполнить с минимальной задержкой |
| Runtime | Задаётся в коде через `SetMergePolicy` |

Runtime-слияние:

```python
builder.SetMergeKeyArgs(param1, ...)  # подстановки для шаблона ключа
```

### Обработчики ошибок (runtime-аргументы)

```python
builder.SetErrbackArgs(param1, ...)
builder.SetExtendedErrbackArgs(param1, ...)  # для extended errback
builder.SetCancellationErrbackArgs(param1, ...)
builder.SetImmediateCancellationErrbackArgs(param1, ...)
builder.SetErrbackUser(user_id)  # для multitenancy
```

Extended errback передаёт `sbis.Record` с полями: `Ошибка`, `Сообщение`, `ДопИнфо`, `Ид`, `Type`, `ErrorCode`.

### Приоритет сценария

```python
builder.SetPriority(9)  # 0 (низший) — 9 (высший), default 5
```

### Задержка запуска

```python
delay = datetime.datetime.now() + datetime.timedelta(minutes=20)
builder.SetDelayedUntil(delay)  # макс. 62 дня
```

### Максимальное время выполнения

```python
w = builder.Build()
w.SetMaxExpectedDurationInSeconds(300)  # при превышении DWC пишет в лог с именем ответственного
```

### Пакетная отправка

```python
sender = workflow2.Sender()
for i in range(10):
    builder = workflow2.WorkflowBuilder(workflow_name)
    # ... конфигурация ...
    w = builder.Build()
    # ... задачи ...
    sender.AddWorkflow(w)
sender.Commit(sbis.PublicationPolicy.ppIMMEDIATELY)
```

Объект `Sender` автоматически создаёт пакет при повторных вызовах `AddWorkflow()`.

---

## Задачи

### Создание

```python
w = workflow2.WorkflowBuilder(workflow_name).Build()
task = w.CreateTask(task_name)    # task_name = имя из метаданных Task infos
task.service = serviceCloudName   # сервис-исполнитель (если не в метаданных)
task.user = userId                # для multitenancy
task.SetMethodArgs(param1, ...)   # Runtime-аргументы метода БЛ
w.AddTask(task)
# Быстрое добавление (если всё задано в метаданных):
w.AddTask(task_name)
```

```cpp
dwc2::Workflow w = dwc2::WorkflowBuilder(workflow_name).Build();
dwc2::Task task = w.CreateTask(task_name);
task.SetService(L"service-name"_sv);
task.SetMethodArgs(param1, param2);
w.AddTask(task);
```

### Доступность метода задачи

- Сервис-инициатор = целевой сервис → **Trusted Application Contract** и выше
- Сервис-инициатор ≠ целевой сервис → **Service Contract** и выше
- **Internal** — недоступен снаружи в любом случае

### Метаданные задачи (Task infos в .dwc)

| Поле | Описание |
|------|----------|
| Name | Имя задачи |
| Method name | `ИмяОбъекта.ИмяМетода` |
| Method args | Runtime / Placeholder / Constant (JSON) |
| Service | Сервис-исполнитель (опционально, можно задать в коде) |
| Using error recovery policy | Флаг + retries + interval |
| Limit type / Limit key template | Ограничение параллельных задач |

### Параметры задачи

| Параметр | Python | C++ | Ограничение |
|----------|--------|-----|-------------|
| Приоритет | `task.priority = 100` | `task.SetPriority(100)` | 0–100 |
| Таймаут | `task.SetTimeout(60)` | same | Минуты, default 3ч, max 4320 мин |
| Error recovery | В метаданных (.dwc) | same | max 10 retry, max 1500 мин interval |

### Обмен данными между задачами

Результат предыдущей задачи → аргумент следующей через тип `Placeholder` в метаданных задачи.

---

## Использование в price-formation

```python
# DWC-Migration-SDK: Онлайн ставит DWC-задачи вместо событий
import workflow2
builder = workflow2.WorkflowBuilder("Card.HandleChangeData")
w = builder.Build()
task = w.CreateTask("card_handle_change_data")
task.service = "discount-cards"
task.SetMethodArgs(card_id, data)
w.AddTask(task)
workflow2.Sender().AddWorkflow(w).Commit(sbis.PublicationPolicy.ppIMMEDIATELY)
```

Ключевые ссылки:
- [[DWC-Migration-SDK]] — перевод 14 событий на DWC-задачи (дедлайн 30.04.2026)
- [[PassUpdater-Service]] — использует DWC для обновления образов карт
