---
type: session
address: c-000012
title: "PromoCode SafeDelete — промокод остаётся в Sabyget после удаления"
created: 2026-05-14
updated: 2026-05-19
tags:
  - bugfix
  - promocode
  - sabyget
  - sdk-notification
  - individual-promo-code
  - discount-cards
status: needs-action
related:
  - "[[Promocode-Subsystem-Overview]]"
  - "[[DWC-Promocode-Events-Migration]]"
  - "[[SabyGet-Loyalty-Subsystems]]"
  - "[[DiscountCard-Subsystem-Overview]]"
---

# PromoCode SafeDelete — промокод остаётся в Sabyget после удаления

**Статус:** Правки в `price-formation` **НЕ коммитить**. Правильный фикс — в `discount-cards` (одна строка SQL). Нужно передать ответственному за SDK.

## Суть бага

После удаления индивидуального промокода через крестик в онлайн-админке промокод продолжает отображаться у клиента в разделе «Промокоды» в Sabyget. Воспроизводится с и без фичи `dwc_promocode_type`.

`PromoCode.SafeDelete(Id: 6531)` → `{"Deleted": [], "SetNotUsed": [6531]}` — прошла деактивация (первый нажим X). Второй нажим дал бы `Deleted`.

## Структура данных

```
"ВидКарты"[ROOT]  — Тип=6 (Individual), Раздел=NULL, id=X
  └── "ВидКарты"[EMISSION]  — Тип=6, Раздел=ROOT, id=Y
        └── "Карта"[CARD]  — Эмиссия=EMISSION, Лицо=person_id
```

В discount-cards зеркалируется как:
```
CardType[CTHead]  — OnlineCardTypeID=X, Folder=NULL
CardType[CT]      — OnlineCardTypeID=Y, Folder=X
Card[C]           — PersonID=person_id, OnlineCardTypeID=Y
```

## Два канала уведомления

| Событие | Обновляет | Что проверяет Sabyget |
|---|---|---|
| `publish_promocode_type_data_changed` | `CardType.Enabled` | CT."Enabled" (EMISSION) — да; CTHead."Enabled" (ROOT) — **нет** |
| `notify_on_promo_code_change_bulk` | `Card.Enabled` | C."Enabled" |

## Фильтр Sabyget (`SQL_ACTIVE_PROMOCODE_CONDITION_TMPL`)

```sql
CT."Enabled"        -- Enabled EMISSION (NOT ROOT)
AND C."Enabled"     -- Enabled Card
AND (CT."Info"->>'EndDate') IS NULL OR ... >= CURRENT_DATE
AND (C."Info"->>'EndDate') IS NULL OR ... >= CURRENT_DATE
```

`CTHead` (ROOT) уже джойнится в `_SQL_GET_PROMOCODES`:
```sql
LEFT JOIN "CardType" CTHead
    ON CT."ClientID" = CTHead."ClientID" AND CT."Folder" = CTHead."OnlineCardTypeID"
```

Но `CTHead."Enabled"` **не проверяется в WHERE**.

## Root cause

`disable_promo_codes` вызывает `publish_promocode_type_data_changed(PromocodeTypeID=ROOT_ID, Enabled=False)` → обновляет `CTHead.Enabled=False` в discount-cards. Но Sabyget не читает `CTHead.Enabled` в фильтре → ROOT деактивирован, а промокод остаётся видимым.

Баг существует с марта 2023 (с момента появления `disable_promo_codes`).

## Правильный фикс: discount-cards SQL (одна строка)

В файле `discount-cards/www/DCService/dcservice/sabyget/promocode/get_list.py`, в `SQL_ACTIVE_PROMOCODE_CONDITION_TMPL` добавить:

```sql
CT."Enabled"
AND C."Enabled"
AND (CTHead."OnlineCardTypeID" IS NULL OR CTHead."Enabled")  -- ← добавить
AND (CT."Info"->>'EndDate') IS NULL OR ...
AND (C."Info"->>'EndDate') IS NULL OR ...
```

`IS NULL` нужен для не-индивидуальных типов (`PROMOCODE_FOR_PURCHASE`), где CTHead = NULL (LEFT JOIN).

**Почему это правильнее** чем фикс в price-formation:
- Существующий `publish_promocode_type_data_changed` уже корректно синкает ROOT.Enabled в discount-cards
- Restore (активация ROOT обратно) работает автоматически через тот же механизм — без дополнительного кода
- Нет риска затереть `UseLimit`/`EndDate` через JSONB merge
- Нет дополнительных SQL-запросов и уведомлений при SafeDelete

## Что было сделано в price-formation (НЕ коммитить)

В ходе расследования внесены изменения, которые решают баг, но сложнее правильного фикса:

