---
type: meta
title: "Lint Report 2026-06-14"
created: 2026-06-14
updated: 2026-06-14
tags: [meta, lint]
status: developing
---

# Lint Report: 2026-06-14

## Summary

- Pages scanned: ~334 wiki pages
- Issues found: 10
- Auto-fixed: 10
- Needs review: 1 (missing 2026-06-14 batch source entry)

---

## BLOCKER — Address Collision (FIXED)

**`c-000105` shared by two pages:**
- `wiki/concepts/Wasaby-BL-Async-Sync-Cloud-Calls.md` (created 2026-06-12)
- `wiki/concepts/Wasaby-Dev-Standards.md` (created 2026-06-14 batch)

Root cause: 2026-06-12 session created collision file claiming c-000105 manually; 2026-06-14 batch ingest allocated c-000105 legitimately (counter wasn't incremented after the 2026-06-12 session).

**Fix applied:** Unique content from collision file (module list C++ examples, `SetHighDeliveryGuarantee` C++ API, absolute-URL warning) merged into `[[Wasaby-BL-AsyncInvoke]]` (c-000073). Collision file deleted. Counter state now consistent: peek = c-000144, highest observed = c-000142.

---

## HIGH — Connectivity Gaps (FIXED)

Four complement page pairs covering the same platform topic from different angles with **zero cross-links** between them. Fixed by adding bidirectional wikilinks in both `related:` frontmatter and body sections.

| Old page (price-formation) | New page (wasaby.Backend batch) | Status |
|---|---|---|
| [[DWC-Distributed-Workflow-Coordinator]] | [[Wasaby-DWC]] (c-000137) | Fixed ✓ |
| [[LRS-Long-Request-Service]] | [[Wasaby-Long-Running-Operations]] (c-000114) | Fixed ✓ |
| [[Profiles-Service]] | [[Wasaby-Profiles-Service]] (c-000136) | Fixed ✓ |
| [[Sync-Broker]] | [[Wasaby-Sync-Broker]] (c-000142) | Fixed ✓ |

Additionally, [[Wasaby-BL-AsyncInvoke]] gained links to [[Wasaby-BL-Objects]] and [[Sync-Broker]], and gained an absolute-URL auth warning absent in the duplicate.

---

## HIGH — Missing `scripts/detect-transport.py` (FIXED)

The wiki-lint skill references `bash scripts/detect-transport.sh` to auto-create `.vault-meta/transport.json`. Neither `.sh` nor `.py` existed.

**Fix applied:** Created `scripts/detect-transport.py`. Detects obsidian-cli in PATH → `"cli"`, MCP server env vars → `"mcp-obsidian"` / `"mcpvault"`, else `"filesystem"`.

Note: `scripts/allocate-address.py` already existed — no `.sh` → `.py` migration needed for address allocation.

---

## HIGH — Index Orphans (FIXED)

14 pages existed in the vault but were absent from `wiki/index.md`:

**Concept pages (9):**
- [[CursorNavigation-Mechanism]]
- [[PriceFormation-Test-Framework]]
- [[ReferralStub-TargetAction-Pattern]]
- [[Report-Prefetch-Service]]
- [[ReportPrefetch-DB-Schema]]
- [[Franchise-Contract-API]]
- [[Franchise-Loyalty-Architecture]]
- [[Franchise-Loyalty-System]]
- [[Franchise-SabyNet-Subsystem]]

**Source pages (5):**
- [[saby-api-docs-2026-05-21]]
- [[sbis-api-sbis-mcp-2026-05-21]]
- [[sbis-jsonrpc-protocol-format]]
- [[wasaby-sharedfuture-2026-05-22]]
- [[sveshnikov-stub-creation-thoughts-2026-05-28]]

**Fix applied:** All 14 added to `wiki/index.md` in appropriate sections.

**Additional orphan (deleted):** `Wasaby-BL-Async-Sync-Cloud-Calls.md` was also an index orphan. Deleted as part of collision fix above.

---

## MEDIUM — Duplicate Index Entry (FIXED)

`[[Wasaby-BL-Objects]]` appeared twice in `wiki/index.md`:
- Stale entry (no address, old description from pre-batch session)
- Current entry `(c-000111)` added by 2026-06-14 batch

**Fix applied:** Stale entry removed.

---

## MEDIUM — Dead Links (FIXED)

Two dead wikilinks in source files pointing to renamed page:

- `[[DistributionStorage-DB-Schema]]` in [[distribution-storage-db-2026-06-12]] → `[[UpdateSystem-DistributionStorage-DB]]`
- `[[DistributionStorage-DB-Schema]]` in [[distribution-storage-technical-2026-06-12]] → `[[UpdateSystem-DistributionStorage-DB]]`

**Fix applied:** All 3 occurrences (2 frontmatter + 1 body) replaced.

---

## LOW — Backslash Wikilinks (RESOLVED)

Previous lint reports flagged `\]]` terminated wikilinks in `cherry-picks.md` and `Хоттабыч-System.md`. Scan on 2026-06-14 found no remaining occurrences — these were fixed in the 2026-06-04 lint session.

---

## LOW — Missing 2026-06-14 Batch Source Entry

The 38-page wasaby.Backend batch ingest (c-000105..c-000142, date 2026-06-14) has no corresponding source entry in `wiki/index.md` Sources section. All individual concept pages are indexed, but the ingest session itself has no provenance record.

**Suggest:** Add source entry `[[wasaby-backend-batch-2026-06-14]]` if a source file was created during that session.

---

## Address Validation

- Counter state: peek = `c-000144`
- Highest `c-` address observed: `c-000142`
- Post-rollout pages checked: 38 (c-000105..c-000142); all passing after collision fix
- Collision resolved: `c-000105` was assigned to two pages — fixed
- Legacy pages pending backfill: many pre-2026-04-23 pages without addresses (expected, informational)

---

## Semantic Tiling

См. [[tiling-report-2026-06-14]] для полного списка пар.

- Errors (>=0.95): **6 пар**
- Review (0.92–0.95): **35 пар**
- Calibrated: **true** (114 пар размечено вручную 2026-06-14; пороги подняты с 0.90/0.80 до 0.95/0.92)

### Ошибки (>=0.95) — после калибровки

| Пара | Sim | Вердикт |
|---|---|---|
| Entity–Entity (3 пары сотрудников) | 0.96–0.98 | Distinct — похожий формат биографий |
| `BonusSettings-Sync-Restart-Bug` ↔ `BrokerLoyalty-BonusSettings-Race-Fix` | 0.9605 | Две части одного бага — разные RCA, не дубли |
| `ReleasePlans-System` ↔ `UpdateSystem-ReleasePlans` | 0.9547 | Operational vs Technical — разные углы, добавлены перекрёстные ссылки |
| `release-plans-*` ↔ `update-system-work-registry-*` (source пара) | 0.9540 | Source ↔ concept — ожидаемо, не дубли |

### Итог калибровки

- Истинных дублей в Error-зоне (0.90): **0**
- Шум: entity-entity (похожие форматы), concept-source (страница создана из источника), Tensor-Company (общие Saby-слова)
- Поднятые пороги сократили Review с 5117 до **35 пар**

### Рекомендация

Review-зона (0.92–0.95) содержит реальные кандидаты на проверку: DiscountCard-кластер (4 страницы), UpdateSystem-WorkRegistry кластер, FileStorage/SabyDisk, Async-Calls-Bus/Wasaby-MQ. Проверить вручную перед следующим линтом.

---

## Scripts Status

| Script | Language | Status |
|---|---|---|
| `scripts/allocate-address.py` | Python | Exists ✓ |
| `scripts/detect-transport.py` | Python | Created ✓ (this session) |
| `scripts/tiling-check.py` | Python | Exists ✓ |
| `scripts/boundary-score.py` | Python | Exists ✓ |
| `scripts/sabydoc-extract.py` | Python | Exists ✓ |
| `scripts/allocate-address.sh` | Bash | Exists (superseded by .py) |

Tiling run completed: 315 страниц встроено (353 отсканировано, 38 пропущено). Калибровка выполнена 2026-06-14.

---

## Pending Actions

1. Add source entry for the 2026-06-14 wasaby.Backend batch ingest (38 pages, no provenance record in Sources section)
