---
address: c-000131
created: 2026-06-14
updated: 2026-06-14
type: concept
title: "Wasaby Report Prefetch — кэширование больших отчётов"
tags:
  - wasaby
  - middleware
  - caching
  - reports
  - performance
  - backend
status: current
related:
  - "[[Wasaby-BL-Calls]]"
  - "[[Wasaby-Long-Running-Operations]]"
sources:
  - ".raw/wasaby.Backend/Middleware/Платформенный механизм кэширования отчетов (report-prefetch-service)/Платформенный механизм кэширования отчетов (report-prefetch-service).sabydoc"
---

# Wasaby Report Prefetch

Механизм кэширования больших отчётов (`report-prefetch-service`). Решает проблему медленных многостраничных отчётов — кэширует сразу N страниц при первом запросе.

**Отличие от кэширования методов**: обычное кэширование хранит только одну страницу. Prefetch кэширует сразу весь большой лимит и отдаёт страницы из кэша без повторных вызовов первички.

## Паттерн использования

```python
# 1. Переименовать оригинальный метод в *WithoutCaching
# 2. Создать обёртку, которая вызывает Prefetch.List

@staticmethod
def Example_List(ДопПоля, Фильтр, Сортировка, Навигация):
    Фильтр.AddString('PrefetchMethod', 'Example.ListWithoutCaching')
    Фильтр.AddInt32('PrefetchPages', 50)         # кол-во страниц за 1 вызов первички
    return sbis.Prefetch.List(ДопПоля, Фильтр, Сортировка, Навигация)
```

Подключить модуль `Report Prefetch` из репозитория `service-engine`.

> [!warning] Все вызовы `Prefetch.List` должны содержать фильтр `PrefetchPreSort` — это обязательное требование (см. новость платформы).

## Ключевые параметры фильтра

### Основные

| Параметр | Тип | Описание |
|----------|-----|----------|
| `PrefetchMethod` | String | Метод первички (источника отчёта) |
| `PrefetchEndpoint` | String | Сервис первички (опционально) |
| `PrefetchPages` | Int32 | Кол-во страниц для кэша (default: 50 для плоских, 500 для иерархии) |
| `PrefetchSessionId` | UUID | ID микросессии (создаётся автоматически при первом вызове) |
| `PrefetchSessionLiveTime` | TimeInterval | Время жизни кэша |
| `PrefetchOnlyCache` | Boolean | Вернуть только из кэша (без вызова первички) |
| `PrefetchThrowErrors` | Boolean | Пробрасывать ошибки вместо fallback на прямой вызов |

### Асинхронное заполнение

| Параметр | Тип | Описание |
|----------|-----|----------|
| `PrefetchAsyncSave` | Boolean | Синхронный малый лимит + асинхронный большой в фоне |
| `PrefetchAsyncSaveAll` | Boolean | Асинхронный запрос всего отчёта при старте |
| `PrefetchForceAsyncSave` | Boolean | Всегда сохранять асинхронно |

### Иерархические отчёты

| Параметр | Тип | Описание |
|----------|-----|----------|
| `PrefetchPreSort` | Boolean | Предварительная сортировка разворота (обязательный) |
| `PrefetchHierarchyColumn` | String | Поле идентификатора родителя (default: "Раздел") |
| `PrefetchIdColumn` | String | Поле идентификатора записи (default: "DBId") |
| `PrefetchLevels` | Int32 | Кол-во кэшируемых уровней (-1 = все) |
| `PrefetchSpredHierarchy` | Boolean | Кэш разворота всего отчёта для ускорения работы с разворотом раздела |

### Хэш и сортировка

| Параметр | Тип | Описание |
|----------|-----|----------|
| `PrefetchIgnoredInHash*` | Any | Поля, начинающиеся с этого префикса, не влияют на хэш кэша |
| `PrefetchDefaultSortRows` | Boolean | Сортировка на стороне Prefetch (без перезапроса первички) |
| `PrefetchCustomeSortRows` | String | Кастомный метод сортировки |
| `PrefetchSortGroup` | String | Поле с приоритетом группы при сортировке |

## Результат Prefetch.List

В outcome добавляются поля:

| Поле | Тип | Описание |
|------|-----|----------|
| `PrefetchDataExist` | Boolean | Данные существуют в кэше |
| `PrefetchDataCreated` | DateTime | Дата создания сессии |
| `PrefetchDataValidUntil` | DateTime | До когда кэш валиден |
| `PrefetchSessionId` | UUID | ID сессии (передавать в следующие запросы) |

## Управление сессиями

```python
# Создать сессию с нужным временем жизни
Prefetch.CreateSession(...)   # перегрузки 0, 1, 2

# Удалить кэш явно (иначе удалится по истечении времени жизни)
Prefetch.DiscardSession(session_id)
```

## Поведение при ошибках

По умолчанию (без `PrefetchThrowErrors`): при недоступности сервиса кэширования или ошибке — прозрачный fallback на прямой вызов первички, в outcome — нулевая сессия. Пользователь ошибки не видит.

## Связанные страницы

- [[Wasaby-BL-Calls]] — обычные списочные методы (без кэша)
- [[Wasaby-Long-Running-Operations]] — для многоэтапных длительных операций
