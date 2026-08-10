---
type: concept
address: c-000004
title: "DWC-Card-Events-Migration"
created: 2026-05-13
updated: 2026-08-10
tags:
  - dwc
  - discount-card
  - migration
  - loyalty
status: developing
related:
  - "[[DWC-Distributed-Workflow-Coordinator]]"
  - "[[DWC-Migration-SDK]]"
  - "[[DWC-BonusSettings-Events-Migration]]"
  - "[[DWC-Promocode-Events-Migration]]"
  - "[[DiscountCard-Subsystem-Overview]]"
  - "[[Saby-Feature-Toggles-API]]"
  - "[[Loyalty-Events-External-Consumers]]"
---

# DWC-Card-Events-Migration

Миграция событий карты лояльности с STOMP-событий на DWC-сценарии. Feature flag: `dwc_card`.
Цель — один DWC-обработчик `Card.HandleChangeData` вместо события `online.loyalty-card.card-data.changed`.
`notify_card_data_changed` принимает любое подмножество данных карты — и для общих изменений, и для изменений баланса бонусов.

**Архитектурное решение (2026-05-27):** Отдельный обработчик `Card.HandleChangeBonusBalance` был удалён по итогам ревью.
`notify_bonus_balance_changed` делегирует в `notify_card_data_changed` (и всегда делал это в не-DWC пути).
Семантика изменения баланса сохраняется на уровне Python-функции, не DWC-сценария.

---

## Rollout: массовое включение не запланировано (2026-07-28)

Источник: [[dwc-card-events-rollout-status-2026-07-28]]

Поручение от 03.07.26 («включить фичу на всех») по состоянию на 2026-07-28 **не поставлено в план работ**. [[Тимошенко А.А.|Тимошенко]] спрашивает Омельяненко Е. про срок, предполагая перенос на август — ответа на момент захвата нет. Флаг `dwc_card` остаётся выключенным по умолчанию вне явно включённых стендов/аккаунтов.

> [!gap] Возможная связь с флаки-автотестами ДК
> [[DiscountCardType-Settings-Async-Load-Flaky-Autotest]] фиксирует ожидание команды тестирования, что этот DWC-переход устранит асинхронность между созданием типа ДК и готовностью данных настроек — на практике (2026-07-29) флаки сохраняется. Не выяснено, включён ли `dwc_card` на затронутом тестовом стенде.

## Забытые сценарии — задача №08106197 (2026-08-10)

Регламент «Ошибка», ветка `26.4200/bugfix/aatimoshenko/08106197` от `rc-26.4200`.

Первая волна миграции покрыла только «профильные» точки в `loyaltycard/notify.py` и `personalcard/merge.py`. Два публикующих места остались на событиях, потому что живут **вне** пакета `discountcard/loyaltycard` и при обходе кода не попались:

| Забытая точка | Событие | Переведена на |
|---------------|---------|---------------|
| `dcservice/servicediscountcard/notify_changed.py` → `async_notify_changed_cards` | `online.loyalty-card.card-data.changed` | `Card.HandleChangeData` |
| `loyaltyprograms/bonus/notify_sabyget.py` → `BonusOperationEventQueue.publish` | `discount-cards.bonusoperation.online` | `Card.HandleChangeBonusBalance` |

Урок: искать публикацию надо **по имени события через grep по всему репозиторию**, а не по пакетам предметной области. `async_notify_changed_cards` вызывается из ~10 мест (создание/изменение/выдача карты, импорт карт и персональных карт, смена персоны, вступление в ПЛ, объединение частных лиц, удаление клиента).

> [!note] `Card.HandleChangeBonusBalance` вернулся, но в другой роли
> Сценарий, удалённый в rc-26.4100, обслуживал `notify_bonus_balance_changed` (изменение баланса карты) — там делегирование в `Card.HandleChangeData` осталось. Новый одноимённый сценарий обслуживает **поток бонусных операций** из `notify_sabyget` (метод СДК `Card.HandleChangeBonusBalance` существовал всегда — это обработчик события `discount-cards.bonusoperation.online`, `Online.orx:513`).

### Батчинг снимается при переходе на DWC

Событийный путь бьёт операции пачками по 50 — это ограничение размера сообщения шины. При DWC батчинг **убран**: сценарий объявлен с `one_task="1"` и `limit_key_template="%1%"` (ключ = ClientID), поэтому несколько задач подряд для одного клиента конфликтовали бы по ключу ограничения. Ставится одна задача на весь RecordSet.

