---
type: concept
title: "Parameters API (клиентское и серверное)"
tags:
  - wasaby
  - infrastructure
  - parameters
  - api
status: current
related:
  - "[[Parameters-Service]]"
created: 2026-04-12
updated: 2026-04-12
---

# Parameters API

## Клиентское API (TypeScript)

Библиотека `ParametersWebAPI/Scope`.

```typescript
require(['ParametersWebAPI/Scope'], function(ConfigLoader) {
    // Запись
    ConfigLoader.USER.set('TestSetting', 'test_value');

    // Чтение USER-параметров
    ConfigLoader.USER.load(['ИдентификаторНашейОрганизации', 'TestSetting'])
        .then(function(cfg) {
            console.log(cfg.get('TestSetting')); // test_value
        });

    // Чтение ACCOUNT-параметров
    ConfigLoader.ACCOUNT.load(['РежимОтображенияСпискаСотрудников'])
        .then(function(cfg) { ... });
});
```

### Методы клиентского API

| Метод | Описание | Возвращает |
|---|---|---|
| `load(params[], ignoreCache?)` | Загрузка параметров | `Promise<IConfig>` |
| `set(key, value)` | Установить значение | `Promise<Boolean>` |
| `remove(key)` | Удалить параметр | `Promise<Boolean>` |
| `fill(params)` | Предзагрузка без запроса в сервис | void |

> GLOBAL и ACCOUNT нельзя записывать с клиента.

### Browser BL-методы (ParameterExt.*)

| Метод | Описание |
|---|---|
| `ParameterExt.Set(key, value, scopeType)` | Запись из браузера |
| `ParameterExt.Get(key, scopeType)` | Чтение одного параметра |
| `ParameterExt.GetByScope(scopeType, keys[], accessTime)` | Чтение всех параметров scope |
| `ParameterExt.Erase(key, scopeType)` | Удаление |

## Серверное API (Parameter.*)

Поставляется в модуле **Parameter Service RPC**.

### Чтение

| Метод | Описание |
|---|---|
| `Parameter.Read(scopeType, scope, key)` | Читает один параметр |
| `Parameter.GetByScope(scopeType, scope)` | Все параметры scope |
| `Parameter.GetByScope(scopeType, scope, accessTime)` | С фильтром по времени |
| `Parameter.GetMultiple(scopeType, scope, keys[])` | Несколько параметров |
| `Parameter.GetMultiple(scopeType, scope, keys[], accessTime)` | То же с фильтром |
| `Parameter.MultiGet(parameters RS)` | Несколько параметров разных scope |
| `Parameter.GetByClientId(clientIds[], keys[])` | Параметры всех пользователей клиентов |
| `Parameter.GetByScopeAndNamespace(scopeType, scope, namespace)` | По пространству имён |

### Запись/Удаление

| Метод | Описание |
|---|---|
| `Parameter.Set(key, value, scopeType, scope)` | Запись / перезапись |
| `Parameter.MultiSet(parameters RS)` | Массовая запись разных scope |
| `Parameter.Erase(key, scopeType, scope)` | Удаление |
| `Parameter.EraseAllByScopeAndNamespace(scopeType, scope, namespace)` | Удаление пространства имён |

### Формат Scope

- `scopeType=0` (GLOBAL): `scope=null`
- `scopeType=1` (USER): `scope="5609234"` (UID)
- `scopeType=4` (DEVICE): `scope="usd-pupkin.corp.tensor.ru"`

> [!note] Массовые методы (MultiGet/MultiSet) не кэшируются. Несколько отдельных read-вызовов могут быть лучше для нагрузки.
