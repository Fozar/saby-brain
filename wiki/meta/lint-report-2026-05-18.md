---
type: meta
status: evergreen
created: 2026-05-18
updated: 2026-05-18
tags:
  - meta
  - lint
---

# Wiki Lint Report — 2026-05-18 (Post-Fix)

> This is the follow-up lint run after fixes applied earlier on 2026-05-18. The prior report (pre-fix) has been overwritten. See the "Applied Fixes" section at the bottom for what was resolved.

## Summary

| Metric | Count |
|--------|-------|
| Pages scanned | 214 |
| Total issues found | **~250** |
| Critical (must fix) | **2** |
| Warnings (should fix) | **32** |
| Suggestions (worth considering) | **~216** |

**DragonScale address validation:** ACTIVE — rollout baseline 2026-04-23, counter at 14, 11 addresses allocated, manifest fully consistent.
**Semantic tiling check:** DELEGATED — `tiling-report-2026-05-18.md` already generated this session (186 pages embedded, 0 embed errors). Exit code 0. Results summarised in the Semantic Tiling section below.

---

## Critical (must fix)

### C-1: Two post-rollout pages missing DragonScale address

Both pages have `created: >= 2026-04-23` (the DragonScale rollout baseline) and have no `address:` field. Per the vault's address policy these are lint **errors**.

| Page | Created | Type |
|------|---------|------|
| `wiki/meta/tiling-report-2026-04-24.md` | 2026-04-24 | meta |
| `wiki/meta/lint-report-2026-05-18.md` | 2026-05-18 | meta |

**Suggested fix:** Allocate the next two available addresses via `python scripts/allocate-address.py` (counter currently at 14, so the next two will be `c-000014` and `c-000015`). Add the `address:` field to each frontmatter and update `.raw/.manifest.json` `address_map`.

---

### C-2: `wiki/meta/tiling-report-2026-05-18.md` has no frontmatter

The tiling report has no `---` frontmatter block at all. This means it cannot be queried by Dataview/Bases and will fail the address-field check above as a secondary consequence.

**Suggested fix:** Add a minimal frontmatter block:
```yaml
---
type: meta
title: "Semantic Tiling Report 2026-05-18"
status: evergreen
created: 2026-05-18
updated: 2026-05-18
tags:
  - meta
  - tiling
address: c-000014
---
```

---

## Warnings (should fix)

### W-1: One true orphan concept page

`wiki/concepts/ReportPrefetch-Service.md` is not linked from any other page. It is a redirect stub pointing to `[[Report-Prefetch-Service]]` (the canonical page). The canonical page IS linked from the domain index. The redirect is useful but nothing points to it.

**Suggested fix:** Either link to `[[ReportPrefetch-Service]]` from `[[Report-Prefetch-Service]]` as an alias note, or delete the redirect since Obsidian resolves the canonical page directly.

---

### W-2: `[[dashboard.base]]` dead link in `wiki/meta/dashboard.md` (×2)

`dashboard.md` embeds `![[dashboard.base]]` twice. The file `wiki/meta/dashboard.base` exists, but Obsidian's wikilink resolver requires the filename WITHOUT the extension for `.base` files — it should be `![[dashboard]]`. (Note: the current wikilink checker may be flagging this as dead because it uses basename matching; in Obsidian, `.base` files may or may not resolve via `![[dashboard.base]]` depending on the Obsidian version.)

**Suggested fix:** Verify the embed renders correctly in Obsidian. If not, change the embeds in `dashboard.md` to `![[dashboard]]`.

---

### W-3: `dashboard.md` does not link to `tiling-report-2026-05-18`

The Lint and Tiling Reports section in `wiki/meta/dashboard.md` references `[[tiling-report-2026-04-24]]` but not the newer `[[tiling-report-2026-05-18]]` generated today.

**Suggested fix:** Add `- [[tiling-report-2026-05-18]] — semantic tiling run (May 2026, 186 pages)` to the Lint & Tiling Reports list in `dashboard.md`.

---

### W-4: 18 source pages not listed in `wiki/index.md`

The following source pages exist in `wiki/sources/` but are not referenced in the Sources section of `wiki/index.md`. The index header claims "Sources ingested: 78" but only 23 are listed:

