---
address: c-000134
created: 2026-06-14
updated: 2026-06-14
type: concept
title: "Wasaby Multimedia Loader — загрузка файлов из интернета"
tags:
  - wasaby
  - middleware
  - files
  - download
  - antivirus
  - backend
status: current
related:
  - "[[Wasaby-File-Transfer]]"
  - "[[Wasaby-BL-Calls]]"
sources:
  - ".raw/wasaby.Backend/Middleware/Сервис скачивания внешних медиа ресурсов (multimedia-loader)/Инструкции по использованию API сервиса multimedia-loader.sabydoc"
---

# Wasaby Multimedia Loader

`multimedia-loader` — сервис загрузки файлов из интернета по URL с проверками (MIME-тип, размер, антивирус) и опциональной загрузкой на file-transfer или SbisDisk.

## API

### MultimediaLoader.Get/1 — простая загрузка

```cpp
// C++
auto url = "https://example.com/image.png";
auto result = blcore::Object("MultimediaLoader", "test-multimedia-loader")
    .Invoke<Record>("Get", url);
// result["url"]   — актуальная ссылка
// result["file"]  — RpcFile с данными
// result["status"]["success"]        — bool
// result["status"]["msg"]            — описание ошибки
// result["status"]["pipeline_status"] — MimeType/ResourceSize/Antivirus...
```

### MultimediaLoader.Get/2 — с параметром link_only

```cpp
auto result = blcore::Object("MultimediaLoader", "test-multimedia-loader")
    .Invoke<Record>("Get", url, false /* link_only */);
// link_only=true — вернуть только ссылку (без передачи бинарных данных)
```

### MultimediaLoader.GetWithPipeline/2 — с конвейером операций

Позволяет задать кастомный набор проверок и действий.

**C++** (через библиотеку из модуля `MultimediaLoader Lib`):
```cpp
auto pipeline = pipeline::Pipeline();
pipeline.Add(pipeline::MimeType("doodle"));
pipeline.Add(pipeline::ToFileTransfer());
pipeline.ReturnOnlyLink();

auto result = blcore::Object("MultimediaLoader", "test-multimedia-loader")
    .Invoke<Record>("GetWithPipeline", url, pipeline.ToHashTable());
```

**Python** (через JSON напрямую):
```python
pipeline = {
    "is_return_only_link": True,
    "operations": [
        {"name": "ToFileTransfer", "enable": True, "storage_name": "my-storage"}
    ]
}
result = sbis.BLObject("MultimediaLoader", sbis.EndPoint("test-multimedia-loader"))\
    .Invoke("GetWithPipeline", url, pipeline)
```

## Параметры pipeline (JSON)

| Поле | Тип | Описание |
|------|-----|----------|
| `is_return_only_link` | bool | Вернуть только ссылку без файла |
| `is_our_sequence_order` | bool | Сменить порядок операций на переданный (осторожно!) |
| `is_only_ours` | bool | Применять ТОЛЬКО операции из pipeline, без базовой конфигурации (осторожно!) |
| `operations` | Array | Список операций (см. ниже) |

### Операции конвейера

| Операция (name) | Параметры | Описание |
|-----------------|-----------|----------|
| `DownloadTimeout` | `download_timeout` (мс) | Таймаут загрузки |
| `MediaMaxSize` | `media_max_size` (байты) | Максимальный размер файла |
| `Antivirus` | `use` (bool) | Проверка антивирусом |
| `MimeTypes` | `mime_types` (str[]) | Проверка допустимых MIME-типов |
| `ToFileTransfer` | `enable`, `storage_name` | Загрузить на file-transfer |
| `ToSbisDisk` | `enable`, `path` | Загрузить на SbisDisk |

### Логика конвейера

По умолчанию: базовая конфигурация сервиса + переданные операции в конец.

- `is_our_sequence_order=true` — порядок из pipeline, отсутствующие → в начало
- `is_only_ours=true` — только операции из pipeline (отсутствующие в конфиге пропускаются)

> [!warning] `OnlyOurs` / `OurSequenceOrder` — использовать только если точно понимаете последствия.

## Связанные страницы

- [[Wasaby-File-Transfer]] — хранилище временных файлов (используется ToFileTransfer)
- [[Wasaby-BL-Calls]] — вызов MultimediaLoader через BLObject
