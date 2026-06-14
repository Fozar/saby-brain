---
type: concept
title: "Loyalty Cloud Config & Scheduler"
updated: 2026-04-10
tags:
  - loyalty
  - cloud
  - scheduler
  - dcservice
  - price-formation
status: current
related:
  - "[[Loyalty-Public-API]]"
  - "[[Wasaby-Framework]]"
  - "[[price-formation/_index]]"
created: 2026-04-10
---

# Loyalty Cloud Config & Scheduler

Cloud parameters and scheduler tasks for the Discount Card Service (Сервис дисконтных карт, СДК).

---

## Cloud Parameters (DCService)

### Anti-bot Security

| Parameter | Description |
|---|---|
| `Безопасность.Антибот.ВремяБлокировки` | Block duration in seconds. Timer resets on each call attempt. Captcha can unblock. |
| `Безопасность.Антибот.МаксимальноеЧислоВызовов` | Max calls within period before blocking |
| `Безопасность.Антибот.Период` | Time window in seconds for call counting |
| `Безопасность.Антибот.Ключ` | Check key: IP or UserID |
| `Безопасность.Антибот.НастройкиДляМетодов` | Per-method fine-tuning (JSON array) |

Per-method config format:
```json
[
  {
    "method": "SAP.Authenticate:2",
    "max_call": 5,
    "interval": 60,
    "lock_time": 300
  }
]
```

### Logging & Access

| Parameter | Description |
|---|---|
| `Ядро.Логирование.ЗаголовкиЗапросов` | Enable request header logging in `invoke.log` |
| `Ядро.Права.Проверять` | Enable user permission checks |

---

## Scheduler Tasks

| Task name | Description | BL Method |
|---|---|---|
| `AccrueHolidayBonus` | Accrue holiday/event bonuses | `BonusSettings.AccrueHolidayBonus` |
| `DCService Vacuum Cleaner` | Run VACUUM ANALYZE on Operation table | `BonusOperation.VacuumCleaner` |
| `SendBonusExpirationNotifications` | Send expiring bonus notifications to clients | `Card.NotifyExpiringBonuses` |
| `RequestCardsDataFromOnline` | Pull card data from online service | `Card.RequestDataFromOnline` |

---

## Service Update Strategy

DCService cannot use master-replica updates because the service handles external requests and writes to pass-updater tables (queue additions and status updates). Master-replica mode makes the DB read-only during update.

**Solution**: Use light update (лёгкое обновление) or light conversion (лёгкая конвертация) when no DB changes are required.

- Use Хоттабыч "Анализ изменения БД" report to assess if light conversion is safe
- Non-light-compatible changes → use ВНР (deployment code via Genie "Deployment code" tab)
- Minimize DB object locks during ВНР to avoid user impact
