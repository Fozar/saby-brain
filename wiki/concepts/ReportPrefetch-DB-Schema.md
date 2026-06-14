---
type: concept
title: "ReportPrefetch DB Schema"
domain: wasaby-infrastructure
status: current
created: 2026-04-13
updated: 2026-04-13
tags:
  - report-prefetch-service
  - database
  - schema
  - wasaby
  - sbis
related:
  - "[[Report-Prefetch-Service]]"
  - "[[Wasaby-BL-List-Methods]]"
  - "[[Wasaby-DB-Access-Patterns]]"
  - "[[Parameters-Service]]"
sources:
  - "[[report-prefetch-db-schema-2026-04-13]]"
---

# ReportPrefetch DB Schema

Database schema for `report-prefetch-service` — the Wasaby platform mechanism that pre-caches large report pages to reduce DB/BL load and speed up paginated report access.

See also: [[Report-Prefetch-Service]] for the overall service description, API, and usage patterns.

---

## Two Schema Versions

### Iterative Version (current)

Designed for large reports (>10 000 records). Supports iterative data loading. Uses a separate `ReportData` table alongside `ReportPage`.

### Old Version (legacy)

Simpler schema for non-iterative reports. Still present for backward compatibility.

---

## Tables

Full table documentation: https://wi.sbis.ru/page/autodoc-db/kaizen/cc91c5ab-d339-4b64-a1bd-2f39bc026e7e

| Table | Purpose |
|---|---|
| **SessionId** | Microsession registry. Each report is bound to a session that defines its TTL and validity. Expired sessions make their reports invisible and eligible for deletion. |
| **StoredReport** | Metadata of all built reports (not the report data itself). Fields: ArgsHash (filter hash), SessionId, Method. |
| **ReportPage** | Page-level storage of report data. Used in the iterative version. |
| **ReportData** | Alternative page storage (used alongside ReportPage in iterative version). |
| **Method** | Method identifier registry. Each report stores its method ID for method-based deletion. Loaded at service start; rarely updated — no extra indexes. |
| **ShardsAmountHistory** | Shard count history. Also loaded at start, rarely updated — no extra indexes. |

### Key Design Decisions

- `StoredReport` stores **report metadata only** — not the actual data. Data lives in `ReportPage`/`ReportData` (paginated).
- Each report holds a reference to `Method` to enable deletion by method name.
- Each report is bound to a `SessionId` — when the session expires, all its reports become invisible and are cleaned up by the scheduler.
- Filter is stored as a **hash** (`ArgsHash`) — fields prefixed with `PrefetchIgnoredInHash` are excluded from hashing.

---

## Typical Queries (Типовые выборки)

### 1. Session information lookup

Used to validate a session when saving a report, requesting report data, or checking session expiry.

- Query: `SessionId` table by `Session` field.

### 2. Report lookup by session + filter hash + method

Used when requesting report data.

- Query: `StoredReport` by `ArgsHash`, `SessionId`, `Method`.

### 3. Page retrieval by report ID + page/cursor

Used when requesting paginated report data. Two navigation modes:

- **Page-based**: `ReportData`/`ReportPage` by `StoredReport` + `BranchId`/`PageNum`
- **Cursor-based**: `ReportData`/`ReportPage` by `StoredReport` + `CursorHash`

### 4. Method and ShardsAmountHistory

No additional indexes — both tables are read at service start and updated very rarely.

### 5. All pages of all reports for a session

Used when saving to `sabyreport` file format.

- Query: `StoredReport` by `SessionId` starting from a given `@StoredReport`.

---

## Indexes

| Index | Used by query |
|---|---|
| `SessionId(Session)` | 1 |
| `StoredReport(ArgsHash)` | 2 |
| `StoredReport(SessionId)` | 2 |
| `StoredReport(Method)` | 2 |
| `ReportData(StoredReport, CursorHash)` | 3 |
| `ReportData(StoredReport, BranchId)` | 3 |
| `ReportData(StoredReport, @ReportData)` | 5 |
| `ReportPage(StoredReport, CursorHash)` | 3 |
| `ReportPage(StoredReport, BranchId)` | 3 |
| `ReportPage(StoredReport, @ReportPage)` | 5 |

---

## Session Lifecycle

1. Session created (via `Prefetch.CreateSession` or implicitly on first `Prefetch.List` call).
2. Reports are stored under the session.
3. Session expires after its TTL.
4. Expired session reports become invisible to users.
5. Scheduler on `report-prefetch-service` deletes expired data automatically.
6. Manual deletion: `Prefetch.DiscardSession`.
