---
type: concept
title: "Скрипты в Wasaby (DeveloperScript)"
tags:
  - wasaby
  - infrastructure
  - scripts
  - DWC
status: current
related:
  - "[[Хоттабыч-System]]"
  - "[[DWC-Distributed-Workflow-Coordinator]]"
  - "[[Wasaby-BL-Methods]]"
created: 2026-04-12
updated: 2026-04-12
address: c-000091
---

# Скрипты в Wasaby (DeveloperScript)

Скрипт — инструмент для разового выполнения произвольного кода разработчика в контексте существующего сервиса.

## Принцип работы

1. Хоттабыч разворачивает копию целевого сервиса (или минимальный сервис) на одной из бизнес-логик
2. В развёрнутый сервис внедряется модуль разработчика
3. Клиенты персональных сервисов разбиваются на группы
4. DWC вызывает `DeveloperScript.ExecuteAll` → методы скрипта вызываются последовательно в лексикографическом порядке
5. Для персонального сервиса: каждый метод выполняется под каждым клиентом через TenantContext

## Создание скрипта (3 шага)

### Шаг 1: Подготовить скрипт

1. В Genie создать `*.orx` (справочник объектов)
2. Внутри создать объект БЛ с именем **`DeveloperScript`** (строго!)
3. Добавить метод типа "Custom method":
   - Без входных параметров
   - Реализация: SQL или Python
   - Имя метода — осмысленное, уникальное в рамках исполнения скриптов

> [!note] Модули s3mod
> Если нужны дополнительные ресурсы — модуль s3mod должен именоваться `DeveloperScript_<Уникальное_имя>`.

### Шаг 2: Создать архив

```
*.zip (кодировка CP866, 7-Zip!)
├── DeveloperScript.orx          ← обязательно в корне
├── developer_script.py          ← основная реализация на Python
├── fix_cloud_clients            ← (опц.) ClientID для fix-среды
├── prod_cloud_clients           ← (опц.) ClientID для prod-среды
└── test_cloud_clients           ← (опц.) ClientID для test-среды
```

Файлы `*_cloud_clients` — plain text, по одному ClientID. Нужны когда скрипт работает с конкретными клиентами в разных средах (fix/prod/test) и параметры различаются.

Для неперсональных приложений: файл `services` со списком сервисов.

Имя архива: `s_<фиопользователя>_<номервнр>_v<версия>.zip`

Номер ВНР берётся из задачи на online.sbis.ru. Версия (`v1`, `v2`, ...) инкрементируется при каждой повторной подаче одного и того же скрипта.

### Шаг 3: ВНР

Задача "Выполнить на рабочем" на online.sbis.ru. Прикрепить переименованный архив.

## Настройки запуска (в Хоттабыче)

| Параметр | Описание |
|----------|----------|
| Останавливаться только на ошибках | По умолчанию включён |
| Режим запуска | Копия сервиса (default) или минимальный сервис |
| Ограничение одновременного выполнения | Max параллельных клиентов (0 = без ограничений) |
| Повторять на всех клиентах | Если предыдущий запуск не завершён |

## Структура файлов

> [!note] Источник примеров
> Шаблоны ниже выведены из реальных архивов (`s_timoshenkoaa_*.zip`), прошедших боевое выполнение. Не претендуют на идеальность, но отражают рабочую практику.



### `DeveloperScript.orx` — шаблон

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<repository orx_version="2.08">
  <object name="DeveloperScript" responsible="Фамилия И.О." responsible_uuid="<uuid>">
    <comment>DeveloperScript</comment>
    <select
      access_mode="0"
      is_service="0"
      name="DeveloperScript.DeveloperScript"
      responsible="Фамилия И. О."
      responsible_uuid="<uuid>"
      returns="NONE"
      type="PYTHON"
    >
      <comment>{"CallExample":"","Comment":"Описание что делает скрипт","DeprecationReason":"","Errors":[]}</comment>
      <definition>
        <language>PYTHON</language>
        <body>file:developer_script.py#run_script()</body>
      </definition>
    </select>
  </object>
