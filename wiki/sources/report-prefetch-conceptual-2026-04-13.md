---
type: source
title: "Концептуальное описание решения и основные алгоритмы (report-prefetch-service)"
source: "https://online.sbis.ru/page/knowledge-bases/694fcc5c-abd7-4c2b-9c9b-761e1fdc92fb"
ingested: 2026-04-13
tags:
  - source
  - wasaby
  - report-prefetch
  - caching
  - platform
status: ingested
related:
  - "[[Report-Prefetch-Service]]"
  - "[[ReportPrefetch-DB-Schema]]"
  - "[[Wasaby-App-Optimization]]"
  - "[[Wasaby-BL-List-Methods]]"
created: 2026-04-13
updated: 2026-04-13
---

# Source: Концептуальное описание решения и основные алгоритмы

**Raw file:** `raw/Концептуальное описание решения и основные алгоритмы.md`
**Source URL:** https://online.sbis.ru (wasaby.Backend / Платформенный механизм кэширования отчетов)
**Date captured:** 2026-04-13
**Section:** wasaby.Backend > Платформенный механизм кэширования отчетов (report-prefetch-service) > Техническая документация > Концептуальное описание решения и основные алгоритмы

## Summary

Концептуальный обзор двухкомпонентной архитектуры системы кэширования отчётов SBIS/Wasaby. Определяет роли модуля `ReportPrefetch` и сервиса `report-prefetch-service`, а также первичный алгоритм работы метода `Prefetch.List/4`.

## Content

### Два компонента системы

**1. Клиентский модуль «ReportPrefetch»** (BL-сторона):
- проверка прав для кэшируемого метода
- вызов кэшируемого метода с большим лимитом
- сериализация результата на страницы
- взаимодействие с `report-prefetch-service`: сохранение отчётов, получение кэшированной страницы, работа с сессиями

**2. Сервис «report-prefetch-service»**:
- хранение сессий кэширования
- постраничное хранение отчётов с привязкой к сессии
- API: сохранить отчёт / получить конкретную страницу

### Основная точка входа

`Prefetch.List/4` — публичный метод модуля `ReportPrefetch`, через который выполняется всё взаимодействие с системой кэширования.

## Pages Content Is Integrated Into

- [[Report-Prefetch-Service]] — концептуальная архитектура, алгоритм Prefetch.List, конвейер обработки
- [[ReportPrefetch-DB-Schema]] — схема БД сервиса: SessionId, StoredReport, ReportPage, ReportData

## Notes

Данный файл — самый краткий из набора 4 raw-документов по report-prefetch-service. Содержательная часть (строки 17–31) описывает архитектуру на уровне компонентов. Остальное — навигационная панель SBIS wiki. Вся информация файла интегрирована в [[Report-Prefetch-Service]].
