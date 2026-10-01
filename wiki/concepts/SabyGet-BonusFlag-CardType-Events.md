---
type: concept
title: "Флаг «Акции и бонусы» на SabyGet: цепочка событий и баг №08276018"
created: 2026-09-01
updated: 2026-09-01
tags:
  - loyalty
  - sabyget
  - events
  - dwc
  - discount-cards
  - bugfix
status: developing
related:
  - "[[Loyalty-Events-External-Consumers]]"
  - "[[DWC-Card-Events-Migration]]"
  - "[[SabyGet-Loyalty-Subsystems]]"
  - "[[DWC-Distributed-Workflow-Coordinator]]"
---

# Флаг «Акции и бонусы» на SabyGet

Задача-триггер: **№08276018** «Не попадает в подборку "Акции и бонусы" заведение после включения изменения настроек дисконтной карты» (Ошибка на стенде, Литвинов А.М., fix.sabyget.ru). Первая итерация фикса — ре-publish события из СДК (MR `discount-cards!27764–27768`, коммит `849006db5`) — прошла, но тестирование вернуло задачу; разбор на логах `fix-online` от 31.08.2026 показал, что событие доходит, а ломает порядок и состав данных.

---

## Полная цепочка от настроек ДК до флага заведения

```
Онлайн: DiscountCardType.UpdateSettings
  → update_settings → update_description
  → loyalty_card_type_event_handle {Type: ANY_DATA_CHANGED}     handle.py:118
  → [async] LoyaltyCardType.AsyncHandle
      → notify_any_data_changed(card_type_id_list)              notify.py:324
          ├ notify_card_type_main_data_changed(skip_notify=True)
          ├ notify_program_data_changed(skip_notify=True)
          └ notify_sale_point_list_changed(skip_notify=True)     → LeftJoin в один набор
      → notify_card_type_data_changed(changes)                   notify.py:127
          └ при DWC_CARD_TYPE: DWC-задача CardType.HandleChangeData (событие НЕ публикуется)

СДК (discount-cards): CardType.HandleChangeData
  → handle_change_data → _upsert_card_type
  → notify_card_type_data_changed → event.Publish('online.loyalty-card.card-type-data.changed',
                                                  application='sabyget')

SabyGet (sabyget/core):
  on_event.py:32   'online.loyalty-card.card-type-data.changed' → Tasks.EventUpdateBonusFlag
  sabyget_dwc/sgd_establishment.py:774  event_update_bonus_flag → DWC Establishment.EventUpdateBonusFlag
  sabyget_service/establishments/events/events_ext.py:884  update_bonus_flag
  → Establishment.UpdateBonusFlag
  → sabyget_service/discount_cards/utils.py:91   set_promotion_and_bonus_flag
  → :231                                          _calculate_by_online_data
  → UPDATE "Заведение" SET "Флаги"[4] = ...
```

`Флаги[4]` — тот самый признак, по которому заведение попадает в подборку. Иконка акций на плитке считается иначе, поэтому симптом бага выглядит как «иконка есть, а в подборке нет».

## Что требует SabyGet от payload

`_calculate_by_online_data` (`sabyget_service/discount_cards/utils.py:231`):

- строки **без `CardTypeID` пропускаются**;
- `flag = all([PublicDistribution, Enabled, not StartDate or StartDate <= today, not EndDate or EndDate >= today])` — отсутствующее поле даёт `None`, то есть **флаг гаснет**;
- `for sale_point in sale_points or [None]` — при пустом `SalePointIDList` в выборку попадают **все заведения аккаунта**.

Плюс `update_bonus_flag` (`events_ext.py:884`) для «сбрасывающего» прохода смотрит только `params[0]`, то есть на батче из нескольких строк отрабатывает лишь по первой.

Вывод: событие обязано нести **полный и актуальный** снимок типа карты, иначе флаг сбрасывается по всему аккаунту.

## Два источника некорректных данных

