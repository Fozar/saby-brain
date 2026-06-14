---
type: concept
address: c-000061
title: "SetLeadPrice — SABYBANK Stub Branch"
created: 2026-05-19
updated: 2026-05-19
tags:
  - price-formation
  - referral
  - sabybank
  - rko
  - implementation
status: current
related:
  - "[[SabyBank-RKO-Referral]]"
  - "[[ReferralProgram-Module]]"
  - "[[Loyalty-Database-Schema]]"
  - "[[SabyBank-Stub-Rewards-Calculation]]"
---

# SetLeadPrice — SABYBANK Stub Branch

Navigation: [[price-formation/_index]] | [[SabyBank-RKO-Referral]]

## Проблема

`ReferralProgram.SetLeadPrice` обновляет `Бонусы` в `ВидЦеныДокумент`, фильтруя по полю `"Документ"` (ID документа продажи). Для программ типа `ProgramType.SABYBANK` записи в `ВидЦеныДокумент` — это **корешки** (стабы заявок на РКО): у них `"Документ" = NULL`, поэтому старый SQL молча обновлял 0 строк.

## Ключевое различие корешка и обычной ВЦД

| Признак | Обычная ВЦД (сделка) | Корешок (стаб) |
|---------|---------------------|----------------|
| `"Документ"` | ID документа продажи | NULL |
| `"ТипСвязи"` | NULL | NOT NULL (10/15/20) |
| Идентификатор | `"Документ"` | `"@ВидЦеныДокумент"` (PK) |

`ТипСвязи IS NOT NULL` — единственный надёжный признак корешка в таблице `ВидЦеныДокумент`.

## Реализация

**Файл:** `priceformationonline/referralprogram/referralprogram/set_lead_price.py`

Логика ветвления:
1. `ReferralProgramRepository.read(program_id)` вызывается до SQL (перенесён из `_write_to_history`).
2. Если `referral_program.program_type == ProgramType.SABYBANK` → выполняется `_SQL_SET_STUB_PRICE`.
3. Иначе → существующий путь через `_SQL_SET_LEAD_PRICE`.

### SQL для корешков

```sql
UPDATE "ВидЦеныДокумент"
SET "Бонусы" = $2::NUMERIC(32, 2)
WHERE
    "ВидЦены" = $1::INT
    AND "@ВидЦеныДокумент" = ANY($3::INT[])
    AND "ТипСвязи" IS NOT NULL
RETURNING "@ВидЦеныДокумент";
```

`$3` — список `@ВидЦеныДокумент` (PK корешков), в отличие от стандартного пути где `$3` — `"Документ"` (ID сделок).

### История

Для SABYBANK-пути история **не пишется** — у корешков нет записей в сервисе маркетинга (`get_sales_sources_lead_info` не применимо).

### Рефакторинг _write_to_history

Сигнатура изменена: принимает `referral_program: ReferralProgram` вместо `program_id: int`, убран внутренний вызов `ReferralProgramRepository.read`. Избавляет от двойного запроса к БД.

## Документация обновлена в .orx

В `ReferralProgram.orx` обновлены:
- Комментарий метода: упоминание SABYBANK / корешков
- `selection.marked`: описание двух вариантов ID
- Return: «обновленных записей» вместо «сделок»

## Тест

**Файл:** `tests/tests_priceformationonline/referralprogram/referralprogram/set_lead_price.py`

`test_2_sabybank_stub`:
1. Создаёт программу + партнёра + эмиссию вручную (по образцу `create_stub.py`)
2. Создаёт корешок через `sbis.ReferralProgram.CreateStub`
3. Мокирует `ReferralProgramRepository.read` → `program_type = ProgramType.SABYBANK`
4. Вызывает `SetLeadPrice(marked=[stub.id], price=500)`
5. Проверяет `updated == 1` и `bonuses == 500`

> Важно: кастомная ORM (`tests_helpers.db.orm.core`) не создаёт `field_id` accessor для ForeignKey. Используй `partner.id` напрямую, не `referral_code.person_id`.
