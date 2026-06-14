---
type: source
title: "Wasaby BL List Advanced Patterns"
source_files:
  - "raw/Навигация по курсору.md"
  - "raw/Множественная навигация в списочных контролах.md"
  - "raw/Порционная загрузка данных.md"
  - "raw/Массовая отметка записей.md"
  - "raw/Показать отмеченные.md"
  - "raw/Как перенести записи, подпадающие под условия фильтрации, в указанную папку.md"
  - "raw/Суммировать.md"
  - "raw/Стандартные параметры фильтрации списочного метода.md"
  - "raw/Как сделать поиск с учетом неверной раскладки клавиатуры пользователя.md"
  - "raw/Как в результатах поиска по реестру построить хлебные крошки.md"
ingested: 2026-04-14
tags:
  - wasaby
  - list-methods
  - navigation
  - mass-operations
status: ingested
related:
  - "[[Wasaby-BL-List-Advanced]]"
  - "[[Wasaby-BL-List-Methods]]"
created: 2026-04-14
updated: 2026-04-14
---

# Source: Wasaby BL List Advanced Patterns

10 документов из Wasaby Backend Knowledge Base (link.sbis.ru), раздел «Работа со списками», декабрь 2025.

## Темы

**Навигация:**
- [[Wasaby-BL-List-Advanced#Навигация по курсору]] — механизм, индексы, 3 направления, nextPosition
- [[Wasaby-BL-List-Advanced#Множественная навигация (Multi-Root Navigation)]] — иерархические списки с развёрнутыми узлами
- [[Wasaby-BL-List-Advanced#Порционная загрузка данных]] — iterative flag + nextPosition в метаданных

**Массовые операции:**
- [[Wasaby-BL-List-Advanced#Массовая отметка записей (ListIterator)]] — ListIterator, selection, алгоритм обхода
- [[Wasaby-BL-List-Advanced#Показать отмеченные (ShowMarked)]] — ShowMarked с путями для хлебных крошек
- [[Wasaby-BL-List-Advanced#Перенос записей в папку (MoveToFolder)]] — blhelpers.MoveToFolder
- [[Wasaby-BL-List-Advanced#Суммирование (Sum.ByMethod)]] — DWC-итерации, 30 сек/итерация

**Фильтрация и поиск:**
- [[Wasaby-BL-List-Advanced#Стандартные параметры фильтрации]] — ИдО / СписокИдО / Раздел
- [[Wasaby-BL-List-Advanced#Поиск с учётом неверной раскладки (TranslitListCall)]] — 5 раскладок, switchedStr
- [[Wasaby-BL-List-Advanced#Хлебные крошки в иерархическом поиске (ListWithParents)]] — CoreUtils.ListWithParents

## Ключевой инсайт

Курсорная навигация — основа для 4 из 10 паттернов: порционная загрузка, ShowMarked, ListIterator (рекомендуется), Sum.ByMethod. Декларативный метод поддерживает ИдО/СписокИдО/Раздел из коробки.
