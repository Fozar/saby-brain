---
type: synthesis
address: c-000069
title: "GetIndividualBatch AttachPersonId Timeout Fix"
created: 2026-05-25
updated: 2026-06-10
tags:
  - price-formation
  - promocode
  - dwc
  - performance
  - bug
status: fixed
related:
  - "[[DWC-Distributed-Workflow-Coordinator]]"
  - "[[DWC-Card-Events-Migration]]"
  - "[[Price-Formation-Test-Runner]]"
  - "[[PromoCode-NotifyGenerated-DWC-Ordering]]"
---

> [!warning] Follow-up регресс
> Этот фикс внёс регресс: синхронный notify SabyGet после фоновой привязки слал пустой `PersonID`. Разбор и фикс (уведомление финальной задачей того же DWC-сценария) — [[PromoCode-NotifyGenerated-DWC-Ordering]].

# GetIndividualBatch AttachPersonId Timeout Fix

## Баг

При рассылке на SabyGet метод `PromoCode.GetIndividualBatch` падает с ошибкой **«Не хватает данных для формирования подстановок»**.

Root cause: внутри генерации промокодов для каждого получателя синхронно вызывается `CRMClients.AttachPersonId`. Каждый вызов занимает **~5 с**. При 100 получателях суммарное время >300 с → таймаут метода → промокоды не генерируются.

## Код-путь

```
PromoCode.GetIndividualBatch
  → _generate_promo_codes_w_persons()
    → sbis.IndividualPromoCodeEmission.Generate(ClientIds=[...], MAIL type)
      → generate() in generate.py
        → для каждого client_id: attach_person_to_client(client_id)  ← УЗКОЕ МЕСТО
          → sbis.CRMClients.AttachPersonId(...)  ← ~5 с каждый вызов
```

**Файл:** `priceformationonline/loyaltyprograms/individual_promo_code_emission/generate.py`, строки 165–173.

Ключевое наблюдение: `AttachPersonId` только регистрирует персону в Saby. Результат вызова **полностью игнорируется** (try/except sbis.Warning pass). Промокоды привязываются по `@Лицо`, полученному заранее через `CRMContactDriver.GetMassClientByContact` в `_find_persons`. Значит, `AttachPersonId` не влияет на корректность генерации.

## Происхождение

На летучке **2026-05-22** с Омельяненко Егором предложен DWC-подход:
> «Нормально было бы, чтобы это через ДВС вызывалось, и какой-то progress-bar был. Когда рассылка создалась, пускай сколько надо отрабатывает.»
> Ссылка на аналог: «лимиты» — там прогресс-бар уже реализован.

---

## Рассматриваемые решения

### Вариант A — только AttachPersonId в DWC (минимальный)
- Генерация кодов остаётся синхронной
- Цикл `attach_person_to_client` убирается из транзакции
- После коммита транзакции запускается DWC `IndividualPromoCodeEmission.AttachPersons`
- DWC в фоне привязывает персон
- `GetIndividualBatch` возвращает коды сразу

### Вариант B — вся генерация в DWC (архитектурный)
- `GetIndividualBatch` запускает DWC и не ждёт результата
- **Нерешённый вопрос:** как рассылка получает готовые промокоды?
  - Двухфазный сценарий: `GetIndividualBatch` возвращает pending, рассылка перезванивает позже
  - Предгенерация: DWC запускается на более раннем этапе (создание/запуск рассылки), к моменту вызова коды уже в БД
- Требует изменения контракта с системой рассылок

**Текущий статус (2026-06-04):** Федько Юрий принял решение двигаться через **DWC + LRS**. Уточняется конкретная схема с Омельяненко Егором.

## DWC-паттерн (для варианта A)

По образцу `Bonus.CreateSmscNotifications` (kind="background", one_task="1"):

