---
type: session
address: c-000011
title: "DWC Card HandleChangeData — Session Note"
created: 2026-05-13
updated: 2026-05-13
tags:
  - price-formation
  - dwc
  - discount-cards
  - implementation
  - migration
status: developing
related:
  - "[[DWC-Migration-SDK]]"
  - "[[DiscountCard-Subsystem-Overview]]"
  - "[[DWC-BonusSettings-Events-Migration]]"
  - "[[DWC-Promocode-Events-Migration]]"
  - "[[DWC-Distributed-Workflow-Coordinator]]"
---

# DWC Card Events Migration — Card.HandleChangeData

Navigation: [[DWC-Migration-SDK]] | [[DiscountCard-Subsystem-Overview]]

Реализован первый этап перевода событий по картам на DWC. Событие `online.loyalty-card.card-data.changed`
заменено постановкой DWC-задачи `Card.HandleChangeData` при включённом флаге `dwc_card`.

---

## Декомпозиция (все 4 задачи по картам)

Полная карта событий → DWC для дисконтных карт (этап "Карты → DWC" из [[DWC-Migration-SDK]]):

| Задача | Событие | DWC-обработчик | Приоритет | Файл изменения | Статус |
|---|---|---|---|---|---|
| Изменение данных | `online.loyalty-card.card-data.changed` | `Card.HandleChangeData` | Высокий | `loyaltycard/notify.py` | ✅ Реализовано |
| Изменение бонусного баланса | `discount-cards.bonusoperation.online` | `Card.HandleChangeBonusBalance` | Высокий | `loyaltycard/notify.py` | ⏳ |
| Удаление карты | `online.loyalty-card.card.deleted` | `Card.HandleDelete` | Средний | `loyaltycard/notify.py` | ⏳ |
| Слияние карт | `online.loyalty-card.card.merged` | `Card.HandleMerge` | Низкий | `personalcard/merge.py` | ⏳ |

Scaffolding и AT-покрытие входят в каждую задачу отдельно.

---

## Задача 1: Card.HandleChangeData (реализована)

### Изменённые файлы

| Файл | Изменение |
|---|---|
| `PriceFormation.feature` | Добавлен `<feature id="dwc_card">` |
| `priceformationcommon/helpers/feature.py` | Добавлен `DWC_CARD = 'dwc_card'` рядом с `DWC_CARD_TYPE` |
| `DiscountCard.dwc` | Добавлен workflow `Card.HandleChangeData` |
| `priceformationonline/discountcard/loyaltycard/notify.py` | DWC-ветка в `notify_card_data_changed` |
| `tests/.../discountcard/loyaltycard/notify.py` | Тесты event-пути и DWC-пути |

### Паттерн изменения notify_card_data_changed

```python
# Новые импорты
from priceformationcommon.helpers.feature import check_feature, Feature
from priceformationonline.discountcard.loyaltycardtype.notify import send_changes_via_dwc

# DWC-ветка — после подготовки changes, перед батч-логикой
if check_feature(Feature.DWC_CARD):
    send_changes_via_dwc(changes, 'Card.HandleChangeData', 'HandleChangeData')
    return
```

**Поведение DWC-пути**: весь RecordSet отправляется одной задачей (`batch_size` игнорируется) — аналогично `notify_card_type_data_changed` с `DWC_CARD_TYPE`.

### Единственная точка входа покрывает всех вызывающих

- `loyaltycard/handle.py:392, 398` — изменение данных карты (sale stats, stamp stats, any data)
- `loyaltycardtype/handle.py:578` — изменение штампиков при смене типа карт
- `regcloneclientdatahdl/handle_client_cloning.py:118` — клонирование клиента

### DWC workflow в DiscountCard.dwc

```xml
<workflow name="Card.HandleChangeData" kind="lrs" limit_key_template="%1%" limit_value="1"
          responsible="Тимошенко А.А." responsible_uuid="0862a7d6-c1c6-4642-81aa-685d2e2400cb" ...>
  <task name="HandleChangeData" service="discount-cards">
    <method name="Card.HandleChangeData">
      <arg kind="runtime"/>
    </method>
  </task>
</workflow>
```

`limit_key_template="%1%"` = ClientID → максимум 1 воркер СДК на клиента одновременно.

### Тест-паттерн

```python
_IMPL_PATH = 'priceformationonline.discountcard.loyaltycard.notify'

@patch('event.Publish')
class NotifyCardDataChanged(TransactionTestCase):
    # test_event: флаг выкл → event.Publish вызван, log_event вызван
    # test_dwc:   @enable_features([Feature.DWC_CARD])
    #             → send_changes_via_dwc вызван с ('Card.HandleChangeData', 'HandleChangeData')
    #             → event.Publish НЕ вызван
```

Патчим `send_changes_via_dwc` в пространстве `loyaltycard.notify` (не в `loyaltycardtype.notify`),
так как функция импортирована и живёт в локальном namespace.

---

## Технические решения

**send_changes_via_dwc**: импортируется из `loyaltycardtype.notify` без рефакторинга. Оба модуля —
сиблинги в пакете `discountcard`. Перенос в common — отдельный рефакторинг после всех 4 задач.

**Задача 2 (HandleChangeBonusBalance)**: в DWC это отдельный сценарий, не `HandleChangeData`.
`notify_bonus_balance_changed` → `notify_card_data_changed` — пути разводятся на уровне
`notify_bonus_balance_changed`: при `DWC_CARD` вкл → `Card.HandleChangeBonusBalance`, иначе →
старый путь через `notify_card_data_changed`.

---

## Критерии приёмки

- Нет регресса при `dwc_card` выкл
- При `dwc_card` вкл: создаётся DWC-задача, событие не публикуется
- Массовый импорт карт → одна DWC-задача на клиента (не N событий)
