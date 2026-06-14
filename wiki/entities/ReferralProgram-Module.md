---
type: entity
title: "ReferralProgram Module (price-formation)"
updated: 2026-04-10
tags:
  - entity
  - price-formation
  - referral
  - python
  - sbis
status: current
related:
  - "[[price-formation/_index]]"
  - "[[Multitenancy-Architecture]]"
  - "[[Python-Code-Standards-SBIS]]"
created: 2026-04-10
---

# ReferralProgram Module (price-formation)

Partner referral system in `PriceFormation.Online`. Manages partner links, lead tracking, rewards, and statistics.

> [!key-insight] Not to confuse
> This module (`referralprogram/`) is completely separate from `loyaltyprograms/referralbonus`. Different module, different purpose.

**Path:** `www/service/Модули/PriceFormation.Online/priceformationonline/referralprogram/`

---

## Core Classes

### `ReferralProgram` (core.py)

Program model. Key fields:

| Field | Type | Description |
|-------|------|-------------|
| `id_` | int | ID |
| `name` | str | Name |
| `product` | str | Site product ID |
| `theme_id` | int | CRM theme ID |
| `price_per_lead` | Money | Reward per lead |
| `price_per_lead_type` | int | 0=fixed (RUB), 1=percent |
| `price_per_visitor` | Money | Reward per visitor |
| `uuid` | UUID | Unique identifier |
| `ad_object` | int | Marketing source ID (AdObject) |
| `feedback_widget_id` | str | Feedback widget ID |

Key methods: `from_db_record()`, `to_db_record()`, `get_api_record()`, `get_partners()`

### `ReferralProgramRepository` (core.py)

```python
ReferralProgramRepository.get_linked_emission_id(referral_program_id: int) -> int
ReferralProgramRepository.bulk_has_referral_codes(referral_program_ids: list[int]) -> sbis.RecordSet
ReferralProgramRepository.create(referral_program: ReferralProgram, is_draft: bool = True)
ReferralProgramRepository.update(referral_program: ReferralProgram)
ReferralProgramRepository.read(referral_program_id: int) -> ReferralProgram
ReferralProgramRepository.delete(referral_program_id: int | list[int]) -> bool
```

### `ReferralBusinessGroup` (core.py)

Inherits `BusinessGroup`. Manages participant composition.
```
TYPE = UUID('5ccfa95d-d44b-41ce-8888-c1cbd7362264')
FOLDER_ATTRIBUTE_NAME = 'ReferralProgram'
```

### User Roles

| Constant | Level | Permissions |
|----------|-------|-------------|
| `OWNER_ADMIN` | 3 | Full admin |
| `OWNER_MODERATOR` | 2 | Create/edit programs and partners |
| `OWNER_MEMBER` | 1 | Basic operations |
| `PARTNER_ADMIN` | 3 | Partner admin |
| `PARTNER_MANAGER` | 1 | Partner basic |

Access check: `check_business_group_role(business_group_id, min_role)`

---

## Public API

```python
# CRUD
sbis.ReferralProgram.Create(filters)
sbis.ReferralProgram.Read(id, method_name, filters)
sbis.ReferralProgram.Update(record)
sbis.ReferralProgram.Delete(id)

# Lists
sbis.ReferralProgram.GetList(additional_fields, filters, sorting, navigation)
sbis.ReferralProgram.GetJoinableList(filters, navigation)
sbis.ReferralProgram.GetPartnerList(filters, navigation)

# Partner management
sbis.ReferralProgram.Join(program_id, partner_client_id, partner_id)
sbis.ReferralProgram.JoinByPartner(group_id, program_id)
sbis.ReferralProgram.UpdatePartner(program_id, record)

# Referral links
sbis.ReferralProgram.GetReferralLink(program_id, partner_client_id, partner_id)
sbis.ReferralProgram.GetReferralLinkByPartner(group_id, program_id)
sbis.ReferralProgram.GetReferralLinkForPartner(group_id, program_id)

# Leads
sbis.ReferralProgram.CreateLead(program_id, feedback_form, partner_client_id, partner_id)
sbis.ReferralProgram.GetLeadList(additional_fields, filters, sorting, navigation)
sbis.ReferralProgram.GetLeadPeriodList(filters, navigation)

# Stats
sbis.ReferralProgram.GetStats(filters)
sbis.ReferralProgram.GetStatsByPartner(filters)

# Invoices
sbis.ReferralProgram.CreateInvoice(filters)
sbis.ReferralProgram.CreateInvoiceForPartner(group_id, data)
```

