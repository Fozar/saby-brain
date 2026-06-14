---
type: concept
title: "Saby Feature Toggles API"
created: 2026-04-10
updated: 2026-04-13
tags:
  - feature-flags
  - api
  - wasaby
  - backend
  - frontend
  - mobile
  - offline
status: current
related:
  - "[[Saby-Service-Config]]"
  - "[[Loyalty-Cloud-Config]]"
  - "[[DWC-Migration-SDK]]"
---

# Saby Feature Toggles API

Сервис переключателей функционала (feature-ctrl). Управляет состоянием (включён/выключен) именованных переключателей с гранулярностью до конкретного пользователя. Используется для безопасного вывода нового функционала в работу.

> [!key-insight] Время жизни
> Переключатели **временные** — после окончания вывода функционала должны быть удалены. Для постоянных настроек используйте [[Saby-Service-Config|параметры сервисов]].

## Декларация фичи: первый шаг

> [!key-insight] Правило: сначала .feature файл
> При создании новой фичи **первым делом** объявить её в `.feature` файле — до любого кода, который её использует.

`.feature` — декларативный ресурс Wasaby, который описывает переключатель. Компилятор платформы обрабатывает эти файлы и делает переключатель доступным во всех слоях (C++/Python/JS/offline).

**Порядок действий:**
1. Создать `.feature` файл с описанием переключателя
2. Подключить в cmake (`compiled_resources ... RESOURCES_LIST ... feature`)
3. Только после этого писать код с `Feature('my_feature').IsOn(...)`

> [!warning] Нельзя пропускать декларацию
> Использование переключателя без `.feature` файла — антипаттерн. В offline/mobile первый запрос всегда вернёт `false`, пока компилятор не обработал ресурс.

---

## Идентификатор переключателя

- Максимум **20 символов**
- Допустимы: строчная латиница, цифры, `-` и `_`
- Пример: `red_button`, `new_feature`

## Backend (Web-приложения)

### Зависимости

**C++:**
- cmake: `sbis_add_sdk_dependencies(sbis-feature300)`
- include: `#include <feature/feature.hpp>`
- Для сброса кэша по событию: модуль `Feature Access Client Cache Reset`

**Python:**
- модуль: `import sbis_feature`
- Для Python также нужен модуль `Feature Access Client - Py`

### Варианты вызова IsOn (3 перегрузки)

| Вариант | Сигнатура | Когда использовать |
|---------|-----------|-------------------|
| а) Для всех | `IsOn()` | Только если переключатель никогда не задаётся на клиентов/пользователей. Самый быстрый. |
| б) По клиенту | `IsOn(client_id)` | Если не задаются конкретные пользователи. Чуть медленнее. |
| **в) Рекомендуемый** | `IsOn(client_id, user_id)` | **Всегда корректен.** Использовать по умолчанию. |
| сессия | `IsOnBySession()` | Берёт client/user из текущей сессии. |

> [!warning] Важно
> Если передать `client_id`/`user_id` из сессии, а сессии нет — значения неопределены, метод вернёт `false`.

### Python-примеры (рекомендуемый вариант)

```python
import sbis_feature

red_button = sbis_feature.Feature('red_button')

# Простая проверка
if red_button.IsOn(client_id, user_id):
    # включено
    pass

# С извлечением значения
if red_button.IsOn(client_id, user_id):
    value = red_button.GetValue()  # str или None

# С флагами
RED_THEME = 0
GREEN_THEME = 1
if red_button.IsOn(client_id, user_id):
    if red_button.FlagsIsTrue(RED_THEME):
        pass
```

### C++-примеры (рекомендуемый вариант)

```cpp
Feature red_button("red_button");

if (red_button.IsOn(client_id, user_id)) {
    OptString value = red_button.GetValue(client_id, user_id);
}
```

### Полный API класса Feature (Web, C++ и Python)

| Метод | Описание |
|-------|----------|
| `IsOn()` | Состояние для всех |
| `IsOn(client)` | Состояние для клиента |
| `IsOn(client, user)` | Состояние для пользователя |
| `IsOnBySession()` | Состояние из текущей сессии |
| `GetValue()` / `GetValue(client)` / `GetValue(client, user)` | Значение переключателя (только при `IsOn`==true) |
| `GetValueBySession()` | Значение для текущей сессии |
| `FlagsIsTrue(position)` | Флаг по позиции (только при `IsOn`==true) |
| `GetEnabledFeaturesFromBitmap(client, user)` | Набор включённых переключателей из служебного битмапа `__sbis__f_bitmaps` |
| `Clear()` (static) | Сброс локального LRU-кэша |

> [!warning] GetValue и FlagsIsTrue
> Вызывать **только после** `IsOn(...) == true`. При выключенном переключателе результат не определён.

## Mock для юнит-тестирования

Добавить в `sbis_rpc_service.ini`:

