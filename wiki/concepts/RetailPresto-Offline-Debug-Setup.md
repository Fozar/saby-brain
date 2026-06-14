---
type: concept
title: "RetailPresto Offline Debug Setup"
address: c-000074
created: 2026-06-11
updated: 2026-06-11
tags:
  - retail
  - presto
  - offline
  - development
  - debug
  - s3mod
  - s3srv
status: current
related:
  - "[[Wasaby-Module-System]]"
  - "[[Loyalty-In-Products]]"
  - "[[PriceFormation-Backend-Architecture]]"
  - "[[Алябушев-Александр-Александрович]]"
---

# RetailPresto Offline Debug Setup

Пошаговая инструкция по подключению своих изменений BL в офлайн-приложениях Saby Retail и Saby Presto для отладки.

> [!key-insight] Только Debug-версия
> Начиная с версии 25.6218 ресурсы офлайн-приложений **предкомпилируются** в бинарные библиотеки. Файлы `.s3mod` в Release-сборке — бинарники, их подмена не работает. Все шаги ниже применимы **только к Debug-версии** приложения.

---

## Пути установки

| Продукт | user_data |
|---------|-----------|
| Saby Retail | `C:\ProgramData\Saby Retail` |
| Saby Presto | `C:\ProgramData\Saby Presto` |

Версионированная директория: `СБИС-Розница\<версия>\`.

---

## Шаг 0 — Отключить автообновление

Файл: `СБИС-Розница\user_data\service\user-config.ini`

```ini
[Updater]
АвтоматическоеОбновление=Нет
```

---

## Шаг 1 — Удалить MetaMainService из MainService.s3srv

Файл: `СБИС-Розница\<версия>\service\meta\MainService.s3srv`

Внутри блока `<items></items>` удалить строку:

```xml
<bl_module id="7b08fb3e-ef0b-4c63-b89d-a5df2451eca0" name="MetaMainService" url="./../modules/MetaMainService/MetaMainService.s3mod"/>
```

---

## Шаг 2 — Переключить конфиг на RetailCore.s3srv

Файл: `СБИС-Розница\<версия>\service\sbis-config.ini`

В блоке `[Базовая конфигурация]` заменить значение поля `Модули`:

```ini
[Базовая конфигурация]
Модули=meta/RetailCore.s3srv
```

---

## Шаг 3 (опционально) — Убрать MetaMainServiceDB

Нужно только если требуется конвертация БД postgres.

Файл: `СБИС-Розница\<версия>\service\meta\RetailCore.s3srv`

Внутри блока `<items></items>` удалить строку:

```xml
<bl_module id="b4c443ad-2fd8-47f0-b730-4b9f75542e17" name="MetaMainServiceDB" url="./../modules/MetaMainServiceDB/MetaMainServiceDB.s3mod"/>
```

---

## Шаг 4 — Очистить user_data и запустить

Удалить содержимое папки `user_data`, запустить Offline.

---

## Шаг 5 — Если добавились новые файлы

Удалить индексы, чтобы они пересоздались:

```
service\files.index
service\folders.index
```

---

## Альтернативный способ (проще, если нет доступа к MainService.s3srv)

Файл: `СБИС-Розница\<версия>\service\modules\MetaMainService\MetaMainService.s3mod`

Удалить часть строки, указывающую на скомпилированную библиотеку:

```
bl_module_library="meta_main_service"
```

---

## Исторический контекст

До версии 25.6218 достаточно было подменить файлы и перезапустить — ресурсы не предкомпилировались. Начиная с 25.6218 введена предкомпиляция, поэтому требуется описанный обходной путь.

**Авторы алгоритма:** Ушаков Тимофей (оригинальная инструкция 2025-02), Козлобродов Илья (обновление для 25.6218, 2025-08), Михайленко Елена (рабочий алгоритм).
