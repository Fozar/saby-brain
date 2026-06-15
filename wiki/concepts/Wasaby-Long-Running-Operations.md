---
address: c-000114
created: 2026-06-14
updated: 2026-06-14
type: concept
title: "Wasaby Long-Running Operations (LRS)"
tags:
  - wasaby
  - backend
  - lrs
  - long-running
  - workflow
  - middleware
status: current
related:
  - "[[Wasaby-BL-Calls]]"
  - "[[Wasaby-Service-Framework]]"
  - "[[LRS-Long-Request-Service]]"
sources:
  - ".raw/wasaby.Backend/Middleware/Длительные операции/Длительные операции.sabydoc"
  - ".raw/wasaby.Backend/Middleware/Длительные операции/Работа с длительными операциями на бизнес-логике.sabydoc"
---

# Wasaby Long-Running Operations (LRS)

LRS (Long Request Service) — сервис длительных операций Wasaby. Надстройка над DWC (Dispatcher Workflow Coordinator). Позволяет выполнять тяжёлые сценарии в фоне, отображая прогресс пользователю.

## Концепция

```
Пользователь запускает операцию
        ↓
LRS принимает WorkflowBuilder.Build() → ставит в очередь
        ↓
Задачи выполняются последовательно (по умолчанию) в пуле rpLOW
        ↓
UI получает обновления прогресса через push
        ↓
По завершении — уведомление, ссылка для скачивания или диалог
```

**Длительная операция** = упорядоченный набор задач (методов БЛ) + правила передачи данных между ними.

## Создание длительной операции (Python)

```python
import workflow2

# 1. Создать WorkflowBuilder с ID типа операции
w_builder = workflow2.WorkflowBuilder("Download")

# 2. Установить описание (отображается пользователю)
w_builder.SetDescriptionArgs("такого то реестра")

# 3. Настроить LongRequestSettings (опционально)
settings = workflow2.LongRequestSettings()
settings.SetCustomData({'type': 'export', 'id': 'b750d86e-...'})
w_builder.SetLongRequestSettings(settings)

# 4. Создать и настроить задачи
task = CreateTask("Excel.Download")
task.SetMethodArgs(doc_id)
task.SetDescriptionArgs("такой то страницы")
AddTask(task)

# 5. Отправить на выполнение
workflow2.Sender.AddWorkflow(w_builder.Build())
# или: workflow2.Sender.Commit(sbis.…)
```

## Конфигурация в метаданных (Genie)

Поле `.dwc`, атрибут `Workflow kind` = **Long request**.

| Атрибут метаданных | Описание |
|---|---|
| `Workflow kind = Long request` | Включает LRS, высокий приоритет |
| `Lrs has result` | Последняя задача должна вернуть Record с результатом |
| `Lrs result message tmpls` | Шаблон строки результата: `"Выгружено %1% записей"` |
| `Lrs show task log` | Always / Task failed only / Never |
| `Lrs result action visibility` | All / Popup panel / History |
| `Lrs description template` | Шаблон описания операции |
| `Lrs is modal` | Операция в модальном окне |

Описание задачи: если не задано → задача служебная, не отображается в журнале.

**Ограничение**: описание операции/задачи — не более 16 000 символов.

## Формат результата последней задачи

Последняя задача операции возвращает `Record` со следующими полями:

| Поле | Тип | Описание |
|------|-----|----------|
| `ResultLink` | Текст | Ссылка для скачивания файла |
| `ResultLinkCurrentTarget` | Boolean | `true` → скачать; `false` → открыть в новом окне |
| `ResultValidUntil` | DateTime | Срок действия ссылки |
| `ResultTmpl` | Текст | Путь до JS-функции (для кастомного диалога) |
| `ResultTmplParams` | JSON | Аргументы для `ResultTmpl` |
| `HasErrors` | Boolean | Помечает операцию ошибочной при успешном завершении |
| `UseResult` | Boolean | Показывать кнопку результата даже при ошибке |

```python
# Пример: результат со ссылкой на скачивание
import datetime

params = Record()
params.AddString("id", ticket)
link = PrepareGetRPCInvocationURL("FileTransfer.Download", params)
valid = datetime.datetime.now() + datetime.timedelta(hours=24)

record = Record()
record.AddString("ResultLink", link)
record.AddDateTime("ResultValidUntil", valid)
return record
```

## Прогресс и уведомления

```python
# Отправить текстовый статус в UI (внутри задачи)
workflow2.LongRequestNotify("Обработано 150 из 1000 записей")
```

Стандартный прогресс считается автоматически: выполнено задач / всего задач.

## Отмена из UI

При нажатии «Прервать» вызываются:
- `CancellationErrback` — штатная отмена
- `ImmediateCancellationErrback` — немедленная отмена

Задаются при создании `WorkflowBuilder`.

## Ограничения

- Длительная операция **должна** завершаться **одной** задачей (не блоком параллельного выполнения)
- Нельзя завершать параллельным блоком задач

## Управление для администратора

Меню: Настройки → Мониторинг → Длительные операции  
Администратор и Руководитель могут управлять чужими операциями.

## Связанные страницы

- [[Wasaby-BL-Calls]] — AsyncInvoke как альтернатива для простых фоновых задач
- [[Wasaby-Task-Queue]] — очередь задач для фоновой обработки
- [[LRS-Long-Request-Service]] — детальная документация LRS: шардирование, бесшовное обновление, схема БД