```python
if check_feature(Feature.DWC_CARD):
    # Задача ставится одна на все операции: батчи нужны только для ограничения размера сообщения шины.
    send_changes_via_dwc(event_data, 'Card.HandleChangeBonusBalance', 'HandleChangeBonusBalance')
else:
    batch_size = 50
    ...
```

Тот же подход в `notify_card_data_changed`: параметр `batch_size` при включённом флаге игнорируется.

---

## Статус (2026-08-10)

| Сценарий | Статус | Источник |
|----------|--------|---------|
| `Card.HandleChangeData` | ✅ реализован | `notify_card_data_changed` (все изменения данных, включая бонусы) |
| `Card.HandleChangeData` (забытая точка) | ✅ 08106197 | `dcservice/.../notify_changed.py` → `async_notify_changed_cards` |
| `Card.HandleDelete` | ✅ реализован | `notify_card_deleted` |
| `Card.HandleMerge` | ✅ реализован | `personalcard/merge.py` → `_notify_loyalty_card_merged` |
| `Card.HandleChangeBonusBalance` | ✅ 08106197 | `notify_sabyget.py` → `BonusOperationEventQueue.publish` |
| ~~`Card.HandleChangeBonusBalance` (старый)~~ | ~~удалён~~ | был `notify_bonus_balance_changed`, убран в rc-26.4100 |

---

## Feature Flag

`dwc_card` — объявлен в `PriceFormation.feature`, класс `Feature.DWC_CARD` в
`priceformationcommon/helpers/feature.py`. Один флаг покрывает все Card-сценарии.

---

## Реализованные сценарии

### Card.HandleChangeData

**DWC-workflow:** `DiscountCard.dwc`  
**Точка входа:** `loyaltycard/notify.py` → `notify_card_data_changed`  
**Ветка (строка 68):**
```python
if check_feature(Feature.DWC_CARD):
    send_changes_via_dwc(changes, 'Card.HandleChangeData', 'HandleChangeData')
    return
```
Без флага публикует событие `online.loyalty-card.card-data.changed`.

Данные перед отправкой: добавляется поле `ClientID`, переименовываются `CardId→CardID` и `LastSaleId→LastSaleID`.

### notify_bonus_balance_changed → Card.HandleChangeData

`notify_bonus_balance_changed` запрашивает данные только по `['Card', 'Bonus']` и делегирует в `notify_card_data_changed`:

```python
changes = get_card_data(card_id_list, ['Card', 'Bonus'], ...)
if not changes:
    return
notify_card_data_changed(changes, batch_size)
```

`notify_card_data_changed` сама решает — событие или DWC. Таким образом, изменения баланса
идут через `Card.HandleChangeData`, как и любые другие изменения карты.

**Тест:** `NotifyBonusBalanceChanged.test_calls_notify_card_data_changed` — мокирует
`notify_card_data_changed` и проверяет вызов с `(changes, 400)`.

### Card.HandleMerge

**DWC-workflow:** `DiscountCard.dwc`  
**Точка входа:** `personalcard/merge.py` → `_notify_loyalty_card_merged`  
**Ветка:**
```python
if check_feature(Feature.DWC_CARD):
    send_changes_via_dwc(data, 'Card.HandleMerge', 'HandleMerge')
else:
    event.Publish('online.loyalty-card.card.merged', data, event.Visibility.evSERVER_ONLY)
```

Данные: `sbis.Record` с полями `SourceCardID` (ftINT32), `TargetCard` (ftRECORD, результат `get_card_partial_info`), `ClientID` (ftINT32).  
Тесты: `tests/.../personalcard/merge.py`, класс `NotifyLoyaltyCardMerged`.

**Заметка о `task.priority`:** `send_changes_via_dwc` не выставляет приоритет задачи. Для явного низкого приоритета нужен inline-диспатч с `task.priority = 100` (по аналогии с промокодами, где `task.priority = 50` = нормальный). Пока реализовано через `send_changes_via_dwc` — уточнить у автора задачи нужное значение.

---

## Общий паттерн DWC-вызова

Используется `send_changes_via_dwc` из `loyaltycardtype/notify.py`:

```python
def send_changes_via_dwc(changes, workflow_name, task_name, limit_key_args=None):
    limit_key_args = limit_key_args or (str(sbis.Session.ClientID()),)
    workflow_builder = (
        workflow2.WorkflowBuilder(workflow_name)
        .SetLimitKeyArgs(*limit_key_args)
        .Build()
    )
    task = workflow_builder.CreateTask(task_name)
    task.SetMethodArgs(changes)
    workflow_builder.AddTask(task)
    workflow2.Sender().AddWorkflow(workflow_builder).Commit(sbis.PublicationPolicy.ppIMMEDIATELY)
```

