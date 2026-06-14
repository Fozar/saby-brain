---
type: concept
title: "Claude Code — переключение на VseGPT"
created: 2026-06-09
updated: 2026-06-09
tags:
  - claude-code
  - vsegpt
  - configuration
  - api-provider
status: current
related:
  - "[[Claude Code]]"
  - "[[LLM Wiki Pattern]]"
---

# Claude Code — переключение на VseGPT

Claude Code поддерживает замену Anthropic API на совместимые провайдеры через переменные окружения. [VseGPT](https://vsegpt.ru) — российский агрегатор LLM-моделей с OpenAI-совместимым API.

## Конфигурация

Добавить в `~/.claude/settings.json` → секция `env`:

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://services.vsegpt.ru:3000",
    "ANTHROPIC_AUTH_TOKEN": "<ваш токен VseGPT>",
    "CLAUDE_CODE_ENABLE_TELEMETRY": "0",
    "API_TIMEOUT_MS": "3000000",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "moonshotai/kimi-k2.5",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "moonshotai/kimi-k2.5",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "moonshotai/kimi-k2.5"
  }
}
```

## Ключевые параметры

| Параметр | Назначение |
|---|---|
| `ANTHROPIC_BASE_URL` | Перенаправляет все API-вызовы на VseGPT endpoint |
| `ANTHROPIC_AUTH_TOKEN` | Токен VseGPT вместо Anthropic API key |
| `CLAUDE_CODE_ENABLE_TELEMETRY` | `"0"` — отключает телеметрию (рекомендуется при смене провайдера) |
| `API_TIMEOUT_MS` | Таймаут 50 минут — нужен, т.к. сторонние провайдеры медленнее |
| `ANTHROPIC_DEFAULT_*_MODEL` | Маппинг Haiku/Sonnet/Opus → конкретная модель провайдера |

## Замечания

- `moonshotai/kimi-k2.5` — модель Moonshot AI, доступная через VseGPT; можно заменить любой совместимой моделью из каталога VseGPT
- При смене обратно на Anthropic — убрать эти переменные из `env`
- Токен получить на [vsegpt.ru](https://vsegpt.ru) в личном кабинете
