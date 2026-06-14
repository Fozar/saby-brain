---
type: concept
address: c-000055
title: "Price-Formation Test Runner"
created: 2026-05-20
updated: 2026-05-20
tags:
  - price-formation
  - testing
  - infrastructure
  - sbis
status: current
related:
  - "[[Wasaby-Platform-Modules]]"
  - "[[Wasaby-Service-Architecture]]"
---

# Price-Formation Test Runner

Тесты price-formation запускаются через SDK-фреймворк (`test_framework`), но для запуска отдельных тестов (класс, файл, директория) используются прямые вызовы Python.

## PyCharm Content Roots

![[pycharm-content-roots-price-formation.png]]

Source Folders: `tests-helpers`, `tests_new`, `tests_new\online\src`, `www\service\Модули\PriceFormation.{Common,Online,Offline}`, `DCCommon`, `DCRights`.
Excluded: `venv`, `venv_tests`, `venv64`, `tests_new\online`, `tests_new\desktop`, `tests_new\online_with_discount_core`.

## Ключевые пути

| Переменная   | Значение                                                                               |
| ------------ | -------------------------------------------------------------------------------------- |
| Run dir      | `C:/Users/aa.timoshenko/PycharmProjects/test_build/price-formation/tests/<project>/run` |
| Python       | `C:/Users/aa.timoshenko/PycharmProjects/price-formation/venv_tests/Scripts/python.exe`  |
| Src root     | `C:/Users/aa.timoshenko/PycharmProjects/price-formation/tests_new/<project>/src`        |
| Project root | `C:/Users/aa.timoshenko/PycharmProjects/price-formation`                                |

`<project>` — имя тест-проекта, которым запускался `test_manager`: `online`, `desktop`, `online_with_discount_core`. Определяется по тому, что было собрано последним. Для реферальных программ — `online`.

**Обязательно:** рабочая директория всегда `run/` — там находится `sbis_root/` (DLL-загрузчик + `from sbis import *`) и скомпилированные модули.

`tests/` — хардлинки на `tests_new/online/src/` (одинаковые inode).

## Запуск по классу или методу

```bash
cd "<run_dir>"
PYTHONPATH="<project_root>" "<python>" -m unittest \
  tests.tests_priceformationonline.referralprogram.referralprogram.create_lead_for_partner.CreateLeadForPartnerTest
# метод: добавить .test_create_lead_by_owner
```

`PYTHONPATH` указывает на project root, чтобы `tests.xxx` резолвился через `tests/` пакет.

## Запуск по файлу

```bash
cd "<run_dir>"
"<python>" py_tests_runner.py "<src_root>" create_lead_for_partner.py \
  --driver unittest --package_name Online
```

`py_tests_runner.py` лежит в `run/`, внутри делает `unittest.TestLoader().discover(src, pattern)`.

## Запуск по директории (модулю)

```bash
cd "<run_dir>"
"<python>" py_tests_runner.py \
  "<src_root>/tests_priceformationonline/referralprogram/referralprogram" \
  --driver unittest --package_name Online
```

Передаётся абсолютный путь к поддиректории — discover находит все тесты внутри.

## Таймауты Bash

| Уровень | timeout (мс) |
|---------|------------|
| Метод / класс | 30 000 |
| Файл | 60 000 |
| Небольшая директория | 120 000 |
| Крупная директория / подпакет | 300 000 |
| Вся suite | 600 000 |

## Инфраструктура

- **SDK test_framework** (`SBISPlatformSDK_263000/tools/test_framework`) — полный pipeline: cmake + ninja сборка → `test.entry` lookup → `py_tests_runner.py`. Для CI/полного прогона.
- **`py_tests_runner.py`** — непосредственный Python-лаунчер. Принимает `src_path` + опциональные имена файлов. Загружает `sbis_root` (инициализация платформы), потом `unittest.discover`.
- **`sbis_root/`** — пакет в `run/`, содержит `loader.pyd` (C-расширение), делает `LoadServiceModules()` + `from sbis import *`. Без него `import sbis` упадёт.
- **`test.entry`** — JSON-файл рядом с тест-пакетом: `{"py_unittest": "Online"}`. SDK использует его для обнаружения тестов.

## Skill

В проекте есть `/run-tests` skill (`.claude/skills/run-tests/SKILL.md`). Вызывай его вместо ручного составления команды:

```
/run-tests CreateLeadForPartnerTest
/run-tests create_lead_for_partner.py
/run-tests @tests/tests_priceformationonline/referralprogram/referralprogram
```