```python
# generate.py — после with CreateTransaction:
if generation_type == IndividualPromoCodeGenerationType.MAIL:
    _start_attach_persons_dwc(persons_ids)

def _start_attach_persons_dwc(client_ids):
    client_ids_rs = create_record_set(
        [{'ClientId': cid} for cid in client_ids],
        [('ClientId', sbis.FieldType.ftINT64)]
    )
    wflow = workflow2.WorkflowBuilder('IndividualPromoCodeEmission.AttachPersons').Build()
    task = wflow.CreateTask('IndividualPromoCodeEmission.AttachPersons')
    task.SetMethodArgs(client_ids_rs)
    wflow.AddTask(task)
    workflow2.Sender().AddWorkflow(wflow).Commit(sbis.PublicationPolicy.ppIMMEDIATELY)
```

Нужно добавить:
- `LoyaltyPrograms.dwc` — workflow `IndividualPromoCodeEmission.AttachPersons` (kind="background")
- `LoyaltyPrograms.orx` — BL-метод `IndividualPromoCodeEmission.AttachPersons`
- Новый файл `attach_persons.py` — DWC-обработчик

## История попыток исправления

### 2026-05-26 — Параллелизация (rc-26.3200, НЕДОСТАТОЧНО)

Задеплоен фикс: вызовы `AttachPersonId` распараллелены через `ParallelTask` (лимит платформы — 16 потоков одновременно).

**Результат тестирования (01.06.2026, Куимова Наталья):** из 659 отправок — доставлено ~70%. Статус у оставшихся 30%: «Не хватает данных для формирования подстановок».

**Вывод:** параллелизация ускоряет в ~16 раз, но для крупных рассылок (500+ клиентов) всё равно таймаут. Фундаментальная проблема не устранена.

### Новый контекст (2026-06-03, Журавлев Петр)

`PromoCode.GetIndividualBatch` возвращает **не только промокод, но и ссылку** — оба значения используются как подстановки в рассылке. Это важно при проектировании DWC-решения: нужно вернуть оба поля.

### 2026-06-08 — DWC вариант A (выкачен и откачен 09.06, one_task mismatch)

Реализован вариант A: `_start_attach_persons_dwc` запускал воркфлоу `IndividualPromoCodeEmission.AttachPersons` (`Commit(ppIMMEDIATELY)`), добавляя по задаче на каждого клиента (`for client_id in client_ids: wflow.AddTask(...)`).

**Результат (08.06.2026):** упали **все** рассылки — воспроизведено даже на 3 получателях (Богда, Борис Акимов100/101). На стороне рассылки у каждого получателя статус «Не доставлено» / «Не хватает данных для формирования подстановок» (код 233).

**Root cause (из лога, события 08-06 15:50):**
```
ERROR: В декларативном описании сценария IndividualPromoCodeEmission.AttachPersons
       указано, что он состоит из одной задачи
```
Трейс: `get_individual_batch.py:83` → `_generate_promo_codes_w_persons:255` → `IndividualPromoCodeEmission.Generate` → `generate.py:181` → `_start_attach_persons_dwc:259` → `sbis.error.Error`.

В `LoyaltyPrograms.dwc` воркфлоу был объявлен `one_task="1"` (сценарий из одной задачи), а код добавлял N задач. DWC валидирует это несоответствие на `Commit` → бросает `Error` → падает весь `generate()` → `GetIndividualBatch` отдаёт ошибку → ошибка подстановок у каждого получателя, **независимо от размера рассылки**. Отсюда «вообще не отправляются на любое количество клиентов».

**Откат:** коммит `0a1dd9218e` (09.06.2026) — удалены `_start_attach_persons_dwc`, workflow из `.dwc` и тесты DWC. Ветка вернулась к ParallelTasks.

**Урок при повторной попытке DWC:** при `one_task="1"` нужна ОДНА задача со списком `client_ids` и обработчик-цикл внутри (как `Bonus.CreateSmscNotifications`), либо `one_task="0"` для набора задач. Несоответствие декларации `one_task` и числа `AddTask` — фатально для всей транзакции.

