---
type: concept
address: c-000052
title: "ImportDiscountCard DCS Counter Bug"
created: 2026-05-18
updated: 2026-05-18
tags:
  - discount-card
  - import
  - dcs
  - bugfix
  - process-file
status: resolved
related:
  - "[[DiscountCard-Subsystem-Overview]]"
  - "[[ImportDiscountCard-Franchise-Client-Import]]"
  - "[[FranchiseCard-Import-POS-SaleValidation-Bug]]"
---

# ImportDiscountCard DCS Counter Bug

## Симптом

После импорта дисконтных карт через `ImportDiscountCard.ProcessFile` счётчик карт под типом карты в реестре инсайда (`discount-card-admin`) не увеличивается. При ручной выдаче карты счётчик увеличивается корректно. Задача: 05134174.

## Root Cause

В `_parse_data` (файл `process_file.py`) возвращаемое значение `_extract_cards_from_data` не присваивалось переменной:

```python
# Было (баг):
cards_id_list = []
self._extract_cards_from_data(data)   # return value discarded
# cards_id_list всегда == []

# Стало (фикс):
cards_id_list = self._extract_cards_from_data(data)
```

`_extract_cards_from_data` внутри себя строит список card_id и возвращает его, но результат игнорировался. В итоге `cards_id_list` всегда был пустым, `if cards_id_list:` никогда не выполнялся, и `async_notify_changed_cards` не вызывался.

Как следствие, сервис дисконтных карт (СДК) не получал событие `online.loyalty-card.card-data.changed` и не знал о созданных картах — счётчик в реестре не обновлялся.

## Смежный баг с франшизными картами

Ранее ([[FranchiseCard-Import-POS-SaleValidation-Bug]]) аналогичная проблема была обнаружена только для франшизных карт — их фиксили отдельным явным вызовом `async_notify_changed_cards([card.card_id])` в `_handle_franchise_card_post_save`. Это работало, но создавало дублирующую логику.

После основного фикса (возврат значения из `_extract_cards_from_data`) отдельный вызов в `_handle_franchise_card_post_save` стал избыточным — батчевый вызов в конце `_parse_data` покрывает все карты, включая франшизные. Он был удалён.

## Итоговые изменения

**`process_file.py`** (два изменения):

1. `_parse_data` строка 1586 — присвоение возвращаемого значения:
   ```python
   cards_id_list = self._extract_cards_from_data(data)
   ```

2. `_handle_franchise_card_post_save` — убран дублирующий вызов `async_notify_changed_cards`:
   ```python
   @staticmethod
   def _handle_franchise_card_post_save(card, client):
       if client and client.id_:
           get_or_create_personal_card_ext(client.id_)
       # async_notify_changed_cards убран — покрывается батчем в _parse_data
   ```

**`tests/…/importdiscountcard/process_file.py`** (тесты):

- `test_franchise_notifies_dcs_after_import` — поднят с уровня `_parse_card` на `_parse_data`, `_parse_client` мокируется через `patch.object(FileParser, '_parse_client', ...)`
- `test_regular_card_notifies_dcs_after_import` — новый тест, проверяет что обычная (нефраншизная) карта тоже вызывает `async_notify_changed_cards`

## Паттерн: мёртвый код из-за потерянного return value

```python
# Типичная ошибка: метод что-то возвращает, но вызывается как процедура
result = []
self._build_result(result_arg)  # возвращает список, но мы его не ловим
if result:  # всегда False
    do_something(result)
```

Обнаруживается только при ревью или через наблюдаемый side-effect (отсутствие уведомления).

## Логи и диагностика

- Лог `выдача карт pre-test-online-18-05-2026` — `ProcessFileLRS` выполнен, событие `card-data.changed` **отсутствует**
- Профилирование — `_parse_data` завершается за 1272 мс/24 карты, `async_notify` не вызывается
- После фикса: батч `async_notify_changed_cards(cards_id_list)` отправляет все card_id разом в конце `_parse_data`