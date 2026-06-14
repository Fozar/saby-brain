---
type: source
title: "База данных — Franchise Loyalty DB Changes"
source: "raw/База данных.md"
origin_url: "https://online.sbis.ru/knowledge-bases/001495c1-d301-490a-9531-0b6fe60059d7?folder=2f3526bc-8224-4fc8-8b70-41164a62deba&published=null&mode=table"
created: 2026-04-10
ingested: 2026-04-10
tags:
  - loyalty
  - database
  - franchise
  - sbis
  - price-formation
related:
  - "[[Loyalty-Database-Schema]]"
  - "[[DiscountCard-Subsystem-Overview]]"
  - "[[Franchise-Loyalty-Architecture]]"
  - "[[price-formation/_index]]"
updated: 2026-04-10
status: archived
---

# Source: База данных — Franchise Loyalty DB Changes

**Source file:** `raw/База данных.md`
**Origin:** SBIS Knowledge Base (29 Jan)
**Domain:** [[domains/price-formation/_index|Price Formation]]

---

## Summary

Documents schema changes made to the Loyalty system online tables to support **franchise (франшиза / соцсеть)** scenarios. Changes span both the main online loyalty tables and the separate Discount Card Service (СДК) database.

This is linked to a parallel franchise project: https://project.sbis.ru/uuid/9cc6e3d9-f0da-4cb4-9bb2-6cff8f5b3d7f/page/project-main

---

## Changes Documented

### Online Loyalty Tables

**ВидЦеныЛица** — new field:
- `ТипЛица` (Перечисляемое) — type of link between ВидЦены and a person: employee, client, or partner

**ВидЦеныРасширение** — new field:
- `GroupId` (UUID) — identifier of the social network group (franchise) to which the promotion belongs

**ВидЦены** — new JSON attribute:
- `Атрибуты.FranchiseRole` (int): `1` = Owner (Владелец), `2` = Participant (Участник)
- `Атрибуты.AgentGroupFolder` (bool): flag for social network group section in the promotion hierarchy

**ВидКарты** — new JSON attributes:
- `Атрибуты.FranchiseRole` (int): `1` = Owner, `2` = Participant
- `Атрибуты.OwnedFranchiseUUIDList` (List[str]): franchise IDs where the current account is owner
- `Атрибуты.FranchiseUUIDList` (List[str]): franchise IDs for which the record is active

### СДК (Discount Card Service) Tables

**CardType** — new JSON field:
- `Info.FranchiseUUIDList` (List[UUID]): franchise IDs for which the record is active

**Operation** — new fields:
- `CardUUID` (UUID): UUID of the discount card
- `PriceEntityUUID` (UUID): UUID of the price type (bonus program) in online

---

## Pages Created / Updated

- Created: [[Franchise-Loyalty-Architecture]]
- Updated: [[Loyalty-Database-Schema]]
