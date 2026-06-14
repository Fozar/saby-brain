---
address: c-000133
created: 2026-06-14
updated: 2026-06-14
type: concept
title: "Wasaby Informers Service — информеры и счётчики"
tags:
  - wasaby
  - middleware
  - ui
  - counters
  - redis
  - backend
status: current
related:
  - "[[Wasaby-BL-Calls]]"
  - "[[Wasaby-MQ]]"
sources:
  - ".raw/wasaby.Backend/Сервисы общего назначения/Сервис информеров/Сервис информеров.sabydoc"
  - ".raw/wasaby.Backend/Сервисы общего назначения/Сервис информеров/Руководство разработчика/Добавление нового информера_счетчика.sabydoc"
  - ".raw/wasaby.Backend/Сервисы общего назначения/Сервис информеров/Руководство разработчика/Пример обращения к сервису.sabydoc"
---

# Wasaby Informers Service

Централизованное хранение и горячий кэш числовых значений для UI-элементов:
- **Информер** — UI-элемент в тулбаре (иконка + счётчик или таймер)
- **Счётчик** — числовое значение в пунктах аккордеона и навигации

Хранилище: **Redis** (без БД). Данные имеют TTL. При отсутствии запускается механизм восстановления.

## Запись значения (прикладной сервис → Informers)

```python
# Обновить счётчик: Counters.Set(1) на сервисе informers
obj = sbis.EndPoint("informers")
auth_data = sbis.AuthByExtID(account)
Counters = obj.AsyncInvoke('Set', {
    "DateNow": "2018-07-11 12:49:32.376999",
    "DateActual": "2018-07-18 12:49:32.376999",
    "ProfileUUIDS": "a22d930a-1d2a-4c60-bc41-1a8b33b5db4a",
    "Values": [
        {"Name": "my.new.counter", "Value": ..., "counterAll": ..., "counterNew": ...}
    ]
})
```

## Регистрация информера/счётчика

Информеры описываются в конфиге репозитория `git.sbis.ru/engine/informers`:
- `informers.py` — информеры
- `counters.py` — счётчики

### Настройки (dict с ключом = systemName)

| Поле | Тип | Описание |
|------|-----|----------|
| `endpoint` | str | Сервис метода восстановления |
| `object` | str | Объект БЛ восстановления |
| `method` | str | Метод БЛ восстановления |
| `userType` | str | `"profile"` / `"client"` / `"user"` |
| `index` | int | Уникальный числовой ID (ключ Redis) |
| `groupName` | str | Группа (один запрос восстановления для группы) |
| `order` | int | Порядок в UI (снизу вверх) |
| `parallel` | bool | Группировать быстрые Set/Update/Delete за 100мс (снижает нагрузку) |
| `publishEvent` | bool | Публиковать событие при изменении (default: True) |
| `eventName` | str | Дополнительное событие (плюс к стандартному) |
| `eventNameUnique` | str | Только это событие (без стандартного) |
| `reloadAlways` | bool | Вызывать восстановление при каждой загрузке страницы |
| `localization` | str[] | Поля для локализации перед отдачей в UI |
| `applications` | str[] | Приложения, которым публиковать событие |

> [!note] В названии запрещены символы `|` и кириллица.

### Типы группировки вызовов восстановления

- `groupCall` — группировка по имени метода вызова
- `groupMethod` — группировка по методу восстановления
- `groupAuth` — группировка по авторизационным данным

## Процесс восстановления

1. UI вызывает `Informers.GetJoinData([список системных имён])`
2. Если данных нет в Redis → в Redis пишется "заявка"
3. Планировщик каждые 100 мс читает заявки, группирует, вызывает методы восстановления (AsyncInvoke)
4. Метод восстановления → через колбэк или `Informers.Set()` → Redis → событие → UI

## Публичное API

| Метод | Описание |
|-------|----------|
| `Informers.GetJoinData(names)` | Получить данные информеров по именам |
| `Counters.Set(values)` | Установить значения счётчиков |
| `Informers.Set(...)` | Установить значение информера |

## Связанные страницы

- [[Wasaby-BL-Calls]] — вызов `AsyncInvoke('Set', ...)` на сервис informers
- [[Wasaby-MQ]] — механизм событий об изменении информеров
