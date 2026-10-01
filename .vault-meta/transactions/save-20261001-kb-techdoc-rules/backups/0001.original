---
type: concept
title: "Tensor Technical Documentation Standards"
updated: 2026-04-12
tags:
  - tensor
  - documentation
  - standards
  - process
status: current
related:
  - "[[Wasaby-Framework]]"
  - "[[Python-Code-Standards-SBIS]]"
  - "[[tensor-techdoc-standards-2026-04-12]]"
created: 2026-04-12
---

# Tensor Technical Documentation Standards

Standards for writing and maintaining technical documentation (ТД) within the Tensor/SBIS development organization.

---

## When to Create a New ТД

ТД is created per **product**, **subsystem**, or **reusable service**.

- **Subsystem**: a sizeable, functionally isolated part of a product. Always lives inside a product.
- **Service**: create separate ТД only if the service is reused across multiple subsystems. If it serves only one subsystem, add its description inside that subsystem's ТД.

**Key rule**: documentation is **iterative**. After the first project creates a ТД, all subsequent projects only *extend* it — never recreate it from scratch.

> [!key-insight] Don't create ТД per-project
> A new standalone ТД should be rare: only when the project delivers genuinely new, isolated functionality that can be used independently. For extensions, add to the existing ТД. For larger additions with their own page — link them as sub-sections, not new ТД.

---

## Structure of a ТД

Structure depends on the product type:

- **Applied products** (прикладные): no explicit "Technical Documentation" folder — everything in the knowledge base IS the ТД.
- **Internal/platform products**: "How to integrate" and instructions at the root; internal implementation in a "Техническая документация" subfolder.

### Sections Table

| Section | Required? | Audience |
|---|---|---|
| Описание (Description) | Mandatory | All |
| База данных (DB) | Mandatory | Internal team, external dev teams, management |
| Как встраивать / API | If external API exists | Internal, external devs, management |
| Архитектура | For internal products | Internal, management |
| Алгоритмы и процессы | Optional | Internal team |
| Архитектура интерфейса | If UI exists | Internal, management |
| Особенности работы интерфейса | If complex UI logic | Internal, technologists |
| Инструкции по эксплуатации | If admin UIs or ops needed | Internal, external devs, ЦОД, build |
| Организация кода | Mandatory | Internal, external teams |
| Подсистема распределения прав | If access control used | Internal, technologists, management, ЦОД |
| Параметры облака, задачи планировщика | If cloud params/scheduler used | Internal, ЦОД, build |
| Облачный сервис | If cloud service in subsystem | Internal, external, management, ЦОД |

For mobile app products, add: Микросервис, Архитектура интерфейса, Мобильное приложение sections.

---

## Audience Matrix

Who reads which sections:

| Reader | Reads |
|---|---|
| Внутренняя команда разработчиков | Everything |
| Внешние команды разработки | Description, API, DB, Operations, Code org, Cloud/Microservices |
| Управление (directors) | Description, API, DB, Interface architecture, Rights, Cloud/Microservices |
| ЦОД | Description, Operations, Rights, Cloud params, Cloud services |
| Технологи | Description, Interface specifics, Rights |
| Сборка (build team) | Operations, Cloud params |

---

## Formatting Rules

### Format & Storage
- Format: `.sabydoc` (Saby document)
- Storage: product's knowledge base (база знаний разработки продукта)
- Links from Kaizen work-area description required per [organization rules]

### Service Interaction Diagrams
1. **Direction from initiator**: arrows always go `caller → callee`. No bidirectional arrows (request→response is still one-directional).
2. **Service names**: must match names in the Cloud Structure (Структура облака). No synonyms.
3. **Entity connections**: add to architecture diagram if needed for conceptual understanding.
4. **No fan-in arrows**: don't draw multiple arrows converging on one point.
5. **Grouping**: group by functional similarity or physical location (client-side / our datacenter).

### Text Standards
- Cross-reference links: embed on meaningful phrases, not bare URLs.
- Use header articles (заголовочная статья) for sections in "Feed" mode.

### Structure Recommendations
1. Split ТД into separate `.sabydoc` files (at least one per top-level section).
2. For large isolated functional areas within a product — create a subfolder.
3. Templates are guides, not constraints — add sections as needed, but don't cram unrelated content into existing sections; make a new article instead.
4. External materials (Excel, presentations, original diagram sources) → store in Материалы, not the knowledge base.
5. Business process documents → store in the dedicated БП knowledge base.

---

## Anti-Patterns (Учимся писать ТД)

> [!key-insight] ТЗ ≠ ТД
> Technical specifications are **sources of information**, not documentation. Never copy-paste from ТЗ into ТД. ТЗ language ("will be implemented", "requirement #3.2") has no place in ТД. No links from ТД to ТЗ.

**Circular descriptions** — "We implemented service X to provide the user with the ability to do X. It performs function X." The purpose of ТД is to give an outsider understanding of *what it is*, *why it exists*, and *where it fits*.

**Internal inconsistencies** — Text mentions service X but the architecture diagram doesn't show it. DB table has logical FK to another table but the schema omits it. Everything must be consistent.

**Overloaded ("Indian code") schemas** — Schemas should be readable. Avoid:
- WordArt-style framed arrows
- 3D objects on diagrams
- "Connector" decorations
- Extra elements not relevant to the topic

**Verbose text** — Writing well is a skill, not a talent. Practice brevity and clarity.

---

## Iterative Process

```
Project 1 → Create ТД skeleton (Описание, БД, key sections)
Project 2 → Add new sections to existing ТД
Project 3 → Update affected sections, add sub-articles as needed
```

Never start fresh. The skeleton grows and deepens over time.
