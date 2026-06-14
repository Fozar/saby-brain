---
type: concept
title: "Wasaby Platform Modules"
updated: 2026-04-13
tags:
  - wasaby
  - modules
  - python
  - image
  - ipc-storage
  - xml
status: current
related:
  - "[[Wasaby-Module-System]]"
  - "[[Wasaby-CPP-Python-Integration]]"
  - "[[Wasaby-Python-Patterns]]"
created: 2026-04-13
---

# Wasaby Platform Modules

Платформенные сервисные модули СБИС: `sbis`, `sbis_root`, Image, Interprocess Storage, XML-Py.

## sbis — Python API сервисного фреймворка

`sbis` — Python-модуль, предоставляющий доступ к Python API Wasaby Framework.

**В методах БЛ (orx-файлы, справочники объектов) модуль автоматически импортирован** — явный `import sbis` не нужен:
```python
# В методе БЛ в Genie — так:
rec = sbis.Record()
rec.AddString('ФИО', 'Сидоров А.В.')
```

**В отдельных Python-файлах** — нужен явный импорт:
```python
from sbis import Record
rec = Record()
```

### Разработка собственного Python-модуля для БЛ

1. Создать Python-модуль через Genie (из контекстного меню сервисного модуля)
2. Установить зависимость сервисного модуля от **Python** (из SBIS SDK) в `Module dependencies`
3. В сервис добавить модули: **Python**, **Python Core**, **BL Python** (или шаблон `basic_platform.s3srv`)
4. В Custom method / Manually implemented list:
   ```python
   from <mymodulename> import *
   ```

## sbis_root — утилита для автономных скриптов

`sbis_root` — Python-утилита для инициализации ядра без запуска полноценного сервиса.
Импорт автоматически влечёт импорт `sbis`.

### Применение
- Автономные скрипты с доступом к API платформы
- **Отладка через PyCharm** без запуска полного сервиса

### ini-файл для sbis_root

Конфигурация из облака:
```ini
Конфигурация=Адрес='http://xxx-private.sbis.ru/cfg'
[Ядро.Сервер приложений]
ИмяСлужбы=sbis-daemon-name
```

Конфигурация из БД (только cloud control / cloud control api):
```ini
[Базовая конфигурация]
БазаДанных=postgresql: host='example.unix.tensor.ru' port='5432' dbname='cloud' user='user' password='pass'
[Ядро.Сервер приложений]
ИмяСлужбы=sbis-admin-api
```

На Linux: `export LD_LIBRARY_PATH=.`

### Ограничения
> [!warning] Категорически запрещено импортировать `sbis_root` в Python- и orx-файлах на сервисе БЛ — повторно вызывается инициализация ядра!

В отличие от сервиса: нет каркаса (нет отправки логов, нет прослушивания порта). `sbis_root` — только доступ к API.

---

## Image (sbis-img) — обработка изображений

Модуль: **Image** / **Image-BL** (из состава SBIS SDK / ядро Wasaby Framework, проект `sbis-img300`).
Обёртка над **Magick++**. Безопаснее и удобнее прямого использования.

### Поддерживаемые форматы
PNG, JPEG, BMP, TIFF, PSD, GIF, RGB, RGBA.
Многостраничные изображения: только TIFF и GIF.

### Удалённый бэкенд (img-remote)
Для Kubernetes-сервисов без диска (ограничения памяти pod). Выбор бэкенда:
- При создании: передать `LoadOptions(mBackend=remote)`
- Глобально: `Ядро.РаботаСИзображениями.ИспользоватьУдаленныйБэкенд`

Изображения с разными бэкендами не совместимы (нельзя наложить локальное на удалённое).

### Python API

