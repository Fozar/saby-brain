---
type: source
title: "API Франшизы (Franchise Contract API)"
source_file: "raw/API Франшизы.md"
source_url: "https://online.sbis.ru/knowledge-bases/001495c1-d301-490a-9531-0b6fe60059d7?folder=2f3526bc-8224-4fc8-8b70-41164a62deba"
created: 2026-04-10
ingested: 2026-04-10
tags:
  - source
  - franchise
  - api
  - sbis
  - loyalty
domain: price-formation
pages_created: 1
pages_updated: 2
updated: 2026-04-10
status: archived
---

# Source: API Франшизы

**File:** `raw/API Франшизы.md`
**Date captured:** 2026-04-10 (Sa 2 Nov 2025 internal date)
**Origin:** SBIS Knowledge Base (online.sbis.ru)

---

## Summary

Internal SBIS documentation describing the external API surface of the Franchise module (`FranchiseContract.*`). The API manages operators on agency/franchise contracts — adding, removing, querying, and access-controlling users in a client's personal cabinet (ЛК). It also exposes sales-point lists and access data for portals.

Completeness rating stated in source: **100%**.

---

## Pages Created / Updated

- Created: [[Franchise-Contract-API]] — full API reference for the FranchiseContract.* namespace
- Updated: [[domains/price-formation/_index]] — added franchise sub-section and source link
- Updated: [[concepts/_index]] — added franchise API entry under Price Formation

---

## Key Facts Extracted

- 12 external API methods under `FranchiseContract.*`
- Methods split into: lifecycle handlers (OnAccept / OnRestore / OnTerminate) and operator management (Add/Del/Has/List/Data/SetAccess) plus PointSalesList and AccessData
- Operator management operates on a "service contract" (договор обслуживания) identified by document ID
- `SetOperatorAccess` specifically blocks an operator in the client's ЛК (personal cabinet)
- `AccessData` takes a portal ID (not a document ID), unlike other methods
