---
address: c-000125
created: 2026-06-14
updated: 2026-06-14
type: concept
title: "Wasaby Perforator — профилировщик CPU"
tags:
  - wasaby
  - debugging
  - profiling
  - performance
  - cpu
status: current
related:
  - "[[Wasaby-Memray]]"
sources:
  - ".raw/wasaby.Backend/Отладка/Профилирование/Perforator/Perforator.sabydoc"
  - ".raw/wasaby.Backend/Отладка/Профилирование/Perforator/Инструкция для разработчиков.sabydoc"
  - ".raw/wasaby.Backend/Отладка/Профилирование/Perforator/Подготовка к работе.sabydoc"
---

# Wasaby Perforator

**Perforator** — профилировщик CPU от Яндекса. Применяется для анализа производительности кода в prod с минимальной нагрузкой на сервисы. UI: https://perforator.sbis.ru/

## Требования

- **OS**: Red Hat Enterprise Linux 9+ (ядро Linux ≥ 5.7)
- **Python**: 3.9+ (скрипт сбора профиля написан на Python)

## Скрипт

```bash
cd /mnt/heaptrack
wget https://git.sbis.ru/sbis/perforator/-/raw/HEAD/perforator_script.py
```

Параметры: `python3 perforator_script.py -h`

## Заказ профиля через ЦОД

Оформить поручение "Выполнить на рабочем", указать:

1. Название сервиса
2. Длительность сбора (не менее 2 минут)
3. Тип оркестрации:
   - Виртуальные / физические серверы → PID(ы) процессов
   - Kubernetes → имя пода
4. Ссылку на инструкцию для дежурных ЦОД

В результате поручение вернёт ссылку на выборку профилей в UI Perforator.

## Анализ результата

1. Перейти по ссылке на perforator.sbis.ru
2. Выбрать один профиль или агрегировать выборку (с подстройкой интервала)
3. Анализировать интерактивный flamegraph
4. Опционально: экспорт в формате pprof для сторонних инструментов

## Сравнение с Memray

| | Memray | Perforator |
|--|--------|------------|
| Что профилирует | Память (Python) | CPU (любой язык) |
| Разработчик | Bloomberg | Яндекс |
| Запуск | Самостоятельно (скрипт) | Через ЦОД |
| Доступность | Любая среда | Prod / стенды |
| Анализ | Локальные HTML-отчёты | Web UI perforator.sbis.ru |

## Связанные страницы

- [[Wasaby-Memray]] — профилировщик памяти Python
