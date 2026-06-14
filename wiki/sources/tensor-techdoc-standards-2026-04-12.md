---
type: source
title: "Tensor Technical Documentation Standards (batch)"
source_files:
  - "raw/Правила оформления технической документации.md"
  - "raw/Правила оформления технической документации 1.md"
  - "raw/Когда создавать новую ТД.md"
  - "raw/Кто читает техническую документацию.md"
  - "raw/Учимся писать ТД.md"
ingested: 2026-04-12
tags:
  - source
  - tensor
  - documentation-standards
status: ingested
related:
  - "[[Tensor-TechDoc-Standards]]"
created: 2026-04-12
updated: 2026-04-12
---

# Source: Tensor Technical Documentation Standards

Batch of 5 documents from the Tensor/SBIS developer knowledge base on the topic of technical documentation (ТД) standards. All sourced from `link.sbis.ru/programming/knowledge` and `online.sbis.ru`.

## Documents

1. **Правила оформления технической документации** (15 дек'25) — Core rules: structure, sections, formatting standards for schemas and text. Two clips of the same article.
2. **Когда создавать новую ТД** (8 сен'25) — When to create a new ТД vs. extending an existing one.
3. **Кто читает техническую документацию** (22 авг'25) — Audience matrix: who reads which sections.
4. **Учимся писать ТД** (22 авг'25) — Anti-patterns: ТЗ≠ТД, circular descriptions, inconsistencies, overloaded schemas.

## Key Takeaways

- ТД is created per product, subsystem, or reusable service. Not per-project.
- ТЗ ≠ ТД: technical specifications are sources, not documentation.
- Documentation is iterative: build a skeleton, fill it over time.
- New standalone ТД should be rare; prefer extending existing docs.
- Format: Saby `.sabydoc` files in the product's knowledge base.

→ Full structured knowledge: [[Tensor-TechDoc-Standards]]