### `safe_delete_core.py`
- Добавлен вызов `notify_on_promo_code_change_bulk(Enabled=False)` в `disable_promo_codes` для `PromoCodeType.Individual`
- Проблема: передача `UseLimit: None` и `EndDate: None` → JSONB merge `||` затирает существующие значения → промокод становится безлимитным и без даты истечения

### `update.py`
- Добавлена функция `_notify_individual_cards_on_restore` — симметричный вызов при восстановлении (IsActive: False→True)
- Та же проблема с None-значениями

### `tests/safe_delete.py`
- Добавлен тест `test_disable_individual_notifies_sabyget` (патчит `notify_on_promo_code_change_bulk`)

### `tests/update.py`
- Добавлены `test_restore_individual_notifies_sabyget`, `test_update_active_individual_does_not_notify`

## JSONB-уязвимость (почему None-значения опасны)

В discount-cards обработчик делает:
```sql
"Info" = COALESCE("Info", '{}')::JSONB || !Info::JSONB
```

`PROMOCODE_INFO_DATA_FIELDS = CARD_INFO_DATA_FIELDS + ['EndDate', 'UseLimit']`

Если передать `UseLimit: None` — JSONB merge запишет `null` поверх существующего лимита → промокод становится безлимитным. Аналогично для `EndDate`. Для fix этого нужен отдельный SQL-запрос к `Карта` перед уведомлением.

## Тест (написан, но при коммите discount-cards-фикса становится неактуальным)

```python
@patch('priceformationonline.loyaltyprograms.promocode.safe_delete_core.notify_on_promo_code_change_bulk')
def test_disable_individual_notifies_sabyget(self, mock_notify):
    promo_code_type = IndividualPromoCodeEmission.create(name='Test Individual')
    emission = IndividualPromoCodeEmission.create(
        name='Test Emission', is_enabled=1, is_folder=False, folder=promo_code_type
    )
    promo_code = IndividualPromoCode.create(emission=emission)
    result = sbis.PromoCode.SafeDelete(sbis.Record({'Id': [promo_code_type.id]}))
    self.assertEqual(result.SetNotUsed, [promo_code_type.id])
    mock_notify.assert_called_once()
    self.assertEqual(mock_notify.call_args[0][0][0]['PromocodeID'], promo_code.id)
    self.assertFalse(mock_notify.call_args[0][0][0]['Enabled'])
```

## Переписка с Кузаковым (2026-05-19)

Передано Кузакову Юрию (ответственный за SDK/discount-cards) с комментарием:

> SabyGet данные получают с СДК. Анализ стоит оттуда начать. Событие при деактивации типа промокода отправляется. Метод СДК, который вызывает SabyGet — смотрит ли он на признак активности типа промокода или возвращает ли его в результате?

**Ответ Кузакова 1:** Попросил приложить логи.

**Ответ Кузакова 2 (после получения логов SafeDelete):**
> Удалить по крестику (НЕ перевод в недействующие, а именно удалить). А ты привёл логи деактивации.

→ Кузаков перепутал «удалить по крестику» с hard delete. На самом деле первый клик = SafeDelete → деактивация (`SetNotUsed`), второй клик = физическое удаление (`Deleted`). Этот сценарий — именно деактивация.

**Ответ Кузакова 3 (после уточнения):**
> А в Update какие события публикуются?

→ Кузаков сравнивает SafeDelete с Update. Скорее всего проверяет: отличается ли набор событий, и работает ли деактивация через Update корректно в Sabyget.

**Ключевое отличие Update vs SafeDelete** (код: `core.py:notify_on_card_type_change`, строки 846-870):

`PromoCode.Update` вызывает `notify_on_card_type_change`, которая для `PROMO_CODE_INDIVIDUAL`:
1. Шлёт `publish_promocode_type_data_changed(PromocodeTypeID=ROOT, Enabled=IsActive)` — ROOT
2. Делает `IndividualPromoCodeEmission.GetList(PromoCodeTypeId=ROOT)` — получает все EMISSION-ы
3. Для каждой EMISSION шлёт `publish_promocode_type_data_changed(PromocodeTypeID=EMISSION_ID, Enabled=IsActive)`

→ discount-cards получает событие для EMISSION → `CT.Enabled=False` → Sabyget фильтрует → **работает**.

`SafeDelete` вызывает `disable_promo_codes`, которая шлёт событие только для ROOT (по `promo_code.Id` из входных данных, где только ROOT_ID):
→ discount-cards обновляет `CTHead.Enabled=False` (ROOT), но `CT.Enabled` (EMISSION) остаётся True → Sabyget не фильтрует → **баг**.

Фикс в discount-cards (добавить `CTHead.Enabled` в WHERE) решает SafeDelete. При этом Update продолжает работать как раньше (через CT.Enabled).

**Статус:** Ждём фикса от Кузакова Ю. в `discount-cards`.
