---
type: concept
title: "LoyaltyReferral Module Extraction"
created: 2026-06-17
updated: 2026-06-17
tags:
  - referral-program
  - price-formation
  - module-architecture
  - build-system
status: developing
related:
  - "[[ReferralProgram-Data-Model]]"
  - "[[SabyBank-RKO-Referral]]"
  - "[[Wasaby-Service-Node-Architecture]]"
  - "[[Price-Formation-Test-Runner]]"
---

# LoyaltyReferral — выделение рефералки в отдельный СБИС-модуль

Задача №05256826 (автор Самарина И.А., ответственный Михель В.М., срок 2026-08-08): вынести реферальную систему из `PriceFormation.Online` в отдельный BL-модуль `LoyaltyReferral`. Модуль создаётся в `www/service/Модули/LoyaltyReferral/`.

---

## План работ (Мусохранов А.В.)

Делается **отдельными добросками, постепенно**. Прецедент — `PriceFormationOnlineKZ` (делал Кузаков Ю.), вопросы к нему.

1. Завести модуль `LoyaltyReferral`, выбрать компонент (тот же, что у `PriceFormation.Online`).
2. Добавить модуль в online-сборки (там где есть `priceformationonline`).
3. Выставить зависимости — «тут надо подумать» (риск цикла, см. ниже).
4. Перенести код: **а)** реферальных программ сделок, **б)** реферальных программ бонусов.

Проверка после этапов 1–2: убедиться что сборка не крякнула, найти модуль в дистрибутиве (через echo-orx).

---

## Настройки модуля (`.s3mod`)

- `component_uuid="0fd3d60c-48e1-41cd-89a7-b3819a1ad8f2"` — **совпадает с `PriceFormation.Online`** (как и просил Андрей).
- `id="019ed0db-8554-7b4f-ad75-8de5f9a10641"`, `package="Priceformation"`.
- ⚠️ `kaizen_zone="227c23e8-…"` **отличается** от канонической зоны price-formation `d09d92ec-6340-4f46-94f5-b940488a1a81` (у PF.Online и KZ). Требует уточнения.

## Зависимости

Поставлена **одна** зависимость, как у прецедента KZ:

```xml
<depends>
  <module id="f36d1d1d-94fb-4e3b-a980-96a4278e1c9f" name="PriceFormation.Online"/>
</depends>
```

Этого достаточно, пока код рефералки физически лежит внутри `PriceFormation.Online`: всё нужное приходит транзитивно.

**Что использует код рефералки** (`priceformationonline/referralprogram/`):
- `priceformationcommon` (117 импортов), `priceformationonline` (87) — поедут вместе с кодом.
- `Socnet` — это **локальный класс** в `priceformationonline/helpers/business_group.py:502`, НЕ платформенный модуль.
- Внешние платформенные Python-модули и их источники (найдено через saby-search):
  - `multitenancy` → **Multitenancy-Py** (sbis/core) — уже в depends PF.Online.
  - `rightcheck` (`raise_http403_admin_msg`) → **Rights-Py** (sbis/core).
  - `user_service_cloud` (`ClientServiceCloud`) → **UserServiceCloud-Py** (sbis/core).

**Нюанс на этап 3:** PF.Online сам НЕ объявляет `Rights-Py`/`UserServiceCloud-Py` — они приходят транзитивно. Когда код **переедет** в LoyaltyReferral и встанет вопрос обратного вызова (PF.Online → методы рефералки = риск цикла), depends придётся пересобрать явно: `PriceFormation.Common` + `Rights-Py` + `UserServiceCloud-Py` + `Multitenancy-Py` напрямую.

---

## Регистрация в сборках (этап 2)

Поиск по id PF.Online `f36d1d1d-94fb-4e3b-a980-96a4278e1c9f` (расширения s3srv/s3mod/s3cld/s3app/s3distr/s3deploy):

