---
type: concept
title: "ReferralProgram.SetStubPrice/SetLeadPrice — рекорд-результат начисления"
created: 2026-06-16
updated: 2026-06-16
tags:
  - price-formation
  - referral
  - sabybank
  - bl-method
  - implementation
status: developing
related:
  - "[[ReferralProgram-Stub-Implementation]]"
  - "[[ReferralProgram-Data-Model]]"
  - "[[ReferralProgram-GetLeadPeriodList-LeadCount-Source]]"
  - "[[SabyBank-RKO-Referral]]"
---

# ReferralProgram.SetStubPrice/SetLeadPrice — рекорд-результат начисления

Navigation: [[ReferralProgram-Stub-Implementation]] | [[ReferralProgram-Data-Model]] | [[SabyBank-RKO-Referral]]

Задача №04307161 (saby bank, ответственный Михель В.М.). Часть требования: при массовом изменении вознаграждений показывать уведомление «скольким добавилось, скольким нет — как в картах». Эталон — `DiscountCard.BatchDeleteOrLock/1`, который возвращает `Record({'DeletedCount', 'LockedCount'})`.

---

## Решение

Оба BL-метода ранее возвращали `int` (число обновлённых строк). Теперь возвращают `sbis.Record` с двумя полями:

| Поле | Смысл |
|------|-------|
| `AccruedCount` | по скольким заявкам/корешкам вознаграждение **начислено** |
| `NotAccruedCount` | по скольким **не начислено** = `len(marked) − accrued` |

Именование по образцу `DiscountCard.BatchDeleteOrLock` (причастие + `Count`).

«Не начислено» = ID был в `selection.marked`, но `UPDATE` не затронул строку:
- **SetStubPrice** — корешок с неуспешным статусом (`ТипСвязи != LinkType.REQUEST_SUCCESS`).
- **SetLeadPrice** — сделка не подошла под условие (`v."Тип" != PriceEntityType.REFERRAL_LEAD` / не та программа).

`accrued = returned_rows.Size()` (`RETURNING`), `requested = len(marked)`. Пустой фильтр → `{AccruedCount: 0, NotAccruedCount: 0}`.

---

## Изменённые файлы

| Файл | Действие |
|------|----------|
| `priceformationonline/referralprogram/referralprogram/set_stub_price.py` | возврат → `sbis.Record`, хелпер `_build_result(accrued, requested)` |
| `priceformationonline/referralprogram/referralprogram/set_lead_price.py` | то же |
| `ReferralProgram.orx` | у обоих `<select>`: `returns="SCALAR"` → `returns="RECORD"`; скалярный `<return>` заменён на `AccruedCount` + `NotAccruedCount` |
| `tests/...referralprogram/set_stub_price.py`, `set_lead_price.py` | ассерты → `result.Get('AccruedCount'/'NotAccruedCount')` |

Пути от `www/service/Модули/PriceFormation.Online/`.

---

## Хелпер

```python
def _build_result(accrued: int, requested: int) -> sbis.Record:
    return sbis.Record({'AccruedCount': accrued, 'NotAccruedCount': requested - accrued})
```

Хелпер дублируется в обоих файлах (правило проекта **1 файл = 1 BL-метод**, общего модуля под это не заводили).

---

## .orx запись (фрагмент return)

```xml
<select ... name="ReferralProgram.SetStubPrice" returns="RECORD" type="PYTHON">
  ...
  <return name="AccruedCount">
    <comment>Количество корешков, по которым вознаграждение начислено</comment>
    <format><type>INTEGER</type></format>
  </return>
  <return name="NotAccruedCount">
    <comment>Количество корешков, по которым вознаграждение не начислено</comment>
    <format><type>INTEGER</type></format>
  </return>
</select>
```

---

## Нюансы

- `ReferralProgram.uax` правок не требует — там только права (`privilegy`), не формат возврата.
- Других Python-вызовов этих методов нет; на `int` опирался только клиент/UI (отдельная задача — уведомление на фронте здесь не делалось).
- Pyright ругается `Cannot access attribute "Get" for class "int"` в тестах — авто-стаб `sbis` ещё держит старую сигнатуру `int`, перегенерится из `.orx` при сборке. В рантайме метод реально возвращает `Record`.

---

## Тесты

`SetStubPrice` + `SetLeadPrice` — **9 тестов, OK**. Ключевой кейс новой логики: `test_3_non_success_stubs_silently_skipped` — два неуспешных корешка в `marked` → `AccruedCount=0`, `NotAccruedCount=2`.
