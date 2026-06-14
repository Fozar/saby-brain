---
type: decision
title: "ReferralProgram.DetachPartner — Реализация для AT"
created: 2026-04-12
updated: 2026-04-12
decision_date: 2026-04-12
status: active
tags:
  - price-formation
  - referral
  - autotesting
  - bl-method
  - implementation
related:
  - "[[AT-Coverage-ReferralDeals-Project]]"
  - "[[ReferralDeals-System]]"
  - "[[Loyalty-Database-Schema]]"
---

# ReferralProgram.DetachPartner — Реализация для AT

Navigation: [[AT-Coverage-ReferralDeals-Project]] | [[ReferralDeals-System]] | [[Loyalty-Database-Schema]]

Новый BL-метод для обеспечения повторяемости AT-сценариев Этапа 6 проекта [[AT-Coverage-ReferralDeals-Project]].

---

## Проблема

После первого присоединения партнёра к офферу метод `join()` блокирует повторный Join через `is_referral_code_exists_for_partner`. Для AT-сценариев нельзя создавать новых партнёров/офферы на каждый прогон — это засоряет схемы и ломает тесты через несколько дней.

---

## Решение: `ReferralProgram.DetachPartner`

Выбран **DetachPartner** (не ForceDelete), так как он хирургичнее: удаляет только реферальный код партнёра, позволяя переиспользовать один оффер в цикле AT.

### Ограничения безопасности

- Защита от боя: `sbis.CloudEntity.SysName() == 'prod'` → `sbis.Error`
- Роль: `OWNER_MODERATOR` (аналогично `SafeDelete`)
- `access_mode="0"` — только под владельцем, не публичный API

---

## Изменённые файлы

| Файл | Действие |
|------|----------|
| `priceformationonline/referralprogram/referralprogram/core.py` | +`SQL_GET_REFERRAL_CODE_CARD` + `get_referral_code_card()` |
| `priceformationonline/referralprogram/referralprogram/detach_partner.py` | Новый файл |
| `ReferralProgram.orx` | +`<select>` для `ReferralProgram.DetachPartner` |
| `tests/...referralprogram/detach_partner.py` | 4 unit-теста |

Все пути от `www/service/Модули/PriceFormation.Online/`.

---

## Логика удаления

```python
# 1. Проверка prod-стенда
if sbis.CloudEntity.SysName() == 'prod':
    raise sbis.Error('Метод нельзя вызывать на бою')

# 2. Получить @Карта + UUID
card_id, identifier = get_referral_code_card(referral_program_id, partner_id)

# 3. Транзакция
with sbis.CreateTransaction(READ_COMMITTED, WRITE):
    delete_source_by_ext_id([str(identifier)], [SourceType.REFERRAL_CODE])  # CRM source
    sbis.SqlQuery('DELETE FROM "ВидЦеныДокумент" WHERE "Карта" = $1', card_id)  # FK зависимость
    sbis.SqlQuery('DELETE FROM "Карта" WHERE "@Карта" = $1', card_id)
```

### Порядок операций в транзакции

1. Удалить CRM-источник (`AdObject.DeleteByExtId`)
2. **Превентивно** удалить `ВидЦеныДокумент."Карта" = card_id`
3. Удалить `Карта` запись

---

## Анализ FK-зависимостей

`ВидЦеныДокумент."Карта"` имеет тип `LINK1-N` с `on_delete="0"` (RESTRICT) → прямой DELETE из `Карта` упадёт, если есть зависимые строки.

### Когда `ВидЦеныДокумент` содержит строки для реферального кода

| Сценарий присоединения | Создаёт `ВидЦеныДокумент`? |
|---|---|
| Копирование реферальной ссылки | Нет |
| Копирование ссылки на виджет | Нет |
| Виджет «Станьте участником» (`JoinByPartner`) | Нет |
| Отправка заявки (`CreateLead`) | **Только если** сделка закрыта успешно → `HandleLeadStateChanged` → `save_bonus_processing` |

Для чистых AT-сценариев присоединения строки в `ВидЦеныДокумент` не создаются. Превентивное удаление покрывает случай полного AT-цикла (join → заявка → закрытие).

### Цепочка зависимостей при Join

Все методы присоединения ведут к одному коду:
- `JoinByPartner` → `multitenancy.CreateMultitenantEndpointByClientId(owner).ReferralProgram.Join()`
- `CreateLead` → если не присоединён → `sbis.ReferralProgram.Join()`
- Любой виджет присоединения → `JoinByPartner`

Итог: всегда создаётся ровно одна запись в `Карта` + один `AdObject` в CRM. Других зависимостей нет.

---

## .orx запись

```xml
<select access_mode="0" call_timeout="15000" category="Join" is_service="0"
        module_api_part="1" name="ReferralProgram.DetachPartner"
        responsible="Тимошенко А.А." responsible_uuid="0862a7d6-c1c6-4642-81aa-685d2e2400cb"
        returns="SCALAR" type="PYTHON">
  <parameter name="ReferralProgramId"><format><not_null>true</not_null><type>INTEGER</type></format></parameter>
  <parameter name="PartnerId"><format><not_null>true</not_null><type>INTEGER</type></format></parameter>
  <return name="___SBIS_SCALAR_RETURN___"><format><type>BOOLEAN</type></format></return>
</select>
```

---

## AT-цикл использования

```
ReferralProgram.GetPartnerList(...)     → партнёр есть
ReferralProgram.DetachPartner(id, pid) → true
ReferralProgram.GetPartnerList(...)     → партнёра нет
ReferralProgram.Join(id, null, pid)    → success (без «уже присоединён»)
↻ повторять неограниченно
```

---

## Тесты

- `test_detach_removes_card` — запись `@Карта` удалена из БД
- `test_detach_calls_delete_source` — `AdObject.DeleteByExtId` вызван с UUID карты
- `test_partner_not_joined_raises_warning` — `sbis.Warning` если партнёр не присоединён
- `test_detach_allows_rejoin` — после детача повторный `Join` проходит