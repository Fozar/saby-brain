---
address: c-000292
type: concept
title: "Лицензия внешних систем при открытии смены — №07282570"
created: 2026-11-09
updated: 2026-11-20
status: developing
related:
  - "[[Loyalty-November-2026-WorkPlan]]"
  - "[[zvonok-matyushev-timoshenko-plan-2026-11-09]]"
  - "[[Loyalty-External-License-PremiumBonus-Registration-07282658]]"
  - "[[Loyalty-External-License-Customer-Selection-07282646]]"
  - "[[Loyalty-License-Dispatcher-PromoCode-Migration-09281060]]"
  - "[[zvonok-matyushev-timoshenko-license-dispatcher-2026-11-19]]"
---

# Лицензия внешних систем при открытии смены

## Задача

№07282570: https://online.sbis.ru/opendoc.html?guid=019fa782-257b-7bb1-82fa-f9d935fbd046&client=3

Ноябрьский план №606980697, пункт `635460072`. Срок пункта: **2026-11-29**; срок карточки: **2026-11-29**. Плановая оценка: 1.7 ч.

Веха: 27.1100 online/inside (27.1000 Platforma) до 06.02.27.

## Где остановились

**Второй этап запушен в коммите `3423267fa6`, поверх `f02bcec58c`.** По предложению Матюшева от 20.11 балансная проверка и разбиение точек вынесены в `BillingHelper`; диспетчер выбирает небалансную проверку по базовому классу параметра. Из стэша взяты контракт `License.Require` и обработка сбоя при пересчёте; сам стэш сохранён. Под `check_feature(Feature.EXT_LOYALTY_LICENSE)` один запрос проверяет лицензию аккаунта без списания, результат записывается для подключённых точек. Нет точек — старые записи удаляются. При сбое подбора точек интеграций или неизвестном ответе биллинга прежние записи сохраняются, балансные обновляются. `GetTypesBySalePoint` и `CheckLicense` не менялись. 11 изолированных тестов прошли, pylint рабочего кода 10/10. На SDK 271000 первый прогон выявил цикл: обработчик интеграций импортирует настройки бонусов, которые используют диспетчер. Перенос импорта в метод подбора точек устранил цикл; до слияния 45 штатных тестов лицензирования прошли. В !154956 был конфликт с `rc-27.1100`: локально сохранены релизные ID Pro/Max и откат на Basic при выключенной фиче, а также новая проверка через BillingHelper и правка импорта. По просьбе пользователя ветка перебазирована на `rc-27.1100` (`ae5d408565`), merge-коммит `fd141f9139` удалён из истории ветки. Остались два коммита `f02bcec58c` и `3423267fa6`; правки по ревью во втором. Дерево файлов не изменилось. GitLab подтверждает отсутствие конфликта в !154956. Critical: импорт классов настроек перенесён в метод подбора точек. Medium: `GetSalePoints` и реализация iikoCard теперь статические, без чужого `self`. После слияния прошли 72 целевых теста лицензий и обработчика интеграций на SDK 271000. Первый общий прогон прервался из-за кодировки при выводе знака рубля; повторный запущен с UTF-8.

