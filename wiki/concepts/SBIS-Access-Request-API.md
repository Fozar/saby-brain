---
type: concept
title: "SBIS — API запросов доступа (Rightcheck)"
address: c-000019
tags:
  - wasaby
  - security
  - access-control
  - python
  - http403
status: current
created: 2026-05-19
related:
  - "[[Wasaby-Access-Control]]"
  - "[[Wasaby-BL-Advanced]]"
  - "[[Wasaby-BL-Methods]]"
updated: 2026-05-19
---

# SBIS — API запросов доступа (Rightcheck)

Когда БЛ обнаруживает недостаток прав, она бросает специальный HTTP 403, который платформа превращает в кнопку «Запросить доступ» на интерфейсе.

## Концепция

**Запрос доступа** — платформенный документ ЭДО. Два регламента:
- Запрос к разделу/документу — создаётся при 403 на функционал/документ.
- Запрос по IP — при входе с неразрешённого IP.

Исполнитель запроса = пользователь с ролью «Администратор настроек доступа» (переопределяется на уровне регламента).

Платформа автоматически: формирует документ → вычисляет исполнителя → выдаёт доступ при положительном решении → уведомляет автора.

### Требования к исключению

1. HTTP-код = 403.
2. Сериализуемо.
3. Содержит данные в формате параметров `AccessRequest.Send`.

Используй хэлперы из модуля `rightcheck` — они формируют `Http403` (Python) / `ResourceForbidden` (C++) с нужными данными автоматически.

---

## Python хэлперы (`from rightcheck import ...`)

### raise_http403_by_constraint

Для нехватки прав **по ограничениям** (myOfficeDocs, ourOrgs и т.п.). Текст «Запроса доступа» формируется автоматически.

```python
raise_http403_by_constraint(
    zones: list[str] | None,  # None → участки из Session.Rights()
    constraint: str,          # идентификатор ограничения
    ids: list | None,         # сущности (None для Запрещено/Разрешено)
    is_read: bool,            # True = блок "На чтение", False = "На изменение"
    detail_msg: str | None,   # в лог, не в документ
    user_msg: str | None,     # пользователю, не в документ
)
```

```python
rec = sbis.CheckRights.AccessAreaRestrictions("ourOrgs", STAFF_AREA)
if rec.Access & AccessFlags.READ:
    if our_org not in rec.Restrictions.Get("Read", []):
        raise_http403_by_constraint(zones=[STAFF_AREA], constraint="ourOrgs",
                                    ids=[cur_org], is_read=True)
```

### raise_http403_by_zone_access

Для нехватки **уровня доступа к одному участку**.

```python
raise_http403_by_zone_access(zone: str, access: sbis.AccessFlags,
                              detail_msg=None, user_msg=None)
```

C++ shortcut: `CheckRights.ThrowIfNotPermittedByAccess(Zone, Access)`.

### raise_http403_by_access

Для нехватки уровня доступа на **одном или нескольких участках**.

```python
raise_http403_by_access(
    zones: list[str],
    access: sbis.AccessFlags,
    is_or_logic: bool,  # True = достаточно одного участка; False = нужны все
    detail_msg=None,
    user_msg=None,
)
```

C++ shortcut: `CheckRights.ThrowIfNotPermittedByAccess(Zones, Access, IsOrLogic)`.

### raise_http403_by_access_dict

Передаёт готовый словарь `{area_id: access}` (результат `AccessAreas.ToDict()`).

```python
access_dict = sbis.CheckRights.AccessAreas([STAFF_AREA, TASKS_AREA], sbis.Record()) \
                               .ToDict("AccessArea", "Access")
if not staff_access & AccessFlags.WRITE and not tasks_access & AccessFlags.ADMIN:
    raise_http403_by_access_dict(access_dict=access_dict, is_or_logic=True)
```

C++ shortcut: `CheckRights.ThrowIfNotPermittedByAccessDict(access_dict, IsOrLogic)`.

### raise_http403_admin_msg

Произвольный текст в документ «Запрос доступа».

```python
raise_http403_admin_msg(admin_msg: str, detail_msg=None, user_msg=None)
```

---

## C++ хэлперы

Аналоги всех Python-хэлперов описаны в:
`core/sbis-permission-checker/rights_error.hpp` (ветка rc-23.5000).

---

## sbis.CheckRights API (сводка)

| Метод | Что возвращает |
|-------|---------------|
| `AccessAreaRestrictions(constraint, zone)` | Record с Access + Restrictions для одного участка |
| `AccessAreasRestrictions(constraint, zones)` | merged Restrictions для нескольких участков |
| `ZoneAccess(zone)` | AccessFlags уровень доступа |
| `AccessAreas(zones, rec)` | RecordSet с AccessArea + Access per zone |

---

## Метод БЛ

**`Персонал.RightsOnEmployee(FaceId, AccessAreas, AccessLevel)`** — проверяет права на сотрудника с учётом ограничений `MyOfficeDocs` и `OurOrganization` для переданных участков и уровня доступа.

---

## Внедрение на интерфейсе

```javascript
import { createAccessDeniedError } from 'TransportCore/transport';

const errorController = new ErrorController({}).process({
    error: createAccessDeniedError([AccessZone.MY_PROFILE], MY_PROFILE_PAP, true),
    mode: ErrorViewMode.include,
});
```

Платформа поддерживает кнопку запроса:
- при недоступности страницы (403 при загрузке),
- при ошибке вызова метода БЛ в компоненте.
