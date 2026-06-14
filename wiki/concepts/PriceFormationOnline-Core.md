---
type: concept
title: "PriceFormationOnline — Core"
tags: [price-formation, core, python, online, statistics, history]
status: evergreen
related:
  - "[[PriceFormation-Backend-Architecture]]"
  - "[[PriceFormationOnline-Helpers]]"
  - "[[PriceFormation-Common-Helpers]]"
  - "[[Акции-Subsystem-Overview]]"
  - "[[Bonus-Programs-Architecture]]"
  - "[[DiscountCard-Subsystem-Overview]]"
created: 2026-04-10
updated: 2026-04-10
---

# PriceFormationOnline — Core

Базовые модули онлайн-части: `www/service/Модули/PriceFormation.Online/priceformationonline/core/`

Структура: `core/core/history/`, `core/priceentity/`, `core/priceformation/`, `core/statistics.py`, `core/price_entity_sale_doc.py`

---

## History Tracking (`core/core/history/`)

### `price_entity.py` — история ВидЦены (автор: Помпеев А.А.)

**`PriceEntityHistory(HistoryObject)`**:
- `_verb_to_create = 'Создан'`
- `_verb_to_delete = 'Удален'`
- `_send_to_history(cls, id_, name, messages, action)` — отправить запись в реестр истории; если `name` не передан — читает из `sbis.PriceEntity.Прочитать(id_)`

### `price_entity_common.py` — общие хуки истории (автор: Помпеев А.А.)

Хуки, вызываемые из `.hox`-файлов по событиям BL:

- `on_after_create(new_record)` — маршрутизирует по типу: RETAIL_GIFT_DISCOUNT→GiftHistory, DISCOUNT-архетип→DiscountHistory, BONUS-архетип→BonusHistory, BONUS_DEC_RULE→pass
- `on_after_update(old_record, new_record)` — маршрутизирует по типу на update-хендлеры
- `on_after_delete(old_record)` — скидки, бонусы, праздничные бонусы, наценки, подсказки
- `on_set_not_used(new_record)` — скидки, бонусы, праздники, наценки, bonus_dec_rules
- `get_history_object_by_type(price_entity_type)` → DiscountHistory / BonusHistory / Stub
- `get_history_instance_names(ids, caption)` → `sbis.Record` — имена для сервиса истории (SQL по ВидЦены)

SQL константа: `_SQL_GET_NAMES`

---

## Price Entity Management

### `price_entity_sale_doc.py` — типы связей документов ВидЦены

**`LinkType`**:
- `PROMOTION_CHANGE = 1` — документ изменения акции
- `RETAIL_AGGREGATE = 2` — агрегат применения розничной акции
- `PROMOTION_AGGREGATE_MONTH = 3` — месячный агрегат применения
- `REVIEW_BONUS = 4` — бонусы за отзывы
- `PARTNER_AGGREGATE = 5` — агрегат применения партнёрской акции
- `NEW_FREE_LINK_TYPE_1 = 6`, `NEW_FREE_LINK_TYPE_2 = 7` — зарезервированы

### `priceentity/set_not_used.py` — перевод в статус "не используется"

`set_not_used(price_entity_list: list[int])`:
1. SQL UPDATE: ВидЦены.Используется = 0 для указанных IDs, возвращает обновлённые записи
2. Вызывает `on_set_not_used` для каждой записи
3. Синхронизирует в брокер через `price_entity_to_broker()`

SQL константа: `_SQL_UPDATE`

---

## Sales Point Tree (`priceformation/sales_point_tree.py`, автор: Литвинцева М.А.)

`sales_point_tree(add_fields, filters, sort, navigation)` → `RecordSetType`:
1. Вызывает `sbis.SalesPoint.Tree()`
2. Фильтрует поля из соображений безопасности (оставляет whitelist)
3. Whitelist: Id, Folder, Folder@, Folder$, Name, YouAreHere, Company, CompanyFolder, SalesPoints, Filials, Visible, RealCompany, MainCompany, CompanySPP, IsParent, CompanyName, CompanyNode, ASPNode, AdditionalSP, SPType, ChildsSPType, Collages
4. Мигрирует формат записи в новую структуру

---

## Cloud Statistics (`statistics.py`)

Модуль сбора аналитики о применении программ лояльности и промо-активностей.

### Константы и классы

**`CloudStatsFunctional`** — функциональные области:
- `BONUS='Бонусы'`, `PROMPT='Подсказки'`, `PROMOTION='Скидки и акции'`
- `PROMOTION_CONDITIONS='Условия акций'`, `PROMO_CODE='Промокоды'`
- `NUMBERED_CARD='Дисконтные карты'`, `INTEGRATION='Интеграция'`
- `LOYALTY='Лояльность'`, `REFERRAL_PROGRAM='Реферальные программы'`

