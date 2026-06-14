---
type: concept
title: "DWC Client Library v1 (Deprecated)"
updated: 2026-04-10
tags:
  - concept
  - wasaby
  - dwc
  - deprecated
  - api
status: deprecated
related:
  - "[[DWC-Distributed-Workflow-Coordinator]]"
  - "[[DWC-Migration-SDK]]"
created: 2026-04-10
---

# DWC Client Library v1 (Deprecated)

Navigation: [[DWC-Distributed-Workflow-Coordinator]] | [[DWC-Migration-SDK]]

> [!stale] Устарела!
> Это описание **старой версии** клиентской библиотеки DWC. Используйте **[[DWC-Distributed-Workflow-Coordinator]]** (v2, модуль `workflow2`).

---

## Подключение

**Python:** `import workflow`  
**C++ headers:** `#include <sbis-workflow-coordinator-client/workflow_service.hpp>` + `workflow.hpp` + `task.hpp`

---

## Сценарии

### Создание

```python
# Python
w = workflow.WorkflowService.Instance().CreateWorkflow(workflowName, serviceName)
```

```cpp
// C++
dwc::Workflow w = dwc::WorkflowService::Instance().CreateWorkflow(workflowName, serviceName);
```

- `name` — имя сценария, макс. 128 символов, без кавычек и спецсимволов
- `issuer` — системное имя сервиса-источника (должен быть в "Управлении облаком")
- Третий аргумент `True` → синхронная отправка (для >100 задач, ограничение RabbitMQ)

### Отправка на выполнение

```python
w.Commit(workflow.CommitPolicy.cpIMMEDIATELY)
```

Политики запуска:
- `cpIMMEDIATELY` — немедленно
- `cpON_TRANSACTION_COMMIT` — после завершения транзакции
- `cpON_REQUEST_FINISH` — после завершения метода БЛ

### Обязательные параметры

```python
w.SetResponsible("Иванов И.И.", "Отчетность")
```

`resp` и `group` — обязательны! Без них сценарий не отправится.

### Политика обработки ошибок

```python
w.SetErrorPolicy(workflow.ErrorPolicy.epCONTINUE)
```

- `epABORT` (по умолчанию) — прервать на первой ошибке
- `epCONTINUE` — пропускать задачи с ошибкой

### Обработчик ошибок (Errback)

```python
w.SetErrback(methodNameErrback, param1, ...)
w.SetErrbackUser(userId)  # для multitenancy сервисов
```

Метод: `"ИмяОбъектаБЛ.ИмяМетода"`, первый аргумент должен быть placeholder.

### Обработчик отмены пользователем

```python
w.SetCancellationErrback("Obj.CancellationErrback", "End over run")  # после всех задач
w.SetImmediateCancellationErrback("Obj.ImmediateErrback", "Just canceled")  # в точке отмены
```

### Приоритет сценария

```python
w.SetPriority(9)  # 0 (низший) — 9 (высший), по умолчанию 5
```

### Слияние сценариев

```python
w.SetMergePolicy(keyValue, workflow.MergePolicy.mpMERGE_ANY_STATE)
```

Политики слияния:
- `mpNO_MERGE` (по умолчанию) — без слияния
- `mpMERGE_ANY_STATE` — слить с любым (ожидающим или выполняемым)
- `mpMERGE_NOT_RUNNING` — слить только с ожидающим
- `mpMERGE_ARRAY` — объединить массивы первых аргументов

Ключ слияния — макс. 128 символов. Если задан ключ → политика должна ≠ `mpNO_MERGE`.

### Задержка запуска

```python
delay = datetime.datetime.now() + datetime.timedelta(minutes=20)
w.SetDelay(delay)  # макс. 62 дня
```

### Пакетная отправка

```python
batch = workflow.WorkflowService.Instance().CreateWorkflowBatch()
for i in range(0, 10):
    w = batch.CreateWorkflow(workflowName, serviceName)
    task = workflow.Task()
    task.service = serviceCloudName
    task.SetMethod(methodName, param)
    w.AddTask(task)
    w.Finalize()  # обязательно
batch.Commit(workflow.CommitPolicy.cpIMMEDIATELY)
```

---

## Задачи

### Создание и добавление

```python
task = workflow.Task()
task.service = serviceCloudName          # сервис-исполнитель
task.user = userId                       # для multitenancy
task.SetMethod("Obj.Method", param1, param2)  # имя + параметры
w.AddTask(task)
```

C++: добавление через `workflow << task;`

### Параметры задачи

| Параметр | Python | C++ | Значение |
|----------|--------|-----|----------|
| Приоритет | `task.priority = 100` | `task.SetPriority(100)` | 0–100, выполняется раньше при очереди |
| Таймаут | `task.SetTimeout(60)` | `task.SetTimeout(60)` | Минуты, default 3ч, max 4320 мин (3 дня) |
| Error recovery | `task.SetErrorRecoveryPolicy(retries, interval)` | same | Повторы при ошибке; max 10 retry, max 1500 мин interval |
