---
type: concept
title: "Prompts — Cashier Hints Subsystem"
updated: 2026-04-10
tags:
  - loyalty
  - price-formation
  - sbis
  - prompts
status: current
related:
  - "[[Loyalty-Product-Overview]]"
  - "[[Loyalty-Database-Schema]]"
  - "[[Loyalty-Sale-Application]]"
  - "[[Акции-Subsystem-Overview]]"
  - "[[DiscountCard-Service-API]]"
  - "[[price-formation/_index]]"
created: 2026-04-10
---

# Prompts — Cashier Hints Subsystem (Подсказки)

Popup notifications shown to cashiers at POS, reminding them of available discounts, promotions, bonus programs, loyalty cards, upsell items, or promo codes relevant to the current sale.

---

## Business Value

### Direct value for the buyer
1. **Speed** — cashier instantly sees actionable hints (e.g., "Promotion: 2 for the price of 3"), no delays or consultations.
2. **Accuracy** — system auto-applies eligible discounts; customer pays exactly the correct amount.
3. **Personalization** — hints can be customer-specific ("birthday today — offer a gift certificate").

### Indirect value
- Reduces queues (higher POS throughput)
- Surfaces promotions the customer didn't know about
- New cashiers perform as confidently as experienced ones

---

## Technical Architecture

**Подсказка** = a `ВидЦены` entry (Тип=18) following the same data model as discounts/promotions. The hint calculation mechanism is identical to discount calculation.

### Display Controller
A lazy-initialized `Контроллер Подсказок` manages hint display per active document:
- Initialized on first receipt of hints from `CalculateDiscount`, receiving document ID, price ID, and client.
- Calls `dataHandler(prompts)` with the returned RecordSet.
- Tracks **displayed hint IDs in session storage** to avoid repeating hints for the same document. Default TTL: **1 hour** (configurable via cloud settings, not editable from UI).
- Display delay configurable via global settings.

### Retail flow
```
User edits sale
  → RetailSaleDoc.CalculateDiscount(WithPrompts=true)
    → Returns Prompts: RecordSet
      → Frontend lazy-inits Контроллер Подсказок
        → Controller shows eligible prompts (filtered by session cache + delay)
```

### Warehouse (складские документы) flow
Identical to retail but uses `WarehouseSaleDoc.CalculateDiscount`. Controller is created per document (not per session).

### Sync
Hints sync to desktop apps (Retail + Presto) via the **existing loyalty sync mechanism**.

---

## Information Model

### Подсказка (Prompt)
Applied object. Shares the `ВидЦены` data model.

| System name | Localized | Type | Description |
|---|---|---|---|
| `Message` | Сообщение | String | Text shown at POS |
| `IsActive` | Используется | Boolean | Is the hint currently active |
| `PromptConditions` | Условия | УсловияПодсказки | Display conditions |
| `Promotion` | Акция | Акция | Linked promotion (on approval) |
| `Description` | Описание | String | Auto-generated description |
| `PromptProfit` | Выгода | ВыгодаПодсказки | Benefit offered |

### УсловияПодсказки (PromptConditions)
Service type.

| System name | Localized | Type | Description |
|---|---|---|---|
| `Gender` | Пол | Enum | Show only for male/female |
| `ExcludedNomenclature` | НоменклатурыИсключенные | Nomenclature[] | Do NOT show when these items are in cart |
| `Quantity` | Количество | Number | Show at specific item quantity |
| `SalesSum` | НаСумму | Number | Show at specific sale total |
| `SaleType` | ТипПродажи | Enum | 0=wholesale, 1=retail |

### ВыгодаПодсказки (PromptProfit)
Service type. Determines interaction behavior.

| System name | Localized | Type | Description |
|---|---|---|---|
| `Nomenclatures` | Номенклатуры | Nomenclature[] | Items to offer (click → add to sale) |
| `DiscountCard` | ДисконтнаяКарта | ВыпускКарт | Card to issue (click → open card issuance dialog) |

**Text-only hints** have no benefit object and no user interaction.

---

## Interaction by Benefit Type

| Benefit type | Interaction |
|---|---|
| **Nomenclatures** | List of items shown; click item → added to sale via existing mechanism |
| **DiscountCard** | Card name + "Выдать" button; click → opens card issuance dialog for current client |
| **Text only** | Display only, no action |

---

## API

### RetailSaleDoc.CalculateDiscount
Used for retail sale loyalty calculation. Returns `Prompts: RecordSet` with hints matching current conditions when called with `WithPrompts` flag.

### WarehouseSaleDoc.CalculateDiscount
Used for warehouse/supply document loyalty calculation. Same `Prompts: RecordSet` output.

Objects and methods documented at:
- `Prompt` object in `PriceFormation.Online` module
- `Prompt` object in `PriceFormation.Common` module

---

## Database

### ВидЦены (Тип=18 — Подсказка)

| Field | Type | Description |
|---|---|---|
| `@ВидЦены` | PK | Hint identifier |
| `Используется` | Boolean | Active flag |
| `Название` | Text | Name |
| `Тип` | Enum | **18** = Подсказка |
| `Сообщение` | Text | Message shown at POS |
| `Атрибуты` | JSONB | Key `Prompt`: `{DiscountCardId}` — linked card emission. Key `Gender`: String — gender condition |

### ВидЦеныРасширение

| Field | Type | Description |
|---|---|---|
| `@ВидЦены` | PK | Hint identifier |
| `Акция` | N→1(ВидЦены) | Reference to linked promotion |

Condition storage (except Gender) follows the **promotions mechanism** — same schema as [[Акции-Subsystem-Overview]].

---

## Access Rights

| Application | Access area | Required level |
|---|---|---|
| **Presto** | «Presto» | «Просмотр и изменение» or «Полный с настройками» |
| **Retail** | «Магазин» | «Просмотр и изменение» or «Полный с настройками» |

---

## Key Insights

> [!key-insight] Same model as promotions
> Подсказки reuse the `ВидЦены` data model entirely — conditions, storage, sync, and calculation follow the same code path as discounts. Тип=18 is the only differentiator.

> [!key-insight] Session deduplication
> The hint controller stores displayed IDs in session storage (default 1h TTL) to prevent the same hint showing twice for the same document in a session. This is controlled by cloud settings, not UI.
