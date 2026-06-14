---
type: concept
title: "DCCommon — Helpers Overview"
updated: 2026-04-13
tags:
  - price-formation
  - helpers
  - python
status: evergreen
related:
  - "[[PriceFormation-Backend-Architecture]]"
  - "[[PriceFormation-Common-Helpers]]"
  - "[[Wasaby-Python-Patterns]]"
  - "[[Wasaby-RecordSet-Performance]]"
  - "[[Bonus-Programs-Architecture]]"
  - "[[DiscountCard-Subsystem-Overview]]"
  - "[[PassUpdater-Service]]"
created: 2026-04-13
---

# DCCommon — Helpers Overview

Module `DCCommon` (`www/service/Модули/DCCommon/dccommon/`) — shared utilities for discount cards: barcodes, encryption, stand management, questionnaires, branding, and bonus balance calculation.

See also: [[PriceFormation-Backend-Architecture]] for the module map, [[PriceFormation-Common-Helpers]] for Common helpers.

---

## Barcode & QR (`helpers/barcode.py`)

**BarcodeType** — types: EAN-8, EAN-13, UPC-E/A, Code128/39, QR, DataMatrix, ITF-14, GS1-128

**GenerateBarcodeType** — formats: SVG=0, PNG=1, PNG_FROM_SVG=2

Functions:
- `generate_barcode(data, barcode_type, need_short_link)` → `(short_link, barcode_bytes)` or `barcode_bytes`
- `get_qr_code(url, need_short_link=False)` — generate QR code

External services: VED (barcode generation), URL-shortener.

---

## Encryption (`helpers/encryption.py`)

- `get_encryption_key()` — legacy key (cached, `@functools.lru_cache`)
- `get_crypto_key()` — current key (cached)
- `get_encrypted_card_key(client_id, card_id)` → `"<client_id>_<card_id>"` in encrypted form
- Validation: Base64 length divisible by 4
- Dependencies: `pnt_toolbox.crypto`

Used by [[DiscountCard-Algorithms-Processes]] for confidential data encryption.

---

## Stand Detection (`helpers/stand.py`)

- `CURRENT_HOST` — site reference from Configuration
- `get_stand_prefix()` → `"dev"` from `"//dev-online.sbis.ru"` (regex parsing)

---

## Digital Wallet & Questionary (`helpers/questionary.py`)

Classes:
- `PassType` — APPLE_WALLET=`'aw'`, GPAY=`'gp'`
- `CardPreferredPass` — APPLE_WALLET=2, GPAY=1
- `PromocodePreferredPass` — APPLE_WALLET=1, GPAY=2

Functions:
- `get_download_app_link(client_id, card_type_sale_points)` — "smart" app download link
- `get_pass_qr(pass_uuid)` — QR for digital card/pass
- `get_pass_type_for_promocode(preferred_pass)` → `PromocodePreferredPass`
- `get_pass_type_for_creating_preview(preferred_pass)` → `PassType`
- Integration: Showcase service for published sale points

See [[PassUpdater-Service]] for the full pass update pipeline (Task/Request/MessageBox model).

---

## Card Theming (`core/brandbook.py`)

- `provide_dc_theme_data(theme)` — ensure frame data is present in theme (adds defaults)
- `JSON_DEFAULT_THEME_DATA` — default frame configuration:
  - Front side (`discountcard-design`): stamps, cashback, discount, bonuses
  - Back side (`discountcard-back-side-design`)
  - Colors, layout, barcode type, visibility flags

---

## Bonus Balance Calculation (`core/calculate_bonus_balance.py`)

**Availability(StrEnum)**:
- `AVAILABLE = 'A'`
- `DELAYED = 'D'`
- `EXPIRED = 'E'`

**BonusOperationsRecordSetType(sbis.RecordSet)**:

Fields:
| Field | Description |
|-------|-------------|
| BonusId | Operation ID |
| BonusUUID | Operation UUID |
| Datetime | Operation datetime |
| ExpirationDatetime | Expiry datetime |
| Bonus | Bonus amount |
| Availability | A/D/E status |

Metadata fields on RecordSet:
| Field | Description |
|-------|-------------|
| AvailableBonusBalance | Currently spendable balance |
| TotalBonusBalance | Total balance including delayed |
| BalanceDateTime | Balance as-of datetime |
| NextChangeDatetime | Next balance change event |

`calculate_bonus_balance(bonus_operations)`:
- Matches deductions against accruals
- Classifies bonuses: Available / Delayed / Expired
- Returns RecordSet with balance and metadata

> [!tip] Algorithm detail
> The matching algorithm pairs deductions with accruals in chronological order, consuming the oldest accruals first. Delayed bonuses (not yet active) and expired bonuses are classified separately from available ones. See [[Bonus-Programs-Architecture]] for the broader accrual and supplementary accrual flow.

---

## Related Pages

- [[PriceFormation-Backend-Architecture]] — module map showing where DCCommon sits
- [[PriceFormation-Common-Helpers]] — Common helpers (logging, datetime, record utilities)
- [[DiscountCard-Subsystem-Overview]] — full СДК architecture and service decomposition
- [[DiscountCard-Algorithms-Processes]] — confidential data encryption, inter-service diagrams
- [[PassUpdater-Service]] — AW vs GPay pass update pipeline
- [[Bonus-Programs-Architecture]] — bonus accrual flows and balance calculation context
- [[Wasaby-Python-Patterns]] — sbis.Error/Warning, CreateTransaction patterns
- [[Wasaby-RecordSet-Performance]] — RecordSet optimization (BonusOperationsRecordSetType uses sbis.RecordSet)
