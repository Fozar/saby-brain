---
address: c-000119
created: 2026-06-14
updated: 2026-06-14
type: concept
title: "Wasaby Parameters Service (parameters)"
tags:
  - wasaby
  - backend
  - middleware
  - parameters
  - settings
  - api
status: current
related:
  - "[[Wasaby-BL-Calls]]"
  - "[[Wasaby-Service-Framework]]"
sources:
  - ".raw/wasaby.Backend/Middleware/Сервис параметров/Сервис параметров.sabydoc"
  - ".raw/wasaby.Backend/Middleware/Сервис параметров/Как встраивать (API parameters).sabydoc"
---

# Wasaby Parameters Service

Сервис `parameters` — хранилище именованных значений с областью видимости (scope). Заменяет специализированные таблицы в схеме online для хранения пользовательских и системных настроек.

## Области видимости (ScopeType)

| Константа | Значение | Описание |
|-----------|---------|----------|
| `stGLOBAL` | 0 | Глобальные (уровень системы) |
| `stUSER` | 1 | Пользователя |
| `stPROFILE` | 2 | Профиля |
| `stACCOUNT` | 3 | Аккаунта |
| `stDEVICE` | 4 | Устройства |
| `stUSER_DEVICE` | 5 | Пользователя + устройства |

Примеры: история ввода → USER, настройки фильтров → USER, бухгалтерские настройки → ACCOUNT, настройки уведомлений → DEVICE.

Имя параметра: `"Префикс.Суффикс"` — `Префикс` считается пространством имён (вложенность не поддерживается).

## Серверное API (Parameter Service RPC)

Подключить сервисный модуль **Parameter Service RPC** из SBIS SDK.

| Метод | Описание |
|-------|----------|
| `Parameter.Read(ScopeType, Scope, Key)` | Читает один параметр |
| `Parameter.Set(ScopeType, Scope, Key, Value)` | Устанавливает параметр |
| `Parameter.Erase(ScopeType, Scope, Key)` | Удаляет параметр |
| `Parameter.GetByScope(ScopeType, Keys)` | Все параметры scope по ключам |
| `Parameter.GetMultiple(3/4)` | Несколько параметров за раз |
| `Parameter.MultiGet(1)` | Батч-чтение |
| `Parameter.MultiSet(1)` | Батч-запись |
| `Parameter.GetByScopeAndNamespace` | Все параметры namespace |
| `Parameter.EraseAllByScopeAndNamespace` | Удалить все параметры namespace |
| `Parameter.GetByClientId(2)` | Параметры по ClientId |

`Scope` — строка, описывающая владельца (например, ID пользователя). `null` — для глобального.

## Browser/Client API

```javascript
const { ConfigLoader } = require('...');

// USER-scope: записать и прочитать
ConfigLoader.USER.set('TestSetting', 'test_value');
ConfigLoader.USER.load(['TestSetting']).then(cfg => {
    console.log(cfg.get('TestSetting')); // test_value
});

// ACCOUNT-scope
ConfigLoader.ACCOUNT.load(['Учет.УчетПоПодразделениям']);
```

| Метод | Описание |
|-------|----------|
| `load(params, ignoreCache?)` | Загрузить параметры; кэш в браузере |
| `set(key, value)` → `Promise<Boolean>` | Установить |
| `remove(key)` → `Promise<Boolean>` | Удалить |
| `fill(params)` | Предзаполнить без запроса к сервису |

> GLOBAL и ACCOUNT нельзя устанавливать с клиента (управляется параметром облака `Parameter Service.Config.ЗапретитьЗаписьГлобальныхПараметров`).

## Browser-side BL API (ParameterExt)

| Метод | Описание |
|-------|----------|
| `ParameterExt.Set(Key, Value, ScopeType)` | Установить |
| `ParameterExt.Get(Key, ScopeType)` → `String\|null` | Прочитать |
| `ParameterExt.GetByScope(ScopeType, Keys, AccessTime)` | Все параметры scope |
| `ParameterExt.Erase(Key, ScopeType)` | Удалить |

Scope автоматически определяется из сессии пользователя.

## Жизнь параметров

- Автоудаление при отсутствии обращений: 30 дней (боевой сервис: 180 дней)
- Параметр облака: `Parameter Service.Config.Время жизни параметра`
- БД шардированная; к ней пользователь не имеет прямого доступа

## Связанные страницы

- [[Wasaby-BL-Calls]] — вызов Parameter.Read через BLObject
- [[Wasaby-Service-Framework]] — EndPoint сервиса parameters
