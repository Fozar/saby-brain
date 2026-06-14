---
type: source
title: "Схема базы данных (report-prefetch-service)"
source: "https://online.sbis.ru/page/knowledge-bases/694fcc5c-abd7-4c2b-9c9b-761e1fdc92fb"
created: 2026-04-13
ingested: 2026-04-13
tags:
  - source
  - report-prefetch-service
  - database
  - wasaby
  - sbis
related:
  - "[[ReportPrefetch-DB-Schema]]"
  - "[[Report-Prefetch-Service]]"
updated: 2026-04-13
status: archived
---

# Source: Схема базы данных (report-prefetch-service)

**Source URL:** https://online.sbis.ru/page/knowledge-bases/694fcc5c-abd7-4c2b-9c9b-761e1fdc92fb
**Date created:** 02.11.25
**Ingested:** 2026-04-13

## Summary

Internal knowledge-base page documenting the PostgreSQL database schema used by `report-prefetch-service` — the Wasaby platform mechanism for caching large report data. The document covers the versioned (iterative) schema and the legacy (old) schema, all DB tables, typical query patterns (выборки), and the full index table.

## Key Extractions

- [[ReportPrefetch-DB-Schema]] — full schema: tables (SessionId, StoredReport, ReportPage, ReportData, Method, ShardsAmountHistory), typical queries (5 patterns), and all indexes

## Pages Created

- [[ReportPrefetch-DB-Schema]] — DB schema, tables, typical queries, index table

## Pages Updated

- None

## Notes

The document references two schema versions:
- **Iterative version** (current) — supports large reports (>10k records); uses separate `ReportData` and `ReportPage` tables
- **Old version** — legacy schema for smaller/non-iterative reports

The sidebar navigation in the source reveals the broader `report-prefetch-service` knowledge base structure: концептуальное описание, архитектура продукта, подсистемы/сервисы/сущности, схема БД, публичное API, организация кода, архитектура интерфейса, подсистема распределения прав, параметры облака/планировщика, преобразование PDF.
