---
address: c-000112
created: 2026-06-14
updated: 2026-06-14
type: concept
title: "Wasaby Unit Testing (Python & C++)"
tags:
  - wasaby
  - testing
  - pytest
  - backend
  - python
  - cpp
status: current
related:
  - "[[Wasaby-Dev-Standards]]"
  - "[[Wasaby-BL-Calls]]"
sources:
  - ".raw/wasaby.Backend/Отладка/Юнит-тестирование C++ и Python/Юнит-тестирование C++ и Python.sabydoc"
  - ".raw/wasaby.Backend/Отладка/Юнит-тестирование C++ и Python/Примеры тестов на Python (pytest).sabydoc"
  - ".raw/wasaby.Backend/Отладка/Юнит-тестирование C++ и Python/Моки внешних ресурсов.sabydoc"
---

# Wasaby Unit Testing

Юнит-тестирование бэкенда Wasaby через фреймворк test_framework (входит в SBIS SDK). Поддерживает C++ (boost) и Python (pytest / unittest).

## Структура тестового проекта

```
<root>/
  tests/
    my_test_suite/          ← одна папка = один тестовый проект
      src/                  ← исходный код тестов (.py или .cpp)
      clouds/
        test_cloud/
          test_cloud.s3cld  ← метаданные облака (имя папки == имя файла)
          test.s3srv
      resources/            ← файлы; симлинки создаются автоматически
      setup/
        __main__.py         ← запускается после разворота, до тестов
      test.entry            ← JSON-описание теста (обязателен)
```

### test.entry

```json
// Для pytest:
{ "py_pytest": "test_cloud" }

// Для unittest:
{ "pytest_on": "test_cloud" }

// Для C++:
{}
```

Опции `test.entry`:
- `timeout` — прерывание по таймауту (секунды)
- `pytest_args` — доп. аргументы pytest: `"--disable-warnings --durations=1"`
- `skip_missing: true` — игнорировать ошибки загрузки зависимостей
- `in_memory_databases: false` — разворот SQLite на диске (по умолчанию — в RAM)
- `coverage_args` — параметры coverage.py в формате JSON
- `services` — список облаков для развертывания дополнительных сервисов

## Запуск тестов

### Все тесты продукта

```bash
# Windows
py 3.11 "<SDK>/tools/test_framework" "<путь к tests>" --jinnee "<SDK>/tools/jinnee"

# Linux
/opt/python3.11/bin/python3.11 "<путь к tests>" --jinnee ...

# macOS
python3.11 "<путь к tests>" --jinnee ...
```

### Один тестовый проект

```bash
py 3.11 "<SDK>/tools/test_framework" "<путь к tests>" "my_test_suite" --jinnee "<SDK>/tools/jinnee"
```

### Один модуль (только для Python)

```bash
py 3.11 "<SDK>/tools/test_framework" "<путь к tests>" "my_test_suite" -t "simple_test" --jinnee "<SDK>/tools/jinnee"
```

### Ключевые параметры

| Параметр | Описание |
|----------|----------|
| `-j N` / `--jobs N` | Параллельный запуск N тестов |
| `--verbose` | Подробный вывод (рекомендуется для CI) |
| `-c` | Очистить "мусорные" БД от упавших запусков |
| `mode debug` | Режим отладки: окружение создается, тест не запускается |
| `--py_coverage` | Измерение покрытия кода (Python) |
| `--amqp <адрес>` | Адрес AMQP-брокера |
| `--xunit_output <путь>` | Результаты в xUnit-формате для CI |
| `--attempts N` | Повторные попытки при ошибке |

## Запуск в PyCharm

1. Запустить `test_framework` с параметром `debug` — разворачивает окружение
2. В PyCharm → Run → Edit Configurations → pytest
3. Additional Arguments: путь до `src/`
4. Environment variables (Linux/macOS):
   - `PYTHONPATH=<SDK>/tools/python_test_utility:<build>/tests/<suite>/run`
   - `LD_LIBRARY_PATH=.` (Linux) / `DYLD_LIBRARY_PATH=.` (macOS)
5. Working directory: `<build>/tests/<suite>/run`

## Простой pytest-тест

```python
# tests/simple_test_suite/src/simple_test.py
import sbis_root as sbis
from unittest import TestCase

class TextFrameworkExample(TestCase):
    def test_simple(self):
        self.assertEqual(1 + 1, 2)
```

## Тест с вызовом БЛ-метода

```python
import sbis_root as sbis
from unittest import TestCase

class TestBLCall(TestCase):
    def test_call_service(self):
        text = sbis.BLObject("MyObject").Invoke("AnotherMethod", ...)
        self.assertEqual(text, "expected")
```

## Мокирование внешних сервисов

### Python mock_service

