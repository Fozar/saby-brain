---
type: concept
title: "Bonus.GetTotalBalance — реализация и архитектура"
updated: 2026-04-10
tags:
  - loyalty
  - bonuses
  - franchise
  - sql
  - price-formation
  - sbis
status: current
related:
  - "[[Bonus-Programs-Architecture]]"
  - "[[Franchise-Loyalty-Architecture]]"
  - "[[Loyalty-Franchise-Mechanics]]"
  - "[[DiscountCard-Service-API]]"
  - "[[Wasaby-DB-Access-Patterns]]"
created: 2026-04-10
---

# Bonus.GetTotalBalance

Новый BL-метод (ORX: `Bonus.GetTotalBalance`) для получения суммарного бонусного баланса аккаунта.

**Файл**: `priceformationonline/loyaltyprograms/bonus/get_total_balance.py`

---

## Назначение

- **Локальный баланс** (не-франшизные карты) — из локальной БД через SQL
- **Франшизный баланс** — из СДК: `Card.GetBonusBalanceByCardType` (по UUID типа карты) и `Card.GetBonusBalanceByCards` (по UUID персональных счетов)
- **НЕ использовать**: `Card.GetBonusBalanceByClient` — возвращает ненадёжные данные

Правильная логика взята из `get_client_list_with_stats_totals`.

---

## Сигнатура

```python
@logging()
def get_total_balance(
        filter_: RecordType,
        *,
        _precomputed: RecordType | None = None,
) -> Decimal | None:
```

- `AgentGroupId` в filter_ — UUID бизнес-группы франшизы; партнёры (не владельцы) получают `None`
- `_precomputed` — оптимизация: если вызывающий уже выполнил SQL (например, `get_client_list_with_stats_totals`), повторный SQL не делается

> [!open-question] Открытые вопросы дизайна
> - Нужен ли `AgentGroupId` в `filter_` или он должен определяться иначе?
> - Нужен ли `_precomputed`?
> - Return type: `Decimal | None` или `int | None`?

---

## Логика расчёта

```
1. agent_group_id = filter_.Get('AgentGroupId')
2. Если agent_group_id задан И НЕ в owned_franchise_ids → return None (партнёр)
3. has_franchise = bool(FranchiseBusinessGroup.get_list())
4. SQL → balance_data (или _precomputed)
5. local_balance = balance_data.Get('AvailableBonusBalance') or 0
6. franchise_balance = SDK (card types) + SDK (personal cards with UUID)
7. total = local + franchise → int/Decimal или None если 0
```

---

## SQL: IsFranchise — ключевые паттерны

Два CTE используют **разные критерии** для `IsFranchise`:

### personal_accounts (Эмиссия IS NULL)
```sql
P."ИдентификаторФизЛица" IS NOT NULL AS "IsFranchise"
FROM "Карта" AS C
LEFT JOIN "ЧастноеЛицо" AS P ON P."@Лицо" = C."Лицо"
```
Персональная карта — франшизная, если физлицо имеет `ИдентификаторФизЛица` (UUID в сервисе профилей).

### cards_only (с эмиссией, Тип=0 или 2)
```sql
(
    (E."Атрибуты" ->> 'FranchiseRole')::INTEGER IS NOT NULL
    OR (EP."Атрибуты" ->> 'FranchiseRole')::INTEGER IS NOT NULL
) AS "IsFranchise"
```
Нумерованная карта — франшизная, если у эмиссии (или родительской папки) есть `FranchiseRole`.  
JOIN к `ЧастноеЛицо` не нужен — UUID физлица не требуется для `GetBonusBalanceByCardType`.

> [!key-insight] Разница между CTEs
> - `personal_accounts`: IsFranchise = person UUID присутствует (SDK вызов по UUID карты)
> - `cards_only`: IsFranchise = emission FranchiseRole присутствует (SDK вызов по UUID типа карты)

---

## SQL FILTER с `!has_franchise`

Паттерн из `get_client_list_with_stats.py` (строки 500–504):
```sql
SELECT
    SUM("AvailableBonusBalance")
        FILTER (WHERE NOT !has_franchise OR NOT "IsFranchise") AS "AvailableBonusBalance",
    ARRAY_AGG("ClientCardUUID")
        FILTER (WHERE !has_franchise AND "IsFranchise" AND "ClientCardUUID" IS NOT NULL) AS "ClientCardUUIDList",
    ARRAY_AGG(DISTINCT "CardTypeUUID")
        FILTER (WHERE !has_franchise AND "IsFranchise" AND "CardTypeUUID" IS NOT NULL) AS "FranchiseCardTypeUUIDList"
FROM combined
```

- `!has_franchise=false` → все карты в `AvailableBonusBalance`, SDK не вызывается
- `!has_franchise=true` → франшизные карты идут в SDK, не в локальный баланс

---

## FranchiseBusinessGroup.get_list() в тестах

> [!warning] Частая ошибка в тестах
> `FranchiseBusinessGroup.get_list()` — запрос к БД (НЕ EndPoint). Мок EndPoint не влияет на `has_franchise`.
>
> Для тестов с франшизным балансом нужно явно патчить:
> ```python
> with patch('priceformationonline.loyaltyprograms.bonus.get_total_balance.FranchiseBusinessGroup') as mock_fg:
>     mock_fg.get_list.return_value = [Mock()]  # has_franchise = True
> ```

---

## Баги, найденные при ревью

| Баг | Было | Стало |
|-----|------|-------|
| `personal_accounts.IsFranchise` | `TRUE` | `P."ИдентификаторФизЛица" IS NOT NULL` |
| JOIN в `cards_only` | `LEFT JOIN "ЧастноеЛицо"` (не используется) | Убран |
| SQL FILTER | без `!has_franchise` | Добавлен `!has_franchise` во все FILTER |
| Дублирование | `filter_.Get('AgentGroupId')` повторно в SQL-функции | Убрано, AgentGroupId не нужен в SQL params |

---

## SDK-хелперы

```python
_get_balance_by_cards(card_uuids)
    → sbis.EndPoint(ServiceName.discount_cards).Card.GetBonusBalanceByCards(uuids)
    → dict[CardUUID, Bonus] или None при ошибке (+ WarningMsg)

_get_balance_by_card_type(agent_group_id, card_type_uuid)
    → sbis.EndPoint(ServiceName.discount_cards).Card.GetBonusBalanceByCardType(uuid)
    → float или None при ошибке/партнёрской роли
```

---

## Связанные файлы

- `get_total_balance.py` — новый BL-метод
- `get_client_list_with_stats.py` — источник правильной логики (строки 370–863)
- `tests/.../loyaltyprograms/bonus/get_total_balance.py` — 8 тестов
