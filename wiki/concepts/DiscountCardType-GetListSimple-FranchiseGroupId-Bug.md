---
type: concept
title: "Bug: DiscountCardType.GetListSimple returns empty with FranchiseGroupId=non-UUID"
updated: 2026-04-14
tags:
  - bug
  - discount-cards
  - loyalty
  - offline
  - retail
status: current
related:
  - "[[DiscountCard-Subsystem-Overview]]"
  - "[[Loyalty-Desktop-Broker-Migration]]"
created: 2026-04-14
---

# Bug: DiscountCardType.GetListSimple returns empty with FranchiseGroupId=non-UUID

**Задача/ошибка:** 4283565 — «Не отображаются типы карт в разделе Дисконтные карты офлайн приложения»
**Окружение:** Розница офлайн 26.1213
**Дата:** 2026-04-10
**Серьёзность:** Незначительная (клиент 9 672 730)

---

## Симптом

Раздел «Дисконтные карты» в офлайн-приложении показывает пустой список типов карт.
Помогало пересоздание БД, но проблема повторялась.

## Диагностика

### Что НЕ является причиной

Синхронизация карт (старый механизм, без фич) работает корректно:
- `PFSync.GetEmission` → вызывается каждые ~10 мин, отрабатывает без ошибок
- `sync_emission` возвращает `{Updated: null, Deleted: null, Inserted: null}` — данные в локальной БД актуальны
- Данные в локальной таблице `ВидКарты` **есть**

### Реальная причина

Фронтенд делает **два** вызова `DiscountCardType.GetListSimple`:

| # | Лимит | ДопПоля | Фильтр | Результат |
|---|---|---|---|---|
| 1 | 2 | `[]` | пустой | ✅ 2 записи (авто-провал в единственный тип) |
| 2 | 20 | `ShowClientCount, ShowDesignSettings, meta/isFranchiseeAccount` | `FranchiseGroupId="retail"`, `IsActive=true`, `Period=[2026-03-01, 2026-03-31]` | ❌ 0 записей |

Второй вызов (для отображения реестра) передаёт `FranchiseGroupId = "retail"`.

### SQL-механизм фильтра

В `_sql_get_list_simple` (`get_list_simple.py`):
```sql
{% item ifnotnull FranchiseGroupId %}
    vc."Атрибуты" -> 'FranchiseUUIDList' @> to_jsonb(array[!FranchiseGroupId::text])
{% enditem %}
```

Условие проверяет, содержит ли JSONB-массив `FranchiseUUIDList` переданную строку.
В `FranchiseUUIDList` хранятся UUID-ы (`xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`).
Строка `"retail"` не является UUID → совпадений нет → **0 строк**.

### Прочие поля фильтра

- `IsActive=true` — не причина: limit=2 без IsActive тоже возвращает 2 активных карты
- `Period=[...]` — бэкенд его не обрабатывает, молча игнорируется (не задокументировано)

## Локация кода

- **Метод:** `DiscountCardType.GetListSimple`
- **Файл:** `www/service/Модули/PriceFormation.Common/priceformationcommon/discountcard/discountcardtype/get_list_simple.py`
- **SQL-условие:** строки ~306-307 (`ifnotnull FranchiseGroupId`)
- **Построение params:** ~382-390 (цикл по filter_ полям)

## Решение

Проблема на стороне **фронтенда**: при вызове реестра передаётся `FranchiseGroupId = "retail"` вместо `null`.
Бэкенд воспринимает это как валидный UUID для поиска в `FranchiseUUIDList`, результат всегда пустой.

Фронтенд должен:
- Не передавать `FranchiseGroupId` (или передавать `null`) когда фильтрация по группе франшизы не нужна
- Либо передавать реальный UUID группы франшизы

Возможный backend-guard: валидировать что `FranchiseGroupId` является UUID перед добавлением в params фильтра.

## Паттерн: как отлаживать «пустой список» в офлайне

1. Проверить `MainService-client.log` — найти вызовы `GetListSimple`, посмотреть REQUEST + RESPONSE
2. Сравнить два вызова (авто-провал с limit=2 vs реестр) — разница в фильтрах
3. Проверить `MainService-events.log` на `sync_emission` — убедиться что данные в БД есть
4. Если sync в порядке, а list пустой — причина в фильтрах запроса к локальной БД