---
type: concept
title: "Сервис временных файлов (file-transfer)"
tags:
  - wasaby
  - infrastructure
  - storage
  - file-transfer
status: current
related:
  - "[[SabyDisk-Platform]]"
  - "[[FileStorage-Service]]"
  - "[[Binary-Storage-Options]]"
  - "[[Async-Calls-Bus]]"
  - "[[LRS-Long-Request-Service]]"
created: 2026-04-12
updated: 2026-04-12
---

# Сервис временных файлов (file-transfer)

Временное файловое хранилище с автоудалением по таймауту. Без резервирования и репликации.

## Две задачи

1. **Возврат результата длительной операции клиенту** (например, выгрузка в Excel через LRS)
2. **Передача файлов между сервисами БЛ** (Huge Payload Protocol в [[Async-Calls-Bus]])

## Хранилища (storage)

Трёхуровневая иерархия:
1. **Физическое хранилище** — путь к сетевому диску
2. **Группировка** — по прикладным областям (семействам)
3. **Логическое хранилище** — то, с чем работает пользователь API

Хранилища задаются через `dpack`-файлы. Конфигурируются в `file-transfer-admin` на `cloud.sbis.ru`.

Для добавления нового хранилища → задача на А. Демина (указать: название, ответственный, семейство, размер Гб, TTL, внешний доступ R/W, CDN-кэширование).

> [!note] Если внешняя запись разрешена — чтение должно быть запрещено (защита от вредоносных файлов).

Ограничение: имя файла ≤ **512 символов**.

## API

### Внутреннее API (из БЛ, через File-transfer client / SBIS SDK)

| Метод | Описание |
|---|---|
| `FileTransfer.Upload(file: RpcFile, storage: String) → String` | Загрузить файл; возвращает ID (`01917537...`) |
| `FileTransfer.Download(id, storage) → RpcFile` | Скачать по ID |
| `FileTransfer.Delete(id, storage)` | Удалить (ошибки нет если файл не найден) |

### Внешнее API (из браузера)

```
GET https://dev-online.sbis.ru/file-transfer/service/?method=FileTransfer.Download&params=<base64>
# или REST-стиль:
GET https://dev-online.sbis.ru/file-transfer/service/<storage>/<id>
```

Файл не удаляется при первом скачивании — удаляется по таймауту.

### REST API (chunked upload)

PUT/GET с форматом идентификатора `ГГГГММДДЧЧ-имя.расширение`. Поддерживает `Chunked transfer encoding`.

## Метрики (в мониторинг)

| Метрика | Частота |
|---|---|
| `filetransfer.storage.current_size` | 30 сек |
| `filetransfer.storage.size_limit` | 30 сек |
| `filetransfer.total_space` | 60 сек |

Теги: `resource`, `storage_name`, `owner`, `interval`.

## Режим обслуживания

При очистке/расширении хранилища:
1. Ожидание завершения текущих операций
2. Ответ `503 X-FileTransfer-Maintenance: <тип>` + `Retry-After: 3-5с`
3. Синхронизация всех процессов сервиса в режим обслуживания

Старые файлы удаляются **планировщиком задач**, не немедленно.
