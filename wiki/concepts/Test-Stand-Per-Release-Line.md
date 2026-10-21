---
type: concept
title: "Тестовый стенд по линейкам версий: worktree, tm.ps1, конфигурации PyCharm"
created: 2026-10-08
updated: 2026-10-12
status: developing
tags:
  - price-formation
  - testing
  - test-manager
  - pycharm
  - worktree
  - sdk
related:
  - "[[PriceFormation-Test-Framework]]"
  - "[[Price-Formation-Test-Runner]]"
---

# Тестовый стенд по линейкам версий

Как переключаться между мажорными ветками price-formation без полной пересборки стенда `test_manager.py`. Схема настроена 08.10.2026 в сессии Claude Code. Первая полная сборка в `D:/dev/pf-26.61` прошла 12.10.2026 (SDK 266000), стенд поднялся, тесты прогнаны; про грабли см. раздел «Запуск в фоне и прокси».

## Почему переключение было долгим

Всё окружение `test_manager.py` привязано к папке репозитория, а не к версии:

| Что | Где | Что происходит при смене мажора |
|---|---|---|
| Сборка | `../test_build/<имя папки>` | по умолчанию стирается при каждом запуске (`--clear_build`) |
| vendor (discount-core, pnt-toolbox, expression-converter, stats-core, reports-core) | путь из `--test_vendor_path`, один на всех | каждый раз `git stash`, `fetch`, `switch rc-XX.XXXX`, `pull` |
| БД | `_sbis_test_db_<время>` в локальном PostgreSQL, ссылка в `tests/<проект>/run/sbis-rpc-service.ini` внутри сборки | создаётся заново при деплое |
| Код модулей | в сборку не копируется, стенд читает его из рабочей папки | одна папка = один стенд |

Старые конфигурации PyCharm передавали `--test_vendor_path ./../`, то есть vendor-ом была сама `PycharmProjects` с рабочими клонами discount-core и pnt-toolbox. Каждый деплой делал в них `git stash` и переключал ветку.

## Какой SDK у ветки

SDK берётся не из имени ветки, а из переменной в `tests_new/CMakeLists.txt` (`$ENV{SBISPlatformSDK_NNNNNN}`). На 08.10.2026:

| Ветки | SDK |
|---|---|
| rc-26.5100, хотфиксы 26.5104…26.5125 | 265100 |
| rc-26.4100, 26.4104 | 264100 |
| rc-26.4200…26.4248 | 264200 |
| rc-26.3264 | 263200 |
| rc-26.6100, rc-26.6200 | 266000 |

Хотфиксы почти всегда на SDK своей линейки. Пока SDK `X100` не выпущен, линейка живёт на `X000` (ветки `X000` при этом нет). Когда в rc-ветке CMakeLists переключат на новый SDK, а он не установлен, `test_manager` остановится на проверке окружения («Требуемая версия SDK не установлена»). Проверка идёт до очистки сборки, так что стенд не теряется.

## Схема

- Одна постоянная папка-worktree на линейку: `D:/dev/pf-26.51` (от rc-26.5100), `D:/dev/pf-26.61` (от rc-26.6100). Ветки задач и хотфиксов линейки переключаются внутри неё. Отдельная папка нужна только линейке со своим SDK (например 26.42xx или 26.32xx).
- Сборка: `D:/dev/test_build/<имя папки>`, разводится сама по имени папки.
- vendor: `D:/dev/vendor/<линейка>` (`D:/dev/vendor/26.61`). Привязан к линейке, а не к номеру SDK: vendor это исходники, от SDK он не зависит, а смена SDK внутри линейки не должна вызывать новый клон. На какую rc-ветку переключить vendor, `test_manager` решает сам по имени ветки.
- Репозиторий не меняли: всё вне git.

## Обёртка tm.ps1

`C:\Users\aa.timoshenko\bin\tm.ps1`, в PowerShell доступна как `tm` (функция в `$PROFILE`). Что делает:

- линейку берёт из имени ветки (`26.6100/feature/...`, `rc-26.6125` дают `26.61`); при detached HEAD берёт её из SDK в CMakeLists, причём `X000` считается линейкой `X1` (`266000` даёт `26.61`);
- загружает `.env` из корня репозитория: там правильные пути к SDK, а часть системных переменных испорчена (в `SBISPlatformSDK_263100`, `263200`, `264000`, `262200` лежит копия PATH, `264100` указывает на Temp);
- ставит `PgPassword=postgres`, если не задан;
- переходит в корень репозитория (test_manager считает пути от текущей папки) и запускает `py -3 test_manager.py --test_vendor_path D:/dev/vendor/<линейка>` с остальными аргументами как есть.