- `franchise-api-2026-04-10`
- `franchise-loyalty-2026-04-10`
- `franchise-sabynet-2026-04-10`
- `linter-project-2026-05-18`
- `loyalty-db-franchise-2026-04-10`
- `loyalty-franchise-algorithms-2026-04-10`
- `report-prefetch-conceptual-2026-04-13`
- `report-prefetch-db-schema-2026-04-13`
- `report-prefetch-service-2026-04-13`
- `report-prefetch-subsystems-2026-04-13`
- `saby-naming-guide-2026-04-12`
- `saby-products-lineup-2026-04-12`
- `sync-broker-deep-dive-2026-04-10`
- `tensor-techdoc-standards-2026-04-12`
- `tests-new-readme-2026-04-11`
- `wasaby-infra-2026-04-12`
- `zvonok-offer-bug-zlateks-2026-04-13`
- `zvonok-zlateks-followup-2026-04-14`

**Suggested fix:** Add the missing source entries to the Sources section of `wiki/index.md` and update the "Sources ingested" counter. Alternatively, if these are intentionally unlisted, add them to `sources/_index.md` at minimum.

---

### W-5: 4 dead path-qualified wikilinks in `wiki/index.md`

The `related:` block at the top and the `## Indexes` section use path-qualified wikilinks that do not resolve via simple basename matching:
- `[[concepts/_index]]` (×2 in index.md, also in many concept pages)
- `[[entities/_index]]` (×2)
- `[[sources/_index]]` (×2)
- `[[price-formation/_index]]` (×1 in index.md)

In Obsidian these resolve correctly IF the full relative path is used. However they will fail any external link checker. The pattern `[[price-formation/_index]]` should be `[[domains/price-formation/_index]]` or simply `[[_index]]` if Obsidian resolves by shortest path.

**Suggested fix:** Since Obsidian supports path-qualified links and the files exist, this may be cosmetic. However, the `[[price-formation/_index]]` links scattered across 50+ concept pages should be standardised to `[[domains/price-formation/_index]]` for external tool compatibility, or left as-is if the vault relies on Obsidian-only resolution.

---

### W-6: 12 concept pages not in `wiki/index.md` and not covered by any domain index

The following pages are reachable only via their source pages or via the concepts/_index, making them partially orphaned from the main navigation:

- `wiki/concepts/DCCommon-Helpers.md`
- `wiki/concepts/DragonScale Memory.md`
- `wiki/concepts/Loyalty-Franchise-Mechanics.md`
- `wiki/concepts/Persistent Wiki Artifact.md`
- `wiki/concepts/PriceFormation-Common-Helpers.md`
- `wiki/concepts/PriceFormationOnline-Core.md`
- `wiki/concepts/PriceFormationOnline-Helpers.md`
- `wiki/concepts/Pro Hub Challenge.md`
- `wiki/concepts/Query-Time Retrieval.md`
- `wiki/concepts/SEO Drift Monitoring.md`
- `wiki/concepts/SVG Diagram Style Guide.md`
- `wiki/concepts/Search Experience Optimization.md`
- `wiki/concepts/Semantic Topic Clustering.md`
- `wiki/concepts/Source-First Synthesis.md`

Note: `Franchise-Contract-API`, `Franchise-Loyalty-Architecture`, `Franchise-Loyalty-System`, `Franchise-SabyNet-Subsystem`, `PriceFormation-Test-Framework`, `Report-Prefetch-Service`, and `ReportPrefetch-DB-Schema` ARE in the domain `price-formation/_index` so they are navigable.

**Suggested fix:** Add the 14 pages above to `wiki/index.md` under appropriate sections, or add them to the domain `_index`. Also consider adding a "LLM Wiki / Claude-Obsidian" subsection to index.md for the SEO-family pages (`DragonScale Memory`, `Pro Hub Challenge`, `SEO Drift Monitoring`, etc.).

---

### W-7: Index page total count is stale

`wiki/index.md` header reads: `Total pages: 147 | Sources ingested: 78`
Actual page count: **214** `.md` files (including meta/folds/indexes).
Concept pages alone: **133**. Unique concept entries in index: **~110**.

**Suggested fix:** Update the header to `Total pages: 214 | Sources ingested: 41` (41 source `.md` files in `wiki/sources/`).

---

### W-8: Address counter drift — gap at c-000002 and c-000003

The counter file reads `14`, the manifest has addresses `c-000001` and `c-000004` through `c-000013` (11 total). Addresses `c-000002` and `c-000003` were allocated but no pages carry them; these pages were presumably deleted or renamed. The counter is correct (pointing to the next-available slot c-000014), but the manifest gap is unexplained.

