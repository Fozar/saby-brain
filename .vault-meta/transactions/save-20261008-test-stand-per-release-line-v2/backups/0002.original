---
type: concept
title: "PriceFormation Test Framework"
updated: 2026-04-11
tags:
  - price-formation
  - testing
  - unit-tests
  - pycharm
  - cmake
  - wasaby
  - sbis-feature
status: current
related:
  - "[[PriceFormation-Backend-Architecture]]"
  - "[[Saby-Feature-Toggles-API]]"
  - "[[Wasaby-BL-Objects]]"
  - "[[Python-Code-Standards-SBIS]]"
created: 2026-04-11
---

# PriceFormation Test Framework

Система юнит-тестов для репозитория `price-formation`. Расположена в `tests_new/`. Работает на основе SDK-утилиты `test_framework` + cmake/ninja (без genie и дистрибутива).

Официальный гайд: https://wi.sbis.ru/doc/platform/application-debugging/unit-tests-framework/

Контактное лицо: **Ушаков Тимофей (Т.Л.)**

---

## Три тестовых проекта

| Проект | Назначение | Особенности |
|--------|-----------|-------------|
| `Desktop` | Офлайн (POS/Розница/Presto) — `PriceFormation.Offline` | Стандартные зависимости |
| `Online` | Онлайн, без ядра расчёта — `PriceFormation.Online` | Стандартные зависимости |
| `OnlineWithDiscountCore` | Онлайн + C++ ядро расчёта (`CalcDiscount`) | Нужны дополнительные зависимости при сборке |

Структура в репо: `tests_new/<Desktop|Online|OnlineWithDiscountCore>/`.

---

## Предварительные требования

### Git симлинки (Windows)
Тесты используют git-симлинки для прокидывания модулей. По умолчанию отключены на Windows.

```bash
# Глобально (от администратора)
git config --global core.symlinks true

# Для существующего репо
git config core.symlinks true

git fetch
```

> Старые версии git не поддерживают симлинки. На Linux настройка не нужна.

### Директория сборки
Создать папку `build` вне проекта — для выходных файлов cmake.

