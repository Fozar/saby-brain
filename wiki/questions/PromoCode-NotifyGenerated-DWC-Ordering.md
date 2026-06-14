---
type: synthesis
title: "PromoCode NotifyGenerated — уведомление SabyGet после привязки персон (DWC)"
created: 2026-06-11
updated: 2026-06-11
tags:
  - price-formation
  - promocode
  - dwc
  - sabyget
  - bug
question: "После выноса AttachPersonId в фоновый DWC уведомление SabyGet шлёт пустой PersonID — как починить?"
answer_quality: solid
status: developing
related:
  - "[[GetIndividualBatch-AttachPersonId-Timeout-Fix]]"
  - "[[Wasaby-BL-AsyncInvoke]]"
  - "[[DWC-Distributed-Workflow-Coordinator]]"
  - "[[DWC-Promocode-Events-Migration]]"
  - "[[Promocode-Subsystem-Overview]]"
---

# PromoCode NotifyGenerated — уведомление SabyGet после привязки персон (DWC)

## Регресс, внесённый таймаут-фиксом

[[GetIndividualBatch-AttachPersonId-Timeout-Fix]] вынес `CRMClients.AttachPersonId` в фоновый DWC-сценарий `IndividualPromoCodeEmission.AttachPersons` (`one_task="0"`, ~5с/клиент уходит в фон). Но в `generate.py` сразу после генерации **синхронно** оставался вызов `_get_promo_codes_data_for_notify` → `notify_on_promo_code_change_bulk`, который шлёт в SabyGet событие с полем `PersonID`.

`PersonID` берётся из `CRMClients.GetClientInfo` → поля `ИдентификаторФизЛица`. Это поле проставляет **именно** `AttachPersonId`. Раз привязка теперь асинхронная, на момент синхронного уведомления `ИдентификаторФизЛица` ещё `NULL` → **в SabyGet уходит пустой `PersonID`**.

Тонкость, которую важно не перепутать: оригинальная заметка таймаут-фикса верно говорила, что *результат* `AttachPersonId` игнорируется — но это про **корректность генерации** (промокоды привязываются по `@Лицо`, полученному заранее через `CRMContactDriver.GetMassClientByContact`). Уведомление SabyGet — отдельный канал, и для него привязка персоны обязательна. Неважно, кладём ли мы `PersonID` в payload события или SabyGet читает `ИдентификаторФизЛица` сам при обработке — в обоих случаях привязка должна завершиться **до** уведомления.

## Решение: уведомление — тоже DWC-задача, последняя в сценарии

Зависимость «notify после всех attach» — это **барьер**. Варианты:

- **Обычный `AsyncInvoke`** ([[Wasaby-BL-AsyncInvoke]]): порядок не гарантирован, цепочка только через per-call callbacks (callback = «после одного метода»). Барьера «после N задач» нет — отслеживать завершение N независимых вызовов вручную хрупко.
- **DWC** ([[DWC-Distributed-Workflow-Coordinator]]): сценарий = упорядоченный набор задач. Привязка **уже** живёт в DWC. Добавление финальной задачи уведомления в тот же сценарий и есть штатный способ выразить зависимость.

Вердикт — **DWC, обычный async недостаточен** (а не избыточен).

### Гарантия порядка

Ключевой факт из API `workflow2.Workflow`: `OpenParallelBlock()` / `CloseParallelBlock()` — **явный** opt-in. Без них `AddTask` строит **последовательную** цепочку, исполняемую в порядке добавления. У сценария `parallel_blocks_used="0"`, поэтому: задачи привязки добавляются первыми, задача(и) уведомления — последними → уведомление гарантированно отрабатывает после всех привязок. (Прежняя заметка про «DWC может параллелить one_task=0» — нестрогая формулировка; авто-реордеринга без parallel-block нет.)

## Что меняется в коде

