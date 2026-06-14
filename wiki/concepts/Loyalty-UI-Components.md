---
type: concept
title: "Loyalty UI Components"
updated: 2026-04-10
tags:
  - loyalty
  - ui
  - components
  - frontend
  - price-formation
status: current
related:
  - "[[Loyalty-Product-Overview]]"
  - "[[Loyalty-In-Products]]"
  - "[[price-formation/_index]]"
created: 2026-04-10
---

# Loyalty UI Components

Frontend component reference for the SBIS loyalty system. Component paths follow the `LoyaltyOnline/`, `LoyaltyRetail/`, `LoyaltyCore/`, `Loyalty/` namespace pattern.

---

## Widgets

### Standard Widgets (donut chart + table)
All built on `LoyaltyWidgets.Core.donutchart:Content` base layout:

- `LoyaltyWidgets/Bonus` — bonus program widget
- `LoyaltyWidgets/Promotion` — promotion widget
- `LoyaltyWidgets/PromoCode` — promo code widget

### Non-standard Widgets
Built without shared base components:

- **ActiveClients** — active clients widget
- **Referral system** — referral program widget

---

## Promotions & Discounts

### Universal Components
- `LoyaltyOnline/Promotion/FormOpener` — promotion card form opener
- `LoyaltyOnline/Promotion/selector:LookupSelector` — autocomplete field for promotion selection
- `LoyaltyOnline/Promotion/selector:Stack` — selection dialog (supports creating promotions during selection)
- `LoyaltyCore/Promotion/publication:Carousel` — promotion banner carousel for SabyGet
- `LoyaltyCore/Promotion/publication:View` — single promotion banner
- `LoyaltyOnline/Core/Promo/entity:View` — link button for loyalty entities (promotions, promo codes, hints, surcharges) linked to a product list

### Promo Code Components
- `LoyaltyOnline/PromoCode/FormOpener` — promo code settings card
- `LoyaltyOnline/PromoCode/selector:Lookup` — promo code selection field
- `LoyaltyOnline/PromoCode/selector:Stack` — promo code selection dialog

---

## Sale Components

| Component | Description |
|---|---|
| `LoyaltyRetail/Sale/Bonus/buttons` | Bonus action buttons on sale |
| `LoyaltyRetail/Sale/Bonus/client` | Bonus display in client window on sale |
| `Loyalty/Sale/Promotion/button:View` | Discount button on sale |
| `Loyalty/Sale/Common/info` | Combined discounts + bonuses + cards panel on sale |
| `Loyalty/Sale/Bonus/dialog` | Bonus dialog on sale |
| `Loyalty/Sale/Promotion/editor` | Discount editor panel on sale |
| `LoyaltyRetail/Sale/DiscountCard/edit` | Discount card display/edit on sale (new sale only) |

---

## Bonus Management

| Component | Description |
|---|---|
| `LoyaltyOnline/DiscountCard/registry:View` | Client registry for bonus programs |
| `LoyaltyOnline/Bonus/registry:Browser` | Bonus accrual registry |
| `LoyaltyOnline/Bonus/registry:EmptyTemplate` | Empty state for bonus registry |
| `LoyaltyOnline/Bonus/settings:View` | Bonus program global settings |
| `LoyaltyOnline/Bonus/settings:showHistory` | Helper to open settings history panel |
| `LoyaltyOnline/Core/bonus:ParamsEditor` | Bonus parameters editor |
| `LoyaltyOnline/Core/bonus:ActivationType` | Activation timing (immediate / deferred) |
| `LoyaltyOnline/Core/client:OpenLink` | Client name link button (opens client card) |
| `LoyaltyOnline/Bonus/Accrual/Helper:openManualAccrual` | Manual accrual dialog opener for client segments |
| Bonus Calculator | Calculate bonus program outcomes |

---

## Condition Components

All in `LoyaltyOnline/Core/condition:` namespace:

| Component | Description |
|---|---|
| `Editor` | Condition list editor |
| `AccrualPeriodItem` | Accrual period for bonus conditions |
| `ClientItem` | Client condition |
| `RegionItem` | Region condition |
| `LogicalNomenclaturesItem` | Nomenclature wrapper in conditions |
| `PayTypeItem` | Payment type dropdown |
| `PeriodItem` | Date/time period |
| `PromoCode` | Promo code condition |
| `CONDITIONS` | Enum of available condition types |
| `getSelectedConditions` | Returns selected condition IDs |
| `updateHideTitles` | Hide redundant condition labels |
| `validateTimeInterval` | Time interval validator |
| `validateDateRange` | Date range validator (no-op, for API compatibility) |

Special condition components (`LoyaltyOnline/Core/Promo/condition:`):
- `ApplyWithPromotions` — discount fires simultaneously with selected promotions
- `Summable` — discount fires alongside the best discounts in sale
- `Dropdown` — priority condition (overrides all other discounts)

---

## Common Card Components

- `LoyaltyOnline/Core/FolderDialog` — folder/section editing dialog

---

## Chart Components (`LoyaltyOnline/Core/groupTemplate:`)

| Component | Description |
|---|---|
| `LinearChart` | Line chart for loyalty registries |
| `ColumnChart` | Bar chart for loyalty registries |
| `LinearTooltip` | Tooltip for line chart |
| `tooltipFormatter` | Formats and splits tooltip into triads |

---

## Import Components (`LoyaltyOnline/Core/import:`)

| Component | Description |
|---|---|
| `FormatButton` | Button opening format requirements dialog |
| `FormatDialog` | Displays import format requirements |
| `Results` | Import results panel |

Used for: price imports, discount card imports, etc.
