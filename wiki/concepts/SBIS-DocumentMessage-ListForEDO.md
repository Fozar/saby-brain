---
type: concept
address: c-000059
title: "SBIS DocumentMessage.ListForEDO"
created: 2026-05-21
updated: 2026-05-21
tags:
  - saby
  - api
  - sbis-mcp
  - messaging
status: current
related:
  - "[[SBIS-Record-Format]]"
  - "[[SBIS-Internal-API-Methods]]"
  - "[[Saby-External-API-Tasks]]"
  - "[[Saby-API-Protocol]]"
---

# SBIS DocumentMessage.ListForEDO

`DocumentMessage.ListForEDO` — внутренний метод SBIS для получения списка диалогов (сообщений), привязанных к документу или задаче. Реализован как MCP-инструмент `sbis_list_task_messages` в проекте `sbis-mcp`.

---

## Запрос

Эндпоинт: `POST https://online.sbis.ru/service/` (стандартный JSON-RPC, [[Saby-API-Protocol]])

```json
{
  "jsonrpc": "2.0",
  "method": "DocumentMessage.ListForEDO",
  "params": {
    "Фильтр": {
      "s": {
        "appendLikes": "Логическое",
        "document":    "Строка",
        "fromTheme":   "Строка",
        "scroll":      "Строка",
        "toRequestOnly": "Строка"
      },
      "d": {
        "appendLikes":   true,
        "document":      "<document_uuid>",
        "fromTheme":     "<document_uuid>",
        "scroll":        "up",
        "toRequestOnly": "after"
      }
    },
    "Навигация": {
      "s": {
        "Direction": "Строка",
        "HasMore":   "Логическое",
        "Limit":     "Число целое",
        "Position":  "Запись"
      },
      "d": {
        "Direction": "forward",
        "HasMore":   true,
        "Limit":     20,
        "Position":  null
      }
    },
    "Сортировка": null,
    "ДопПоля": []
  },
  "id": 1
}
```

- `document` и `fromTheme` — один и тот же UUID документа/задачи.
- `scroll`: `"up"` — загружает более старые сообщения, `"down"` — более новые.
- `toRequestOnly`: `"after"` — не запрашивать дополнительно связанные документы.
- Фильтр и Навигация передаются в формате [[SBIS-Record-Format]] **Protocol 1/2** (`d`/`s` как объекты), несмотря на то, что основной транспорт использует protocol 7.

### Пагинация (позиция)

При передаче `Position` для следующей страницы:
```json
"Position": {
  "d": ["2026-04-23 09:10:23.103000+0300"],
  "s": [{"t": "Строка", "n": "themeDatetime"}],
  "_type": "record",
  "f": 1
}
```

---

## Ответ

Ответ использует формат [[SBIS-Record-Format]] с ключами `d` (строки данных) и `s` (схема).

### Схема (s)

| Индекс | Поле          | Тип         | Описание                       |
|--------|---------------|-------------|--------------------------------|
| 0      | `theme`       | UUID        | ID диалога/темы                |
| 1      | `themeDatetime` | Datetime  | Дата-время первого сообщения   |
| 2      | `themeMessage` | UUID       | ID первого сообщения           |
| 3      | `findMessage` | UUID        | null                           |
| 4      | `isMainTheme` | Логическое  | Основная тема (обычно false)   |
| 5      | `message`     | Запись      | null в текущих ответах         |
| 6      | `pairMessages`| Запись      | Объект с полными данными диалога |

### Поле pairMessages (индекс 6)

Содержит вложенный объект `{"d": {...}}` с полями (доступны напрямую по имени):

| Поле                         | Тип       | Описание                          |
|------------------------------|-----------|-----------------------------------|
| `messageFirstText`           | JSON-str  | Текст первого сообщения (rich text) |
| `messageFirstPersonName`     | Строка    | Имя отправителя первого сообщения |
| `messageFirstDatetime`       | Datetime  | Время первого сообщения           |
| `messageFirstIsIncoming`     | Логическое| `true` если входящее              |
| `messageLastText`            | JSON-str  | Текст последнего сообщения        |
| `messageLastPersonName`      | Строка    | Имя отправителя последнего        |
| `messageLastDatetime`        | Datetime  | Время последнего сообщения        |
| `themeMessagesCount`         | Число     | Всего сообщений в диалоге         |
| `themeOtherParticipants`     | Массив    | Участники диалога (`name`, `person`, `fio`) |

### Пагинация в ответе

Курсор следующей страницы в секции `m`:
```json
"m": {
  "d": {"nextPosition": [null]},
  "s": {"nextPosition": "JSON-объект"}
}
```
- `result["m"]["d"]["nextPosition"][0]` — объект-курсор или `null` (нет следующей страницы).
- Из курсора извлекается datetime: `cursor["d"][0]`.

---

## Rich text формат

`messageFirstText` и `messageLastText` — JSON-сериализованные деревья в формате S-expressions:
```
[["p", {"version": "2"}, ["span", {"class": "..."}, "Текст сообщения"]]]
```
Парсинг: рекурсивный обход, строки — листья, теги `p`/`div`/`br` → добавить `\n`.

---

## Реализация в sbis-mcp

### models.py

- `_extract_rich_text(raw)` — извлекает plain text из rich text JSON.
- `_walk_rich_node(node)` — рекурсивный обход дерева.
- `TaskMessage` — dataclass: `theme_id`, `datetime`, `sender_name`, `is_incoming`, `text` (raw), `last_datetime`, `last_sender_name`, `last_text` (raw), `messages_count`, `participants`.
  - `to_brief_text()` — компактная однострочная (двустрочная для многосообщных диалогов) сводка: `← Имя [дата]: текст 150 символов`.
  - `from_sbis_row(row, schema)` — парсит строку из `result["d"]` с учётом схемы; ищет данные в `pairMessages` (индекс 6), потом в `message` (индекс 5).
- `TaskMessageListResult` — dataclass: `messages`, `has_more`, `next_position`, `raw_count`.
  - `from_sbis_result(result)` — парсит полный ответ API включая пагинацию из `m`.

### client.py

```python
def list_task_messages(self, document_id, limit=20, position=None) -> TaskMessageListResult
```
Строит Position-запись из строки datetime, вызывает `self.call("DocumentMessage.ListForEDO", params)`.

### server.py MCP-инструмент

```
sbis_list_task_messages(document_id, limit=20, position=None, output_format="text")
```
- `output_format="text"` — компактная сводка для LLM.
- `output_format="dict"` — структурированный JSON.

---

## Нюансы

- `message` (индекс 5) в реальных ответах = `null`; все данные в `pairMessages` (индекс 6).
- Каждая строка в `d` — это **диалог** (тема), не отдельное сообщение. В одном диалоге может быть `themeMessagesCount > 1`.
- `scroll="up"` + `Position` = загрузка более старых диалогов (хронологически до курсора).
- `document_id` одновременно идёт в `document` и `fromTheme`.