---

## DB Schema

| Table | Role |
|-------|------|
| `ВидЦены` | Referral programs |
| `ВидЦеныВидКарты` | Program-emission link |
| `Карта` | Partner referral codes |
| `ВидКарты` | Card emissions |
| `ВидЦеныЛица` | Partner whitelist |
| `ВидЦеныДокумент` | Reward accruals (also serves as lead "stub" in SabyBank) |

Program attributes stored as JSON in `Атрибуты` field of `ВидЦены`. Partner code attributes in `Атрибуты` of `Карта`.

---

## Key Scenarios

### Create Program
1. `Create()` creates `ВидЦены`
2. Creates business group (`ReferralBusinessGroup`)
3. Creates card emission (`ВидКарты`) for referral codes
4. Creates marketing source (`AdObject`) for tracking

### Partner Join
1. Verify partner in business group
2. Generate UUID referral code
3. Create `Карта` with `PartnerId`, `PartnerName`, `AdObject`, `AdObjectUUID`
4. Create separate marketing source for partner code

### Get Referral Link
1. Find partner referral code (or auto-join)
2. Get `AdObject` from `Карта` attributes
3. Build link: `{site_url}?utm_rfcid={ClientID}_{AdObject}`

### Lead Lifecycle
1. `CreateLead()` creates CRM Lead with partner source
2. On state change: `handle_lead_state_changed()`
3. If successful:
   - CURRENCY: save to `ВидЦеныДокумент`
   - PERCENT: delegate to bonus system
4. History logged via `ReferralLeadHistory`

### Stats (`GetStats`)
Aggregates from 3 sources:
1. `ВидЦеныДокумент` - reward amounts
2. `get_sales_sources_stats` - lead count (marketing system)
3. `get_source_detail` - visitor count (tracking system)

---

## External Dependencies

| Module | Purpose |
|--------|---------|
| `priceformationcommon.discountcard.emission` | Card emission management |
| `priceformationonline.helpers.marketing` | AdObject create/get + stats |
| `priceformationonline.helpers.business_group` | Business group management |
| `priceformationonline.core.statistics` | Cloud statistics |
| `multitenancy` | Cross-account calls (partner calls owner's account) |
| `user_service_cloud` | User/account data |
| `sbis` | Platform API |

---

## SabyBank Extension (ТЗ: Рефералка в Заявках в банк на РКО)

Specialized referral program subtype "Заявки на РКО" for bank loan applications via API.

**Key differences from standard referral program:**
- No CRM theme, feedback widget, product link, or reward amount fields (rewards set manually)
- Banks are partners (not regular users)
- No manual lead creation - leads come via API
- Partner view: stub page (bank managers use their own systems)

**SabyBank API methods (called strictly in Tensor account):**
- `GetBankParticipants()` - returns bank accounts participating in referral programs: `{"RefProgID": {"Type": "...", "Participants": [{bank_name, bank_account}]}}`
- `CreateLeadStub(program_id, bank_account, app_id, metadata)` - creates lead stub (finds partner by bank account via social network, finds `Карта`, creates `ВидЦеныДокумент`)
- `UpdateLeadStub(app_id, metadata)` - updates stub status when bank API changes application status

All statistics built from stubs. Manual reward assignment via editing `Бонус` field of `ВидЦеныДокумент`.