```python
import sbis
import mock_service

def MyMockFunction(id: int, key: str) -> sbis.Record:
    rec = sbis.Record()
    rec['Result'] = 'mocked'
    return rec

def test_with_mock():
    mock = mock_service.MockService("my-service")
    mock.AddMethod("MyObject.MyMethod", MyMockFunction)
    with mock:
        result = sbis.BLObject("MyObject", sbis.EndPoint("my-service")).Invoke("MyMethod", ...)
        assert result['Result'] == 'mocked'
```

**Важно**: функции-моки обязательно должны содержать type hints — без них фреймворк не может вывести сигнатуру.

### Таблица типов для type hints

| Python type hint | Тип Saby |
|-----------------|----------|
| `None` | ftUNDEFINED |
| `int` | ftINT64 |
| `float` | ftDOUBLE |
| `str` | ftSTRING |
| `bytes` | ftBINARY |
| `date` | ftDATE |
| `time` | ftTIME |
| `datetime` | ftDATETIME |
| `timedelta` | ftTIMEINTERVAL |
| `Decimal` | ftDECIMAL |
| `UUID` | ftUUID |
| `dict` | ftHASH_TABLE |
| `Record` | ftRECORD |
| `RecordSet` | ftRECORDSET |
| `list[int]` | ftARRAY_INT64 |
| `list[float]` | ftARRAY_DOUBLE |
| `list[str]` | ftARRAY_TEXT |
| `list[bool]` | ftARRAY_BOOLEAN |
| `list[date]` | ftARRAY_DATE |
| `list[time]` | ftARRAY_TIME |
| `list[datetime]` | ftARRAY_DATETIME |
| `list[timedelta]` | ftARRAY_TIMEINTERVAL |
| `list[Decimal]` | ftARRAY_DECIMAL |
| `list[UUID]` | ftARRAY_UUID |
| `ObjectId` | ftIDENTIFIER |
| `Navigation` | ftNAVIGATION |
| `SortingList` | ftSORTING |
| `RpcFile` | ftRPC_FILE |
| `Flags` | ftFLAGS |

> [!warning] Нельзя замокать из Python методы с оригиналами на C++, если те используют типы, не имеющие представления в Python.

### C++ mock_service (тест без сервиса)

**CMakeLists.txt**:
```cmake
sbis_add_sdk_dependencies(sbis-lib300 sbis-bl-core300 sbis-rpc-service300 sbis-mock-service)
sbis_enable_static_build(GENERATE_STATIC_INITIALIZERS INITIALIZERS "InitTest")
```

Нужно реализовать функцию `InitTest` в namespace `sbis::<имя_проекта>_initializers` (дефисы → подчёркивания):
```cpp
namespace sbis { namespace test_some_lib_initializers {
    void InitTest() { /* инициализация BL Core */ }
}}
```

```cpp
BOOST_AUTO_TEST_CASE(TestSomeLib) {
    // Создаём мок для внешнего сервиса
    auto mock = mock_service::MockService("service_name"_sv);
    // Добавляем заглушку метода
    mock.AddMethod("MyObject.MyMethod"_sv, [](String s) -> bool {
        return s == "FF";
    });
    // Вызываем тестируемый код
    MyFunction();
    // mock автоматически уничтожается при выходе из области видимости
}
```

### C++ mock_service (тест мобильного микросервиса с сервисом)

В отличие от теста без сервиса, здесь облако уже развёрнуто. Нужно:
1. Добавить модуль `MockService` в s3srv тестового облака через Genie
2. В CMakeLists.txt добавить только `sbis-mock-service` (без `sbis-lib300` и InitTest)

```cmake
sbis_add_sdk_dependencies(sbis-mock-service)
```

Код теста аналогичен тесту без сервиса — тот же `mock_service::MockService("service_name"_sv)`.

### monkeypatch для EndPoint (pytest)

```python
def test_monkeypatch_all(monkeypatch):
    class NonExistEndpoint:
        class NonExistTestObject:
            @staticmethod
            def NonExistTestMethod():
                return "mocked"
    
    def mock_endpoint(name, *args, **kwargs):
        if name == "NonExistEndpoint":
            return NonExistEndpoint
        raise Exception("Only mock 'NonExistEndpoint' endpoint")
    
    monkeypatch.setattr(sbis, "EndPoint", mock_endpoint)
    assert function_undertest() == "expected"
```

## Анализ результатов

После выполнения теста:
```
build/tests/my_test_suite/run/
  output.txt    ← результаты тестов
  logs/         ← логи сервисов
  tmp/          ← логи разворота окружения
```

## Покрытие кода

```bash
py 3.11 "<SDK>/tools/test_framework" "<tests>" --py_coverage --py_coverage_format html
```

Отчёт создаётся в `coverage_<test_name>/` в рабочей директории.
