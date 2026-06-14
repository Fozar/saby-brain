---
type: concept
title: "Схема дистрибутивов основного сервиса Wasaby"
tags:
  - wasaby
  - infrastructure
  - distribution
  - deployment
status: current
related:
  - "[[Хоттабыч-System]]"
  - "[[Wasaby-Local-Stand-Setup]]"
  - "[[Multitenancy-Architecture]]"
created: 2026-04-12
updated: 2026-04-12
---

# Схема дистрибутивов основного сервиса Wasaby

Основной сервис = multitenancy-сервис **online** (онлайн.сбис.ру).

**Идея**: явно разделить базовый функционал СБИС и региональные особенности через служебные `s3srv`-файлы.

## Базовые дистрибутивы

| Дистрибутив | Состав | Назначение |
|-------------|--------|------------|
| `online32` | bl-модули | Базовые модули для всех клиентов (int32 ключи ЭДО) |
| `online64` | bl-модули | Миксин поддержки int64 ключей ЭДО |
| `online` | online32 + online64 | Базовый BL-сервис |
| `online-ps` | ui-модули | Базовые UI-модули для всех клиентов |

> [!note] online32/online64 существуют временно, до конвертации всех клиентов под int64.

## Региональные пакеты

| Пакет | Описание |
|-------|----------|
| `online-bl-ru` / `online-ui-ru` | Только для клиентов России |
| `online-bl-kz` / `online-ui-kz` | Только для клиентов Казахстана |

**Правило**: если модуль нужен для конкретной страны → включать в региональный пакет, не в базовый.

## Приложения (дистрибутивы) для клиентов

```
online-ru (Россия, int64)
├── BL: online-ru (online + online-bl-ru)
└── UI: online-ps-ru (online-ps + online-ui-ru)

online-kz (Казахстан)
├── BL: online-kz (online + online-bl-kz)
└── UI: online-ps-kz (online-ps + online-ui-kz)

online32-ru (Россия, int32 — переходный)
├── BL: online32-ru (online32 + online-bl-ru)
└── UI: online-ps-ru
```

**Запрещено**: добавлять модули непосредственно в `online-ru`, `online-kz` и `online-ps-*` — только в базовый или региональный пакет.

## Приложения Тензора (online-master)

Цели: отказ от имени "inside", отдельные дистрибутивы по странам, разделение общего и национального.

| Пакет | Описание |
|-------|----------|
| `online-master-bl` / `online-master-ui` | Тензор в любой стране |
| `online-master-bl-ru` / `online-master-ui-ru` | Тензор в России |
| `online-master-bl-kz` / `online-master-ui-kz` | Тензор в Казахстане |

```
online-master-ru
├── BL: online-master-ru (online-ru + online-master-bl-ru)
└── UI: online-master-ps-ru (online-ps-ru + online-master-ui-ru)

online-master-kz
├── BL: online-master-kz (online-kz + online-master-bl-kz)
└── UI: online-master-ps-kz
```

**Запрещено**: включать модули непосредственно в `online-master[-ps]-**`.

## Специальные дистрибутивы

### Демо-аккаунт
```
online-demo-ru: online-ru + online-demo-bl | online-ps-ru + online-demo-ui
online-demo-kz: online-kz + online-demo-bl | online-ps-kz + online-demo-ui
```

### Пробный аккаунт
```
online-try-account-ru: online-ru + online-try-account-bl | ...
online-try-account-kz: online-kz + online-try-account-bl | ...
```

## Файловые типы

| Расширение | Тип |
|------------|-----|
| `.s3cld` | Описание облачного приложения |
| `.s3srv` | Описание сервиса (BL или UI) |
| `.s3mod` | Описание модуля |
| `.orx` | Справочник объектов БЛ |
| `.s3distr` | Схема сборки дистрибутива (версия SDK, дата, номер сборки) |

## Сетевой диск с дистрибутивами

```
Windows: \\sbis-dev.corp.tensor.ru\programmers\СБиС_3\Локальный стенд\test\<версия>\win\
Linux:   smb://sbis-dev.corp.tensor.ru/programmers/СБиС_3/Локальный стенд/test/<версия>/nix/
```
