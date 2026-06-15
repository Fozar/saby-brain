---
address: c-000137
created: 2026-06-14
updated: 2026-06-14
type: concept
title: "Wasaby DWC — Distributed Workflow Coordinator"
tags:
  - wasaby
  - middleware
  - async
  - workflow
  - backend
status: current
related:
  - "[[Wasaby-Request-Broker]]"
  - "[[Wasaby-MQ]]"
  - "[[Wasaby-Scheduler]]"
  - "[[DWC-Distributed-Workflow-Coordinator]]"
sources:
  - ".raw/wasaby.Backend/Middleware/Сервис DWC/Сервис DWC.sabydoc"
  - ".raw/wasaby.Backend/Middleware/Сервис DWC/Как встраивать (API сервиса DWC).sabydoc"
---

# Wasaby DWC

**Distributed Workflow Coordinator** — сервис для описания и выполнения сложных асинхронных бизнес-сценариев в кластерах сервисов СБИС.

## Ключевые понятия

| Термин | Описание |
|--------|----------|
| **Сценарий** | Упорядоченный набор задач и правил передачи данных между ними (граф задач) |
| **Задача** | Метод БЛ, вызываемый в рамках сценария с заданными параметрами, реквизитами пользователя и политиками запуска |

## Задачи DWC

- Выполнение сложных async бизнес-сценариев (граф задач) в облаке
- Ограничение нагрузки параллельных вызовов на сервисы (rate limiting)
- Уменьшение количества вызовов на юнит: слияние вызовов, удаление ненужных повторяющихся
- Отложенное исполнение сценариев
- Предоставление статистики по классам сценариев

## Принцип работы

1. Через клиентскую библиотеку DWC настраивается **сценарий**: граф задач (последовательных и/или параллельных) с ограничениями нагрузки на целевые сервисы
2. Исполнение делегируется сервису DWC
3. DWC выполняет вызовы на сервисы облака в асинхронной манере, соблюдая порядок задач и ограничения нагрузки; организует очереди при превышении лимитов

## Python API (`workflow2`)

```python
import workflow2

# Создать сценарий
builder = workflow2.WorkflowBuilder(workflow_name='MyScenario')
workflow = builder.Build()

# Добавить задачи
builder.AddTask(task)           # из объекта задачи
builder.AddTask('TaskName')     # задача описана в .dwc метаданных

# Отправить в DWC
workflow2.Sender().AddWorkflow(workflow).Commit(sbis.PublicationPolicy.ppIMMEDIATELY)
```

## C++ API (`dwc2`)

```cpp
dwc2::WorkflowBuilder builder(name);
auto wf = builder.Build();
// добавить задачи...
dwc2::Sender::Commit(wf, ppIMMEDIATELY);
```

## Политики публикации

| Политика | Описание |
|----------|---------|
| `ppIMMEDIATELY` | Отправить немедленно |
| `ppON_TRANSACTION_COMMIT` | После коммита транзакции БД |
| `ppON_REQUEST_FINISH` | После завершения текущего BL-запроса |

## Метаданные сценария (.dwc файл)

| Поле | Описание |
|------|---------|
| `Name` | ≤128 символов, без кавычек |
| `Comments` | Описание |
| `Responsible` | Ответственный |
| `Application area` | Область применения |
| `Workflow kind` | `Background` / `Long request` / `User` |
| `Merge policy` | Политика слияния (см. ниже) |
| `Priority` | 0–9, по умолчанию 5 |
| `Is single task workflow` | Флаг одиночной задачи |
| `Is using parallel blocks` | Параллельное выполнение |
| `Is using conditional blocks` | Условное выполнение |
| `Is dynamic tasks enabled` | Динамические задачи (требует whitelist; согласовать с Бойцов Е.А.) |

### Политики слияния (Merge policy)

| Политика | Поведение |
|----------|-----------|
| `No Merge` | Не сливать |
| `Merge any state` | Слить в любом состоянии |
| `Merge not running` | Слить если не выполняется |
| `Merge array` | Слить массивом |
| `Merge with minimal delay` | Слить с минимальной задержкой |
| `Runtime` | Определяется в runtime |

## Возможности задач

- Параллельные блоки
- Условные блоки
- Итеративные задачи
- Таймауты
- Ресурсные лимиты
- Динамические задачи (whitelist)
- Отсоединённые задачи (detached)

## Связанные страницы

- [[Wasaby-Request-Broker]] — более простой async-брокер с per-request статусом (используется DWC/Scheduler)
- [[Wasaby-MQ]] — RabbitMQ шина, базовый транспорт async-вызовов
- [[Wasaby-Scheduler]] — планировщик задач (Create through Genie)
- [[Wasaby-Mass-Mailings]] — массовые рассылки: выполняются через DWC per subscriber
- [[DWC-Distributed-Workflow-Coordinator]] — DWC v2: детальный API, WorkflowBuilder, политики слияния (price-formation)
