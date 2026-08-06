---
type: decision
address: c-000259
title: "Сумма сделки в корешке: поле LeadSum реализовано"
created: 2026-08-06
updated: 2026-08-06
decision_date: 2026-08-06
status: active
tags:
  - price-formation
  - referral-program
  - sabybank
  - implementation
related:
  - "[[ReferralStub-DealSum-Field]]"
  - "[[ReferralProgram-GetPartnerList-Stub-Stats]]"
  - "[[ReferralStub-Backfill-Service-Method]]"
  - "[[ReferralProgram-GetLeadPeriodList-Stub-Mode]]"
  - "[[SabyBank-RKO-Referral]]"
  - "[[Тимошенко А.А.]]"
---

# Сумма сделки в корешке: поле LeadSum реализовано

Navigation: [[SabyBank-RKO-Referral]] | [[ReferralStub-DealSum-Field]]

Задача №08052776 («Записывать в корешок сумму сделки + в методе конвертации исторических данных.
Сообщить Артемьеву Даниилу», этап «Новые заявки отображаются в SabyBank»). Закрывает отложенный
пункт 3 решения [[ReferralStub-DealSum-Field]] — «пока писать пусто/ноль».

## Что было

Колонка `Сумма` таблицы `ВидЦеныДокумент` **уже агрегировалась** в `GetPartnerList`
(`SUM("Сумма")` → `LeadSum` / `PositiveLeadSum`, `get_partner_list.py:477,492`, сдано
[[ReferralProgram-GetPartnerList-Stub-Stats|2026-07-31]]), но не заполнялась ни одним путём создания
корешка. В коде это было явно зафиксировано комментарием «поле "Сумма" пока не заполняется».

## Решение

Поле API названо **`LeadSum`** — одноимённо колонке `GetPartnerList`, куда сумма и агрегируется
(промежуточные варианты `Amount` / `RequestSum` отклонены; `RequestSum` был реализован и переименован
до коммита). Тип — `MONEY`, необязательное.

Три пути наполнения:

| Путь | Источник суммы |
|---|---|
| `CreateStub` (API SabyBank) | `Request.LeadSum` — присылает вызывающая сторона |
| `UpdateStub` (API + событие смены состояния сделки) | `Request.LeadSum`; `NULL` — не обновлять |
| `CreateStubsForExistingLeads` (конвертация исторических данных) | `ДокументРасширение.Сумма` сделки из `SourcesSales.GetRawDocs` |

`HandleLeadStateChanged._update_stub_by_lead` прокидывает `lead_info.Get('ДокументРасширение.Сумма')`
в `UpdateStub` — иначе у обычных (не SabyBank) реферальных сделок сумма осталась бы пустой навсегда:
корешок создаётся в момент создания сделки (`create_lead.py`), когда суммы ещё нет.

> [!key-insight] LeadSum — факт по заявке, а не начисление
> В `UpdateStub` сумма обновляется **при любом статусе и без прав OWNER_ADMIN**, в отличие от
> соседнего `Price` (только `Status=15` + OWNER_ADMIN). Вознаграждение — управленческое решение
> владельца сети, сумма сделки — внешний факт. В историю корешка (`ReferralStubHistory`,
> см. [[ReferralStub-History-Scope-Cut]]) изменение суммы не пишется: события для неё нет,
> постановка не требует.

Наружу сумма отдаётся в `ReadStub` и `GetStubList` (UI пока не потребляет — колонки суммы по
отдельному корешку на фронте нет, читается только агрегат в реестре партнёров).

## Проверенный факт: `ДокументРасширение.Сумма` входит в стандартный формат `GetRawDocs`

Первая редакция решения добавляла поле в `additional_fields` вызова `GetRawDocs` с комментарием
«в формат по умолчанию не входит» — **это неверно**. Доказательство обратного лежит в самом
репозитории: `get_lead_list.py:131` делает `record.Set('ДокументРасширение.Сумма', ...)` (перетирая
сумму сделки вознаграждением), а `Set` — в отличие от `Put` — работает только по уже существующему
полю; фронт реестра «Заявки» (`client/LoyaltyOnline/ReferralLeadNew/Deals/PrefetchResources.ts:108`)
доп. полей не передаёт вовсе. Вызов оставлен с `additional_fields=[]`.

Переиспользуемое правило: **`Set` vs `Put` в коде-потребителе — доказательство наличия поля в формате
ответа чужого сервиса**, когда исходники сервиса недоступны.

## Затронутый код

`www/service/Модули/LoyaltyReferral/`:
- `ReferralProgram.orx` — `LeadSum` в `Request` у `CreateStub`/`UpdateStub`, в возвратах `ReadStub`/`GetStubList`
- `.../create_stub.py` — колонка `Сумма` в `_SQL_INSERT_STUB`
- `.../update_stub.py` — `"Сумма" = CASE WHEN $7 IS NOT NULL THEN $7 ELSE "Сумма" END`
- `.../create_stubs_for_existing_leads.py` — сумма в bulk-insert и в выборку `Stubs` для сверки из
  консоли (алиас `unnest` — `lead_sum`, не `sum`: конфликт с ключевым словом)
- `.../handle_lead_state_changed.py`, `.../read_stub.py`, `.../get_stub_list.py`
- `.../get_partner_list.py` — снят устаревший комментарий

11 новых тестов, прогон пакета `tests/tests_loyaltyreferral/referralprogram/referralprogram` — 293/293 OK,
pylint 10.00/10. Не закоммичено.

## Открытое

- [ ] **Сообщить Артемьеву Даниилу** — до этого корешки SabyBank остаются с пустой суммой: поле
      заполнится только когда их сторона начнёт слать `LeadSum` в `CreateStub`/`UpdateStub`
- [ ] **Доброска существующим корешкам не сделана.** `CreateStubsForExistingLeads` идемпотентен по
      `OperationId` и повторный прогон уже созданные корешки пропускает — сумму им не проставит.
      Отдельная задача, продолжение [[ReferralStub-Backfill-Service-Method]]
- [ ] Проверка на стенде: автотесты мокают CRM, реальное наполнение `ДокументРасширение.Сумма`
      из `GetRawDocs` автотестами не доказывается
- [ ] **`LeadSum` заказан ещё в двух методах.** Проект [[ReferralProgram-Part2-Project]] требует
      `LeadSum`/`PositiveLeadSum` в `ReferralProgram.GetList` ([[ReferralProgram-Folders-Priority-Sprint|спринт №2]],
      статистика на плитке оффера) и в `ReferralProgram.GetListByContractor`
      ([[ReferralProgram-ContractorCard-Programs-Tab|спринт №3]], вкладка «Программы» в карточке контрагента).
      Сейчас поле отдаётся только в `GetPartnerList`/`ReadStub`/`GetStubList` — выдача наружу закрыта не полностью
