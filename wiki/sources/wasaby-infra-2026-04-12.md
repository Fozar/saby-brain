---
type: source
title: "Wasaby Infrastructure Docs 2026-04-12"
date: 2026-04-12
tags:
  - wasaby
  - infrastructure
  - cloud-management
  - deployment
  - access-control
status: ingested
pages_created:
  - "[[Хоттабыч-System]]"
  - "[[Wasaby-Patches]]"
  - "[[Wasaby-Scripts]]"
  - "[[Wasaby-Access-Control]]"
  - "[[Wasaby-Cloud-Management]]"
  - "[[Wasaby-Request-Routing]]"
  - "[[Wasaby-Distribution-Schema]]"
  - "[[Wasaby-Local-Stand-Setup]]"
created: 2026-04-12
updated: 2026-04-12
---

# Wasaby Infrastructure Docs 2026-04-12

13 статей из внутренней базы знаний Tensor/SBIS, сохранённых через Obsidian Web Clipper.

## Источники

| Файл | Тема |
|------|------|
| `Хоттабыч.md` | Система обновлений Хоттабыч |
| `Патчи.md` | Создание и применение патчей |
| `Скрипты.md` | DeveloperScript: скрипты через Хоттабыч |
| `Приложения.md` | Структура облака (cloud-ctrl) |
| `Руководство пользователя.md` | Очередь: текущая загрузка сервисов |
| `Пользователи облака.md` | Пользователи в cloud-ctrl |
| `Клиенты.md` | Клиенты в cloud-ctrl |
| `Роли.md` | Система ролей Wasaby |
| `Участок системы (зона доступа).md` | Subject Area / .uax |
| `Ограничения.md` | Access Area: ограничения и области видимости |
| `Маршрутизация запросов к web-сервисам.md` | HTTP/AMQP маршрутизация |
| `Описание схемы дистрибутивов...md` | Схема файлов дистрибутива online-ru/kz |
| `Python.md` | Настройка локального стенда |

## Key Insights

- **Хоттабыч** — центральная точка управления обновлениями; патчи заменяют файлы в дистрибутиве без пересборки, скрипты выполняют код через DWC
- **DeveloperScript** — специальный объект БЛ с жёстким именованием; методы выполняются лексикографически под каждым клиентом
- **Права доступа** — трёхуровневая система: участок (.uax) → роль (.rlx) → пользователь; объединение = максимальный доступ
- **Маршрутизация** — nginx upstream по URL-пути; `?srv=1` → служебный пул; при обновлениях учитываются `x_version`/`x_module`
- **Дистрибутивы** — чёткое разделение: online32/online (базовые) → online-bl-ru/kz (региональные) → online-master-bl (Тензор); добавлять модули только в нижние уровни
