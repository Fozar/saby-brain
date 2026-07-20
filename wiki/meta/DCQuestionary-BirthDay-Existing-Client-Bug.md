---
type: decision
address: c-000196
title: "Анкета выдачи ДК — не проставляется дата рождения существующему клиенту"
created: 2026-07-20
updated: 2026-07-20
tags:
  - bugfix
  - price-formation
  - dcquestionary
  - discountcard
  - crmclients
  - crm-integration
status: fixed
related:
  - "[[ImportDiscountCard-Franchise-Client-Import]]"
  - "[[PriceFormation-Backend-Architecture]]"
---

# Анкета выдачи ДК — не проставляется дата рождения существующему клиенту

Задача №0625711 (Ошибка на стенде): https://dev.sbis.ru/opendoc.html?guid=019efce3-392a-7ed5-9928-2cd65865c38e&client=3

## Симптом

При выдаче дисконтной карты через анкету (`Бизнес → скидки и акции → дисконтные карты`, `cardTypeId=9080`) существующему клиенту без указанной даты рождения — дата рождения не проставляется в карточку клиента. Для новых клиентов работает исправно.

## Root cause: собственная регрессия от апрельского фикса

MR !141867 (коммит `dc4e7882`, 2026-04-23, ветка `26.2220/bugfix/aatimoshenko/04201386`) в рамках фикса **другого** бага (задача `8c629584-c23b-48a1-9056-225541dc7897` — анкета недопустимо перезаписывала уже заданную ДР существующего клиента) убрал `'BirthDay'` из `update_fields` в `_get_or_create_customer` (`priceformationonline/dcquestionary/discountcardquestionary/create_card.py`):

```diff
-    update_fields = ['BirthDay', 'Gender', 'Email', 'PartialAddFieldsValues']
+    update_fields = ['Gender', 'Email', 'PartialAddFieldsValues']
```

Это устранило перезапись, но заодно исключило любую возможность впервые проставить ДР существующему клиенту, у которого она не была указана. Классический «блант-фикс»: вместо условной логики («обновлять только если пусто») поле было исключено из обновления целиком.

## Ключевая находка: CRMClients.GetCustomerOrCreate не умеет "update if empty"

`CRMClients.GetCustomerOrCreate.MethodOptions.UpdateFields` — это плоский список полей для безусловного обновления существующего клиента; условной семантики «обновить, только если поле пусто» метод не поддерживает (подтверждено Лукьяновым Н., ответственным за метод, в переписке по задаче 2026-07-13). Это общий паттерн, актуальный для любого поля CRM-клиента (не только BirthDay), которое нужно «дозаполнить, но не перезаписать».

**Рекомендованный им обходной путь** (переиспользуемый рецепт):
1. Добавить `MethodOptions.NeedSearchResult=True` в вызов `GetCustomerOrCreate`.
2. Прочитать нужное поле из `result.Get('SearchResult')` — это снимок найденного клиента ДО применения `SaveParams`/`UpdateFields`.
3. Если поле там пусто — отдельным точечным вызовом `CRMClients.SaveCustomer(sbis.Record({'CustomerID': ..., '<Field>': ...}))` установить значение.

### Форма ответа GetCustomerOrCreate — CustomerID может быть и в корне, и в SearchResult

Локально в price-formation нет задокументированного контракта ответа `GetCustomerOrCreate`. Два разных вызывающих читают `CustomerID` по-разному:
- `create_card.py` (без `NeedSearchResult`) — `result.Get('CustomerID')` из корня.
- `process_file.py` (импорт клиентов, см. [[ImportDiscountCard-Franchise-Client-Import]]) — `result.Get('SearchResult').Get('CustomerID')`; та же страница фиксирует: «Оба метода (`CreateCustomerWithConfirmedPerson` и `GetCustomerOrCreate`) возвращают `SearchResult.CustomerID`» — т.е. `SearchResult` присутствует в ответе независимо от `NeedSearchResult`, а корневой `CustomerID` в `create_card.py`, видимо, дублирует то же значение.

Поскольку эмпирически проверить нельзя без юнит-тестов на реальном стенде, в фиксе применён **защитный фолбэк**: `customer_id = result.Get('CustomerID') or (search_result.Get('CustomerID') if search_result else None)` — работает независимо от того, куда платформа фактически положит поле.

## Fail-closed guard (важный урок ревью)

Первая версия guard'а была `if not search_result.Get('BirthDay'):` без проверки `search_result` на истинность — если `SearchResult` вдруг не пришёл (`None`), `not None` = `True` → код записал бы ДР без всякой проверки, воспроизведя **тот самый** баг, который апрельский MR устранял. Правильная защита — **fail closed**: писать только когда `SearchResult` присутствует и **положительно подтверждает** пустоту поля:

```python
if not is_new_customer and birth_day and search_result and not search_result.Get('BirthDay'):
    with Try('Не удалось обновить дату рождения существующего клиента, ошибка:'):
        sbis.CRMClients.SaveCustomer(sbis.Record({'CustomerID': customer_id, 'BirthDay': birth_day}))
```

Мягкий `Try(...)` (без `new_error`/`with_exc`) — та же логирующая, не блокирующая обработка ошибок, что уже использовалась в этом файле для необязательных побочных эффектов (начисление за реф. программу). Выдача карты не должна падать из-за неудачного дозаполнения ДР — цепочка `create_card → get_or_create_client → _get_or_create_customer` в принципе не обёрнута в транзакцию.

## Что НЕ исправлено (смежные находки, отдельные задачи)

Та же категория проблемы («безусловная перезапись BirthDay через UpdateFields») существует ещё в двух местах, без связанных жалоб:
- `loyaltyprograms/loyaltyprogram/helpers.py:1218` (`get_or_create_customer_by_personal_data`) — включает `BirthDay` в `UpdateFields`, если передан `BirthDate` и `update_existing_client=True`.
- `discountcard/importdiscountcard/process_file.py:283-296` (`ClientImportProcessor.save`, см. [[ImportDiscountCard-Franchise-Client-Import]]) — `UpdateFields = ['BirthDay', 'Gender', 'ContactData', 'Address']`, `SearchResult.BirthDay` никогда не читается — т.е. при батч-импорте дата рождения существующего клиента может быть молча перезаписана.

По правилам регламента «Ошибка» — не исправляются в рамках этой задачи (нет отдельной жалобы, риск расширения фикса).

## Тесты

`tests/tests_priceformationonline/dcquestionary/discountcardquestionary/create_card.py`, класс `GetOrCreateClient`, новый параметризованный тест `test_birth_day_update_for_existing_client` (3 кейса: существующий клиент без ДР → `SaveCustomer` вызван; существующий клиент с ДР → не вызван; новый клиент → не вызван). Существующие `test_get_customer_or_create_call*` обновлены под `NeedSearchResult: True`.

## Статус

Реализовано, тесты зелёные. Коммит — по формату `<описание на русском> + ссылка на задачу &client=3`, только после явного одобрения пользователя (правило проекта price-formation: коммит не создаётся по инициативе агента).
