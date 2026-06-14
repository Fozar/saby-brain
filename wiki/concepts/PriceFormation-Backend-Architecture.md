---
type: concept
title: "PriceFormation Backend Architecture"
updated: 2026-04-10
tags:
  - price-formation
  - backend
  - python
  - wasaby
  - architecture
status: current
related:
  - "[[Loyalty-Database-Schema]]"
  - "[[Wasaby-BL-Objects]]"
  - "[[Wasaby-BL-Methods]]"
  - "[[Bonus-Programs-Architecture]]"
  - "[[DiscountCard-Subsystem-Overview]]"
  - "[[Promocode-Subsystem-Overview]]"
  - "[[Акции-Subsystem-Overview]]"
  - "[[Markup-Subsystem]]"
  - "[[ExternalLoyalty-Integrations]]"
  - "[[Sync-Broker-Architecture]]"
  - "[[PriceFormation-Test-Framework]]"
  - "[[PriceFormation-Common-Helpers]]"
  - "[[DCCommon-Helpers]]"
created: 2026-04-10
---

# PriceFormation Backend Architecture

Python бэкенд репозитория `price-formation`. Путь: `www/service/Модули/`.

---

## Модули верхнего уровня

| Модуль | Python-пакет | Назначение |
|--------|-------------|------------|
| `PriceFormation.Common` | `priceformationcommon` | Общая бизнес-логика, хелперы, базовые классы |
| `PriceFormation.Online` | `priceformationonline` | e-commerce ценообразование (основной модуль) |
| `PriceFormation.Offline` | `priceformationoffline` | Розница / склад / POS (кассы) |
| `DCCommon` | `dccommon` | Бонусный баланс, штрих-коды, шифрование, управление стендами |
| `DCRights` | — | Права доступа |
| `PriceFormationInside` | — | Внутренние инструменты (inside.sbis.ru) |
| `PriceFormationOnlineKZ` | — | Казахстанская локализация Online |
| `PriceFormationOnlineUZ` | — | Узбекистанская локализация Online |
| `PriceFormationPublic` | — | Публичное API |
| `PricingRetailOnline` | — | Ритейл Online ценообразование |

---

## PriceFormation.Common

**Роль:** разделяемая логика без привязки к каналу продаж. Online и Offline наследуют или переопределяют.

### Субпакеты

| Пакет | Содержимое |
|-------|------------|
| `core/` | `price_entity.py` — базовая сущность ВидЦены; `doc.py` — документооборот; `history_object.py`; `retail.py`; `sync.py` |
| `helpers/` | Утилиты: дата/время, деньги, номенклатура, локация, блокировки, логирование, работа с feature-флагами, CRM-клиент, упаковка |
| `discountcard/` | Базовые классы для ДК |
| `loyaltyprograms/` | → `loyaltyprogram/`, `promocode/` |
| `saledoc/` | Документ продажи (общие части) |
| `sync/` | `core.py` — механизм синхронизации |
| `discount/` | Базовая логика скидок |
| `prompt/` | Подсказки кассиру (база) |
| `dcservice/` | Сервис дисконтных карт (общее) |
| `price/` | Ценовые вычисления |

### Wasaby-артефакты

- `.orx` — регистрация объектов БЛ: `Core`, `DiscountCard`, `LoyaltyPrograms`, `Prompt`, `SaleDoc`
- `.s3mod` — манифест модуля
- `.dicx` — маппинг таблиц БД (изменение требует пересборки проекта)
- `.uax` — права доступа
- `.rlx` — локализация
- `.feature` — декларация feature-флагов

---

## PriceFormation.Online

**Роль:** основной e-commerce модуль. Содержит полные реализации всех подсистем лояльности.

### Субпакеты

| Пакет | Ключевые файлы / дочерние пакеты |
|-------|-----------------------------------|
| `loyaltyprograms/bonus/` | ~20 методов: `get_list`, `get_client_list_with_stats`, `accrue_for_closed_sales`, `get_calculator_data`, `read_settings`, `notify_sabyget`, … |
| `loyaltyprograms/promotion/` | Полный CRUD Акции + `handle_status`, `set_franchise`, `has_available`, `get_gift_list`, `notify_on_publish_changed` |
| `loyaltyprograms/promocode/` | Полный CRUD + `handle`, `sync`, `notify`, `notify_concierge`, `history` |
| `loyaltyprograms/bonus_dec_rule/` | Правила вычета бонусов |
| `loyaltyprograms/partner_promo_code/` | Партнёрские промокоды |
| `loyaltyprograms/individual_promo_code_emission/` | Индивидуальная эмиссия |
| `loyaltyprograms/activity_promo_code/` | Промокоды за активность |
| `loyaltyprograms/priceentitycardtype/` | Связь ВидЦены ↔ ВидКарты |
| `loyaltyprograms/referralbonus/` | Реферальные бонусы |
| `loyaltyprograms/publicationofpromotions/` | Публикация акций |
| `markup/` | Наценки (Тип=32) |
| `referralprogram/` | Реферальная программа (лиды, вознаграждения) |
| `dcservice/` | Сервис ДК для Online |
| `core/` | `price_entity_sale_doc.py` — применение ВидЦены к документу; `statistics.py` |
| `loyaltyreports/` | Отчёты лояльности |
| `loyaltywidgets/` | Виджеты (Online-специфичные) |
| `helpers/` | Online-хелперы |
| `sync/` | Синхронизация Online→Offline |
| `saledoc/` | Online-специфика документа продажи |

