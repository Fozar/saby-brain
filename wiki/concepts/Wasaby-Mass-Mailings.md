---
address: c-000141
created: 2026-06-14
updated: 2026-06-14
type: concept
title: "Wasaby Mass Mailings Service (md_client)"
tags:
  - wasaby
  - backend
  - mailings
  - dwc
  - subscriptions
  - md-client
status: current
related:
  - "[[Wasaby-DWC]]"
  - "[[Wasaby-Service-Framework]]"
sources:
  - ".raw/wasaby.Backend/Cервис массовых рассылок.sabydoc"
---

# Wasaby Mass Mailings Service

**Сервис массовых рассылок** — механизм выполнения задач только для тех пользователей, которые явно подписались, а не для всех пользователей облака. Задачи выполняются через [[Wasaby-DWC|DWC]] по каждому подписчику.

## Принцип работы

1. Создать задачу (Task) в Genie → авто-деплой
2. Зарегистрировать подписчиков через API
3. Запустить через Scheduler или вручную через BL API

> [!note] Отличие от обычного DWC
> Обычный DWC запускается для всех или конкретного пользователя. Массовая рассылка — только для подписанных пользователей, список которых динамически меняется.

## Python API (`md_client`)

```python
from md_client import MassDistribution

md = MassDistribution('TaskAlias')

# Подписать пользователя
md.SetReceiver(user, key, *args)

# Отписать пользователя
md.DelReceiver(user, key='')

# Применить изменения
md.Commit()
```

### Правила подписок

| Ситуация | Результат |
|----------|----------|
| Тот же `user` + тот же `key` | Заменить существующую подписку |
| Тот же `user` + другой `key` | Две независимые подписки |
| `DelReceiver(user)` без key | Отписать по всем ключам |

## BL API

| Метод | Описание |
|-------|----------|
| `MassDistribution.Commit(TaskAlias, AddedSettings, DeleteSettings)` | Применить изменения подписок |
| `MassDistribution.RunTask(TaskName)` | Запустить задачу вручную |

> [!warning] Ошибка 401
> `MassDistribution.RunTask` вернёт ошибку 401, если задача не зарегистрирована в Genie.

## C++ API

```cpp
MassDistribution::SetReceiver(PrimaryKey user, String key, Args args...);
MassDistribution::DelReceiver(Int64 user, String key = "");
MassDistribution::Commit();
```

## Связанные страницы

- [[Wasaby-DWC]] — DWC: задачи выполняются через DWC per subscriber
- [[Wasaby-Service-Framework]] — контекст развёртывания сервисов
