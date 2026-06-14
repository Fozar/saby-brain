---
address: c-000115
created: 2026-06-14
updated: 2026-06-14
type: concept
title: "Wasaby Task Queue Service (plugin-task-queue)"
tags:
  - wasaby
  - backend
  - task-queue
  - middleware
  - async
status: current
related:
  - "[[Wasaby-BL-Calls]]"
  - "[[Wasaby-Long-Running-Operations]]"
sources:
  - ".raw/wasaby.Backend/Middleware/Сервис очереди задач (plugin-task-queue)/Пользовательская документация/API Сервис очереди задач.sabydoc"
---

# Wasaby Task Queue Service

`plugin-task-queue` — платформенный сервис диспетчеризации заданий между авторами и исполнителями. Общее решение для фоновой обработки задач.

## Концепция

```
Автор → Task.Create(задача, исполнитель)
              ↓
        plugin-task-queue (очередь)
              ↓
Исполнитель → Task.GetByDestinationList() → Task.Processing() → Task.CancelProcessing() / Task.ErrorProcessed()
```

## API для авторов задач

### Task.Create

Создать и добавить одну задачу в очередь.

```python
# Через BLObject
sbis.BLObject('Task', sbis.EndPoint('plugin-task-queue')).Invoke('Create', params)
```

Документация: [wi.sbis.ru/docs/bl/objects/.../Task/methods/Create(1)](https://wi.sbis.ru)

**Возможные ошибки:**
- `"Ошибка в поле '__', в строке '__'"` → некорректные данные задачи; проверить сигнатуру
- `"Задача с ключом __ не будет создана..."` → задача в WaitForTaskExec не найдена или в неверном статусе

### Task.CreateFromRecordSet

Создать несколько задач за один вызов. **Лимит: 256 задач за раз.**

```python
sbis.BLObject('Task', sbis.EndPoint('plugin-task-queue')).Invoke('CreateFromRecordSet', rs)
```

### Task.AbortWaitingForProcess

Прервать задачи, ожидающие выполнения.

### Task.StartDraftTasks / Task.StartWaitingTasks

Запустить задачи из состояния черновик / ожидание.

### Task.HasExecutor

Проверить наличие исполнителя для типа задачи.

## API для исполнителей

### Task.GetByDestinationList

Получить задачи, назначенные текущему исполнителю.

### Task.GetByTaskId

Получить задачу по ID.

### Task.Processing

Подтвердить, что задача взята в обработку.

### Task.CancelProcessing

Отменить обработку задачи (вернуть в очередь).

### Task.ErrorProcessed

Сообщить об ошибке при обработке задачи.

## Вспомогательные методы

| Метод | Описание |
|-------|----------|
| `Task.GetByClient` | Задачи по клиенту |
| `Task.GetStateByKeyList` | Статусы по ключам |
| `Task.PublishTaskListAvailableEvent` | Опубликовать событие о доступных задачах |
| `Task.Get` | **DEPRECATED** (удалён с 25.4100) |
| `Task.GetStateByIdList` | **DEPRECATED** |

## Уведомления об изменении статуса

Сервис публикует события при изменении статусов задач:
- Добавление задачи в очередь
- Завершение выполнения задачи

Подписка через платформенный механизм сервисных событий (STOMP / MessageBroker).

## Связанные страницы

- [[Wasaby-Long-Running-Operations]] — для пользовательских операций с прогресс-баром
- [[Wasaby-BL-Calls]] — AsyncInvoke для простых фоновых вызовов