- **Боевая online-сборка (главная цель):** `online/inside` → `online-inside/s3srv/bl/online32.s3srv:454`. Сюда добавить `<bl_module id="..." name="LoyaltyReferral"/>` — отдельной доброской в том репозитории.
- **Наши тестовые сборки** (price-formation, уже сделано): `tests_new/online/clouds/Online/Service.s3srv` и `tests_new/online_with_discount_core/clouds/OnlineWithDiscountCore/Service.s3srv`. В `tests_new/desktop` НЕ добавлять (там нет PF.Online).
- **НЕ трогать:** потребители PF.Online (depends в их `.s3mod`: SabySalon, Основные средства, Retail Online, VirtualShop, wpc/PriceFormation, KZ/UZ/PricingRetailOnline) и чужие тестовые моки (booking, buh, crm, production, warehouse/docs, stats-core).

---

## Echo-метод и тест (этап 3, сделано)

Служебный метод для проверки сборки (удаляется после переноса первого боевого кода):

- `LoyaltyReferral/loyaltyreferral/echo.py` — `def echo(message): return message`.
- `LoyaltyReferral/LoyaltyReferral.orx` — метод `LoyaltyReferral.Echo` (`returns="SCALAR"` STRING, `access_mode="0"`, `category="Echo"` — категория свободнотекстовая, модуль-определяемая). Тело: `from loyaltyreferral.echo import echo / return echo(Message)`.
- Вызов из теста: `sbis.LoyaltyReferral.Echo('ping')`.

**Python-пакет модуля** = подкаталог рядом с `.s3mod` (как `priceformationonline` у PF.Online). Никаких CMakeLists/деклараций пакета не нужно — сборка сама добавляет каталог модуля в путь.

---

## Механика тестов и сборки (важные находки)

- **Тесты `tests_new` — симлинки.** Реальные файлы лежат в `tests/tests_<name>/`, а в `tests_new/online/src/` лежат git-симлинки (mode `120000`) с относительным таргетом `../../../tests/tests_<name>`. Для нового пакета: `tests/tests_loyaltyreferral/` (реальные файлы) + симлинк `tests_new/online/src/tests_loyaltyreferral`. Создавать симлинк на Windows: `MSYS=winsymlinks:nativestrict ln -s ../../../tests/tests_loyaltyreferral tests_loyaltyreferral`. Тест-пакеты обнаруживаются по каталогам, в `CMakeLists.txt` не перечисляются.
- **Запуск теста по файлу:** `cd <RUN_DIR> && python py_tests_runner.py <SRC_ROOT> echo.py --driver unittest --package_name Online`. Базовый класс — `tests_helpers.test_case.TransactionTestCase`. Pyright-ошибки на `sbis`/`tests_helpers` локально — норма (резолвятся только в SDK-рантайме).
- **Пересборка облака под новый модуль:** `python test_manager.py -project online --build true`. Регистрация `.orx`-метода и копирование Python-пакета модуля — **разные шаги**: метод может зарегистрироваться (`sbis.LoyaltyReferral.Echo` существует), а пакет ещё не быть на пути (`No module named 'loyaltyreferral'`) → нужен успешный полный билд. Собранный модуль лежит в `<build>/tests/online/run/modules/<ModuleName>/` (пустой каталог = билд не докопировал файлы).
- ⚠️ **Грабли:** `test_manager.py` гонит cmake/ninja через `subprocess.check_output` (stdout в PIPE). Если завернуть запуск в `| tail`, реальный exit-код маскируется и фоновый билд рапортует «успех» при фактическом провале cmake. Не пайпить вывод билда через tail.

---

## Статус

| Этап | Статус |
|---|---|
| 1. Модуль + компонент + зависимость | ✅ |
| 2. Тестовые сборки (online, online_with_discount_core) | ✅ |
| 2. Боевая `online32.s3srv` | ⬜ доброска в online/inside |
| 3. Echo-метод + тест (зелёный) | ✅ |
| 4. Перенос боевого кода (сделки → бонусы) | ⬜ |

Ветка: `26.4100/feature/aatimoshenko/04307161_3`.