---
address: c-000123
created: 2026-06-14
updated: 2026-06-14
type: concept
title: "Wasaby File Transfer Service (file-transfer)"
tags:
  - wasaby
  - backend
  - middleware
  - files
  - file-transfer
  - lrs
  - huge-payload
status: current
related:
  - "[[Wasaby-Long-Running-Operations]]"
  - "[[Wasaby-BL-Calls]]"
  - "[[Wasaby-Service-Framework]]"
sources:
  - ".raw/wasaby.Backend/Middleware/Системы хранения данных/Сервис временных файлов (file-transfer).pdf"
---

# Wasaby File Transfer Service (file-transfer)

`file-transfer` — сервис временных файлов. Файлы автоматически удаляются по таймауту (не сразу после скачивания). Два основных сценария:

1. **Возврат результата LRS клиенту** — например, выгрузка реестра в Excel (ResultLink в LRS)
2. **Передача файлов между сервисами БЛ** — Huge Payload Protocol

> **Ограничение**: имя файла не более **512 символов**.

## Хранилища

Трёхуровневая иерархия: **Физическое хранилище** → **Группировка по семействам** → **Логическое хранилище**

Логические хранилища и их настройки задаются через dpack-файлы. Просмотр в "Управление облаком" → File-Transfer.

Известные хранилища:

| Хранилище | Объём | Назначение |
|-----------|-------|------------|
| `excel` | 50 ГБ | Результаты выгрузки реестров в Excel |
| `huge_payload_storage` | 500 ГБ | Данные Huge Payload Protocol |
| `help_system` | 10 ГБ | Архивы маршрутов помощи |
| `email_storage` | — | Вложения для писем |

**Добавить новое хранилище**: задача на А. Демина с указанием имени (lowercase_underscores), ответственного, размера (Гб), времени хранения, доступности снаружи (read/write), нужности CDN-кэширования.

> Если внешняя запись разрешена → чтение снаружи должно быть запрещено (безопасность).

## Внутреннее API (из БЛ)

Подключить SDK-модуль **File-transfer client**.

```python
# Загрузка файла (RpcFile → временный ID)
file_id = FileTransferUpload(rpc_file, "excel")
# Возвращает текстовый ID вида: 01917537a4324a51bcf2d800081e927b

# Скачивание ранее загруженного файла
rpc_file = FileTransferDownload(file_id, "excel")
# Можно вызывать несколько раз — файл жив до таймаута

# Удаление файла
FileTransferDelete(file_id, "excel")
# Удаление несуществующего файла — не ошибка
```

## Внешнее API (для браузера / клиента)

**RPC-Download** (GET-запрос на сервис):
```
GET /file-transfer/service/?method=FileTransfer.Download&params=<base64_json>&id=0
```

**REST** (прогрессивный протокол):
```
GET /file-transfer/service/<storage>/<id>
# Пример:
GET /file-transfer/service/excel/2020100215fc1e1b3a214645979abea3a3e39698da
```

**REST PUT** (загрузка порциями, chunked transfer encoding):
```
PUT /file-transfer/service/<storage>/<YYYYMMDDЧЧ>-<name>.<ext>
```

## Связь с LRS

После завершения длительной операции последняя задача возвращает `Record` с `ResultLink` — ссылкой, которая сформирована через `PrepareGetRPCInvocationURL("FileTransfer.Download", params)` с `ResultValidUntil`. Пользователь скачивает файл, кликая на кнопку в UI.

Пример из [[Wasaby-Long-Running-Operations]]:
```python
params = Record()
params.AddString("id", ticket)   # file_id из FileTransferUpload
link = PrepareGetRPCInvocationURL("FileTransfer.Download", params)
```

## Связанные страницы

- [[Wasaby-Long-Running-Operations]] — ResultLink формируется через file-transfer
- [[Wasaby-BL-Calls]] — Huge Payload Protocol использует huge_payload_storage
