---
type: source
title: "Как разрабатывать в Retail/Presto-offline [2025] + диалог о подмене модулей"
address: c-000075
source_url: "https://dev.sbis.ru/news/3fc144de-9554-4919-a223-400cd26fe274"
created: 2026-06-11
ingested: 2026-06-11
tags:
  - retail
  - presto
  - offline
  - development
  - clippings
status: current
related:
  - "[[RetailPresto-Offline-Debug-Setup]]"
  - "[[Wasaby-Module-System]]"
  - "[[Алябушев-Александр-Александрович]]"
---

# Источник: Offline Dev Setup

Два связанных клиппинга на одну тему: новость dev.sbis.ru и подтверждающий диалог.

## Файлы источника

- `.raw/Как разрабатывать в RetailPresto-offline 2025.md`
- `.raw/Просмотр диалога по инструкции с подменой модулей.md`

## Ключевые факты

1. До v25.6218: подмена файлов и перезапуск работала напрямую.
2. С v25.6218: ресурсы предкомпилируются → нужен обходной путь через `MainService.s3srv` + `sbis-config.ini`.
3. Только Debug-версия: Release имеет скомпилированные `.s3mod` в бинарники.
4. Пути данных: `C:\ProgramData\Saby Retail` / `C:\ProgramData\Saby Presto`.
5. При добавлении новых файлов: удалить `service\files.index`, `service\folders.index`.

## Участники обсуждения

- **Ушаков Тимофей** — автор статьи (17.02.2025)
- **Козлобродов Илья** — добавил обновление для v25.6218 (06.08.2025)
- **[[Алябушев-Александр-Александрович]]** — отметил, что за 3 года мало что поменялось; уточнил про Debug-версию
- **Михайленко Елена** — предоставила рабочий алгоритм подмены

## Концепт

→ [[RetailPresto-Offline-Debug-Setup]]
