---
type: source
title: "Алгоритмы и процессы (Лояльность — Франшиза)"
source: "https://online.sbis.ru/knowledge-bases/001495c1-d301-490a-9531-0b6fe60059d7?folder=2f3526bc-8224-4fc8-8b70-41164a62deba&published=null&mode=table"
raw_file: "raw/Алгоритмы и процессы.md"
ingested: 2026-04-10
tags:
  - loyalty
  - franchise
  - sbis
  - algorithms
status: current
related:
  - "[[Loyalty-Franchise-Mechanics]]"
  - "[[Loyalty-Database-Schema]]"
  - "[[Loyalty-Product-Overview]]"
  - "[[DiscountCard-Algorithms-Processes]]"
created: 2026-04-10
updated: 2026-04-10
---

# Source: Алгоритмы и процессы (Лояльность — Франшиза)

**Raw file:** `raw/Алгоритмы и процессы.md`
**Ingested:** 2026-04-10
**Domain:** [[price-formation/_index]]

## Summary

SBIS knowledge-base article covering the base mechanisms of the Loyalty BL (Business Logic layer) when working with the Franchise system. Documents:

1. Five events БЛ Лояльности subscribes to for franchise lifecycle operations.
2. How franchise folder records are created in ВидЦены / ВидКарты.
3. The `FranchiseRole` attribute (1 = owner, 2 = participant/franchisee) as a quick-look marker.
4. The `AgentGroupFolder` attribute marking franchise folder records.
5. GroupId tracking in `ВидЦеныРасширение.GroupId` for all entities belonging to a social-network group.
6. Synchronization of promotional data from Owner to Participants.
7. Bonus balance retrieval process.
8. Bonus accrual and deduction flows.

The source references sequence diagrams for connection/disconnection of participants, synchronization, and bonus operations (images not available in raw capture).

## Pages Created

- [[Loyalty-Franchise-Mechanics]] — new concept page

## Pages Updated

- [[DiscountCard-Algorithms-Processes]] — added cross-reference note
- [[Loyalty-Database-Schema]] — added FranchiseRole / AgentGroupFolder attribute notes