## РЕШЕНО (2026-06-10) — DWC `one_task="0"`, повтор Варианта A с исправлением

Повторно реализован **Вариант A** (вынос `AttachPersonId` в фоновый DWC), но с устранением единственной причины отката 08–09.06: воркфлоу теперь объявлен **`one_task="0"`** (набор задач), что снимает фатальную валидацию `Commit` при N задачах.

Согласовано с пользователем: `one_task="0"` без чанков, **без фича-флага**.

**Изменения:**

1. `generate.py`:
   - Убран блок `sbis.ParallelTasks()` + обёртка `_attach_person_safe` из транзакции; удалён импорт `attach_person_to_client`.
   - Возвращён `import workflow2`.
   - После выхода из `with CreateTransaction(...)`: `if MAIL and persons_ids: _start_attach_persons_dwc(persons_ids)`.
   - `_start_attach_persons_dwc` создаёт по DWC-задаче на клиента (`CreateTask('AttachPersonId')` → `SetMethodArgs(Record({'CustomerID': cid}))` → `SetUser` → `AddTask`), `Commit(ppIMMEDIATELY)`.
2. `LoyaltyPrograms.dwc` — воркфлоу `IndividualPromoCodeEmission.AttachPersons`: `kind="background"`, **`one_task="0"`** (+`conditional_blocks_used/parallel_blocks_used/workflow_part_limits_used="0"`). Задача маппится напрямую на существующий БЛ-метод `CRMClients.AttachPersonId` — **новый orx-метод и python-обработчик НЕ нужны**.
3. Тесты восстановлены: `test_qr_with_persons` (проверяет уход в DWC, `AddTask.call_count == amount`) и `test_mail_does_not_call_attach_synchronously` (`AttachPersonId` синхронно не вызывается). `Generate`: 8/8 OK. pylint 10/10.

**Почему `one_task="0"` корректен здесь, а `one_task="1"` падал:** при `one_task="0"` DWC ожидает набор задач, поэтому N `AddTask` валидны и DWC может параллелить задачи между собой. Прошлая попытка добавляла те же N задач при объявлении `one_task="1"` → `Error` на `Commit`.

**Важная поправка по ветке:** работа ведётся на **`rc-26.3211`** (ошибка вынесена туда), ветка `26.3211/bugfix/aatimoshenko/04295801_2`. НЕ на rc-26.4100. При переносе был конфликт в `.dwc`: в rc-26.3211 `Promocode.HandleApply` ещё `kind="user" one_task="1"` (в rc-26.4100 — `kind="lrs" one_task="0"`); оставлена версия rc-26.3211, добавлен только новый воркфлоу.

### Открытый вопрос (масштаб)
`one_task="0"` без чанков создаёт по задаче на клиента. Для очень больших рассылок (1500+) это много DWC-задач; при необходимости — перейти на чанкование (N клиентов на задачу) или single-task + внутренний ParallelTasks (как `Bonus.CreateSmscNotifications`). Пока не требуется.

## Контекст принятого ранее направления (DWC + LRS)

Федько Юрий (2026-06-04): *«видимо нужен всё-таки подход через DWC, LRS»*. Вариант B (вся генерация в DWC через LRS, progress-bar, аналог «лимиты») остаётся архитектурной перспективой, но текущий фикс закрывает баг минимальными средствами.

## Связанные файлы

- `www/service/Модули/PriceFormation.Online/priceformationonline/loyaltyprograms/individual_promo_code_emission/generate.py`
- `www/service/Модули/PriceFormation.Online/priceformationonline/discountcard/discountcard/set_for_client.py` — `attach_person_to_client`
- `www/service/Модули/PriceFormation.Online/priceformationonline/loyaltyprograms/promocode/get_individual_batch.py`
- `www/service/Модули/PriceFormation.Online/LoyaltyPrograms.dwc`
- `www/service/Модули/PriceFormation.Online/LoyaltyPrograms.orx`
