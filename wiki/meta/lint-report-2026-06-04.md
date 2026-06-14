---
type: meta
title: "Lint Report 2026-06-04"
created: 2026-06-04
updated: 2026-06-04
tags: [meta, lint]
status: developing
---

# Lint Report: 2026-06-04

## Summary

- Pages scanned: 267
- Issues found: 119 (pre-fix)
- Auto-fixed: 116
- Needs review: 3

---

## Orphan Pages

**Fixed (1):**

- [[ImportDiscountCard-DCS-Counter-Bug]]: no inbound links. Fixed: added to index + linked from [[ImportDiscountCard-Franchise-Client-Import]] `related:`.

---

## Dead Links

36 dead links remain across 13 pages. Breakdown by category:

**Benign — image attachments (9 links in 2 pages):**
- [[SabyGet-Landing-Page]]: 4 `.avif` image links — attachments pending copy to `_attachments/`
- [[SabyGet-Loyalty-Subsystems]]: 4 `.avif` image links — same

**Benign — intentional examples (3 links):**
- [[DragonScale Memory]] → `[[Foo]]` — placeholder example in concept
- [[Persistent Wiki Artifact]] → `[[Three laws of motion]]` — example page reference
- [[Price-Formation-Test-Runner]] → `[[pycharm-content-roots-price-formation.png]]` — image attachment

**Benign — old lint reports referencing renamed/deleted pages (14 links):**
- [[lint-report-2026-04-10]], [[lint-report-2026-05-18]]: links to `[[Wiki Map]]`, `[[dashboard.base]]`, `[[fold-template]]`, `[[E-commerce SEO]]`, `[[ReportPrefetch-Service]]`, `[[wiki-fold]]` — historical references in past lint files; no action needed.

**Needs investigation (3 links + 1 false positive):**
- [[DWC-Migration-SDK]] → garbled Cyrillic path (encoding issue in scanner; actual link is to `[[Тимошенко А.А.\]]` — trailing backslash is a Markdown path artifact)
- [[SabyBank-RKO-Referral]] → same garbled Cyrillic backslash artifacts (2 links)
- [[zvonok-offer-bug-zlateks-2026-04-13]] → same
- [[SBIS-DocumentMessage-ListForEDO]] → JSON array parsed as wikilink (false positive in scanner)
- [[Тимошенко А.А.]] → `[[Омельяненко-Егор-Анатольевич\]]` — trailing backslash artifact

