---
type: session
title: "DWC BonusSettings Events Migration"
created: 2026-04-12
updated: 2026-04-12
tags:
  - dwc
  - bonus-settings
  - migration
  - price-formation
  - events
status: developing
related:
  - "[[DWC-Migration-SDK]]"
  - "[[DWC-Promocode-Events-Migration]]"
  - "[[DWC-Distributed-Workflow-Coordinator]]"
  - "[[Bonus-Programs-Architecture]]"
---

# DWC BonusSettings Events Migration

Реализация этапа «Настройки бонусов» в рамках проекта [[DWC-Migration-SDK]].

Ответственный: [[Тимошенко А.А.]] Ветка: `rc-26.3100`.

---

## Текст задачи

> **Перевод событий по настройкам бонусов на DWC**
>
> В рамках проекта «Использование DWC вместо событий между онлайном и сервисом ДК» перевести 2 события по настройкам бонусов:
>
> 1. `online.loyalty-system.holidays.changed` → DWC-задача `BonusSettings.HandleChangeHolidaySettings` (приоритет: средний)
> 2. `online.loyalty-system.promotion.enabled` → DWC-задача `BonusSettings.HandleChangePromotionSettings` (приоритет: средний)
>
> **Критерий приёмки:** нет регрессии; при включённом флаге оба события не отправляются, DWC-задачи ставятся корректно.

---

## Карта событий → DWC

| Событие | DWC-сценарий | Приоритет | Источник в Онлайне |
|---|---|---|---|
| `online.loyalty-system.holidays.changed` | `BonusSettings.HandleChangeHolidaySettings` | Средний (50) | `bonus/crud/notify_sdk.py` → `notify_sdk()` |
| `online.loyalty-system.promotion.enabled` | `BonusSettings.HandleChangePromotionSettings` | Средний (50) | `promotion/has_available.py` → `_notify_loyalty_is_on()` |

---

## Реализация

### Feature flag

`DWC_BONUS_SETTINGS = 'dwc_bonus_settings'` добавлен в класс `Feature` (`priceformationcommon/helpers/feature.py`), после `DWC_PROMOCODE_TYPE`.

### DWC-сценарии (`LoyaltyPrograms.dwc`)

Два новых workflow с параметрами: `application_area="warehouse"`, `kind="lrs"`, `limit_key_template="%1%"`, `limit_value="1"`, `merge_policy="none"`, `error_policy="abort"`.

- `BonusSettings.HandleChangeHolidaySettings` — task → `service="discount-cards"`, args: `{ClientID, HolidayEnabled}`
- `BonusSettings.HandleChangePromotionSettings` — task → `service="discount-cards"`, args: `{ClientID, LoyaltyEnabled}`

### `bonus/crud/notify_sdk.py`

`notify_sdk()` переключается по флагу:
- **ON**: `_send_holiday_settings_via_dwc(holiday_enabled)` — `WorkflowBuilder('BonusSettings.HandleChangeHolidaySettings').SetLimitKeyArgs(ClientID)`, `task.priority = 50`
- **OFF**: `event.Publish('online.loyalty-system.holidays.changed', ...)`

`client_id = sbis.Session.ClientID()` вынесен в переменную в DWC-функции (паттерн линтера).

### `promotion/has_available.py`

Блок `if _has_available:` переключается по флагу:
- **ON**: `_send_promotion_settings_via_dwc()` — аналогичный паттерн WorkflowBuilder
- **OFF**: `_notify_loyalty_is_on()` (старая функция остаётся)

---

## Паттерн DWC (средний приоритет)

```python
def _send_xxx_via_dwc(...) -> None:
    client_id = sbis.Session.ClientID()
    data = create_record_with_format([...])
    workflow_builder = (
        workflow2.WorkflowBuilder('BonusSettings.HandleChangeXxx')
        .SetLimitKeyArgs(str(client_id))
        .Build()
    )
    task = workflow_builder.CreateTask('HandleChangeXxx')
    task.priority = 50  # средний приоритет
    task.SetMethodArgs(data)
    workflow_builder.AddTask(task)
    workflow2.Sender().AddWorkflow(workflow_builder).Commit(sbis.PublicationPolicy.ppIMMEDIATELY)
```

Ключ лимита = `ClientID` → 1 воркер СДК на клиента (средний приоритет: DB load < 85%).

---

## Изменённые файлы

| Файл | Изменение |
|---|---|
| `PriceFormation.Common/priceformationcommon/helpers/feature.py` | +`DWC_BONUS_SETTINGS` |
| `PriceFormation.Online/LoyaltyPrograms.dwc` | +2 workflow |
| `PriceFormation.Online/priceformationonline/loyaltyprograms/bonus/crud/notify_sdk.py` | event → DWC |
| `PriceFormation.Online/priceformationonline/loyaltyprograms/promotion/has_available.py` | event → DWC |