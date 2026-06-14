---
type: source
title: "SBIS API Reference — sbis-mcp project"
address: c-000027
source_path: "C:/Users/aa.timoshenko/PycharmProjects/sbis-mcp/docs/sbis-api.md"
ingested: 2026-05-21
tags:
  - saby
  - api
  - source
  - json-rpc
status: ingested
related:
  - "[[SBIS-Record-Format]]"
  - "[[SBIS-Internal-API-Methods]]"
  - "[[Saby-External-API-Auth]]"
  - "[[Saby-External-API-Tasks]]"
  - "[[Saby-API-Error-Codes]]"
created: 2026-05-21
updated: 2026-05-21
---

# SBIS API Reference — sbis-mcp project

Файл `docs/sbis-api.md` из проекта `sbis-mcp`. Документ выведен из анализа сетевых логов SBIS (`.sbislog`) и описывает транспорт, форматы данных и известные API-методы.

## Что охвачено

- JSON-RPC 2.0 транспорт (auth + service endpoints)
- Колоночный Record/Recordset формат (`f`/`d`/`s`) → [[SBIS-Record-Format]]
- Стандартные параметры листовых методов (Фильтр, Навигация как record-объекты)
- Паттерн `ПрочитатьДляУчастника`
- Внутренние методы: `ПунктПлана`, `СлужЗап`, `Документ`, `Проект` → [[SBIS-Internal-API-Methods]]
- Поля фильтра и ответа `ПунктПлана.СписокПунктов` (10 фильтр-полей, 93+ поля ответа)
- Поля фильтра `СлужЗап.СписокПодзадач` (13 полей)

## Контекст

Документ создан как часть проекта `sbis-mcp` — MCP-сервера для работы с задачами SBIS. Связан с [[Saby-External-API-Auth]] и [[Saby-External-API-Tasks]] (документация того же API с другого угла: внутренний vs внешний).