```python
import img

# Основной класс — Image. Большинство методов возвращают self (цепочки).
image = img.Image('path/to/file.tiff')

# Геометрия
image.Resize(800, 600).Rotate(90).Flip().Flop()
image.Crop(from_left, from_top, width, height)
image.Zoom(50)   # % от текущего размера
image.SetDepth(256)

# Цвет
image.MakeGrayScale()
image.ColorSpace = img.ImageColorspace.RGB  # RGB/CMYK/YUV/GRAY

# Сохранение
image.Save('out.jpg', img.ImageFormat.JPG)
image.Save('out.png')   # формат по умолчанию — PNG

# Многостраничные (TIFF/GIF)
frames = img.Image('multi.tiff').DecomposeMultiPageImage()
img.Image().ComposeMultiPageImage(frames).Save('new_multi.tiff')

# Пакетный режим (для удалённого бэкенда)
batch = img.TransformationBatch()
batch.Resize(200, 100).Rotate(90)
image.ApplyBatch(batch)  # один удалённый вызов вместо нескольких
```

**Загрузка из URL / удалённого метода** (модуль Image-BL):
```python
image = imgbl.LoadImageFromUrl(url)
image = imgbl.LoadImageFromInvoke(imgbl.ServiceMethodWithArgs("remote-svc", "Object.GetImage", 1, "arg"))
```

### Ключевые классы

| Класс | Описание |
|-------|----------|
| `Image` | Основной класс. Все манипуляции, загрузка, сохранение. |
| `Pixel` | Пиксель. `image[row][col]` для доступа к пикселям. |
| `LoadOptions` | Опции загрузки: бэкенд, формат, диапазон страниц, токен отмены. |
| `TransformationBatch` | Пакетное преобразование (для удалённого бэкенда). |
| `ImageFormat` | `PNG`, `JPG`, `BMP`, `TIFF`, `PSD`, `GIF`, `RGB`, `RGBA` |
| `ImageColorspace` | `RGB`, `CMYK`, `YUV`, `GRAY`, `Unknown` |

---

## Interprocess Storage — разделяемое хранилище

Модуль: **Interprocess Storage** (бинарная библиотека `sbis-interprocess-storage`).
Ключ-значение хранилище в **разделяемой памяти сервера**. Доступно из разных процессов одного сервера.

Размер: параметр `Хранилище.МаксимальныйРазмерХранилища`. При переполнении — LRU-вытеснение.

> [!warning] Сохранность данных не гарантируется. Для Python требуется модуль **Interprocess Storage-Py**.

### Python API

```python
import ipc_storage

# Получить именованный контейнер
storage = ipc_storage.GetStorage("my_cache")

# Чтение (возвращает None при отсутствии или ошибке типа)
val = storage.ReadString("key")
val = storage.ReadInt("counter")
val = storage.ReadRecord("data")
# Bulk-чтение
vals = storage.ReadArrayString(["k1", "k2"])

# Запись
storage.Write("key", "value")
storage.Write({"k1": v1, "k2": v2})      # dict
storage.Write([("k1", v1), ("k2", v2)])  # list of tuples

# Проверка/удаление
storage.HasValue("key")           # True/False
storage.Remove("key")             # True если удалён
storage.RemoveArray(["k1", "k2"]) # кол-во удалённых
storage.Clear()                   # очистить контейнер

storage.TotalMemorySize()   # свободные байты
storage.Name()              # имя контейнера
```

Поддерживаемые типы: String, Int, Float, Bool, Date, Time, DateTime, TimeInterval, HashTable, Decimal, RpcFile, ByteVector, Record, RecordSet.

**Межпроцессный обмен**: разные процессы с контейнером одинакового имени — доступ к одним данным.

---

## XML-Py (sbis-xml) — безопасная обработка XML

Модуль: **XML-Py** (поставляется с SBIS SDK).

**Проблема**: стандартные `xml.dom` и `xml.sax` запрещены (угрозы безопасности: XXE, Billion Laughs и др.).
**Решение**: `sbis-xml` — drop-in replacement с API, совместимым с `xml.dom`/`xml.sax`, использует **xerces** под капотом.

```python
from sbis_xml import dom
# Далее — API аналогично xml.dom.minidom
```

Требование: зависимость от модуля **XML-Py** → автоматически поставляется с SBIS SDK.

---

## Связанные страницы

- [[Wasaby-Module-System]] — как подключать сервисные модули, зависимости
- [[Wasaby-CPP-Python-Integration]] — паттерны интеграции C++ и Python
- [[Wasaby-Python-Patterns]] — стандарты Python-кода в Wasaby