</repository>
```

- `access_mode="0"` — стандартный; `access_mode="1"` — ограниченный (для скриптов, работающих только с конкретными клиентами)
- `comment` в `<select>` — JSON, поле `Comment` — описание для интерфейса Хоттабыча
- `<body>` всегда ссылается на `file:developer_script.py#run_script()` (имя файла и функции фиксированы)

### `developer_script.py` — шаблон

```python
"""ВНР для <краткое описание>"""

import sbis


def run_script():
    client_id = sbis.Session.ClientID()
    is_local_stand = False  # True при отладке на стенде

    # ... логика ...

    if not is_local_stand:
        sbis.DeveloperScriptAPI.LogMsg(
            f'<результат>. ClientID: {client_id}'
        )
```

- Функция входа всегда называется `run_script()` (без параметров)
- `sbis.Session.ClientID()` — получить текущего клиента (используется для логов и per-client dispatch)
- `is_local_stand = False` → логируется в систему; `True` → только локальная отладка без вывода
- `sbis.DeveloperScriptAPI.LogMsg(...)` — вывод в лог ВНР (не в сервис логов!)

### Паттерн: per-client dispatch

Когда скрипт нужно запустить с разными параметрами для fix/prod/test, параметры захардкожены через `client_id`:

```python
def run_script():
    client_id = sbis.Session.ClientID()
    if client_id == 113707965:    # test
        emission_id = 10
    elif client_id == 202754788:  # fix
        emission_id = 34
    elif client_id == 33790852:   # prod
        emission_id = 8
    else:
        sbis.DeveloperScriptAPI.LogMsg(f'Не предназначен для этого клиента: {client_id}')
        return
    # ... работа с emission_id ...
```

ClientID среды удобно хранить в файлах `*_cloud_clients` рядом в архиве — для документирования и воспроизведения.

## Логирование

Внутренний метод исполнения: `DeveloperScriptExecuteAll` (через DWC). Фильтр в сервисе логов: сервис=целевой, метод=`DeveloperScriptExecuteAll`. Каждый метод обрамляется:
```
[script][start][DeveloperScript.НазваниеМетода][ID клиента]
[script][finish][DeveloperScript.НазваниеМетода][ID клиента]
```

> [!warning] Не использовать сервис логов для результатов — логи могут быть очищены досрочно, и быстрые методы могут не залогироваться вовсе.

## DeveloperScriptAPI — полное API

### Redis (данные по клиентам)

```python
sbis.DeveloperScriptAPI.LogRedis(Data: sbis.Record)
```
- Record → JSON → Redis hash-таблица, ключ = ID клиента
- При повторной записи по тому же клиенту — **перезапись** (не append)
- После завершения скрипта хэш-таблица → json-файл → хранилище файлов

**Построение sbis.Record для LogRedis:**

```python
result = sbis.Record()
result.AddInt64('ВсегоДК', total)        # целое 64-бит с значением
result.AddInt32('Count', count)          # целое 32-бит с значением
result.AddString('Info', 'текст')        # строка с значением
result.AddBool('Flag', True)             # булево с значением
sbis.DeveloperScriptAPI.LogRedis(result)
```

> [!warning] Не `AddInteger` — такого метода нет. Правильно: `AddInt32` / `AddInt64`.
> Для счётчиков (COUNT(*)) используй `AddInt64` — безопасно при любом размере таблицы.
- Скачать из отчёта скрипта
- **Ограничение: ≤ 5 МБ на клиента** (Redis, online/inside only)
- Данные в разрезе приложения: 1 файл на приложение

### Файловые логи на БЛ

```python
sbis.DeveloperScriptAPI.LogMsg(Message: str)
```
Пишет в CSV: `[дата/время, ID клиента, сообщение]` (персональный) или `[дата/время, сообщение]` (неперсональный).