```ini
Feature control.Mocking.On = true
Feature control.Mocking.OnToggles = {"test_feature1": "", "test_feature2": "text_value"}
```

Все ключи в `OnToggles` считаются включёнными с указанным значением. Остальные — выключены.

## Frontend (Web-приложения)

Модуль: `import { Feature } from 'Feature/feature'` (или `'FeatureAccess/feature'`)

### Асинхронный запрос (значение доступно)

```javascript
Feature.require(['redbutton']).then(([feature]) => {
    if (feature.isOn()) {
        const value = feature.getValue();
    }
});
```

### Синхронный запрос (только состояние, без значения)

```javascript
const [redbutton, all_of_me] = Feature.get(['redbutton', 'all_of_me']);
if (redbutton) { /* включён */ }
```

> [!note] Предзагрузка для синхронного метода
> Нужна предзагрузка через `FeatureAccess/feature:Factory` (в preload страницы) или через `Feature.require()`. Состояние синхронных фич формируется единожды при рендере.

### WML-шаблон (HOC)

```xml
<Feature.access:Container idFeature="{{['redbutton']}}">
    <Controls.buttons:Button ... />
</Feature.access:Container>
```

### Debug: stub/unstub

```javascript
Feature.stub('my_feature', true);   // принудительно включить
Feature.stub('my_feature', false);  // принудительно выключить
Feature.unstub('my_feature');       // вернуть исходное
```

Работает для `get()`, `require()`, `isOn()`.

### testLoadBitmap(client, user)

```javascript
const enabled = await Feature.testLoadBitmap(12345, 67890);
// → Promise<string[]> — список включённых фич
```

Только для диагностики расхождений, не заменяет `get()`/`require()`.

## Управление пунктом аккордеона

В navx/pagex:

```xml
<item id="structure" feature="new_feature">  <!-- скрыт, пока new_feature выключен -->
<item id="structure" feature="!new_feature"> <!-- инверсия: скрыт при включённом -->
```

> [!warning]
> Если переключатель не существует на сервисе — пункт **скрывается**. Удалять атрибут нужно **до** удаления переключателя.

## Backend мобильного приложения

- Основной сервис наследовать от `FeatureServiceMobile.s3srv`
- Свой сервис наследовать от `FeatureBase.s3srv`
- В cmake: `sbis_add_subproject("rights/distr/feature-service")`

> [!warning] Асинхронность в МП и offline
> Первый запрос к фиче вернёт `false`. Реальное состояние обновится только после синхронизатора. Ожидать: задержка = время инвалидации + время синхронизатора. Подписка: `FeatureOnSync`.

## Offline-приложение

| s3srv шаблон | Назначение |
|---|---|
| `FeatureServiceOffline.s3srv` | Основная реализация, только один на приложение |
| `FeatureClientOffline.s3srv` | Вспомогательный прокси, можно несколько |

- C++: родитель `FeatureClientOffline.s3srv`
- Python: родитель `FeatureClientOfflinePy.s3srv`

### Предзагрузка статусов (offline/mobile)

1. При первом запуске: синхронизатор наполняет кэш статусами "для всех"
2. При авторизации (`BeforeAuthentificationComplete`): загружаются статусы для клиента/пользователя (лог: `"FeaturePrimaryFillCache"`)

Нюансы:
- **Значения и флаги не предзагружаются** — только состояния. Загрузятся при первом запросе.
- Инвалидация предзагруженного кэша: 1 секунда, `need_update = false` → обновится при следующей синхронизации после первого запроса
- Desktop: компилятор уже включён. Mobile: нужно включить компилятор `.feature` ресурсов в cmake (`compiled_resources ... RESOURCES_LIST ... feature`)

## Микросервис C++ (статические методы)

Для микросервисов интерфейс отличается — статические методы класса `Feature`:

```cpp
#include <feature_service/feature.hpp>

Feature::HasOn("red_button")                    // для всех
Feature::HasOn("red_button", client_id)         // по клиенту
Feature::HasOn("red_button", client_id, user_id) // по пользователю
Feature::IsOnBySession("red_button")
Feature::GetValue("red_button")
Feature::FlagsIsTrue("red_button", RED_THEME)
Feature::FlagsIsTrue("red_button", client_id, RED_THEME)
```

### События микросервиса

```cpp
#include <feature_service/feature_update_event.hpp>

// OnSync — список изменившихся фич
FeatureUpdateEvent::Instance().OnSync()->RegisterCallbackFunction({ ... });

// FeatureOnSync — конкретная фича
FeatureUpdateEvent::Instance().FeatureOnSync(L"feature_name")->RegisterCallbackFunction({ ... });
```

## Связанные страницы

- [[Saby-Service-Config]] — параметры сервисов vs переключатели: когда что использовать
- [[Loyalty-Cloud-Config]] — облачные параметры DCService, антибот
- [[DWC-Migration-SDK]] — пример использования feature flags для поэтапного вывода (дедлайн 30.07.26)
