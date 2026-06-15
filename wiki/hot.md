---
type: meta
title: "Hot Cache"
updated: 2026-06-15
tags:
  - meta
  - hot-cache
status: evergreen
related:
  - "[[index]]"
  - "[[log]]"
  - "[[overview]]"
---

# Recent Context

## 2026-06-15 — Линт + калибровка тайлинга

- Создан `scripts/detect-transport.py` (Python-замена для отсутствовавшего .sh)
- Исправлена коллизия `c-000105`: Wasaby-BL-Async-Sync-Cloud-Calls удалён, уникальный контент влит в [[Wasaby-BL-AsyncInvoke]]
- Добавлены перекрёстные ссылки: DWC, LRS, Profiles, Sync-Broker (4 пары)
- 14 orphan-страниц добавлены в index.md; 3 мёртвые ссылки исправлены
- **Слияние**: [[Async-Calls-Bus]] → [[Wasaby-MQ]] (контент поглощён; входящие ссылки переключены; исходный файл ожидает удаления — нужно разрешение)
- Тайлинг откалиброван: 114 пар размечено, истинных дублей 0; пороги 0.90/0.80 → **0.95/0.92**; Error: 114 → 6, Review: 5117 → 35

## 2026-06-14 — wasaby.Backend batch ЗАВЕРШЁН (c-000105..c-000142, 38 страниц)

| Категория | Страницы |
|---|---|
| Стандарты | [[Wasaby-Dev-Standards]], [[Wasaby-SQL-Standard]], [[Wasaby-Python-Standard]], [[Wasaby-Cpp-String-Standard]] |
| Фреймворк | [[Wasaby-Service-Framework]], [[Wasaby-BL-Calls]], [[Wasaby-BL-Objects]], [[Wasaby-Service-Node-Architecture]] |
| Тестирование/Отладка | [[Wasaby-Unit-Testing]], [[Wasaby-Memray]], [[Wasaby-Perforator]], [[Wasaby-Python-Debug]] |
| БД/Хранилища | [[Wasaby-SQL-DBA]], [[Wasaby-ClickHouse]], [[Wasaby-FTS]], [[Wasaby-File-Transfer]] |
| Async/Очереди | [[Wasaby-MQ]], [[Wasaby-Request-Broker]], [[Wasaby-Scheduler]], [[Wasaby-DWC]], [[Wasaby-Long-Running-Operations]], [[Wasaby-Task-Queue]], [[Wasaby-Mass-Mailings]] |
| Middleware | [[Wasaby-Report-Prefetch]], [[Wasaby-HTML-Converter]], [[Wasaby-Informers]], [[Wasaby-Multimedia-Loader]], [[Wasaby-PDF-Transformer]], [[Wasaby-Image-Service]] |
| Инфра/Прочее | [[Wasaby-i18n]], [[Wasaby-Third-Party-Libraries]], [[Wasaby-Parameters-Service]], [[Wasaby-Distributed-Locks]], [[Wasaby-History-Service]], [[Wasaby-Profiles-Service]] |
| Клиентские события | [[Wasaby-STOMP]], [[Wasaby-Sync-Broker]] |
| C++ инфра | [[Wasaby-Conan]] |

**Важные заметки:**
- `PyCharm` для отладки: максимальная версия **2022.3.3**
- `Prefetch.List`: **PrefetchPreSort обязателен** для иерархических отчётов
- `distributed-locks`: `ResourceId` не включает account/user — добавлять самому
- `delayedPrint=true` в HTML-конвертере: JS должен вызывать `window.tensor.waitPrint()` каждые ≤5с

История предыдущих сессий (июнь 2026) — [[log]].

---

## Price Formation Domain

SBIS/Saby loyalty + price formation, ветка `rc-26.3211`.
- Wasaby: 3-level (s3cld/s3srv/s3mod), JSON-RPC, declarative resources
- DB: `ВидЦеныДокумент` (события лояльности), `Карта` (ДК/промокод)
- DWC: `workflow2`. Python: 120 chars, CamelCase ok, no wildcard imports

## Active Threads

- **Loyalty Desktop Broker Migration**: [[Loyalty-Desktop-Broker-Migration]] — feature flag `lty_broker_card_type`, ~60д
- **SabyBank RKO Referral**: [[SabyBank-RKO-Referral]] — релиз 18.08.2026

---

Navigation: [[index]] | [[log]] | [[overview]]
