---
type: concept
title: "Таймаут генерации 20 000 промокодов (№10304201)"
created: 2026-11-02
updated: 2026-11-02
status: testing
tags: [price-formation, promocode, test-stand, bugfix]
related:
  - "[[PromoCode-Generation-Memory-Optimization]]"
  - "[[Promocode-Subsystem-Overview]]"
---

# Таймаут генерации 20 000 промокодов

## Задача
Ошибка на стенде №10304201, веха 26.6100, Рыбкин А.С.
https://online.sbis.ru/opendoc.html?guid=01a18bd7-655d-7e4a-ad25-6c5df56017cb&client=3
Приемочные автотесты (TestIndCodeRules01.test_01_field_quantity): при генерации 20 000 промокодов падает ошибка «Не удается сгенерировать промокоды, настройте правило генерации».

## Где остановились
Ветка `26.6100/bugfix/aatimoshenko/10304201` от `origin/rc-26.6100`.
Реализован фикс в `individual_promo_code_emission/generate.py`:
1. `PromoCodesGenerator`: таймаут `_MAX_GENERATION_TIME_FOR_CHUNK` (3 сек) теперь учитывает только чистое процессорное время генерации кандидатов в Python (`generation_time`), исключая ожидание SQL-запроса `_filter_taken`. Убрана ложная проверка таймаута после сбора кодов при `len(generated_numbers) >= amount`.
2. `sql_filter_existing_numbers`: добавлено условие `"Номер" IS NOT NULL` для попадания в частичный индекс `CaseInsensitiveUniqueNumber`.
Добавлены 2 юнит-теста в `tests/.../individual_promo_code_emission/generate.py`:
- `test_filter_taken_slow_does_not_timeout_when_gathered` (красный до фикса, зеленый после)
- `test_generation_timeout_on_exhausted_combinations` (проверка реального таймаута при исчерпании комбинаций)

## Что выяснено по коду
- 20 000 промокодов генерируются двумя пачками по 10 000 (`_INSERT_CHUNK_SIZE`).
- При генерации второй пачки `sql_filter_existing_numbers` проверял 10 000 кандидатов запросом с `ANY($1::text[])`. Без `"Номер" IS NOT NULL` Postgres не применял частичный индекс `CaseInsensitiveUniqueNumber` (у которого в предикате `"Номер" IS NOT NULL`), запрос занимал ~2.9 сек.
- Суммарное время с генерацией превышало 3.0 сек, и таймаут выбрасывался даже после успешного сбора всех 10 000 кодов пачки.

## Решения и почему
- Таймаут 3.0 сек предназначен для защиты от бесконечного цикла подбора случайных уникальных комбинаций при исчерпании алфавита/длины, а не для ограничения времени I/O к БД. Поэтому он накапливает только время работы генератора в Python (`time.monotonic() - gen_start`).
- Добавление `"Номер" IS NOT NULL` в WHERE обеспечивает использование индекса `CaseInsensitiveUniqueNumber`.

## Roadmap
- [x] Согласовать коммит с пользователем
- [x] Закоммитить и запушить ветку
- [x] Создать MR в rc-26.6100
- [ ] Проверка ревью и автотестов
- [ ] Проверка на стенде

## Ссылки
- Коммит: `a2151c2dd7`
- Ветка: `26.6100/bugfix/aatimoshenko/10304201`
- Документ MR: [01a19baf](https://online.sbis.ru/opendoc.html?guid=01a19baf-9b16-7c62-a0c5-bba669eaf61d&client=3) (#634567950)
- GitLab MRs: !153448, !153449, !153450
