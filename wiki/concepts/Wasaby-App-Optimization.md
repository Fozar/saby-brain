---
type: concept
title: "Wasaby App Optimization"
updated: 2026-04-12
tags:
  - wasaby
  - performance
  - optimization
status: current
related:
  - "[[Wasaby-Performance-Budget]]"
  - "[[Wasaby-RecordSet-Performance]]"
  - "[[Wasaby-BL-Advanced]]"
  - "[[Wasaby-DB-Access-Patterns]]"
created: 2026-04-12
---

# Wasaby App Optimization

Обзорная карта инструментов и рекомендаций по оптимизации Wasaby-приложений. Оптимизация — нахождение наилучшего способа решения задачи (скорость загрузки, время выполнения метода). Проводится **после отладки**.

> [!note] Принцип
> Оптимизация уместна не всегда: если выигрыш неощутим на фоне затраченных ресурсов — не оптимизировать.

---

## Уровни оптимизации

### 1. Слой представления данных (UI)

- Общие рекомендации: отказ от jQuery, асинхронная загрузка скриптов
- Пакетирование данных — уменьшение сетевого трафика
- Оптимизация списков с диалогами редактирования
- Кэширование UI-сущностей

### 2. Слой Middleware

- **Препроцессор** — перенос формирования HTML-страниц на сервер представления (увеличивает скорость клиентской части)
- **Кэширование** XML-файлов на middleware
- **[[Report-Prefetch-Service]]** — платформенный механизм кэширования отчётов; постраничное хранение в БД сервиса; конвейер из 11 узлов обработки; индексы для быстрого поиска/сортировки

### 3. Слой бизнес-логики (БЛ)

- **cloud.sbis.ru** — инструмент анализа вызовов БЛ, статистика и логирование
- **Параллельное выполнение** через механизм [[Wasaby-SharedFuture|shared future]] (`FutureInvoke`, `ParallelTasks`)
- **AsyncInvoke** — асинхронный вызов без ожидания ответа
- **Кэширование** результатов методов и данных сессии
- Подробно: [[Wasaby-BL-Advanced]]

### 4. Слой СУБД (PostgreSQL)

- **explain.sbis.ru** — мониторинг PostgreSQL: проблемные запросы, блокировки, ошибки
- Серия семинаров по тонкостям PostgreSQL (внутренний ресурс Тензор)
- Подробно: [[Wasaby-DB-Access-Patterns]]

---

## Python-уровень: RecordSet

Отдельная большая тема — оптимизация работы с `Record`/`RecordSet` при постобработке данных на Python.

- Избегать `IField`-обёрток (`rec['Field']`, `TestField`) в горячем коде
- Избегать Python-обёрток над `Record` без нужды
- Использовать `ToList` / `ToListOf` / `SqlQueryOf` вместо ручного перебора
- Подробно: [[Wasaby-RecordSet-Performance]]

---

## Бюджет производительности

Метрики замеряются инструментом Perfalyze и сравниваются с установленными порогами (VR/TTI/REQ/Size/BL/Leak).

- Подробно: [[Wasaby-Performance-Budget]]

---

## Связанные темы

- [[Wasaby-Performance-Budget]] — пороговые метрики, правила, исключения
- [[Wasaby-RecordSet-Performance]] — оптимизация RecordSet/Record в Python
- [[Wasaby-BL-Advanced]] — кэш, таймауты, Antibot
- [[Wasaby-DB-Access-Patterns]] — SqlQuery, async, bulk ops
- [[Report-Prefetch-Service]] — платформенный кэш отчётов: сессии, конвейер, индексы