**1. Частичный набор от `PROGRAM_DATA_CHANGED`.** `_handle_program_data_changed` (`handle.py:202`) → `notify_program_data_changed(skip_notify=False)` (`notify.py:240-263`) публикует набор ровно из `CardTypeID, BonusDescr, DiscountDescr, Stamps, StampsVisiblePromotionID` + `ClientID`. В логах это видно как `Establishment.UpdateBonusFlag([[7, null, null, {}, null, 13255844]])` → `'[{"account": …, "sale_point": null, "flag": false}]'`. `notify_any_data_changed`, наоборот, джойнит все три части и шлёт полный набор.

**2. Переисполнение DWC-задачи с устаревшим payload.** Хронология ретеста 31.08 (`fix-online`, клиент 12589216, тип карты 1 «Карта Таверны», заведение «Колбаска11» = ТП 1168, `EstUUID 9c6f26b6-964c-49c0-8549-04b9eea22ecb`):

| время (МСК) | что | ТП 1168 |
|---|---|---|
| 14:29:01.773 | `Workflow.FastCreate CardType.HandleChangeData`, log_id `a4e525fe-…` | нет |
| 14:29:02.03 | СДК `v:26.4220-3`, publish `id 01a05794-744d-…` → SabyGet `Tasks.EventUpdateBonusFlag` | нет |
| 14:29:02.18 | `[w][finish] 200 OK` + `Workflow.OnTaskDone` — задача закрыта успешно | |
| 14:29:29.693 | вторая задача, log_id `3b60ae42-…` | **есть** |
| 14:29:29.878 | publish `id 01a05794-e116-…` → `Tasks.EventUpdateBonusFlag` 14:29:29.884 | **есть** |
| 14:30:17.185 | **повтор** задачи `a4e525fe-…` из очереди (`q:1`), publish `id 01a05795-99e2-…` | нет |
| 14:30:34 | тестировщик открывает fix.sabyget.ru | — |

То есть уже завершённая задача была выполнена повторно через 75 секунд и последней донесла до SabyGet устаревший состав ТП. Почему DWC переисполнил успешно закрытую задачу — вопрос к владельцам DWC (сценарий id `72057594049875150`).

## Решение

Публиковать не пришедший в обработчик `data`, а **актуальное состояние типа карты после `_upsert_card_type`**:

- `dccore/cardtype/core.py` — `notify_card_type_data_changed(card_type: CardType)` собирает payload по `CARD_TYPE_DATA_CHANGED_FORMAT`: `CardTypeID, ClientID, Enabled, PublicDistribution, EndDate, SalePointIDList`;
- `dcservice/online/cardtype/handle_change_data.py` — вызов перенесён из начала `handle_change_data` в `_upsert_card_type`, следом за `notify_changes`.

Побочные эффекты: строки без `CardTypeID` (глобальные настройки БП) больше не публикуются — SabyGet их и так отбрасывал; на батч уходит по событию на тип карты, что заодно обходит ограничение `params[0]` в `update_bonus_flag`.

## Инструментальные засечки

- `mcp__sbis__cloud_get_logs`: `from_dt`/`to_dt` задаются в шкале UI `fix-cloud` (в ней 18:29 соответствует 14:29 в выдаче). Окно в «человеческом» времени выдачи молча смещает выборку на четыре часа.
- Тот же инструмент: `message_contains` не матчит служебные строки вида `[AMQP][event]` и не сочетается с `session_id`/`uuid`. Отрицательный результат по нему **не является** доказательством отсутствия строки — проверять контрольным запросом.
- `saby-search` 01.09 отвечал, но с пустым индексом (0 совпадений на `ClientID`, `import sbis`). Обходной путь для чужого репозитория: `git clone --filter=blob:none --depth 1 --branch <rc> https://git.sbis.ru/<group>/<repo>.git` — checkout падает на длинных путях внутри `tests/`, но исходники сервиса выкачиваются.
- `.orx` в GitLab отдаётся как бинарник; `gitlab_file_read` на несуществующий путь отвечает «Project not found», а не «file not found».