**MR первой итерации на доработке.** Коммит `bfc192b062` запушен в `27.1100/feature/aatimoshenko/07282570`. [MR в СБИС](https://online.sbis.ru/opendoc.html?guid=01a1f847-9497-7a0a-952e-ccf331e0fa5a&client=3), [GitLab !154956](https://git.sbis.ru/warehouse/price-formation/-/merge_requests/154956), [!154957](https://git.sbis.ru/warehouse/price-formation/-/merge_requests/154957). В MR только параметр и подбор ТП; пересчёт лицензии не подключён.

**Согласован первый шаг итеративно.** Матюшев попросил сначала декларацию `IntegrationLicense` и подбор ТП в `LicenseConsumersGetter`, без внедрения в `RefreshLicense`. Все его замечания к этому MR учтены: использованы `UDSSettings`/`PremiumBonusSettings`/`IikoCardSettings` из `integration_handler.py` вместо прямого ветвления, таймаут поднят до 5000 мс, добавлен `@logging`, метод нестатический, заданы `MAIN_LICENSE_ID = SALE_POINT_LICENSE_ID = SALE_POINT_LICENSE_BALANCE_ID = 'LOYALTY_INTEGRATION'`. Проверка `if not account` удалена по просьбе пользователя. Ключ типа интеграции — `connection.Get('name')`. 5/5 изолированных тестов со стабами платформы, pylint рабочего кода 10/10. Сборка стенда 266100, ветке нужен SDK 271000.

Расширение `CheckLicense` без ТП и прикладные сценарии остаются в задачах №07282646 и №07282658. Черновое решение полного цикла сохранено в stash `f302e4affe` как исторический вариант; целиком его применять нельзя.

## Постановка и критерий

Внедрить проверку лицензии внешних систем при открытии смены. Доработать RefreshLicense и LicenseDispatcher для небалансного параметра внешних систем. В карточке отдельно написано: «Со стороны кеша и проверок уже поддержано». Критерий плана: в 27.1100 согласно требованиям.

## Что выяснено по коду

**Фронт открытия смены (retail/ui-platform, RetailTestWorkplace) уже интегрирован с кэшем и менять его не нужно:**
- `client/RetailTestWorkplace/Utils.ts`: `shouldCheckLoyalty()` → `LoyaltyLicense.GetTypesBySalePoint(SalePointList)`; `checkLoyaltyLicense()` → `LoyaltyLicense.GetLicenseWarning(SalePointList)`.
- `client/RetailTestWorkplace/Main.ts`: для ТП с непустым `LicenseTypes` создаётся обязательный тест «Проверка лояльности».
- `client/RetailTestWorkplace/Tests/Device/Loyalty.ts`: баннер строится из Caption/Body/Recomendations ответа GetLicenseWarning.
- Скриншот Курникова (вложение, 05.11): показан текст «Нет лицензии "Интеграция с системами лояльности"». Скриншот не доказывает блокировку; ТЗ прямо её исключает.

**Кэш и бэкенд (price-formation):**
- Кэш `LicenseState` (глобальный параметр `PriceFormation.LicenseState`, priceformationcommon/license/core/cache.py): `license_data = {sp_id: {LicenseType: bool}}`.
- `RefreshLicense` (priceformationonline/license/loyaltylicense/refresh_license.py) идёт по `all_license_params = [BasicLicense, ProLicense, MaxLicense]`, собирает потребителей-ТП (`LicenseConsumersGetter`) и зовёт `LicenseDispatcher.check_for_consumers` → `BillingHelper.check_license` → `sbis.License.CheckByConsumers` с балансным параметром `DISCOUNTS_PS`. LOYALTY_INTEGRATION в этом списке нет — кэш этим типом не наполняется.
- Тип `LOYALTY_INTEGRATION` есть в `LicenseType` (types.py) и в License.orx (CheckLicense/GetLicenseInfo его перечисляют), но состояние в кэш не пишется.

**Контракт небалансного параметра (подтверждён фронтом):**
- `loyalty/external-discount`, `client/ExternalBonus/Connection/_base/Preload/LicenseDataFactory.ts`: проверка через `License.Require(Params: {ComponentIDs: ['LOYALTY_INTEGRATION']})` — без потребителей; в ответе флаг по компоненту и `RestrictionConfig[COMPONENT_ID]`.
- Тот же паттерн массово используется в других репозиториях (edo и др.) — это стандартный вызов биллинга для небалансных компонентов.

**Подбор ТП для лицензии интеграций (реализован в MR):**
- `LicenseConsumersGetter.get_integration_sale_points()` (priceformationonline/license/core/license_parameter.py): один пакетный вызов `IntegrationCfg.GetAll` для `uds`, `pb`, `iiko_card` с `account=sbis.Session.ClientID()`, timeout 5000 мс, `@logging`.
- Разбор настроек через `UDSSettings`/`PremiumBonusSettings`/`IikoCardSettings.get_sale_points()` из `loyaltyexternalonline/externalsystem/externalintegration/integration_handler.py`. Пустой `contragents` UDS/PB трактуется как общий профиль на все ТП (`get_sale_point_list(include_additional=True)`). iikoCard — только `salesPointMatching`. Дубли устраняются `set`. Отсутствие ответа сервиса → `sbis.Error`.
- `IntegrationLicense` (LicenseParameterBase): `LICENSE_TYPE = LOYALTY_INTEGRATION`, `MAIN_LICENSE_ID = SALE_POINT_LICENSE_ID = SALE_POINT_LICENSE_BALANCE_ID = 'LOYALTY_INTEGRATION'`, `SUITABLE_REASON_LIST = []` (списания нет). `_get_consumers` возвращает `LicenseConsumers` с отсортированными ТП.
- Тесты: `tests/tests_priceformationonline/licence/license_consumers_getter.py` (TransactionTestCase, super().setUp()) — сбор ТП из нескольких интеграций с дедупликацией и аргументами `GetAll`, общий профиль UDS/PB, пустое сопоставление iiko, пустой список подключений, отсутствие ответа.

**Исторический контекст (для следующих итераций):**
- Отдельная ветка в RefreshLicense с `_get_integration_states` удалена; общий путь — `LicenseConsumersGetter → LicenseDispatcher.check_for_consumers → LicenseConsumers.as_mapping`, параметр выбирает операцию обратным вызовом.
- В стенде 266100 штатный прогон недоступен; на SDK 271000 нужно подтвердить маршрут Online/Desktop и замерить время ответа `GetTypesBySalePoint` при медленном `RefreshLicense`.
- Для регистрации PB без ТП понадобится расширение `CheckLicense`; текущий кеш по ТП для этого не подходит.
- Общее подключение без contragents трактуется как действующее на все ТП; пустой успешный список подключений очищает прежние записи типа; ошибка сервиса сохраняет прежние записи.
- ТЗ проекта, §6.1.4: открытие смены не блокируется; взятие в долг не делается; редактирование настроек не запрещается.

## Решения и почему

Сначала декларация параметра и подбор ТП, затем подключение к RefreshLicense и диспетчеру. Разбор настроек подключений переиспользует `GetSalePoints`-миксин из `integration_handler.py`, чтобы не плодить третью копию правил. Таймаут 5000 мс согласован с Матюшевым. Проверка `if not account` не выполняется — проект такое не проверяет.

Не делаем (scope): фронт, запрет редактирования настроек, долг, сценарии регистрации/выбора клиента, частичное обновление кеша при сохранении настроек.

## Открытые вопросы

1. Прогнать пересчёт `IntegrationLicense` на стенде с SDK 271000.
2. Расширить `CheckLicense` для `LOYALTY_INTEGRATION` без ТП (Online, через диспетчер/BillingHelper) для задач №07282646 и №07282658.
3. Поведение `GetTypesBySalePoint` при пустом/просроченном кеше: Матюшев считает вызов `RefreshLicense` вспомогательным и не хочет ориентироваться на его результат.
4. Штатный прогон и ручная проверка Online/Desktop на SDK 271000.

## Roadmap

- [x] Декларация `IntegrationLicense` и подбор ТП в `LicenseConsumersGetter`.
- [x] MR первой итерации оформлен и запушен.
- [x] Подключить параметр в `RefreshLicense` и `LicenseDispatcher` (вторая итерация).
- [ ] Проверить открытие смены на нескольких ТП одного аккаунта с лицензией и без.
- [ ] Передать общий механизм в задачи регистрации (№07282658) и выбора клиента (№07282646).

## Ссылки

- План: [[Loyalty-November-2026-WorkPlan]].
- Встреча 09.11: [[zvonok-matyushev-timoshenko-plan-2026-11-09]].
- Звонок 19.11: [[zvonok-matyushev-timoshenko-license-dispatcher-2026-11-19]].
- ТЗ проекта: вложение «Техническое задание» от Барышевой, 06.07.2026, §6.1.4.
- MR: [СБИС](https://online.sbis.ru/opendoc.html?guid=01a1f847-9497-7a0a-952e-ccf331e0fa5a&client=3), [GitLab !154956](https://git.sbis.ru/warehouse/price-formation/-/merge_requests/154956), [!154957](https://git.sbis.ru/warehouse/price-formation/-/merge_requests/154957).
- Ветка: `27.1100/feature/aatimoshenko/07282570`, коммит `bfc192b062`.
