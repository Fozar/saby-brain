---
type: concept
title: "Loyalty Database Schema"
updated: 2026-04-10
tags:
  - loyalty
  - database
  - price-formation
  - sbis
status: current
related:
  - "[[Loyalty-Product-Overview]]"
  - "[[Loyalty-In-Products]]"
  - "[[price-formation/_index]]"
  - "[[Wasaby-Framework]]"
  - "[[Franchise-Loyalty-Architecture]]"
created: 2026-04-10
---

# Loyalty Database Schema

Database structure for the SBIS/Saby loyalty and price formation system. Online and offline schemas are conceptually identical.

---

## Core Entity Model

Central entity: **ВидЦены** — represents any price type, discount, bonus program, or special price. All loyalty program types map to this single entity.

```
ВидЦены ──── ВидЦеныРасширение   (extended attributes)
          ├── ПериодДействия      (validity periods)
          ├── ВидЦеныРоль         (user roles for manual discount)
          ├── ВидЦеныРегион       (region restrictions)
          ├── ВидЦеныЛица         (allowed/forbidden buyers)
          ├── ВидЦеныНоменклатура (nomenclature lists)
          ├── ПороговыеУсловия    (threshold conditions)
          └── ВидЦеныВидКарты ── ВидКарты ── Карта
                                              (card instances)

ВидЦеныДокумент ── links ВидЦены + Карта + Sale/Document
```

---

## Table Reference

### ВидЦеныЛица
Links ВидЦены to specific persons (buyers/clients).

| Field | Type | Description |
|-------|------|-------------|
| `ТипЛица` | Enum | Type of link: employee (сотрудник), client (клиент), or partner (партнер). Added for franchise support — see [[Franchise-Loyalty-Architecture]] |

Stores both individual contractors and groups (папки). Role ID as text is a legacy artifact — to be replaced.

---

### ВидЦеныРасширение
Extended attributes for ВидЦены.

| Field | Type | Description |
|-------|------|-------------|
| `GroupId` | UUID | ID of the franchise social network group (соцсеть) to which the promotion belongs |

---

### ВидЦены
Central table for prices, discounts, bonus programs.

**Тип (key values)**:
- `5` — Бонусная программа (БП, accrual rules). See [[Bonus-Programs-Architecture]]
- `9` — Реферальная бонусная программа. See [[Referral-Bonus-Program]]
- `18` — Подсказка кассиру (Cashier Hint/Prompt). See [[Prompts-Cashier-Hints]]
- `32` — Наценка (Markup). See [[Markup-Subsystem]]
- `40` — Правило списания бонусов (BonusDecRule). See [[BonusDecRule-Info-Model]]

БП (Тип=5) related tables: `ВидЦеныНоменклатура` (accrual items), `ВидЦеныЭмиссия` (card emissions), `ВидЦеныЛица` (personal clients), `ВидЦеныДокумент` (event log, Бонусы field = accrual+ / spend−, ДатаВремяСгорания = expiry).

`Атрибуты` JSON field may contain:
- `Bonus` — accrual period, delay, expiration period
- `Discount` — set size, set type for bundle discounts
- `Gift` — gift delivery type, distribution method, item type
- `SetSettings` — hint/tip conditions
- `UdsBonus` — external UDS bonus connection ID
- `ForAllCards` — flag for universal discount availability
- `FranchiseRole` (int) — `1`=Owner, `2`=Participant; present on franchise-shared programs. See [[Franchise-Loyalty-Architecture]]
- `AgentGroupFolder` (bool) — marks a virtual folder node in the promotion hierarchy for franchise group promotions

### ВидЦеныДокумент
**Central statistics table** — every loyalty event on a sale is recorded here. Used for all loyalty reports and statistics.

One row represents one of these:
| Record type | Key fields |
|---|---|
| Assigned price | ВидЦены, Документ/Sale, ДатаВремя |
| Applied discount | ВидЦены, Sale, Сумма, Карта, Применена |
| Linked discount card | Sale, Карта, Сумма=чек |
| Linked personal card | Sale, Карта, Сумма=чек |
| Bonus accrual/spend | ВидЦены, Карта, Бонусы, ДатаВремяСгорания |
| Manual bonus change | ВидЦены, Карта, Responsible |
| Certificate sale/pay/return | Sale, Карта, Атрибуты.Cert.Action |
| Promo code link | Sale, Сумма, PromoCode |
| Promo code issuance | Sale, Карта, Атрибуты.PromoCode.Available/Given |

**Fields**: `Атрибуты` JSON contains `Bonus`, `StatChange`, `Discount`, `Cert`, `Gifts`, `UdsBonus`, `PromoCode`, `Referral` sub-objects.

For СУ (warehouse): `Sale=NULL`. For Розница: `Документ=NULL`.

Two extra fields for report optimization: `NomPrice` and `TotalPrice` — populated on sale closure.

### Карта
Discount cards and certificates. Combination of fields determines card type:

| Field | Plastic/eCard | Personal | UDS | Certificate |
|---|---|---|---|---|
| Эмиссия | + | — | + | + |
| Номер | + | — | — | + |
| Лицо | + | + | + | — |
| ДатаКнц | — | — | — | + |

`Атрибуты` JSON:
- `Cert` — state (0=preparing, 1=active, 2=redeemed), balance
- `Bonus` — BonusId, AvailableBonusBalance, ExpirationDatetime, BonusList

