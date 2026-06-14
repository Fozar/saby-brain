---
type: source
title: "Описание подсистемы — Франшиза (Saby Net)"
source: "https://online.sbis.ru/knowledge-bases/001495c1-d301-490a-9531-0b6fe60059d7?folder=2f3526bc-8224-4fc8-8b70-41164a62deba&published=null&mode=table"
raw_file: "raw/Описание подсистемы.md"
ingested: 2026-04-10
tags:
  - source
  - franchise
  - sabynet
  - loyalty
  - price-formation
related:
  - "[[Franchise-SabyNet-Subsystem]]"
  - "[[Loyalty-In-Products]]"
  - "[[Loyalty-Product-Overview]]"
  - "[[price-formation/_index]]"
created: 2026-04-10
updated: 2026-04-10
status: archived
---

# Source: Описание подсистемы — Франшиза (Saby Net)

**Ingested:** 2026-04-10
**Source type:** Internal knowledge base article (SBIS online)
**Published:** 29 Oct 2025

---

## Summary

Short internal description of the Franchise (Франшиза) subsystem — a separate configuration of the Saby Net application.

Key facts documented:
- Franchise is a separate app configuration built on the same mechanisms as Saby Net.
- Has a custom regulation (регламент) with a reduced field set.
- Supports operator workflows.
- Does **not** have KPI settings.
- Records specific data to statistics.
- Supports shared bonus programs and promotions (акции) across venues working in different accounts.

Links to code artifacts referenced:
- Visual representation config: `edo/edo-client` `regulation_config.py#L356`
- Regulation JSON files: `edo/regulation-json` (two UUIDs: `2ea37571...` and `1ba8e7de...`)
- App configuration: `engine/appconfiguration-datapackage` config UUID `bcd58727...`

---

## Pages Created / Updated

- Created: [[Franchise-SabyNet-Subsystem]]
- Updated: [[Loyalty-In-Products]]
- Updated: [[price-formation/_index]]
