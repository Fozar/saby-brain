---
address: c-000127
created: 2026-06-14
updated: 2026-06-14
type: concept
title: "Wasaby History Service (history-clickhouse)"
tags:
  - wasaby
  - middleware
  - history
  - clickhouse
  - backend
  - audit
status: current
related:
  - "[[Wasaby-ClickHouse]]"
  - "[[Wasaby-BL-Calls]]"
  - "[[Wasaby-Long-Running-Operations]]"
sources:
  - ".raw/wasaby.Backend/Middleware/Сервис истории (history-clickhouse)/Сервис истории (history-clickhouse).sabydoc"
---

# Wasaby History Service

**History** — платформенный сервис истории изменений. Хранит пользовательские события в ClickHouse. Срок хранения: **3 года**.

Предназначен для клиентов портала (не для разработческих логов — у них другие инструменты).

## Концепция

```
Прикладной код → HistoryMsg() → клиент History (async) → БД (ClickHouse)
                                                         ↓
Визуальный клиент → История.History_Common_Object() ← параллельные запросы ко всем БД
```

- **Событие** = сообщение + действие + объект истории + атрибуты
- **Объект истории** — строковый ID типа "Сотрудники", "Продажи"
- **Действие** — строковый ID типа "Создание", "Изменение"
- **Субъект** — вычисляется автоматически (инициатор события)

## Подключение

- **Чтение + запись**: модуль `History`
- **Только запись**: модули `WriteHistory` + `History Metadata`
- Python: дополнительные модули не нужны
- C++: подключить заголовочный файл History

## Запись одного события

**Python:**
```python
attributes = sbis.Record()
attributes["@override_instance_name"] = "Инженер"

sbis.HistoryMsg(
    "Создана роль с названием 'Инженер'",   # сообщение
    "Создание",                              # действие
    "РолиПользователя",                      # объект истории
    attributes                               # атрибуты (опционально)
)
```

**C++:**
```cpp
Record attributes;
attributes.Set<String, String>("@override_instance_name", "Инженер");
String message = "Создана роль с названием 'Инженер'";
String action = "Создание";
String object = "РолиПользователя";
HistoryMsg(message, action, object, attributes);
```

## Запись множества событий

```python
rs = sbis.RecordSet()
event = sbis.Record()
event["Сообщение"] = "Создан сотрудник с именем Соколов Сергей Игоревич"
event["Действие"] = "Создание"
event["Объект"] = "Сотрудники"
event["ИдО"] = 123456  # числовой идентификатор экземпляра
rs.AddRow(event)

sbis.HistoryMsgSet(rs)
```

> [!warning] Для ИдО запрещено значение равное нулю.

## Переопределение атрибутов события

| Поле | Описание |
|------|----------|
| `@override_user_id` | Переопределить ID пользователя |
| `@override_user_name` | Переопределить отображаемое имя |
| `@override_client` | Переопределить ID клиента |
| `@override_instance_name` | Переопределить имя экземпляра |
| `@override_time` | Переопределить время события |
| `additional_id` | Дополнительный ID (строка или UUID, ≠ `@override_user_id`) |

Через контекст сессии:
```python
ctx = sbis.Record()
ctx["override_user_id"] = 42
ctx["override_time"] = datetime.datetime(...)
sbis.SetContextAttributes(ctx, sbis.Session.Context)
```

## Чтение истории

### Общая история объекта

```python
# БЛ-метод: История.History_Common_Object(ДопПоля, Фильтр, Сортировка, Навигация)
```

Параметры фильтра:

| Параметр | Тип | Описание |
|----------|-----|----------|
| `ВремяОт` | datetime | Начало диапазона |
| `ВремяДо` | datetime | Конец диапазона |
| `ВремяОтсчета` | datetime\|null | Для пагинации вниз (null при первом запросе) |
| `Объект` | string[] | Массив объектов истории |
| `ИдО` | int\|int[] | Числовой ID экземпляра |
| `GUID` | str\|str[] | UUID экземпляра |
| `user_id` | int\|int[] | ID пользователя |
| `exclude_actions` | str[] | Исключить действия |
| `Сообщение` | str | Фильтр по тексту |
| `check_site` | bool | False = без привязки к сайту |

## .hox метаданные

Объекты истории описываются в файлах `.hox`. Содержат метаданные: схему атрибутов, права доступа, правила отображения.

## Права доступа

Доступ к просмотру истории определяется через механизм прав платформы Wasaby. Объекты истории могут быть видны только клиенту, только пользователям клиента, или всем (общая история).

## Связанные страницы

- [[Wasaby-ClickHouse]] — хранение данных (бэкенд History Service)
- [[Wasaby-BL-Calls]] — AsyncInvoke для асинхронной записи
- [[Wasaby-Task-Queue]] — альтернатива для очередей задач
