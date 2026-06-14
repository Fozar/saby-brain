---
type: source
title: "Wasaby BL Documentation Batch"
date: 2026-04-10
tags:
  - wasaby
  - business-logic
  - source
status: ingested
created: 2026-04-10
updated: 2026-04-10
---

# Wasaby BL Documentation Batch

**Date:** 2026-04-10
**Sources:** 37 docs from `raw/` — Wasaby Framework service contract documentation

## Summary

Полная документация по сервисному фреймворку Wasaby: объекты БЛ, все типы методов (CRUD/список/файлы/удалённые/произвольные), обработчики, кэширование, таймауты, защита от частых вызовов, область видимости, паттерны Python.

## Pages Created

- [[Wasaby-BL-Objects]] — BL объекты, справочник объектов, сервис контракт, черновики, взаимодействие с БД (pgBouncer, пул соединений, SelectCurrentDB), справочник задач планировщика
- [[Wasaby-BL-Methods]] — таксономия методов, доступность (Service Contract / Internal), наследование, перекрытие по имени
- [[Wasaby-BL-CRUD]] — Create/Read/Update/Delete/Copy/Merge/DeleteSelected/Sync; сигнатуры, поведение, обработчики
- [[Wasaby-BL-List-Methods]] — декларативный и ручной список; параметры ДопПоля/Фильтр/Сортировка/Навигация; типы фильтра (Free/Linked/Hierarchical); лимиты безопасности
- [[Wasaby-BL-Advanced]] — кэширование, таймауты (Call/Execution), Antibot (Frequent call protection), область видимости, обработчики (все типы), Custom method, конфиденциальные данные, удалённые вызовы (Proxy/HTTP), методы работы с файлами
- [[Wasaby-Python-Patterns]] — sbis.Error / sbis.Warning; `with CreateTransaction`; работа с файлами

## Pages Updated

- (none — новые страницы)

## Key Insights

- Списочные методы без навигации — DoS-уязвимость; max лимит с клиента = 100 записей
- `CreateTransaction` без `with` — устарело, логируется как ошибка
- Sync метод устарел — заменяется отдельными вызовами Create/Update/Delete
- Автогенерируемые методы имеют приоритет над Custom при совпадении имён
- Antibot хранит данные в Redis: ключ живёт `Check interval * 2` секунд