### Wasaby-артефакты (сверх Common)

- `.dwc` — DWC-воркфлоу: `LoyaltyPrograms.dwc`, `LoyaltyReports.dwc`
- `.hox` — обработчики событий: `DiscountCard.hox`, `LoyaltyPrograms.hox`, `Markup.hox`, `Prompt.hox`, `ReferralProgram.hox`
- `.cnv` — конвертеры данных
- `.trg` — триггеры БД

---

## PriceFormation.Offline

**Роль:** ценообразование для касс, POS, складских систем (Desktop Розница / Presto).

Более компактный, чем Online. Содержит только подсистемы, нужные офлайн-каналу.

### Субпакеты

| Пакет | Примечание |
|-------|------------|
| `discount/` | Скидки для POS |
| `discountcard/` | ДК для офлайн |
| `loyaltyprograms/` | Программы лояльности (ограниченный набор) |
| `sync/` | `helpers.py` — вспомогательная логика брокерной синхронизации |

**Отсутствуют** относительно Online: `markup/`, `referralprogram/`, `loyaltyreports/`, `loyaltywidgets/`, `dcquestionary/`.

### Wasaby-артефакты (уникальные)

- `.schedule` — задачи планировщика (offline-специфика)

---

## DCCommon

**Роль:** нижний уровень инфраструктуры, используется и Online, и Offline.

| Пакет | Содержимое |
|-------|------------|
| `core/` | Бонусный баланс, шифрование, барко-движок, управление стендами |
| `helpers/` | DCCommon-утилиты |
| `questionary/` | Анкеты клиентов |

---

## Паттерны организации кода

### Один файл — один метод БЛ
Каждый Python-файл в пакете реализует один метод БЛ (CRUD или custom). Например:
```
loyaltyprograms/bonus/get_client_list_with_stats.py  →  Bonus.GetClientListWithStats
loyaltyprograms/promotion/create.py                  →  Promotion.Create
```

### Переопределение Common → Online/Offline
Common содержит базовые заглушки (`__init__.py` с общими константами), Online/Offline переопределяют конкретную логику.

### Feature-флаги
`sbis_feature` недоступен в тестовой среде — всегда мокировать через `@enable_features`. Подробнее: [[PriceFormation-Test-Framework]].

### Sync-брокер
Offline-синхронизация через `PFSync.BrokerSyncLoyalty`. Broker-методы называются `<Entity>FirstSync2`/`RegularSync2`. Билдер: `BrokerBuilder`, не `_send_to_broker`. Feature flag: `lty_broker_card_type`.

---

## Связанные страницы

- [[Loyalty-Database-Schema]] — схема БД (ВидЦены / Карта / ВидЦеныДокумент)
- [[Wasaby-BL-Objects]] — как объекты БЛ регистрируются через `.orx`
- [[Wasaby-BL-Methods]] — таксономия методов
- [[Bonus-Programs-Architecture]] — детали подсистемы бонусов
- [[DiscountCard-Subsystem-Overview]] — детали подсистемы ДК
- [[Promocode-Subsystem-Overview]] — детали промокодов
- [[Акции-Subsystem-Overview]] — детали акций
- [[Markup-Subsystem]] — детали наценок
- [[ExternalLoyalty-Integrations]] — UDS / PremiumBonus / iikoCard
- [[Sync-Broker-Architecture]] — механизм синхронизации Desktop→Cloud
- [[Loyalty-Desktop-Broker-Migration]] — текущий проект миграции на брокер
- [[PriceFormation-Test-Framework]] — три тестовых проекта, test_manager.py, cmake/ninja, мок-паттерны
- [[PriceFormation-Common-Helpers]] — детальный каталог helpers/ в PriceFormation.Common
- [[DCCommon-Helpers]] — детальный каталог helpers/ и core/ в DCCommon