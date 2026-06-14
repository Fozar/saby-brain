---
type: session
title: "DWC Promocode Events Migration"
created: 2026-04-10
updated: 2026-04-10
tags:
  - dwc
  - promocode
  - migration
  - price-formation
  - events
status: developing
related:
  - "[[DWC-Migration-SDK]]"
  - "[[Promocode-Subsystem-Overview]]"
  - "[[DWC-Distributed-Workflow-Coordinator]]"
  - "[[DWC-Client-Library-v1]]"
  - "[[LRS-Long-Request-Service]]"
---

# DWC Promocode Events Migration

Реализация этапа «Перевод событий по промокодам на DWC» в рамках проекта [[DWC-Migration-SDK]].

Ответственный: [[Тимошенко А.А.]] Ветка: `rc-26.3100`.

---

## Текст задачи

> Перевод событий по промокодам на DWC
>
> В рамках проекта «Использование DWC вместо событий между онлайном и сервисом ДК» перевести 4 события по экземплярам промокодов с `event.Publish` на DWC-задачи.
>
> **Цели:**
> - Устранить очереди при массовых изменениях
> - Гарантировать порядок обработки
> - Управлять нагрузкой на сервис ДК
>
> **Реализовать:**
> 1. Feature flag `dwc_promocode` в класс `Feature` (`priceformationcommon/helpers/feature.py`)
> 2. 4 DWC-сценария в `LoyaltyPrograms.dwc`:
>    - `Promocode.HandleChangeData` — изменение данных экземпляра
>    - `Promocode.HandleDelete` — удаление экземпляров
>    - `Promocode.HandleApply` — применение промокода на продаже
>    - `Promocode.HandleUnapply` — отмена применения промокода
> 3. Публичные функции публикации в DWC в `core.py`
> 4. Переключение всех точек `event.Publish` на DWC при включённом feature flag
>
> **Критерий приёмки:** нет регрессии + при недоступности ДК во время изменения лимита — лимит обновляется при восстановлении сервиса.

---

## Контекст

Этап «Выпуски промокодов» (2 события: `PromocodeType.HandleChangeData`, `PromocodeType.HandleDelete`) уже выполнен к началу этой сессии. Реализованный образец в `core.py` и `LoyaltyPrograms.dwc` используется как основа.

4 события по **экземплярам** промокодов (не типам):

| Старое событие | DWC-сценарий | Приоритет |
|---|---|---|
| `online.loyalty-system.promocode-data.changed` | `Promocode.HandleChangeData` | High |
| `online.loyalty-system.promocode.deleted` | `Promocode.HandleDelete` | High |
| `online.loyalty-system.promocode.applied` | `Promocode.HandleApply` | High |
| `online.loyalty-system.promocode.unapplied` | `Promocode.HandleUnapply` | High |

---

## Реализация

### Архитектурный паттерн

Каждая публичная функция публикации (`publish_promocode_data_changed`, `publish_promocode_deleted`) проверяет feature flag `DWC_PROMOCODE`:
- При **включённом** флаге → создаёт DWC workflow через `workflow2.WorkflowBuilder`
- При **выключенном** → публикует событие через `event.Publish` (поведение идентично прежнему)

Для событий с несколькими записями (changed, apply, unapply) — одна задача на запись в одном сценарии. Для deleted — одна задача с массивом ID.

### Изменённые файлы

**1. `priceformationcommon/helpers/feature.py`**
```python
DWC_PROMOCODE = 'dwc_promocode'  # добавлено после DWC_PROMOCODE_TYPE
```

**2. `PriceFormation.Online/LoyaltyPrograms.dwc`**
Добавлены 4 workflow с параметрами: `application_area="warehouse"`, `kind="lrs"`, `limit_key_template="%1%"`, `limit_value="1"`, responsible = [[Тимошенко А.А.]]

**3. `priceformationonline/loyaltyprograms/promocode/core.py`**
- Добавлена `publish_promocode_data_changed(changes)` — публичная функция с feature flag
- Добавлена `_send_promocode_data_changes_via_dwc(changes)` — DWC-отправитель
- Добавлена `publish_promocode_deleted(card_id_list)` — публичная функция с feature flag
- Добавлена `_send_promocode_delete_via_dwc(data)` — DWC-отправитель
- `PromoCodeData.notify_on_card_change` → вызывает `publish_promocode_data_changed()`
- `PromoCodeData.notify_on_card_delete` → вызывает `publish_promocode_deleted()`
- `notify_promocode_data_changed` → использует `publish_promocode_data_changed()` в батчах

**4. `priceformationonline/loyaltyprograms/promocode/notify.py`**
- Добавлены `_send_promo_code_applied_via_dwc(data)` и `_send_promo_code_unapplied_via_dwc(data)`
- `notify_promo_code_applied` и `notify_promo_code_unapplied` переключены на DWC при включённом флаге

**5–9. Остальные файлы** — заменили прямые `event.Publish` на вызовы публичных функций:
- `promocode/safe_delete_core.py` → `publish_promocode_deleted()`
- `partner_promo_code/safe_delete.py` → `publish_promocode_deleted()`
- `individual_promo_code_emission/delete.py` → `publish_promocode_deleted()`
- `individual_promo_code_emission/safe_delete.py` → `publish_promocode_deleted()`
- `individual_promo_code_emission/core.py` → `publish_promocode_data_changed()`
- `activity_promo_code/core.py` → `publish_promocode_data_changed()`

---

## Важные заметки

- **Семантическая путаница applied/unapplied**: вики предупреждала об этом. При тестировании уточнить у ДК правильность маппинга `applied` → `HandleApply` и `unapplied` → `HandleUnapply`.
- **`notify_promo_code_applied`/`unapplied`** вызываются асинхронно через `sbis.BLObject('PromoCode').AsyncInvoke('AsyncHandle', ...)` после коммита транзакции — `workflow2.Sender().Commit(ppIMMEDIATELY)` корректно работает в этом контексте.
- Feature flag `dwc_promocode` — отдельный от `dwc_promocode_type`. Выкатка под флагом запланирована на 30.05.2026.

---

## Даты проекта (из [[DWC-Migration-SDK]])

| Milestone | Дата |
|---|---|
| Разработка завершена | 30.04.2026 |
| Тестирование | 30.04 – 16.05.2026 |
| Выкатка под feature flag | 30.05.2026 |
| Выкатка на всех | 30.06.2026 |
| Полный финал | 30.07.2026 |