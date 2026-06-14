---
address: c-000120
created: 2026-06-14
updated: 2026-06-14
type: concept
title: "Wasaby Distributed Locks Service (distributed-locks)"
tags:
  - wasaby
  - backend
  - middleware
  - distributed
  - locks
  - concurrency
  - python
  - cpp
status: current
related:
  - "[[Wasaby-BL-Calls]]"
  - "[[Wasaby-Service-Framework]]"
  - "[[Wasaby-SQL-DBA]]"
sources:
  - ".raw/wasaby.Backend/Middleware/Сервис распределённых блокировок (distributed-locks)/Сервис распределённых блокировок (distributed-locks).sabydoc"
---

# Wasaby Distributed Locks Service

`distributed-locks` — сервис консультативных распределённых блокировок чтения/записи. Синхронизирует доступ к прикладным ресурсам в распределённой среде.

## Подключение

Добавить в сервис сервисные модули из SBIS SDK:
- **Distributed Locks** — C++ библиотека `sbis-distributed-locks`
- **Distributed Locks-Py** — Python модуль `distributed_locks`

```python
import distributed_locks
```

```cpp
#include <sbis-distributed-locks/read_lock.h>
#include <sbis-distributed-locks/write_lock.h>
#include <sbis-distributed-locks/detached_lock_ref.h>
#include <sbis-distributed-locks/lock_exception.h>
```

## Идентификатор ресурса (ResourceId)

```python
resource_id = distributed_locks.ResourceId(
    resource_class,   # имя прикладной области (напр. "MyUniqueLockClass")
    resource_key,     # ключ ресурса (напр. первичный ключ БД)
    dls_shard         # шард (необязательно; умолч. = основной)
)
```

> [!warning] Уникальность ключа — ответственность разработчика
> Библиотека не добавляет в ключ никаких реквизитов окружения (аккаунт, пользователь). В мультиарендных системах нужно явно включать account/scheme в `resource_key`, иначе возможно пересечение между аккаунтами.

- Длина класса и ключа: не более **128 символов**
- Символы `.` (точки) **запрещены** в обоих полях

## API блокировок

Одинаковый интерфейс для **ReadLock** (общий доступ, несколько держателей) и **WriteLock** (эксклюзивный).

### Методы захвата

| Метод | Поведение при занятости |
|-------|------------------------|
| `Acquire(resource_id, stop_token)` | Ждёт; бросает `LockException` при срабатывании stop_token |
| `TryAcquire(resource_id)` | Немедленно; возвращает `None` / `std::nullopt` |
| `AcquireImmediatelyOrThrow(resource_id)` | Немедленно; бросает `LockException` |
| `AcquireWithTimeout(resource_id, timeout)` | Ждёт не более timeout; не бросает |
| `AcquireWithTimeoutOrThrow(resource_id, timeout)` | Ждёт не более timeout; бросает |

```python
# Пример: WriteLock с ожиданием
write_lock = distributed_locks.WriteLock.Acquire(resource_id, stop_token)

# Пример: ReadLock — немедленный, без исключения
read_lock = distributed_locks.ReadLock.TryAcquire(resource_id)
if read_lock is None:
    # ресурс занят
    ...
```

### Освобождение

Освобождение — при выходе блокировки из области видимости (RAII в C++) или явным вызовом.

### "Отцепленные" ссылки (DetachedLockRef)

Механизм **передачи или разделения** владения эксклюзивной блокировкой без её освобождения — для конвейерной обработки:

```python
# Передать блокировку другому процессу/участнику:
detached_ref = write_lock.Detach()  # создать "отцепленную" ссылку
# ... передать detached_ref через очередь/параметр ...
restored_lock = distributed_locks.WriteLock.Restore(detached_ref)  # восстановить

# Закрыть отцепленную ссылку без восстановления:
detached_ref.Close()
```

## Связанные страницы

- [[Wasaby-SQL-DBA]] — advisory locks (PostgreSQL) как альтернатива для локальной БД
- [[Wasaby-Task-Queue]] — задачи с синхронизацией между исполнителями
- [[Wasaby-BL-Calls]] — вызов методов БЛ с использованием distributed-locks