Параметры DWC workflow (из `DiscountCard.dwc`):
- `kind="lrs"`, `error_policy="abort"`, `merge_policy="none"`
- `limit_key_template="%1%"` (client ID), `limit_value="1"`
- `service="discount-cards"`

---

## Тесты

Тесты в `tests/tests_priceformationonline/discountcard/loyaltycard/notify.py`:

| Класс | Тест | Что проверяет |
|-------|------|---------------|
| `NotifyCardDataChanged` | `test_event` | флаг выкл → публикует событие |
| `NotifyCardDataChanged` | `test_dwc` | флаг вкл → `send_changes_via_dwc('Card.HandleChangeData', ...)` |
| `NotifyBonusBalanceChanged` | `test_calls_notify_card_data_changed` | всегда делегирует в `notify_card_data_changed(changes, 400)` |
| `NotifyCardDeleted` | `test_event` | флаг выкл → событие `online.loyalty-card.card.deleted` |
| `NotifyCardDeleted` | `test_dwc` | флаг вкл → `send_changes_via_dwc('Card.HandleDelete', ...)` |

---

## Паттерн тестов — SimpleRecordMatcher

`SimpleRecordMatcher` делает **полное** сравнение полей, не частичное. Если реальная запись имеет N полей, ожидаемый матчер обязан включать все N полей — иначе `assert_called_once_with` упадёт.

Типичная ошибка: в `data` есть поле `TargetCard` (ftRECORD), а в `SimpleRecordMatcher` передают только `SourceCardID` и `ClientID` — падает, несмотря на то что эти два поля совпадают.

Правильный паттерн при наличии вложенного Record-поля:
```python
_TARGET_CARD = sbis.Record()  # на уровне модуля

@patch(f'{_IMPL_PATH}.get_card_partial_info', new=Mock(return_value=_TARGET_CARD))
...
SimpleRecordMatcher(sbis.Record(
    SourceCardID=_SOURCE_ID,
    TargetCard=_TARGET_CARD,   # тот же объект, что вернул мок
    ClientID=_CLIENT_ID,
))
```

Мок и матчер должны ссылаться на **один и тот же объект** `sbis.Record()`.

---

## Ключевые файлы

| Файл | Роль |
|------|------|
| `DiscountCard.dwc` | DWC workflow definitions |
| `priceformationonline/discountcard/loyaltycard/notify.py` | Точки ветвления (HandleChangeData, HandleChangeBonusBalance) |
| `priceformationonline/discountcard/personalcard/merge.py` | Точка ветвления HandleMerge |
| `priceformationonline/discountcard/loyaltycardtype/notify.py` | `send_changes_via_dwc` helper |
| `priceformationcommon/helpers/feature.py` | `Feature.DWC_CARD` |
| `PriceFormation.feature` | Feature flag declaration |
| `tests/.../loyaltycard/notify.py` | Unit tests (HandleChangeData, HandleChangeBonusBalance) |
| `tests/.../personalcard/merge.py` | Unit tests (HandleMerge) |
| `priceformationonline/dcservice/servicediscountcard/notify_changed.py` | Забытая точка `async_notify_changed_cards` (08106197) |
| `priceformationonline/loyaltyprograms/bonus/notify_sabyget.py` | Забытая точка `BonusOperationEventQueue.publish` (08106197) |

---

## Сценарии проверки для QA (08106197)

Проверять в обоих состояниях `dwc_card`. При включённом флаге в мониторе DWC появляются сценарии `Card.HandleChangeData` и `Card.HandleChangeBonusBalance`, событий быть не должно.

**Карты** (`async_notify_changed_cards`) — создание карты, изменение, выдача клиенту, импорт карт из файла (приоритетный кейс — наибольший объём), импорт персональных карт, смена персоны у карты, вступление в программу лояльности, объединение частных лиц, удаление клиента.

**Бонусы** (`BonusOperationEventQueue.publish`, все через `sbis.Bonus.ChangeHandler`) — продажа с начислением и со списанием, возврат, корректировка продажи, изменение операций на складском документе, реферальная продажа/возврат, ручное изменение баланса (одиночное / удаление / массовое), приветственные бонусы, бонусы за просмотр и отзыв, начисление на праздник и ДР, сгорание.

**Обязательный кейс на объём:** операция, порождающая >50 бонусных движений — раньше уходило пачками по 50, теперь одной задачей.

**Смежное:** событие `referral.bonusoperation.create` в SabyGet шлётся СДК из `Card.HandleChangeBonusBalance` (`handle_change_bonus_balance.py:187`) — теперь приходит по DWC-пути, реферальная статистика должна обновляться.
