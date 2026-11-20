---
type: concept
title: "Кнопка ингеста диалога SBIS в вики (Tampermonkey + opencode serve)"
created: 2026-11-19
updated: 2026-11-19
status: active
tags:
  - tooling
  - wiki
  - sbis
  - tampermonkey
related:
  - "[[index]]"
  - "[[log]]"
---

# Кнопка «⤓ вики» на карточке диалога dev.saby.ru

Userscript для Tampermonkey: кнопка в шапке открытого диалога/звонка/встречи на `dev.saby.ru/page/dialogs`. По клику диалог выкачивается в markdown и автоматически запускается сессия opencode с ингестом в эту вики (скилл wiki-ingest). Файл скрипта: `tools/saby-dialog-ingest.user.js` в репозитории claude-obsidian.

## Как работает

1. **theme_id открытого диалога.** В DOM его нет. В контекст страницы (script-тег, т.к. userscript в изолированном мире) внедряется хук `XMLHttpRequest.send` + `fetch`, который ловит запросы `Message.List` к `/msg/service/` и забирает `params.Фильтр.d[fromTheme]` (индекс поля ищется по `s[]`). Кладётся в `window.__sabyIngestTheme`.
2. **Markdown.** BL-метод `Сообщение.GetMarkdownText` (`POST /msg/service/?x_version=...`, JSON-RPC, params `{theme_id, message_count: 0}`, заголовок `x-originalmethodname` = base64 имени метода) отдаёт весь диалог в markdown с метаданными. Работает из контекста страницы с её куками. Звонок на ~15 мин ≈ 17 тыс. символов.
3. **Сессия opencode.** Локальный `opencode serve --service` (порт 28894). API: `POST /api/session` (location = каталог вики, title = заголовок диалога, agent, model) → `POST /api/session/{id}/prompt` (текст: инструкция + markdown диалога). CORS-заголовков нет, поэтому из браузера только через `GM_xmlhttpRequest`. Открывается вкладка веб-UI: `/server/<base64(сервер)>/session/<id>`.
4. **Авторизация** — Basic `opencode:<password>`, пароль из `~/.config/opencode/service.json` (localhost-only, зашит в скрипт).

## Зафиксированные решения и факты

- Агент `build` (регистр важен: `Build` → «Agent not found»), модель `openai/gpt-6.1-terra` variant `medium` (GPT Terra Medium) — выбор пользователя 19.11.
- Кнопка вставляется в `.msg-ThemeView__actions.msg-header-layout__actions` внутри панели `.msg-ThemeView` (MutationObserver, debounce 300 мс) — работает для звонков, встреч и обычных диалогов.
- `x_version` берётся из performance resource entries страницы, кэшируется.
- Скилл wiki-ingest подхватывается агентом по тексту промпта сам.
- **Хранилище**: `C:\Users\aa.timoshenko\PycharmProjects\claude-obsidian` (корень репозитория — в нём inbox/, .raw/, wiki/). wiki-ingest по умолчанию отказывается брать «корень продукта», поэтому путь передаётся в промпте как явное указание пользователя (правило не применяется) — с v0.2.1 вшит в buildPrompt. Ядро `scripts/claude-obsidian.py` в этом чекауте отсутствует, агент работает без transaction-core.
- Первый живой прогон: звонок с Матюшевым 19.11.26 13:22 (theme_id `01a1f353-ef3d-705a-b9cd-e5b3509c245f`), сессия `ses_e0c7a8c33ffeWucijiNCOQfnwI`.

## Установка

Tampermonkey → Dashboard → Utilities → Import → выбрать `tools/saby-dialog-ingest.user.js`. Требуется запущенный `opencode serve --service`.

## Открытые вопросы

- Не проверено на каналах/группах (только личка, звонки, совещания).
- Если opencode serve не запущен — кнопка покажет ошибку сети (как и задумано).