### SDK
- Отметить галочками: **Backend Python** и **Backend C++**.
- Версия SDK должна соответствовать версии ветки `price-formation`.
- После установки SDK — **обязательно перезапустить компьютер** (иначе ENV-переменные SDK не будут заполнены).
- Установить [Tensor C++ Development для Windows](https://wi.sbis.ru/doc/platform/workplace-settings/windows/cpp/#cpp-workplace-settings-step3).
- Python 3.11 обязателен.

### Репозитории-зависимости (sibling-папка)
Папка `--test_vendor_path` должна содержать и `price-formation`, и `pnt-toolbox` рядом. Для `OnlineWithDiscountCore` дополнительно — ядро расчёта.

---

## Сборка и запуск через test_manager.py (рекомендуется)

`test_manager.py` находится в корне проекта. Автоматически:
- проверяет окружение;
- загружает зависимости (pnt-toolbox и др.);
- собирает тестовый проект;
- запускает его.

### Три конфигурации PyCharm

#### 1. Deploy (сборка проекта)
Тип: Python (не unittest).
```
Script: test_manager.py
Arguments: --test_vendor_path <путь до директории с репозиториями>
```
Запускать при: мажорном переключении вехи, изменении состава `.orx`/`.dicx`/`.s3mod`.

После успешного деплоя в консоли будут выведены параметры среды (версия SDK, директории) и запущен проект Online.

#### 2. Run online (запуск без пересборки)
Тип: Python (не unittest).
```
Script: test_manager.py
Arguments: --test_vendor_path <путь до директории с репозиториями> -restart=True
```
Для Desktop:
```
--test_vendor_path <путь> -restart=True -project=desktop
```
Запущенный проект висит в фоне и поднимает БД. Можно многократно запускать тесты — изменения подтягиваются автоматически.

#### 3. Run unittest (выполнение тестов)
Тип: unittest.
```
Working directory: <build_dir>/price-formation/tests/online/run
Pattern: *
```
Также: Add content roots to PYTHONPATH, Add source roots to PYTHONPATH.
Папку `tests-helpers/tests_helpers` пометить как Sources.

---

## Альтернативная сборка вручную (cmake/ninja)

Используется при проблемах с `test_manager.py`. Запускать **от администратора** в Tensor C++ Developer Command Prompt.

### 0. Подготовка каталога сборки
```cmd
IF EXIST "C:\Saby\builds\price-formation" RMDIR /S /Q "C:\Saby\builds\price-formation"
mkdir C:\Saby\builds\price-formation
cd C:\Saby\builds\price-formation
```

### 1. CMake (генерация проектных файлов)
```cmd
# Всё сразу
cmake C:/Saby/repositories/price-formation/tests_new -DSBIS_UNIT_TESTS=1 -G Ninja

# Или по отдельности
cmake C:/Saby/repositories/price-formation/tests_new/online/src -DSBIS_UNIT_TESTS=1 -G Ninja
# Удалить CMakeCache.txt в каталоге сборки
cmake C:/Saby/repositories/price-formation/tests_new/desktop/src -DSBIS_UNIT_TESTS=1 -G Ninja
```

### 2. Ninja (сборка)
```cmd
ninja
```

### 3. test_framework (деплой + первичный запуск)
```cmd
py -3.7 %SBISPlatformSDK_233100%/tools/test_framework C:/Saby/repositories/price-formation/tests_new --jinnee %SBISPlatformSDK_233100%/tools/jinnee
```
Переменные окружения:
```
PNT_TOOLBOX_PATH=<путь к PntToolbox>
PYTHONIOENCODING=utf8
PYTHONPATH=<путь к tests_new>
IS_TEST_CLOUD=1
```

### 4. Повторный запуск в PyCharm
```cmd
# Online
py -3.7 %SBISPlatformSDK_233100%/tools/test_framework <tests_new> online debug --jinnee <jinnee_path>
# Desktop
py -3.7 %SBISPlatformSDK_233100%/tools/test_framework <tests_new> desktop debug --jinnee <jinnee_path>
```

---

## Написание тестов

### Мок внешних методов и таблиц

Мок-объект расположен: `tests_new/<platform>/clouds/<Cloud>/TestLoyalty`

| Что мокать | Файл | Действие при изменении |
|-----------|------|------------------------|
| Внешние методы БЛ | `TestLoyalty.orx` | Пересборка не требуется |
| Внешние таблицы (dicx) | `TestLoyalty.dicx` | **Требуется пересборка проекта** |

### Мок sbis_feature

Модуль `sbis_feature` **отсутствует** в тестовом проекте — обязательно мокировать:

```python
from tests_helpers import enable_features, with_feature

# Декоратор метода: включает только перечисленные фичи
@enable_features(['promo_code'])
def test_1(self):
    pass

# Декоратор класса: прогоняет тесты ДВАЖДЫ — с включённой и выключенной фичей
@with_feature
class TestMyFeature(unittest.TestCase):
    ...
```

> В основном коде используй `from sbis_feature import Feature; Feature('flag').IsOn()`. В тестах — только через декораторы.

### Пропуск тестов

```python
from tests_helpers import test_new_skip

@test_new_skip
def test_that_cannot_run_in_test_env(self):
    ...
```

Декоратор использует настройку `TestConfig.Project` из ini-файлов тестовых проектов.

---

## Переменные среды SDK (`.env`)

```
SBISPlatformSDK_261100=...
SBISPlatformSDK_262000=...
```

Имя переменной соответствует версии SDK: `SBISPlatformSDK_<MAJOR><MINOR>`.

---

## Связанные страницы

- [[PriceFormation-Backend-Architecture]] — общая карта Python-модулей репозитория
- [[Saby-Feature-Toggles-API]] — полный API Feature-флагов (`IsOn`, `GetValue`, mock/stub)
- [[Wasaby-BL-Objects]] — `.orx`/`.dicx` артефакты, на которых основан мок-механизм
- [[Python-Code-Standards-SBIS]] — стандарты кода Python в проекте
- [[Wasaby-CPP-Python-Integration]] — анти-паттерны при работе с C++-объектами из Python