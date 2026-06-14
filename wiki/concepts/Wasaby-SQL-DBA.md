---
address: c-000113
created: 2026-06-14
updated: 2026-06-14
type: concept
title: "Wasaby SQL/PostgreSQL DBA Resources"
tags:
  - wasaby
  - sql
  - postgresql
  - dba
  - optimization
  - backend
status: current
related:
  - "[[Wasaby-SQL-Standard]]"
  - "[[Wasaby-Service-Framework]]"
sources:
  - ".raw/wasaby.Backend/SQL, PostgreSQL, DBA/DBA.sabydoc"
  - ".raw/wasaby.Backend/SQL, PostgreSQL, DBA/PostgreSQL Antipatterns и оптимизация SQL.sabydoc"
  - ".raw/wasaby.Backend/SQL, PostgreSQL, DBA/SQL HowTo.sabydoc"
  - ".raw/wasaby.Backend/SQL, PostgreSQL, DBA/Анализ запросов в PostgreSQL.sabydoc"
  - ".raw/wasaby.Backend/SQL, PostgreSQL, DBA/Решения для PostgreSQL_SQL.sabydoc"
---

# Wasaby SQL/PostgreSQL DBA Resources

Дайджест статей команды Тензор на Хабре по PostgreSQL и оптимизации SQL. Все статьи публичны и находятся в блоге Тензора на Хабре.

## Инструмент анализа планов

**`explain.tensor.ru`** — сервис визуализации планов PostgreSQL-запросов от Тензора.
- Self-hosted вариант доступен для развертывания на своей площадке
- Поддерживает Timescale, Citus, Greenplum, Redshift
- Умеет сопоставлять план с запросом из лога, кластеризовать миллионы планов

## Категории статей

### DBA — обслуживание и диагностика
- Хранение списков: таблица vs массив vs строка
- Рекомендации по индексам (сервис explain.tensor.ru)
- Реверс-инжиниринг структуры БД по плану запроса
- Мониторинг блокировок (`pg_catalog`, `pg_stat_activity`)
- Очистка таблиц вручную (VACUUM bypass)
- Перенос SEQUENCE между базами
- Поиск бесполезных индексов
- Секционирование: бесшовная миграция, ночное обслуживание

### Антипаттерны и оптимизация
- Index Only Scan — когда он вреден
- Поиск «последних» записей без полного скана
- Batch UPDATE и deadlock
- EXISTS vs IN vs JOIN
- Рекурсия в CTE — типичные ошибки
- NULLS FIRST/LAST и промах по индексу
- Лишние сортировки и GROUP BY
- Внешние ключи как источник блокировок
- EAV-паттерн: варианты и подводные камни

### SQL HowTo — рецепты
- Курсорная пагинация (`WITH TIES`, `LIMIT ... OFFSET` vs курсор)
- Иерархический обход (рекурсивный CTE)
- Подстрочный поиск (FTS, триграммы)
- Агрегаты в БД: зачем, как, прокси-таблицы
- Множественные источники данных (client-side SQL)
- GROUPING SETS для «дырявых» данных
- Advisory locks, LISTEN/NOTIFY

### Анализ запросов в PostgreSQL
- Структурные подсказки в explain.tensor.ru
- Чтение параллельных планов
- Сопоставление лога с планом (Query Profiler)
- Массовая оптимизация запросов

## Ключевые принципы (из статей)

> [!key-insight] Порядок полей в btree-индексе
> Поле с меньшей кардинальностью должно стоять в индексе **раньше** — индекс и меньше, и быстрее. Исключение: btree_gist может вести себя иначе.

> [!key-insight] Deadlock при пакетном UPDATE
> `UPDATE ... WHERE id IN (1, 2, 3)` без явной сортировки может взаимоблокировать транзакции. Решение: всегда сортировать ключи перед batch-обновлением.

> [!key-insight] advisory locks вместо SELECT FOR UPDATE
> Для синхронизации без захвата строк — `pg_try_advisory_lock` / `pg_advisory_unlock`.

## Связанные страницы

- [[Wasaby-SQL-Standard]] — внутренний стандарт написания SQL в Wasaby
- [[Wasaby-Service-Framework]] — как SQL-слой взаимодействует с БЛ