### ВидКарты
Card emissions (types). Hierarchy used for non-adjacent number ranges.

`Атрибуты` for certificates: nominal value, expiration period, usage type (once/partial).

**`ВидКарты.Тип=2`** — тех. вид карты для внешних участников лояльности (PremiumBonus, iikoCard). Не имеет карточки и возможности редактирования. Служит эмиссией для карт участников внешней ЛС.

---

## External Loyalty Integration Tables

### КодыЛиц (External System Links)

Связь физлица СБИС с идентификатором во внешней информационной системе. Используется для синхронизации с UDS, PB, iikoCard.

| Field | Description |
|-------|-------------|
| ФизЛицо (uid) | Идентификатор физлица в СБИС |
| ExternalId | Идентификатор объекта во внешней ИС |
| SystemType | Тип внешней системы (UDS/PB/iikoCard) |

Многие сущности СБИС — «лица» (контрагенты, физлица, номенклатуры). При обмене с внешней ИС назначается однозначный идентификатор для синхронизации. По коду объект определяется всегда; обратное — как получится.

**iiko specific**: В `КодЛица` хранится `iikoCard customer id`. При первой продаже с картой iikoCard покупатель создаётся в СБИС с привязкой к внешнему id.

See also: [[ExternalLoyalty-Integrations]], [[ExternalLoyalty-iiko-Integration]]

`Атрибуты` franchise fields (added for franchise support — see [[Franchise-Loyalty-Architecture]]):
- `FranchiseRole` (int): `1`=Owner, `2`=Participant
- `OwnedFranchiseUUIDList` (List[str]): franchise IDs where this account is owner
- `FranchiseUUIDList` (List[str]): franchise IDs for which this card type is active

### Промокод model
Promo codes reuse the same tables as discount cards:
- **Эмиссия промокода** = ВидКарты with range + linked discounts + issuance period
- **Экземпляр промокода** = Карта with number + optional owner + application limit

Types: general (1 instance), individual (N instances with owner), purchase reward, partner (general with partner).

---

## Key Queries

| Query purpose | Method/function |
|---|---|
| Discount stats (count/sum) | `get_retail_stats_by_nom`, `get_retail_stats` |
| Card sales stats | `DiscountCard.GetRetailStatsByPeriod2` |
| Bonus balance history | `get_bonus_balance` |
| Report totals (single table) | `UseOfPromotion.GetData` |
| Promotion totals | `Promotion.GetSaleTotals` |
| Card search by last digits | Table scan on `Карта.Номер` suffix |
| Price entity full data | `get_price_entity_data` |
| Applied discounts list | `get_applied_discount_list` |
| Available discounts | `get_available_list` |
| Sync data for offline | — (version-aware, strips unsupported fields) |

---

## База данных Сервиса ДК (discount-cards service)

Отдельная БД сервиса СДК хранит карты из Saby Get и карты онлайна.

### Схема сущностей СДК

| Сущность | Описание |
|----------|----------|
| **CardType (Тип карты)** | Базовая сущность: настройки дизайна, уведомлений и т.п. для ДК |
| **Emission (Эмиссия)** | Физический или электронный выпуск для конкретного типа карты |
| **Template (Шаблон)** | Настройки внешнего вида для типа карты |
| **Card (Карта)** | Экземпляр дисконтной карты |
| **PromoCode Type (Тип промокода)** | Тип промокода: дизайн, условия, описание выгоды |
| **PromoCode (Промокод)** | Буквенно-цифровой код для особых условий. Технически — та же дисконтная карта |

### Типовые выборки

| Цель | Метод |
|------|-------|
| Карты персоны в SabyGet | `Card.GetListV2` — по Keys / ClientID+SalePoint+шаблон / поисковой строке |
| Все карты в диагностике | `DiscountCard.GetList/4` — с курсорной навигацией |
| Шаблоны в SabyGet | `Company.GetList` / `CardTemplate.GetList` — только активные |
| Шаблоны в диагностике | `CardTemplate.GetList` (admin) — все, включая неактивные |
| Адресаты рассылки | Поиск активных образов для рассылки |

Подробнее об индексах СДК сервиса: [[DiscountCard-Diagnostic-Service]]

### Franchise additions to СДК tables

**CardType.Info** (JSONB) — new field:
- `FranchiseUUIDList` (List[UUID]): franchise IDs for which this card type record is active

**Operation** — new fields:
| Field | Type | Description |
|-------|------|-------------|
| `CardUUID` | UUID | UUID of the discount card involved in the operation |
| `PriceEntityUUID` | UUID | UUID of the price type (bonus program, ВидЦены) in online — links СДК operations back to loyalty programs |

See [[Franchise-Loyalty-Architecture]] for the full cross-system design.

---

## Notes

> [!key-insight] Single table statistics
> All loyalty events (discounts, bonuses, cards, certificates, promo codes) write to **ВидЦеныДокумент**. This single-table design unifies reporting across all loyalty types. Bonus balance is calculated dynamically from this table.

- `ВидЦеныЛица` stores both individual contractors and groups (папки)
- Role ID as text is a legacy artifact — to be replaced
- Gift promotions in Warehouse (СУ) vs Retail (Розница) use separate implementations; Warehouse will be migrated to match Retail
- UDS bonuses and SBIS bonuses are mutually exclusive per client