**`CloudStatsContext`** — контексты / продукты:
- `SETTINGS`, `ISSUE`, `APPLICATION`, `ACCRUAL`, `FRANCHISE`, `LEAD`, `REVIEW`
- `RETAIL`, `PRESTO`, `SALON`, `ONLINE`, `ACCOMMODATION`, `W_DOC`
- `get_product_name(cls, product_id=UNKNOWN_PRODUCT)` → строка; пытается в порядке: маппинг по ID → USER-AGENT хедер → конфигурация аккаунта
- `UNKNOWN_PRODUCT = -1` — sentinel (None тоже валиден для "Розница")

**`CloudStatsAction`**: `SYNC='Синхронизация'`, `ACCRUAL='Начисление'`

**`CloudStatsNumberedCardAction`** — действия с дисконтными картами:
- `SETTINGS_UPDATE`, `NOTIFICATIONS_ON`, `STAMPS_ON`
- `CARD_ISSUE_QUESTIONARY`, `CARD_ISSUE_SABY_GET`, `CARD_ISSUE_OTHER`
- `CARD_RETAIL_SALE_USE`, `CARD_WAREHOUSE_DOC_USE`

**`CloudStatsReferralAction`**: `SEND_LEAD='Отправлена заявка'`, `RECEIVE_LEAD='Получена заявка'`

**`LoyaltyConditionContext`**: BUY, CLIENTS, PARTNERS, PROMO_CODE, WITH_DISCOUNTS

**`CloudStatsNumberedCardMetric`** — агрегированные метрики (кортежи Functional+Context+Action)

**`SaleDataForStatistics` (dataclass)** — данные продажи для статистики:
- `bonus_dec_types: list`, `bonus_inc_types: list`, `external_discount_types: list`
- `is_auto_promotion_applied: bool`
- `is_bonus_dec_rule_applied: bool` — гибкое списание бонусов
- `is_franchise_promotion_applied: bool`
- `is_percent_markup_applied: bool`
- `is_discount_n_value_applied: bool` — скидка на N-й товар
- `is_discount_with_package_applied: bool` — пакетная скидка
- `is_discount_with_time_check_mode_applied: bool` — временная скидка
- `sale_point: int | None`
- `is_target_pos_list: bool`, `cumul_gift_is_used: bool`

### Функции

**`send_operation_to_cloud_statistics(functional, context, action, ext_data=None)`** — отправить операцию в статистику (Statistics.get_instance().add())

**`async_send_p_use_to_cloud_statistics(...)`** — асинхронная отправка через `sbis.BLObject('PriceFormation').AsyncInvoke()`

**`send_promotion_use_to_cloud_statistics(sale_id, doc_id, context, product_id, promotion_types, source_app_type, app_version, delivery_type, with_bonus_inc, with_bonus_dec)`** — синхронная отправка статистики применения промо

**`send_sale_operation_to_cloud_statistics(sale_id, functional, context, action, product_id, source_app_type, app_version)`** — отправить отдельную операцию продажи

**`send_referral_program_to_cloud_statistics(*, action)`** — отправить активность реферальной программы

**`get_sale_source_info_by_sale_id(sale_id)` → `tuple[ProductIdType, SourceAppType]`** — получить product_id и source_app_type через `sbis.Sale.BuildReadFull()`

**`get_application_by_sale_source_info(product_id, source_app_type)` → `str | None`** — маппинг на строку приложения: `'SbisKiosk'`, `'ret-saby'`, `'retail-saby'`, `'rest-saby'`, `'presto-saby'`, `'salon-saby'`

**`get_sale_data_for_statistics(sale_id, doc_id, promotion_types, with_bonus_inc, with_bonus_dec)` → `SaleDataForStatistics | None`** — извлечь статистические данные из записей продажи (12+ булевых флагов)

**`sql_get_sale_data_for_statistics(sale_id, doc_id, promotion_types)`** — SQL-запрос (WITH + multi-join):
- CTE `BusinessGroupFolders` — для определения франшизной бизнес-группы
- Джойны: ВидЦеныДокумент, ВидЦены, ВидЦеныРасширение, ВидЦеныНоменклатура
- Вычисляет флаги: IsAuto, IsTargetPosList, DiscountWithPackage, IsPercentMarkup и др.
- Фильтрация по sale_id / ReferralSale / doc_id / promotion_types
