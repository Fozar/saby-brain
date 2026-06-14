---
type: source
title: "Подсистемы, сервисы, базовые сущности и их взаимосвязи (report-prefetch-service)"
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
  - "[[Wasaby-App-Optimization]]"
  - "[[Wasaby-BL-Advanced]]"
created: 2026-04-13
updated: 2026-04-13
---

# Source: Подсистемы, сервисы, базовые сущности и их взаимосвязи

**Source URL:** https://online.sbis.ru/page/knowledge-bases/694fcc5c-abd7-4c2b-9c9b-761e1fdc92fb
**Date captured:** 2026-04-13
**Section:** wasaby.Backend / Платформенный механизм кэширования отчетов (report-prefetch-service) / Техническая документация

## Summary

Техническое описание архитектуры сервиса `report-prefetch-service` — платформенного механизма кэширования отчётов. Описывает два основных сценария взаимодействия, порядок выполнения `Prefetch.List`, конвейер обработки отчётов и структуру индексов.

## Pages Created

- [[Report-Prefetch-Service]] — полная архитектура: сценарии, конвейер обработки (9 узлов), индексы, ключевые методы

## Key Insights

- Кэширование отчётов двухэтапное: создание сессии → разбиение большого отчёта на страницы → сохранение в БД сервиса
- Конвейер обработки строится динамически по фильтру запроса; каждый обработчик удаляет из фильтра «свои» поля
- Индекс — отсортированный срез 1+ столбцов отчёта с адресами строк полного отчёта; разбивается на главы при достижении порогового размера
