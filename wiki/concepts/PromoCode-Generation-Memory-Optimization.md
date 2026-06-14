---
type: synthesis
title: "PromoCode-Generation-Memory-Optimization"
created: 2026-06-10
updated: 2026-06-11
tags:
  - price-formation
  - promocode
  - performance
  - memory
  - postgresql
status: fixed
question: "Как генерировать уникальные промокоды с учётом существующих — быстро и дёшево по памяти, не выгружая всю таблицу Карта в Python?"
answer_quality: solid
related:
  - "[[Promocode-Subsystem-Overview]]"
  - "[[Promocode-Info-Model]]"
  - "[[Loyalty-Database-Schema]]"
  - "[[GetIndividualBatch-AttachPersonId-Timeout-Fix]]"
  - "[[Wasaby-BL-Advanced]]"
---

# Генерация промокодов без выгрузки существующих номеров в память

**Статус: реализовано 2026-06-11. Баг #06104810 (стенд dev.sbis.ru).**

## Проблема

`individual_promo_code_emission/generate.py` (строка ~142) перед генерацией выгружает **все** существующие номера заданной длины из таблицы «Карта» в питоновский `set`:

```python
existing_numbers = set(sql_get_existing_numbers(length))
promo_codes_generator = PromoCodesGenerator(character_sets, length, prefix, existing_numbers)
```

- `sql_get_existing_numbers` делает `array_agg("Номер") WHERE length("Номер") = $1 AND "ТипКарты" = 1` — условие по `length()` не покрыто ни одним индексом → полный скан + миллионы строк в памяти у крупных клиентов.
- Тот же паттерн продублирован в `activity_promo_code/generate.py:78`.

## Ключевые факты

- Уникальность номера **уже гарантирована БД**: уникальные индексы `UniqueNumber ("Номер", "ТипКарты")` и `CaseInsensitiveUniqueNumber (upper("Номер"), "ТипКарты")` — PriceFormation.Online.dicx:1881 и :1911. Держать копию всех номеров в Python не нужно.
- Кандидаты генерируются в верхнем регистре (алфавиты `digits`/`ascii_uppercase`, префикс upper-ится) → сравнение через `upper()` корректно.
- `_choose_promo_code_length` подбирает длину с запасом комбинаций (существующие × 1.1) → вероятность коллизии случайного кандидата мала, цикл догенерации сходится за 1–2 итерации.

## Решение

Инвертировать проверку: вместо «выгрузи всё и проверяй в памяти» — «сгенерируй чанк кандидатов и спроси у БД, какие заняты», одним индексным запросом:

```sql
SELECT array_agg(upper("Номер"))
FROM "Карта"
WHERE upper("Номер") = ANY($1::text[])
  AND "ТипКарты" = 1  -- ItemNumberType.PROMO_CODE
```

Запрос попадает в `CaseInsensitiveUniqueNumber` → O(chunk · log N). Память O(chunk ≤ 10 000) вместо O(всех карт).

### Реализованные изменения

**Ветка:** `rc-26.4100` (коммит к задаче #06104810).

#### 1. `individual_promo_code_emission/generate.py`

Новая функция `sql_filter_existing_numbers` заменила `sql_get_existing_numbers`:

```python
def sql_filter_existing_numbers(candidates: list[str]) -> set[str]:
    if not candidates:
        return set()
    query = f"""
        SELECT array_agg(upper("Номер"))
        FROM "Карта"
        WHERE upper("Номер") = ANY($1::text[])
          AND "ТипКарты" = {ItemNumberType.PROMO_CODE}
    """
    result = sbis.SqlQueryScalar(query, candidates)
    return set(result) if result else set()
```

`PromoCodesGenerator.__init__` изменён: `excluded_numbers: Set[str]` → `filter_taken: Optional[Callable[[List[str]], Set[str]]] = None`. Цикл `generate_numbers` батчевый: генерирует chunk → `filter_taken(batch)` → отбрасывает занятые (фиксируются в `_generated_numbers`) → повторяет до набора. Таймаут 3 с остаётся.

#### 2. `activity_promo_code/generate.py`

Обновлён импорт и паттерн создания генератора:
```python
promo_codes_generator = PromoCodesGenerator(
    character_sets, length, prefix, filter_taken=sql_filter_existing_numbers
)
```

#### 3. `individual_promo_code_emission/update.py` — устранение дублирования проверки лицензии

`generate()` и `update()` оба вызывали `License().process_for_sale_point_full()`. Фикс — внутренний параметр `_skip_license: bool = False` в `update()`:

```python
def update(input_data: RecordType, _skip_license: bool = False) -> str:
    ...
    if not _skip_license:
        License(...).process_for_sale_point_full()
```

Снаружи (через БЛ-фреймворк) параметр недоступен — фронтенд никогда не передаст его. Внутренние вызовы из Python:
```python
_update_emission(record, _skip_license=True)
```

Этот паттерн применим везде, где Python-функция за БЛ-методом дублирует проверки, уже выполненные вызывающим методом.

#### 4. Тесты (`tests/.../individual_promo_code_emission/generate.py`)

- `test_filter_taken_callback_excludes_occupied` — юнит с lambda-моком: занятые коды не попадают в результат
- `test_sql_filter_existing_numbers` — интеграционный: создаёт промокоды, проверяет что `sql_filter_existing_numbers` их находит, несуществующий не возвращает

Все 13 тестов ✓.

### Совместимость

- `estimate_available_codes.py` создаёт генератор без колбэка — дефолт `lambda candidates: set()` не ломает.
- `_choose_promo_code_length` / `_sql_count_existing_by_length` не менялись.
- `sql_insert_promo_codes` не менялся — вставка получает уже проверенный набор.
- Гонка параллельных генераций завершится ошибкой уникального индекса — как и прежде.

### Профиль производительности до фикса

Projector-отчёт показывал 5.689 с на `Generate/1`:
- 283 «безымянных» операции = 1658 мс (`CRMClients.AttachPersonId` в ParallelTasks внутри транзакции — откат этого изменения запланирован отдельно)
- `SalesPoint.ListFull` × 2, `LicenseCell.CheckByConsumers` × 2, `IsDemoClient` × 2 — дублирование из-за двойной проверки лицензии
- `EmissionTable.Read` × 3 — дублирование чтения эмиссии
