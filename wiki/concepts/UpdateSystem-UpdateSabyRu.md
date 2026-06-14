---
type: concept
title: "update.saby.ru — CDN Distribution Service"
tags:
  - saby
  - update-system
  - update-saby-ru
  - infrastructure
status: current
related:
  - "[[Хоттабыч-System]]"
  - "[[UpdateSystem-DistributionStorage]]"
created: 2026-06-12
updated: 2026-06-12
address: c-000084
---

# update.saby.ru

CDN-сеть для быстрой раздачи обновлений продуктов Тензора клиентам. Хоттабыч-агенты скачивают дистрибутивы именно с этой сети.

Адрес: `update.sbis.ru` (и региональные зеркала: `-msk-`, `-spb-`, `-yar-`)

## Цель

Быстро раздавать обновления продуктов клиентам через географически распределённую CDN-инфраструктуру.

## Архитектура

```
Хоттабыч → API MASTER → UPDATE-серверы (CDN-провайдеры)
                ↓
           SHAPER (балансировщик)
                ↓
           SYNCER (синхронизация rsync)
```

### Компоненты

| Компонент | Описание |
|-----------|----------|
| **API MASTER** | Наш сервер, управляющий зеркалами раздачи на основании API-вызовов от Хоттабыча |
| **SHAPER** | Наш сервер, проверяющий нагрузку и работоспособность зеркал, корректирующий их «вес» |
| **SYNCER** | Наш сервер, синхронизирующий файлы между зеркалами через rsync, удаляет неиспользуемые каталоги |
| **UPDATE** | Серверы у CDN-провайдеров, синхронизируют файлы через rsync |

### CDN-провайдеры

- **EdgeCenter** (бывший GCORE) — `support@edgecenter.ru`
- **CDNNOW** — `care@cdnnow.ru`

Доступы к панелям управления — через ЦОД по регламенту.

## Компоненты (детально)

| Компонент | Описание |
|-----------|----------|
| `sbis-update-master` | Виртуальный сервер, основная точка API. Начиная с определённой версии обновление происходит с гранулярностью до файла (не только папки). Управляет синхронизацией и её логами. |
| `sbis-update-shaper` | Виртуальный сервер. Получает от master список зеркал, проверяет нагрузку и работоспособность, корректирует «вес» зеркал. |
| `sbis-update-syncer` | Виртуальный сервер. Синхронизирует файлы между зеркалами через rsync, удаляет неиспользуемые каталоги. |
| `sbis-update-nginx` | Виртуальные/физические серверы. Отдают файлы клиентам по HTTPS (зеркала). |
| `sbis-docker-update-balancer` | HELM-чарт, работает в Kubernetes. На основе конфигурации с master-сервера решает, на какое зеркало перенаправить (HTTP 302). |

## API Master-сервера

### Получить статус синхронизации

```
GET /api/sync/{id}
```

- `id` — имя синхронизируемой директории или файла. Без параметра — список всех синхронизаций.
- Если Content-Type не `application/json` — ответ в текстовом формате.

| Код | Ответ | Значение |
|-----|-------|----------|
| 200 | `{ rate: x }` | Число от 0 до 100 (% синхронизации) |
| 404 | `{ message: 'Not synced' }` | Синхронизация с каталогом/файлом не запущена |

### Установить процент синхронизации

```
POST /api/sync/{id}  { "rate": N }
```

| Код | Ответ |
|-----|-------|
| 200 | `{ message: 'Set N' }` |
| 404 | `{ message: 'Not synced' }` |
| 400 | `{ message: 'Invalid sync name' }` |

### Начать синхронизацию каталога или файла

```
POST /api/sync/{id}   # id оканчивается на / для каталога
```

| Код | Ответ |
|-----|-------|
| 200 | `{ message: 'Start sync', type: 'file|folder' }` |
| 403 | `{ message: 'Deny' }` — каталог не в `syncwhitelist` |
| 404 | `{ message: 'No active mirrors' }` |
| 409 | `{ message: 'Sync exists' }` — синхронизация уже запущена |
| 400 | `{ message: 'Invalid sync name' }` — только цифры, буквы, `-`, `_`, `.`, `/` |
| 500 | `{ message: 'Write file error' }` — ошибка записи lock-файла |

### Начать очистку каталогов

```
POST /api/sync/{id}  { "clear": 1 }
```

| Код | Ответ |
|-----|-------|
| 200 | `{ message: 'Start sync', type: 'clean' }` |

> update.sbis.ru не контролирует целостность файла при передаче.

## Репозитории GIT

| Компонент | Репозиторий |
|-----------|-------------|
| sbis-update-master | `https://git.sbis.ru/ha/sbis-update-master` |
| sbis-update-master-web | `https://git.sbis.ru/ha/sbis-update-master-web` |
| sbis-update-balancer | `https://git.sbis.ru/ha/sbis-update-balancer` |
| sbis-update-syncer | `https://git.sbis.ru/ha/sbis-update-syncer` |
| sbis-update-nginx | `https://git.sbis.ru/ha/sbis-update-nginx` |
| sbis-update-shaper | `https://git.sbis.ru/ha/sbis-update-shaper` |
| HELM-чарт балансировщика | `https://git.sbis.ru/ha/charts/sbis-docker-update-balancer` |

## Стенды

| Стенд | Статус |
|-------|--------|
| PRE-DEV | Отсутствует |
| DEV | Не управляется (1 сервер, демо-режим, без синхронизации API) |
| PRE-TEST | Отсутствует (1 сервер, демо-режим) |
| TEST | Есть |
| FIX (FIX-KZ) | Есть |
| PROD | Есть |

## TLS-сертификаты (Минцифры)

Обновление сертификатов на серверах через ssh:
```
ssh update-msk.sbis.ru -p <port>
ssh update-spb.sbis.ru -p <port>
ssh update-yar.sbis.ru -p <port>
```
В nginx: изменить путь `/etc/nginx/ssl` → `/etc/nginx/ssl_mindigit` в конфигах `/etc/nginx/sites/*`, затем `nginx -s reload`.

Права — у Блажевича С.

## Связанные темы

- [[UpdateSystem-DistributionStorage]] — источник файлов для раздачи
- [[Хоттабыч-System]] — клиент, скачивающий дистрибутивы
