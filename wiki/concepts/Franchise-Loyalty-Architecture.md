---
type: concept
title: "Franchise Loyalty Architecture"
updated: 2026-04-10
tags:
  - loyalty
  - franchise
  - database
  - price-formation
  - sbis
status: current
related:
  - "[[Loyalty-Database-Schema]]"
  - "[[DiscountCard-Subsystem-Overview]]"
  - "[[DiscountCard-Service-API]]"
  - "[[Loyalty-Product-Overview]]"
  - "[[Акции-Subsystem-Overview]]"
  - "[[domains/price-formation/_index]]"
  - "[[Loyalty-Franchise-Mechanics]]"
  - "[[Franchise-SabyNet-Subsystem]]"
created: 2026-04-10
---

# Franchise Loyalty Architecture

Support for franchise (франшиза) and social network groups (соцсеть) within the SBIS/Saby loyalty system. Allows a single loyalty program (promotions, bonus programs, discount card types) to be shared across multiple accounts within a franchise network, with explicit Owner/Participant role distinction.

Source: [[loyalty-db-franchise-2026-04-10]] | Parallel project: https://project.sbis.ru/uuid/9cc6e3d9-f0da-4cb4-9bb2-6cff8f5b3d7f/page/project-main

---

## Core Concept

A **franchise group (группа соцсети)** is a set of accounts linked under a franchise umbrella. Within this group:
- One account is the **Owner (Владелец, FranchiseRole=1)** — typically the franchisor who creates and manages the loyalty program
- Other accounts are **Participants (Участники, FranchiseRole=2)** — franchisees who apply the shared program

Franchise identity is tracked via UUID-based lists on key loyalty entities.

---

## Database Schema Changes

### Online Loyalty Tables

#### ВидЦеныЛица
| Field | Type | Description |
|-------|------|-------------|
| `ТипЛица` | Enum | Type of link between ВидЦены and a person: employee (сотрудник), client (клиент), or partner (партнер) |

#### ВидЦеныРасширение
| Field | Type | Description |
|-------|------|-------------|
| `GroupId` | UUID | ID of the social network group (franchise) the promotion belongs to |

#### ВидЦены — Атрибуты JSON additions
```json
{
  "FranchiseRole": 1,       // 1 = Owner (Владелец), 2 = Participant (Участник)
  "AgentGroupFolder": true  // flag: this is a group section in the promotion hierarchy
}
```

#### ВидКарты — Атрибуты JSON additions
```json
{
  "FranchiseRole": 1,                       // 1 = Owner, 2 = Participant
  "OwnedFranchiseUUIDList": ["uuid1", ...], // franchise IDs where this account is owner
  "FranchiseUUIDList": ["uuid1", ...]       // franchise IDs for which this record is active
}
```

### СДК (Discount Card Service) Tables

#### CardType — Info JSON additions
```json
{
  "FranchiseUUIDList": ["uuid1", ...]  // franchise UUIDs for which this card type is active
}
```

#### Operation — new fields
| Field | Type | Description |
|-------|------|-------------|
| `CardUUID` | UUID | UUID of the discount card |
| `PriceEntityUUID` | UUID | UUID of the price type (bonus program) in online |

---

## Key Design Patterns

- **FranchiseRole on ВидЦены and ВидКарты**: determines whether the current account owns or participates in the shared program
- **FranchiseUUIDList**: a record is "active" for all franchises in its list — enables cross-account activation without record duplication
- **OwnedFranchiseUUIDList** (on ВидКарты): used to scope admin/management rights to card types owned by the current account
- **GroupId on ВидЦеныРасширение**: links a promotion to a specific franchise group for filtering/display
- **AgentGroupFolder** (on ВидЦены.Атрибуты): marks a virtual folder node in the promotion hierarchy that groups all franchise-shared promotions

---

## Notes

> [!key-insight] Cross-account loyalty via UUID lists
> The franchise integration is implemented as additive JSON fields on existing entities rather than new relational tables. FranchiseUUIDList on ВидКарты/CardType controls visibility/activation across accounts without duplicating records.

- The `ТипЛица` field on `ВидЦеныЛица` adds semantic context (employee vs client vs partner) to existing person-to-price-type links — this broadens usage beyond pure loyalty customer targeting.
- `Operation.PriceEntityUUID` links СДК operations back to online bonus programs, closing the cross-service traceability gap between card usage events and specific loyalty programs.
- For the event-driven BL lifecycle (which events create/delete franchise folders): see [[Loyalty-Franchise-Mechanics]].