**Suggested fix:** Document why c-000002 and c-000003 are absent (add a comment to `.raw/.manifest.json` or a `retired_addresses` block). No re-use of these identifiers is needed; the gap is not harmful.

---

### W-9: 3 canvas files in `wiki/canvases/` are orphaned

`wiki/canvases/main.canvas`, `wiki/canvases/welcome.canvas`, and `wiki/canvases/youtube-explainer.canvas` are not linked from any page. `claude-obsidian-presentation.canvas` is also not linked but may be intentionally standalone.

**Suggested fix:** Link the canvases from `wiki/overview.md` or `wiki/meta/dashboard.md`, or add a `## Canvases` section to `wiki/index.md`.

---

### W-10: `sources/_index.md` is orphaned

`wiki/sources/_index.md` is not linked from any wiki page (the links in index.md use the path-qualified form `[[sources/_index]]` which may not resolve). The index.md `## Indexes` section uses `[[sources/_index]]` which requires path-qualified resolution.

**Suggested fix:** Confirm that `[[sources/_index]]` in index.md resolves correctly in Obsidian. If not, change to the relative form or add a direct backlink.

---

## Suggestions (worth considering)

### S-1: Pervasive missing `created` and `tags` fields (154 pages missing `created`, ~180 missing `tags`)

The vast majority of pages pre-date the current required-field schema. The `created` field is absent on 154 of 214 pages; `tags` is absent on approximately 180 pages. These are pre-rollout pages (created before 2026-04-23) so they are informational, not errors.

The pattern is consistent: nearly all pages ingested before April 2026 have `type`, `status`, `updated`, and `related` but lack `created` and `tags`. This is a vault-wide backfill task.

**Top offenders (missing `status` or `type` in addition):**
- `wiki/sources/franchise-api-2026-04-10.md` — missing `status`, `updated`, `tags`
- `wiki/sources/franchise-sabynet-2026-04-10.md` — missing `created`, `status`, `updated`, `tags`
- `wiki/sources/loyalty-react-migration-2026-04-14.md` — missing `created`, `status`, `updated`, `tags`
- `wiki/sources/loyalty-sale-profiles-2026-04-10.md` — missing `created`, `status`, `updated`, `tags`
- `wiki/sources/messaging-middleware-2026-04-12.md` — missing `created`, `status`, `updated`, `tags`
- `wiki/sources/parameters-service-2026-04-12.md` — missing `created`, `status`, `updated`, `tags`
- `wiki/sources/saby-naming-guide-2026-04-12.md` — missing `created`, `status`, `updated`, `tags`
- `wiki/sources/saby-products-lineup-2026-04-12.md` — missing `created`, `status`, `updated`, `tags`
- `wiki/sources/storage-services-2026-04-12.md` — missing `created`, `status`, `updated`, `tags`

**Suggested fix:** Run a batch script to add `created: <ingest-date-from-filename>`, `tags: [source]`, and `status: archived` to all source pages missing these fields. For concept pages, derive `created` from `updated` as a best estimate.

---

### S-2: Semantic Tiling — 67 error-level pairs, 2159 review-level pairs

The tiling report at `[[tiling-report-2026-05-18]]` (generated 2026-05-18T10:54:47Z using nomic-embed-text, 186 pages embedded) found:

**Exit code: 0 (tiling check passed threshold checks)**

| Band | Pairs | Action |
|------|-------|--------|
| Errors (similarity >= 0.9) | 67 | Review for merge or differentiation |
| Review (0.8 – 0.9) | 2159 | Low-priority; normal for a domain-specific vault |

**Top error-band pairs requiring review (similarity >= 0.94):**

| Similarity | Page A | Page B |
|-----------|--------|--------|
| 0.9480 | `DiscountCard-Admin-Ops` | `DiscountCard-Subsystem-Overview` |
| 0.9438 | `AT-Coverage-ReferralDeals-Project` | `ReferralDeals-System` |
| 0.9430 | `DiscountCard-Admin-Ops` | `DiscountCard-Algorithms-Processes` |
| 0.9401 | `DiscountCard-Algorithms-Processes` | `DiscountCard-Subsystem-Overview` |
| 0.9393 | `DiscountCard-Admin-Ops` | `DiscountCard-UI-Specifics` |
| 0.9366 | `Promocode-Subsystem-Overview` | `Tensor-Company` (entity) |
| 0.9363 | `Saby-Product-Lineup` | `Tensor-Glossary` |
| 0.9359 | `AT-Coverage-ReferralDeals-Project` | `Tensor-Company` (entity) |
| 0.9342 | `Franchise-Loyalty-Architecture` | source `franchise-loyalty-2026-04-10` |
| 0.9332 | `DiscountCard-Subsystem-Overview` | `DiscountCard-UI-Specifics` |