```python
sbis.DeveloperScriptAPI.LogArrayMsg(Messages: list[str])
```
Аналогично, но один вызов = одна строка CSV, каждый элемент = отдельная ячейка.

```python
sbis.DeveloperScriptAPI.LogsDirectory() -> str
```
Возвращает путь к директории файловых логов. Любые файлы, созданные в этой папке, будут собраны и доступны для скачивания после завершения скрипта.

**Облачные параметры файловых логов:**
- `Управление версиямиСкриптыМаксимальныйРазмерЛога` — лимит файла в МБ (при достижении создаётся следующий файл)
- `Управление версиямиСкриптыМаксимальноеЧислоЛогов` — максимальное число файлов логов
- `Управление версиямиЛогиМинимальныйПериодХранения` — срок хранения файлов (дней)

Файлы каждой БЛ пакуются в отдельный архив (имя = hostname БЛ + системное имя сервиса).

| Способ | Когда использовать |
|--------|-------------------|
| `LogRedis` | Небольшие данные (≤ 5 МБ/клиент) по клиентам online/inside; 1 файл на приложение |
| `LogMsg` / `LogArrayMsg` | Прочие сервисы; данные любого размера (ограничен диском БЛ); 1 архив на БЛ |

## Статусы выполнения

- **Успешно** — метод завершён без ошибок
- **Ошибка** — выполнялся, прервался из-за ошибки (в т.ч. таймаут)
- **Не выполнено** — прервали до завершения (ошибок нет)

На фазе очистки Хоттабыч проверяет асинхронные очереди — должны быть пусты. Если не пусты по истечении таймаута, обновление останавливается. Возобновить — кнопка «Возобновить». **Не использовать «Принудительно завершить»** — скриптовые узлы не остановятся.

## Паттерны

### Выполнение на схеме public (мультиарендный сервис)

```python
# В orx — описать дополнительные методы:
DeveloperScriptBeforeScript()   # до методов на схемах клиентов
DeveloperScriptAfterScript()    # после методов на схемах клиентов
# Выполняются в транзакции с search_path = public
```

### Определение стенда

```python
from sbis import CloudEntity
cloud = CloudEntity.SysName()  # 'prod', 'fix', 'test', 'rc', ...
if cloud == 'prod':
    ...
```
Список стендов: Управление облаком → Настройки → Облака (столбец «Системное имя»).

### CONCURRENTLY-индекс без транзакции

```python
scheme = "_" + sbis.Session.ID()[:8]
drop_sql = f'DROP INDEX CONCURRENTLY IF EXISTS {scheme}."index1"'
create_sql = f'CREATE INDEX CONCURRENTLY "index1" ON "{scheme}"."Table1" ("Col1", "Col2")'

stmt = sbis.GetConnectedDatabase().CreateStatement(False)  # False = без транзакции
stmt.Exec(drop_sql)
try:
    stmt.Exec(create_sql)
except sbis.BadExecStatement:
    stmt.Exec(drop_sql)  # индекс останется в неактуальном состоянии — нужно явно удалить
    raise
```
> [!warning] Индексы, добавленные через ВНР, будут удалены конвертером при следующей конвертации (если не прописаны в .dicx).

### Выполнение на всех БД сервиса

```python
import json
db_config = json.loads(sbis.ConfigGet('clusters.databases'))
futures = [sbis.BLObject("Invoker").FutureInvoke("ExecuteOnDatabase", db['id']) for db in db_config]
for f in futures:
    f.get()
```
Метод `Invoker.ExecuteOnDatabase(db_id)` — устанавливает нужную БД и выполняет скрипт.

### Получение файла из архива скрипта

