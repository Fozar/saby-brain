---
type: source
title: "Wasaby DB Access — 5 docs from raw/"
date: 2026-04-10
source_type: internal-docs
tags:
  - source
  - wasaby
  - database
status: evergreen
related:
  - "[[Wasaby-DB-Access-Patterns]]"
  - "[[Wasaby-Framework]]"
created: 2026-04-10
updated: 2026-04-10
---

# Wasaby DB Access — 5 docs from raw/

**Date:** 2026-04-10
**Sources:** 5 internal Wasaby backend knowledge articles (clipped from link.sbis.ru/wasabybackend/knowledge)

## Files Ingested

1. `raw/Выполнение запросов в БД.md` — sync queries: IStatement + SqlQuery
2. `raw/Асинхронные запросы в БД.md` — async queries: IAsyncQueryResult, Wait patterns
3. `raw/API LISTENNOTIFY.md` — PostgreSQL LISTEN/NOTIFY pub/sub
4. `raw/Массовая выборка и вставка записей в БД.md` — bulk ops: ITableCopier
5. `raw/Шаблоны SQL-запросов.md` — SQL template system: Template/TemplateExecutor/QueryStorage

## Pages Created

- [[Wasaby-DB-Access-Patterns]] — unified concept page covering all 5 patterns

## Key Insights

- All patterns exist in both C++ and Python; Python wraps must use `with` for async/listen RAII.
- Async queries lock the connection for their duration — never save `IAsyncQueryResult` across BL method boundaries.
- SQL Templates are the recommended query-building approach; they prevent SQL injection and support named params + conditional clauses.
- SQLite (desktop/mobile) has restricted support: no async queries, no ITableCopier Get/Put.