Флаги test_manager объявлены как `type=bool`, поэтому выключить флаг можно только пустым значением: `--clear_build=`.

## Запуск в фоне и прокси

Найдено при первой сборке `pf-26.61` (12.10.2026):

- **pip стенда ходит мимо прокси.** jinnee ставит python-библиотеки стенда (`openpyxl`, `python-dateutil`, `tzlocal`) из `http://repo-dev.mgmt.tensor.ru/repository/pypi-repo/simple`. Через корпоративный прокси pip пишет «No matching distribution found for openpyxl», и стенд падает с «Service wasn't deployed, jinnee-utility exited with code 157» (подробности в `tests/online/test/tmp/jinnee.log` сборки). Хост добавлен в `NO_PROXY` блока `env` в `~/.claude/settings.json` (действует с новой сессии), рядом с `ci-conan.tensor.ru`. В текущей сессии хватает `NO_PROXY="$NO_PROXY,repo-dev.mgmt.tensor.ru"` при запуске.
- **В режиме debug стенд ждёт «Press Enter».** Если запустить `tm` в фоне без stdin, test_framework получает EOF и откатывает стенд, каталог `run` остаётся без `py_tests_runner.py`. Держать stdin открытым: `tail -f /dev/null | pwsh -NoProfile -File C:/Users/aa.timoshenko/bin/tm.ps1 -project online -restart=True`.
- Сообщения `fatal: destination path ... already exists` на шаге vendor безвредны: test_manager сначала пробует клонировать, потом переключает существующий репозиторий.
- Ветку задачи нельзя открыть в `pf-26.61`, пока она открыта в другом worktree. Перенос: `git diff` в старом worktree, `checkout --detach` там, `git switch` и `git apply` в `pf-26.61`.

## Что запускать

| Ситуация | Конфигурация | Аргументы |
|---|---|---|
| Первый запуск линейки, сменился SDK, что-то сломалось | Сборка | полная, с очисткой |
| Подтянули ветку, менялись таблицы или методы (`.dicx`, `.orx`) | Досборка | `--clear_build=`: ninja собирает только изменения, vendor подтягивается |
| Менялся только Python | Перезапуск | `-restart=True` |

## Конфигурации PyCharm

Хранятся в `.idea/workspace.xml` (папка `.idea` в gitignore), править только при закрытом PyCharm. В основной папке и в каждом worktree:

- «Стенд»: Сборка ×3 проекта, Перезапуск ×3, Досборка online. Тип Shell Script: `pwsh -NoProfile -ExecutionPolicy Bypass -File tm.ps1 <аргументы>`.
- «Отладка»: Debug (remote debug, порт 5012), в основной папке ещё Run Test Local Stand.
- «Инструменты»: radon, в основной папке ещё Saby Search MCP.
- Шаблоны тестов (Autodetect, Unittests): интерпретатор `venv_tests` основной папки, рабочая папка `$PROJECT_DIR$/../test_build/<имя папки>/tests/online/run`. Тест, запущенный по стрелке у класса, идёт в стенд своей линейки.
- В основной папке 139 сохранённых тестов разложены по папкам объектов БЛ с короткими именами (`find.FindOnline`, пометки `[dc]`, `[desktop]`, «(пакет)», наборы в папке «Наборы»).
- Закрепы записаны в `RunConfigurationStartHistory/pinned`. Формат не проверен: ни в одном проекте закрепов не было.
- Копия старых конфигураций: `.idea/workspace.xml.bak-2026-10-08`.

`.idea` в worktree скопирована из основной папки (misc, modules, iml, vcs, pylint, codeStyles, inspectionProfiles), модуль оставлен `price-formation`, чтобы конфигурации не ломались.

## Скиллы Claude

- `/run-tests` считает пути от папки с кодом: `BUILD = <корень>/../test_build/<имя папки>`. Перед запуском проверяет, что сборка есть и что её SDK (`SBIS_SDK_DIR` в `CMakeCache.txt`) совпадает с SDK ветки в `tests_new/CMakeLists.txt`. Если нет, тесты не запускает и просит Сборку. Для `py_tests_runner.py` ставит `PYTHONPATH` на `run/modules/Python Core`.
- `/test-manager` переписан под `tm` и линейки: какая конфигурация «Стенд» нужна в какой ситуации, как завести папку новой линейки, что значат ошибки проверки окружения. Сборку сам запускает только по прямой просьбе.