```python
# Способ 1: через ConfigGet
module_name = 'DeveloperScript_' + zip_name  # имя модуля = DeveloperScript_ + имя архива (без .zip)
base_path = os.path.normpath(os.path.join(sbis.ConfigGet('Модули'), module_name, 'csv_folder'))

# Способ 2: из py-файла
current_folder = os.path.dirname(os.path.abspath(__file__))
path_to_file = os.path.join(current_folder, 'file.txt')
```
> Использовать `os.path.join` / `os.path.normpath`, не склеивать через `/`. При чтении файлов — указывать encoding (CSV может быть CP1251).

## Ограничения одновременного выполнения

По умолчанию скрипт выполняется одновременно на каждой БД для каждого клиента. Для скриптов с внешними вызовами это создаёт очередь — ограничить через ВНР: поле «Ограничение одновременного выполнения» (диапазон 0–100; 0 = без ограничений).

Число рабочих процессов скриптовой БЛ: по умолчанию 2 (1 для скрипта + 1 для async-вызовов на себя). Для скриптов с self-parallelism — можно запросить больше в ВНР. Максимум: `Управление версиямиСкриптыМаксимальноеЧислоПроцессовСкриптовыхБЛ`.

## Уникальность и повторный запуск

Уникальность определяется по **хэш-сумме архива** (не по имени). Изменение содержимого файлов = новый скрипт. Переименование архива — НЕ новый скрипт.

Если прервали, не выполнив на всех клиентах, — повторный запуск продолжит с необработанных. Принудительный перезапуск на всех — только если все клиенты уже обработаны.

## Локальная проверка

1. Поместить содержимое архива в папку с исходными модулями сервиса
2. Выполнить Deploy сервиса
3. Выдать права на метод в используемую роль
4. Запустить сервис, вызвать `DeveloperScript.НазваниеМетода` любым способом

## Требования к сервису-исполнителю

Для режима "копия сервиса" обязательны модули (гарантированы при наследовании от `basic_platform.s3srv`):
- Python Core
- Cloud Interaction-Py
- Redis Client-Py
- RequestBrokerClient
- HugePayload

## Паттерн: сбор статистики по таблице

Типовой скрипт для анализа данных — считает агрегаты по таблице и логирует через LogRedis (структурированные данные) + LogMsg (дублирование для наглядности).

```python
"""ВНР для сбора статистики по ..."""

import sbis

_SQL = """
    SELECT
        COUNT(*) AS "ВсегоЗаписей",
        COUNT(*) FILTER (WHERE "Поле" IS NULL) AS "БезПривязки"
    FROM
        "{scheme}"."Таблица"
    WHERE
        "Тип" = 0
        AND "СвязанноеПоле" IS NOT NULL
"""

def run_script():
    client_id = sbis.Session.ClientID()
    scheme = '_' + sbis.Session.ID()[:8]

    rs = sbis.GetConnectedDatabase().Query(_SQL.format(scheme=scheme))
    row = rs[0]

    total = row['ВсегоЗаписей']
    without = row['БезПривязки']

    result = sbis.Record()
    result.AddInt64('ВсегоЗаписей', total)
    result.AddInt64('БезПривязки', without)

    sbis.DeveloperScriptAPI.LogRedis(result)
    sbis.DeveloperScriptAPI.LogMsg(f'ClientID={client_id}: всего={total}, без привязки={without}')
```

**Запрос на дисконтные карты без физлица** (реальный пример, поручение №06035683):
```sql
SELECT
    COUNT(*) AS "ВсегоДК",
    COUNT(*) FILTER (WHERE "Лицо" IS NULL) AS "БезФизлица"
FROM "{scheme}"."Карта"
WHERE
    "ТипКарты" = 0           -- только ДК (не промокоды/реферальные)
    AND "Эмиссия" IS NOT NULL  -- без персональных счетов
```
Контекст: продажи безымянной ДК до привязки к клиенту не учитывались в виджете бонусов (баг №04228789). Скрипт — оценка масштаба проблемы.
