---
type: source
title: "Price Formation Docs (docs/ folder)"
source_path: "C:/Users/aa.timoshenko/PycharmProjects/price-formation/docs/"
ingested: 2026-04-10
tags:
  - source
  - price-formation
  - wasaby
  - sbis
status: current
related:
  - "[[price-formation/_index]]"
  - "[[Wasaby-Framework]]"
  - "[[Multitenancy-Architecture]]"
  - "[[DWC-Distributed-Workflow-Coordinator]]"
  - "[[Sync-Broker]]"
  - "[[Python-Code-Standards-SBIS]]"
  - "[[Python-Localization-rk]]"
  - "[[ReferralProgram-Module]]"
created: 2026-04-10
updated: 2026-04-10
---

# Price Formation Docs Ingest (2026-04-10)

12 files from `docs/` in the `price-formation` project.

---

## Files Processed

### prompts/

| File | Pages Created |
|------|--------------|
| `code_standarts.md` | [[Python-Code-Standards-SBIS]] |
| `referral_program.md` | [[ReferralProgram-Module]] |

### projects/

| File | Pages Created |
|------|--------------|
| `Рефералка в Заявках в банк на РКО по API/Техническое задание.md` | [[ReferralProgram-Module]] (extended with SabyBank TZ) |

### wasaby/architecture/

| File | Pages Created |
|------|--------------|
| `Архитектура.md` | [[Wasaby-Framework]] |
| `Архитектура multitenancy-приложения.md` | [[Multitenancy-Architecture]] |
| `Архитектура облака.md` | [[Wasaby-Framework]] (cloud section) |
| `Описание схемы дистрибутивов...md` | [[Wasaby-Framework]] (distributions section) |
| `Сервистные модули.md` | [[Wasaby-Framework]] (service modules section) |
| `Структура проекта приложения.md` | [[Wasaby-Framework]] (project structure section) |

### wasaby/wasabyBackend/

| File | Pages Created |
|------|--------------|
| `Middleware/Сервис DWC/Сервис DWC.md` | [[DWC-Distributed-Workflow-Coordinator]] |
| `Брокер синхронизации/README.md` | [[Sync-Broker]] |
| `Локализация Python/README.md` | [[Python-Localization-rk]] |

---

## Key Insights

1. Wasaby uses 3-level project structure: s3cld (app) / s3srv (service) / s3mod (module)
2. Multitenancy isolation: 1 client = 1 PostgreSQL schema; cross-client FK is forbidden
3. ReferralProgram module is distinct from `loyaltyprograms/referralbonus` - completely separate
4. SyncBrokerClient is a process singleton - concurrent Sync() calls cause state races
5. `rk()` function must not wrap static class variables - translation computed only once