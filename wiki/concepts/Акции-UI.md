---
type: concept
title: "Акции — Интерфейс"
tags:
  - loyalty
  - акции
  - ui
  - components
status: current
related:
  - "[[Акции-Subsystem-Overview]]"
  - "[[Loyalty-UI-Components]]"
  - "[[Promocode-Subsystem-Overview]]"
created: 2026-04-10
updated: 2026-04-10
---

# Акции — Интерфейс

Navigation: [[index]] | [[Акции-Subsystem-Overview]] | [[Loyalty-UI-Components]]

## Страница «Скидки и акции»

Отображает акции со статистикой применения. Позволяет создавать и редактировать акции.

**Корневой компонент**: `LoyaltyOnline/Promotion/registry:Browser`

Структура: иерархический список слева + несколько блоков справа (деталь). Кнопка `+` — создание новой акции.

Состав детальной части зависит от типа выбранной записи в мастере (группа / акция / штампованная акция).

## Общий реестр Акций и Промокодов

Переиспользуемое решение: один набор компонентов для реестра Акций **и** Промокодов, также расширяемый для розницы и порталов.

### Корневой компонент

**`Loyalty/Core/promoRegistry:Base`**

Два режима: только мастер (`onlyMaster: true`) или двухколоночный браузер (мастер-деталь).

Конфигурирует:
- Мастер через `masterTemplate`
- Деталь через `detailTemplate` (дефолт: `Loyalty/Core/promoRegistry:Detail`)
- Пропорции через `propStorageId`
- Фон через `contrastBackground`

### Мастер

Иерархия сущностей (Акции или Промокоды).

| Компонент | Описание |
|-----------|----------|
| `Loyalty/Core/promoRegistry:Master` | Таблица с иерархией (`Controls/treeGrid:View`). Базовый мастер |
| `LoyaltyOnline/Promotion/tile:View` | Плитка с иерархией |
| `LoyaltyOnline/Core/Promo/registry:Master` | Мастер с ПМО и операциями редактирования (`registryTemplate` — выбор вида) |

### Деталь (`Loyalty/Core/promoRegistry:Detail`)

Состоит из блоков (комбинация задаётся через `detailTemplate`):

1. **Карусель / Баннер** — для папок vs. отдельных сущностей
2. **Дополнительная статистика** — между баннером и продажами (сейчас: штампики)
3. **Информация о продажах** — реестр + итоги

> [!key-insight] Деталь имеет отдельный контекст
> Данные для всех блоков загружаются одновременно, перерисовка начинается синхронно после изменения контекста.

### Карусель

**`LoyaltyOnline/Core/Promo/registry:AdCarousel`** — используемый компонент. Отображает только вложенные сущности (папки скрыты). По клику — карточка сущности.

`LoyaltyOnline/Core/Promo/Registry/old:Carousel` — **устаревший**, не использовать для новых реестров.

### Баннер

**`LoyaltyOnline/Core/Promo/registry:Banner`** — название + описание + изображение сущности. Использует `PromoWidget/salesTile:View`.

`LoyaltyOnline/Core/Promo/Registry/old:Description` — **устаревший**.

### Блок продаж (`Loyalty/Core/PromoRegistry/sales:View`)

Состав: итоги (`Header`) + фильтр по периоду + реестр (`Registry`).

Данные в реестре: дата/время, сумма, состав (номенклатуры), сумма скидки, клиент, кассир.

Опции управления через `Base`:
- `salesTemplate` — полный шаблон блока продаж
- `salesRegistryTemplate` — шаблон реестра продаж (рекомендуется `Loyalty/Core/PromoRegistry/sales:Registry`)
- `totalsTemplate` — шаблон итогов (если `showTotalsInRegistry: false`)
- `salesShowFilter` — наличие фильтра (если true — итоги не стоит выносить отдельно)

## Ключевые компоненты

| Компонент | Путь |
|-----------|------|
| Базовый реестр | `Loyalty/Core/promoRegistry:Base` |
| Мастер | `Loyalty/Core/promoRegistry:Master` |
| Деталь | `Loyalty/Core/promoRegistry:Detail` |
| Карусель (актуальный) | `LoyaltyOnline/Core/Promo/registry:AdCarousel` |
| Баннер | `LoyaltyOnline/Core/Promo/registry:Banner` |
| Блок продаж | `Loyalty/Core/PromoRegistry/sales:View` |
| Реестр продаж | `Loyalty/Core/PromoRegistry/sales:Registry` |
| Итоги продаж | `Loyalty/Core/PromoRegistry/sales:Header` |
| Браузер реестра | `LoyaltyOnline/Promotion/registry:Browser` |

Все компоненты в репозитории `warehouse/price-formation`, ветка `client/`.

## Связанные страницы

- [[Акции-Subsystem-Overview]] — обзор подсистемы
- [[Loyalty-UI-Components]] — общая библиотека компонентов лояльности
- [[Promocode-Subsystem-Overview]] — тот же реестр переиспользуется для промокодов
