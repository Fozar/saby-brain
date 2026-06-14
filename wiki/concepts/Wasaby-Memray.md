---
address: c-000124
created: 2026-06-14
updated: 2026-06-14
type: concept
title: "Wasaby Memray — профилировщик памяти Python"
tags:
  - wasaby
  - debugging
  - profiling
  - python
  - memory
status: current
related:
  - "[[Wasaby-Perforator]]"
  - "[[Wasaby-Unit-Testing]]"
sources:
  - ".raw/wasaby.Backend/Отладка/Профилирование/Memray/Memray.sabydoc"
  - ".raw/wasaby.Backend/Отладка/Профилирование/Memray/Инструкция для разработчиков.sabydoc"
  - ".raw/wasaby.Backend/Отладка/Профилирование/Memray/Подготовка к работе.sabydoc"
---

# Wasaby Memray

Bloomberg's **Memray** — профилировщик памяти для Python-процессов. Для нативного C++ используется Heaptrack (не Memray).

## Когда использовать

- Утечки памяти в Python-сервисе
- Анализ потребления памяти конкретным методом BL
- Оценка пика потребления vs утечек

## Требуемые пакеты (Linux)

```bash
# CentOS 7
sudo yum -y install devtoolset-9-gdb libunwind lz4 wget curl jq

# CentOS 8
sudo yum -y install gcc-toolset-9-gdb libunwind lz4 wget curl jq

# Red Hat 9 — gdb уже в базовом образе
sudo yum -y install libunwind lz4 wget curl jq
```

## Скрипт

Скрипт лежит на общей разделяемой директории. Если его нет:

```bash
cd /mnt/heaptrack
wget https://git.sbis.ru/sbis/memray/-/blob/HEAD/memray_script.sh
```

Параметры: `sh memray_script.sh -h`

## Запись профиля

### Локальная сборка (без сторонних символов)

```bash
sh memray_script.sh record --non-root --no-symbols -p <PID>
```

### Локальная сборка с SDK

```bash
sh memray_script.sh record --non-root --symbols /SBISPlatformSDK/debug -p <PID>
```

### Дистрибутивный стенд

```bash
sh memray_script.sh record --non-root --sym-progress \
  -s "online" \
  -d "online-master-ru" \
  --service-build <BUILD_NUMBER> \
  -p <PID>
```

- `-s` — системное имя сервиса (из `.s3srv`)
- `-d` — название дистрибутива (из `.s3distr`)
- `--service-build` — номер сборки (атрибут `build_number` в `.s3distr`); обязателен на локальном стенде (Genie увеличивает его при каждом запуске)

Скрипт запросит реквизиты FTP-сервера с символами (конфиденциально, запрашивать у Бадаева Е.Н. / Елькина Е.В. / Запруднова А.А.)

### Неагрегированный профиль

По умолчанию собирается агрегированный профиль. Для временного анализа:

```bash
sh memray_script.sh record --non-root --no-symbols -p <PID> --non-aggregated
```

> [!warning] 1 минута неагрегированного профиля на ненагруженном online ≈ 150 МиБ.

Остановить: `Ctrl+C` или `-t <секунды>`.

## Анализ результата

### Режимы вывода

| Режим | Описание | Формат |
|-------|----------|--------|
| `flamegraph` | График горячих путей | HTML |
| `table` | Таблица выделений памяти | HTML |
| `tree` | Дерево горячих путей | терминал |
| `summary` | Сводка по функциям | терминал |
| `stats` | Высокоуровневая статистика | терминал |
| `transform` | Конвертация в другие форматы | — |

### Команды анализа

```bash
# Пик потребления памяти (локальный профиль)
sh memray_script.sh flamegraph --no-symbols -p /path/to/profile -- -o /output/path

# Утечки памяти
sh memray_script.sh flamegraph --no-symbols -p /path/to/profile -- --leak -o /output/path

# С нестандартными символами
sh memray_script.sh flamegraph --symbols /some/path -p /path/to/profile -- -o /output/path

# Временной профиль (только из --non-aggregated профиля)
sh memray_script.sh flamegraph --no-symbols -p /path/to/profile -- --temporal -o /output/path

# Справка по конкретному режиму
sh memray_script.sh flamegraph -h
```

## Производственный сервис (боевой)

Заказывать через поручение "Выполнить на рабочем" в ЦОД.

## Связанные страницы

- [[Wasaby-Perforator]] — профилировщик CPU (Perforator от Яндекса)
- [[Wasaby-Unit-Testing]] — моки для тестирования (не профилирования)