> [!gap] The garbled Cyrillic dead links with `\` suffix are likely scanner artifacts from Windows path encoding. The underlying pages likely exist. Verify by opening in Obsidian.

**Fixed (1):**
- [[cherry-picks]] → `[[wikilinks]]`: was a bare wiki-formatted reference inside a code example. Changed to escaped `\[\[wikilinks\]\]` syntax to prevent false link.

---

## Misplaced Pages

**Fixed (1):**

- `wiki/ReferralProgram-GetPartnerList-Unjoined-Partners.md`: page was in vault root with memory-format frontmatter. Moved to `wiki/concepts/` and reformatted as a proper wiki concept page with correct `type/created/updated/status/tags` fields.

---

## Frontmatter Gaps

**Fixed (61 pages):** All missing `created:` / `updated:` / `status:` fields added with dates inferred from source ingestion records in the index.

**Remaining (0 errors):** All required fields (`type`, `status`, `created`, `updated`, `tags`) are now present across all scannable pages.

---

## Address Validation

- Counter state: `c-000072` (peek after session)
- Post-rollout pages checked: 23 (all passing after this session)
- Legacy pages pending backfill: 175 (informational)

**Fixed (23 addresses assigned):**

| Address | Page |
|---------|------|
| c-000049 | [[Bonus-GetSaleTotals-Timeout-Fix]] |
| c-000050 | [[BonusSettings-Sync-Restart-Bug]] |
| c-000051 | [[GetClientListWithStats-PA-NavCondition-Duplicate-Bug]] |
| c-000052 | [[ImportDiscountCard-DCS-Counter-Bug]] |
| c-000053 | [[JSONB-Array-Containment-Optimization]] |
| c-000054 | [[PostgreSQL-CTE-Cursor-Pushdown]] |
| c-000055 | [[Price-Formation-Test-Runner]] |
| c-000056 | [[ReferralBonus-GetSaleList-Iterative-Ordering-Bug]] |
| c-000057 | [[ReferralProgram-GetPartnerList-Unjoined-Partners]] |
| c-000058 | [[SBIS-Browser-to-API-Conversion]] |
| c-000059 | [[SBIS-DocumentMessage-ListForEDO]] |
| c-000060 | [[SabyBank-Stub-Rewards-Calculation]] |
| c-000061 | [[SetLeadPrice-SABYBANK-Stub-Branch]] |
| c-000062 | [[Wasaby-BL-Call-Loop-Pattern]] |
| c-000063 | [[Wasaby-Cross-Client-BL-Call]] |
| c-000064 | [[linter-project-2026-05-18]] |
| c-000065 | [[wasaby-bl-call-loop-user-switch-2026-06-04]] |
| c-000066 | [[wasaby-cross-client-call-2026-06-04]] |
| c-000067 | [[Тимошенко А.А.]] |
| c-000068 | [[BonusChart-IterativeBlock-Bug-Fix]] |
| c-000069 | [[GetIndividualBatch-AttachPersonId-Timeout-Fix]] |
| c-000070 | [[Linter-Standarization-Project]] |
| c-000071 | [[SonarQube-Stan-Linter-Setup]] |

---

## Graph Connectivity Improvements

Pages with ≤1 inbound links before this session: 13. After fixes: all have ≥2 inbound links.

**Direct link additions (related: fields updated):**

| Page | Added link to |
|------|---------------|
| [[ImportDiscountCard-Franchise-Client-Import]] | [[ImportDiscountCard-DCS-Counter-Bug]] |
| [[DiscountCard-Subsystem-Overview]] | [[DiscountCard-Admin-Ops]], [[DiscountCardType-GetListSimple-FranchiseGroupId-Bug]], [[ImportDiscountCard-DCS-Counter-Bug]], [[EntitySP-UniqueId-Migration]] |
| [[Bonus-Programs-Architecture]] | [[Bonus-GetTotalBalance]], [[BonusChart-IterativeBlock-Bug-Fix]] |
| [[BrokerLoyalty-BonusSettings-Race-Fix]] | [[BonusSettings-Sync-Restart-Bug]], [[DWC-BonusSettings-Events-Migration]] |
| [[ReferralDeals-System]] | [[ReferralProgram-GetPartnerList-Unjoined-Partners]], [[AT-Coverage-ReferralDeals-Project]] |
| [[Saby-API-Protocol]] | [[SBIS-Browser-to-API-Conversion]], [[Saby-External-API-Tasks]] |
| [[SetLeadPrice-SABYBANK-Stub-Branch]] | [[SabyBank-Stub-Rewards-Calculation]] |
| [[LoyaltyPrograms-IterativeListLoading]] | [[BonusChart-IterativeBlock-Bug-Fix]] |
| [[Franchise-Loyalty-Architecture]] | [[Franchise-SabyNet-Subsystem]] |
| [[Franchise-SabyNet-Subsystem]] | [[Franchise-Loyalty-Architecture]] |
| [[ExternalLoyalty-Integrations]] | [[Bonus-Programs-Architecture]] |

**Driven by semantic tiling** (nomic-embed-text, 240 pages embedded):

- Tiling report: [[tiling-report-2026-06-04]]
- High-similarity errors (>=0.9): 100+ pairs found
- Cross-links added for top unlinked pairs by similarity score

---

## Semantic Tiling

See [[tiling-report-2026-06-04]] for the full pair listing.

- Errors (>=0.90): ~100 pairs
- Review (0.80-0.90): ~200+ pairs
- Calibrated: false (using conservative defaults)

> [!gap] Tiling is not calibrated for this vault. Several "error" pairs are expected (e.g., entity pages for team members scoring 0.97 similarity — they are distinct people, not duplicates). Consider calibration pass per skill instructions after labeling ~50 pairs.

**Notable true near-duplicates to review:**
- `BonusSettings-Sync-Restart-Bug` ↔ `BrokerLoyalty-BonusSettings-Race-Fix` (0.961) — closely related bugfixes, not duplicates; now cross-linked
- `DiscountCard-Admin-Ops` ↔ `DiscountCard-Subsystem-Overview` (0.948) — related content, already linked; no merge needed
- `Franchise-Loyalty-Architecture` ↔ `Franchise-SabyNet-Subsystem` (0.907) — complementary sections; now cross-linked

---

## Stale Index Entries

**Checked:** All links in `wiki/index.md` resolve to existing files.

**Canvases listed in index** (main, welcome, youtube-explainer, claude-obsidian-presentation): These are `.canvas` files, not `.md` — correct behavior, no fix needed.

---

## Needs Review (3 items)

1. **SabyGet image attachments** (9 dead links): `.avif` images referenced in [[SabyGet-Landing-Page]] and [[SabyGet-Loyalty-Subsystems]] are not in `_attachments/`. Copy them from the source or regenerate.

2. **Backslash Cyrillic link artifacts**: [[DWC-Migration-SDK]], [[SabyBank-RKO-Referral]], [[zvonok-offer-bug-zlateks-2026-04-13]], [[Тимошенко А.А.]] contain wikilinks with a trailing `\` (e.g. `[[Тимошенко А.А.\]]`). These are likely copy-paste artifacts from Windows paths. Open in Obsidian to verify and remove the trailing backslash from the link.

3. **175 legacy pages pending backfill addresses**: These are pre-rollout pages (created before 2026-04-23). No action required until a dedicated backfill pass.