1. **`LoyaltyPrograms.orx`** — новый BL-метод `IndividualPromoCodeEmission.NotifyGenerated`, `is_service="1"`, `returns="NONE"`. Параметр — **голый массив** `PromoCodeIds` типа `INT4[]` (не `Record`; прецедент — `ActivityPromoCode.GetExpirationDates`). `.orx` — это XML (UTF-8), редактируется текстом.
2. **`LoyaltyPrograms.dwc`** — в воркфлоу `IndividualPromoCodeEmission.AttachPersons` добавлена вторая задача-шаблон `NotifyGenerated` (`service="online"`, маппится на новый BL-метод). `error_policy` сменён `abort → continue`, чтобы сбой привязки не блокировал синхронизацию SabyGet. Остаётся `one_task="0"`, `parallel_blocks_used="0"`.
3. **`notify_generated.py`** (новый обработчик) — принимает `promo_code_ids`, **перечитывает** промокоды из `Карта` по `@Карта = ANY(...)`, делает `GetClientInfo` **в момент выполнения** (когда `ИдентификаторФизЛица` уже проставлен) и шлёт `notify_on_promo_code_change_bulk`. Перечитывание из БД, а не передача всех полей в задачу, держит payload задачи в пределах лимита 100 КБ.
4. **`generate.py`** — синхронный notify убран; `_start_attach_and_notify_dwc(clients_to_attach, promo_code_ids)` ставит N задач привязки (только клиентам без персоны — фильтр по `ИдентификаторФизЛица` через `_fetch_clients_data`) + задачи `NotifyGenerated` чанками по `_NOTIFY_CHUNK_SIZE = 1000` промокодов.

### Идентификация «этой пачки»

Нет колонки-маркера пачки. Чтобы уведомить именно сгенерированные сейчас коды (а не все коды эмиссии), в задачу передаются `@Карта`-идентификаторы вставленных промокодов: `int(promo_code.Get('Id').split('-')[-1])` (поле `Id` = `<emission>-<@Карта>`). Чанкование по 1000 ограничивает и payload, и объём работы на задачу.

## Распространение на все типы генерации (направление от 2026-06-11)

Изначально DWC-путь применялся только к `IndividualPromoCodeGenerationType.MAIL`. Решение — **делать так для всех типов**. Для `AUTO` клиентов нет (`ClientId = None`), привязок не будет (`clients_to_attach = []`), но уведомление всё равно уходит в DWC одним механизмом — синхронный `_get_promo_codes_data_for_notify` удаляется полностью. Защита от пустого сценария: запускать DWC только если есть `promo_code_ids`.

**Открытый риск для AUTO-тестов:** AUTO-тесты (`test_qr_*`) не мокали `workflow2` — раньше AUTO шёл синхронным notify. После перевода на DWC они начнут вызывать реальный `workflow2.Sender().Commit(...)`; при переходе на all-types нужно либо замокать `workflow2` в этих тестах, либо убедиться, что Commit в тестовом облаке безопасен.

## Тесты

- MAIL-тесты `test_qr_with_persons` / `test_mail_does_not_call_attach_synchronously`: счётчик `AddTask` = привязки + notify-чанк; `GetClientInfo` замокан (`ToDict → {}`), чтобы фильтр привязки был детерминирован (все клиенты без персоны).
- `test_notify_generated_sends_person_id` — генерирует коды (workflow2 замокан), затем вызывает `notify_generated(promo_code_ids)` с `GetClientInfo`, вернувшим `person_uuid`, и проверяет, что `publish_promocode_data_changed` получил запись с правильным `PersonID`/`ClientName`. Это и есть проверка самой сути фикса: свежий `PersonID` доходит до SabyGet.
- Прогон файла: 13/13 OK (на состоянии «только MAIL»).

## Статус

Реализация была сделана для MAIL и проверена (13/13). Затем поступило указание распространить на все типы; на этом шаге рабочие файлы `.dwc` и тестов были откачены в рабочем дереве (итерация по дизайну продолжается). Задача: <https://dev.sbis.ru/opendoc.html?guid=3b765654-92ae-440f-8000-f88a1d4e6193&client=3>. Ветка контекста — `rc-26.3211`.

## Связанные файлы

- `priceformationonline/loyaltyprograms/individual_promo_code_emission/generate.py`
- `priceformationonline/loyaltyprograms/individual_promo_code_emission/notify_generated.py` (новый)
- `priceformationonline/loyaltyprograms/individual_promo_code_emission/core.py` — `notify_on_promo_code_change_bulk`
- `LoyaltyPrograms.orx`, `LoyaltyPrograms.dwc`
- `tests/tests_priceformationonline/loyaltyprograms/individual_promo_code_emission/generate.py`
