---
type: concept
title: "SabyGet: при присоединении к партнёру франшизы не видно приветственных бонусов"
created: 2026-10-05
updated: 2026-10-05
status: developing
tags:
  - franchise
  - sabyget
  - greeting-bonus
  - loyalty-program
  - tech-design
related:
  - "[[DiscountCard-GetListWithStats-SDK-Call-Loop]]"
---

# SabyGet: при присоединении к партнёру франшизы не видно приветственных бонусов

Задача в разработку №02185039 ([ссылка](https://online.sbis.ru/opendoc.html?guid=f0afb930-9ceb-410e-b523-9664291f2631&client=3)), автор Алябушев А.А., веха 26.6100, срок 28.11.2026. Пришла из ошибки на стенде Дорогунцовой от 01.10.2025 ([ссылка](https://online.sbis.ru/opendoc.html?guid=f54f1072-c7b4-4300-9e21-ac120cd19072&client=3)). На странице присоединения к заведению партнёра франшизы клиент видит только «вы получите», без «100 Б за регистрацию». После присоединения бонусы всё равно начисляются. Задача с февраля 2026 переходила от Курникова к Омельяненко, потом к Кузакову, 05.10 её взял Тимошенко.

В задаче записан путь через СДК, оценка 0.5 + 0.5, исполнитель Кузаков:
1. Новый метод с сигнатурой `LoyaltyProgram.GetBannerList`, который решает, в какой аккаунт идти: для партнёра в аккаунт владельца.
2. `LoyaltyProgram.GetDescriptionBySalePointV2` для партнёра тоже идёт в аккаунт владельца.

## Почему нет сообщения (по коду, 05.10)

- SabyGet (`sabyget/core`, `sgr_establishments.get_bonus_details`) вызывает `GetDescriptionBySalePointV2(point_id, by_referee)` и `GetBannerList(None, {SalePointId}, None, None)` через `sbis.BLObject`, то есть в online аккаунта заведения (партнёра). Ответы уходят в `showcase-service` `Establishment.BonusDetails`. Фронт (`SabyGetReferral/_details/Panel/Preview`) рисует «за регистрацию» из `GreetingBonuses`. Что `GreetingBonuses` собирается из `GreetingValue`, по коду showcase не проверено.
- `GreetingValue` online берёт из настроек бонусов текущего аккаунта (`_get_bonus_settings_params`).
- Настройки приветственных бонусов в аккаунт партнёра нарочно не синхронизируются: `sync/get_bonus_data_for_partner.py` убирает `GREETING_BONUS_SETTING_FIELDS`, `sync/set_bonus_data_for_partner.py` ставит `GreetingValue = None` (`ccf7502184`, Постнов, 2024-09). У партнёра всегда 0.
- Начисление идёт в аккаунте владельца: СДК `LoyaltyProgram.Join` (discount-cards, `dcservice/sabyget/loyaltyprogram/join.py`) по `get_account_franchise_info` подменяет клиента на владельца и передаёт `sale_point=None` + `IsFranchise`. Онлайн `join` и `apply_greeting_global_bonus` с `is_franchise` начисляют `GreetingValue` владельца без проверки точек продаж.

## Варианты

**А. Как в задаче, прокси в СДК.** В `SabyGet.orx` discount-cards методы с `ClientID`, для партнёра вызов online владельца, как `Join`. Плюс: проверка, что именно эта точка продаж входит в договор (подписки socnet). Минусы: три репозитория; SabyGet надо переключать на СДК (чужая команда, файл Палочкина); online-методы надо учить работать без точки продаж: в аккаунте владельца её нет, а `_get_bonus_settings_params(None)` при списке точек `INCLUDED` выключает бонусы.

**Б. Только в online.** `GetDescriptionBySalePointV2` уже знает роль аккаунта (`get_account_franchise`). Для `FRANCHISEE` взять `GreetingValue` владельца через `multitenancy.CreateMultitenantEndpointByClientId(get_owner_account_id(...))`, по образцу `discountcardtype/read_questionary.py`. SabyGet и СДК не трогаем. Минус: франшиза определяется по аккаунту целиком, а не по точке продаж. Так же в этом методе уже выбирается тип карты.

Тимошенко склоняется к Б. `GetBannerList`, похоже, не нужен: начисления владельца при `UseForFranchise` синхронизируются партнёру, но на стенде это не проверено.

## Открытые вопросы

- Выбор варианта: 05.10 подготовлено сообщение Омельяненко с вариантами А и Б. Отправлено ли оно, в этой записи не отражено.
- Точки продаж партнёра вне договора: в Б для них тоже покажутся бонусы владельца, а `Join` начислит по настройкам партнёра, то есть 0.
- Приоритет реферальных приветственных бонусов партнёра при `by_referee`: оставить как сейчас.
- Ветка от `rc-26.6100`. Реализация не начата.