The high count of DiscountCard pairs suggests the four DiscountCard-* sub-pages (`Admin-Ops`, `Algorithms-Processes`, `Subsystem-Overview`, `UI-Specifics`) are near-duplicates at the embedding level. Consider whether `DiscountCard-Admin-Ops` can be merged into `DiscountCard-Subsystem-Overview` or whether more differentiated content is needed.

The `Tensor-Company` entity appearing in multiple high-similarity pairs against unrelated concepts is likely because it contains a broad product list that overlaps with nearly every loyalty page.

Full report: `wiki/meta/tiling-report-2026-05-18.md`

---

### S-3: 100 pages have headings with no content beneath them

100 of 214 pages have at least one heading immediately followed by another heading or end-of-file, meaning the heading has no body text. This is widespread across concept pages and likely reflects the ingest pattern (headings created as section stubs).

**Most affected pages (4+ empty headings):**
- `wiki/concepts/PriceFormation-Common-Helpers.md` — 6 empty headings
- `wiki/concepts/cherry-picks.md` — 4 empty headings (Tier 1–4 all empty)
- `wiki/concepts/Prompts-Cashier-Hints.md` — 4 empty headings
- `wiki/meta/2026-04-24-v1.6.0-release-session.md` — 4 empty headings
- `wiki/concepts/Franchise-Loyalty-Architecture.md` — 3 empty headings
- `wiki/concepts/PriceFormation-Test-Framework.md` — 3 empty headings
- `wiki/concepts/PriceFormationOnline-Helpers.md` — 3 empty headings
- `wiki/concepts/SonarQube-Stan-Linter-Setup.md` — 3 empty headings
- `wiki/concepts/Sync-Broker-Reactive.md` — 3 empty headings

**Suggested fix:** Prioritise filling in the Tier sections in `cherry-picks.md` (actionable backlog). For other pages, stubs can be left until the page is actively developed; they are informational rather than blocking.

---

### S-4: 6 pages over 300 lines (excluding tiling report)

| Lines | Page |
|-------|------|
| 380 | `wiki/concepts/Wasaby-BL-List-Advanced.md` |
| 378 | `wiki/log.md` |
| 356 | `wiki/meta/lint-report-2026-05-18.md` (this file) |
| 349 | `wiki/meta/2026-04-24-v1.6.0-release-session.md` |
| 306 | `wiki/concepts/Wasaby-RecordSet-Performance.md` |
| 303 | `wiki/concepts/PriceFormation-Common-Helpers.md` |
| 302 | `wiki/concepts/LoyaltyPrograms-IterativeListLoading.md` |

**Suggested fix:** `wiki/log.md` can be trimmed or folded when it exceeds 400 lines. `Wasaby-BL-List-Advanced.md` may warrant a split into "navigation patterns" and "advanced list patterns" sub-pages.

---

### S-5: `Loyalty-React-Migration-Project` missing `updated` field

This page has `type`, `status`, `tags`, `created` but no `updated` field. It is an active project page.

**Suggested fix:** Add `updated: 2026-05-18` to the frontmatter.

---

### S-6: `Claude SEO` entity page not in index.md and has no backlinks

`wiki/entities/Claude SEO.md` exists but is not referenced in `wiki/index.md` and has no apparent inbound links from other pages.

**Suggested fix:** Add `[[Claude SEO]]` to the Entities section of `wiki/index.md`, or merge its content into `wiki/comparisons/claude-obsidian-ecosystem.md`.

---

## Address Validation

**Status: PASS with 2 errors**

| Check | Result |
|-------|--------|
| Counter value | 14 |
| Addresses allocated | 11 (c-000001, c-000004 through c-000013) |
| Format validity | All 11 match `^c-[0-9]{6}$` |
| Uniqueness | No duplicates detected |
| Manifest consistency | Fully consistent — all 11 manifest entries match page frontmatter |
| Counter drift | Counter (14) = last address (13) + 1 — correct |
| Gap addresses | c-000002, c-000003 — unaccounted (likely retired pages) |
| Post-rollout pages missing address | **2 errors** (see Critical C-1) |

