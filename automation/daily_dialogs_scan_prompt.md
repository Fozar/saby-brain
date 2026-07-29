Ты выполняешь ежедневный автоматический скан переписок SBIS (MCP `sbis`) и ingest новых сообщений в вики claude-obsidian. Работай в текущей рабочей директории (репозиторий `claude-obsidian`). Действуй автономно, без вопросов пользователю — это unattended-запуск.

## Состояние (state file)

Файл: `automation/dialogs_scan_state.json`, формат:
```json
{"last_scan": "2026-07-29T13:00:00+03:00", "folders": ["Все", "Встречи"]}
```

1. Прочитай `automation/dialogs_scan_state.json`. Возьми `last_scan` (ISO datetime с TZ, обычно +03).
2. Если файла нет — ничего не делай, запиши в лог `automation/logs/daily_dialogs_scan.log` строку с ошибкой "state file missing, run backfill first" и завершись.

## Сбор диалогов

Для каждой папки `folder` из `["Все", "Встречи"]`:

1. Вызывай `mcp__sbis__sbis_list_dialogs(folder=folder, period="all", output_format="dict", page_size=50, position=<next_position с предыдущей страницы или null>)`.
2. Список отсортирован по убыванию `datetime`. Иди по страницам (пока `has_more=true`), пока не встретишь диалог с `datetime <= last_scan` — на этом диалоге и всех последующих страницу можно прекращать пагинацию для этой папки.
3. Собирай диалоги с `datetime > last_scan`: `theme_id`, `title`/`document_name`, `participant_names`, `dialog_type`, `folder`.
4. Объедини результаты обеих папок, убери дубли по `theme_id`.

Если по итогу нет ни одного нового диалога — сразу переходи к шагу "Обновление state" (ничего не ingest'ить, просто обновить `last_scan`).

## Чтение и запись переписок

Для каждого нового/обновлённого `theme_id`:

1. Вызови `mcp__sbis__sbis_read_dialog(theme_id=theme_id, output_format="dict", full=False, limit=100)`.
2. Отфильтруй сообщения с datetime > `last_scan` (остальные отбрось — они уже были обработаны раньше).
3. Если после фильтра сообщений нет — пропусти диалог.
4. Путь файла: `raw/Диалоги SBIS/<theme_id>.md`.
   - Если файла ещё нет — создай с frontmatter:
     ```yaml
     ---
     source_type: sbis_dialog
     theme_id: <theme_id>
     title: <title или document_name (первая строка) или "Без темы">
     participants: [<participant_names>]
     dialog_type: <dialog_type>
     folder: <folder>
     first_ingested: <YYYY-MM-DD сегодня>
     last_updated: <YYYY-MM-DD сегодня>
     ---
     ```
     и телом — сообщения в хронологическом порядке.
   - Если файл уже существует — НЕ переписывай с нуля. Допиши новые сообщения в конец тела файла и обнови `last_updated` в frontmatter.
   - Формат одного сообщения в теле:
     ```
     ## <YYYY-MM-DD HH:MM> — <sender>
     <текст сообщения>
     ```
   - **Идемпотентность**: `last_scan` может быть немного занижен относительно реального времени прошлого скана (например, чтобы гарантированно повторно подобрать диалог, который не удалось прочитать в прошлый раз) — из-за этого окно дат может частично пересекаться с уже обработанным. Перед добавлением сообщения в конец файла проверь, нет ли в файле уже точно такого же блока `## <YYYY-MM-DD HH:MM> — <sender>` с тем же текстом сообщения сразу под ним. Если есть — не добавляй дубликат, пропусти это сообщение.

## Ingest

После обработки всех диалогов (если были изменённые/новые файлы под `raw/Диалоги SBIS/`):

Вызови skill `claude-obsidian:wiki-ingest` в batch-режиме на файлы, которые были созданы/изменены на этом шаге ("just ingest it" — без интерактивных вопросов, это автоматический запуск).

## Обновление state

Запиши в `automation/dialogs_scan_state.json` новый `last_scan` = текущее время (ISO, локальный TZ +03), сохрани `folders` как есть.

## Логирование

Допиши в `automation/logs/daily_dialogs_scan.log` одну строку:
```
[YYYY-MM-DD HH:MM] scanned N dialogs, M new/updated, ingested via wiki-ingest: <краткий summary или "nothing new">
```

Если какой-то вызов MCP `sbis` упал с ошибкой авторизации или иной — запиши это в лог как ERROR и не обновляй `last_scan` (чтобы следующий запуск повторил тот же диапазон).