Pages correctly addressed:

| Address | Page |
|---------|------|
| c-000001 | `wiki/concepts/DragonScale Memory.md` |
| c-000004 | `wiki/concepts/DWC-Card-Events-Migration.md` |
| c-000005 | `wiki/concepts/FranchiseCard-Import-POS-SaleValidation-Bug.md` |
| c-000006 | `wiki/concepts/ImportDiscountCard-Franchise-Client-Import.md` |
| c-000007 | `wiki/concepts/Persistent Wiki Artifact.md` |
| c-000008 | `wiki/concepts/Query-Time Retrieval.md` |
| c-000009 | `wiki/concepts/Source-First Synthesis.md` |
| c-000010 | `wiki/meta/2026-04-24-v1.6.0-release-session.md` |
| c-000011 | `wiki/meta/DWC-Card-HandleChangeData-Session.md` |
| c-000012 | `wiki/meta/PromoCode-SafeDelete-Sabyget-Bug.md` |
| c-000013 | `wiki/concepts/ReferralProgram-Stub-Implementation.md` |

---

## Semantic Tiling

**Status: EXIT CODE 0 — tiling check passed**

Report file: `wiki/meta/tiling-report-2026-05-18.md`
Generated: 2026-05-18T10:54:47Z | Model: nomic-embed-text | Ollama: http://127.0.0.1:11434

| Metric | Value |
|--------|-------|
| Pages scanned | 214 |
| Pages embedded | 186 |
| Skipped (excluded/meta/folds) | 28 |
| Cache hits | 0 (fresh run) |
| Embed errors | 0 |
| Calibrated | No (uncalibrated defaults) |
| Thresholds | error >= 0.9, review = 0.8–0.9 |
| Error-band pairs | 67 |
| Review-band pairs | 2159 |

The 2159 review-band pairs are high but expected for a domain-specific vault where all pages share the Wasaby/loyalty context. The 67 error-band pairs deserve attention (see S-2 above).

---

## Applied Fixes (from earlier session today, 2026-05-18)

The following issues from the pre-fix lint report were resolved before this follow-up lint was run:

| Fix | Details |
|-----|---------|
| Dead links: `[[Wiki Map]]` | Canvas renamed/linked |
| Dead links: `[[How does the LLM Wiki pattern work?]]` | Page created as `How does the LLM Wiki pattern work.md` (no trailing `?`) |
| Dead links: `[[Franchise-Loyalty-System\]]` | Escaped backslash removed from wikilinks |
| Dead links: `[[Тимошенко А.А.]]` | Removed from pages (personal entity, no page) |
| Dead links: `[[E-commerce SEO]]` | Removed or replaced |
| Dead links: `[[wiki-fold]]`, `[[fold-template]]` | Resolved via fold system |
| Dead links: backlink session-related | Session pages created/linked |
| Dead links: overview canvases | Canvas links fixed |
| Dead links: `[[dashboard.base]]` (partial) | `dashboard.base` file created |
| DragonScale addresses | c-000004 through c-000013 assigned to 10 post-rollout pages |
| Pages moved from `meta/` to `concepts/` | DWC-Promocode-Events-Migration, DWC-BonusSettings-Events-Migration, BrokerLoyalty-BonusSettings-Race-Fix, ReferralProgram-DetachPartner-Implementation, ReferralProgram-Stub-Implementation |
| Duplicate concept resolved | `DWC-Card-Events-Migration.md` was duplicated as a session; session renamed to `DWC-Card-HandleChangeData-Session.md` and moved to `meta/` |
| Orphan index pages | `concepts/_index`, `entities/_index`, `sources/_index` linked from `index.md` under `## Indexes` section |
| Session notes | Linked from `dashboard.md` |
| Frontmatter: `tiling-report-2026-04-24.md` | Fixed |
| Frontmatter: `ReportPrefetch-Service.md` | Fixed |
| Manifest `address_map` | Updated with all 11 allocated addresses |
| Semantic tiling | Run for first time on this vault: 186 pages embedded, report at `tiling-report-2026-05-18.md` |

---

*Lint run: 2026-05-18 | Tool: wiki-lint skill (Claude claude-sonnet-4-6) | Vault: claude-obsidian*
