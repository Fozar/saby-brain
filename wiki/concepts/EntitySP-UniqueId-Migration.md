---
type: concept
title: "EntitySP — UniqueId Migration for SalePoint Selector"
created: 2026-04-15
updated: 2026-05-14
tags:
  - entity_sp
  - feature-flag
  - sale-point
  - discount-card
  - migration
status: current
related:
  - "[[DiscountCard-Subsystem-Overview]]"
  - "[[Saby-Feature-Toggles-API]]"
  - "[[PriceFormation-Backend-Architecture]]"
---

# EntitySP — UniqueId Migration for SalePoint Selector

## Проблема

Компонент выбора точки продаж (SalePointSelector) использовал целочисленные `@Лицо` ключи. При выборе головной организации выбирались все её филиалы — баг, потому что `list(map(str, sale_point_id_list))` передавал строки из `@Лицо`, а не UniqueId.

Под фичей `entity_sp` компонент переходит на UniqueId-ключи (строки). Метод конвертации предоставил Милованов Максим:

```python
sbis.OurOrg.ConvertFaceIdsToUniqueIds(face_ids: List[int]) -> List[str]
```

## Правило: хранение не меняется

**`SalePointIdList` везде остаётся `Integer[]`** — на стороне сохранения фронтенд по-прежнему присылает `@Лицо` integers. Конвертация нужна только при **чтении**.

## Паттерн READ-side конвертации

На каждом read-методе, который возвращает список точек продаж для SalePointSelector, нужно:

1. Оставить поле `SalePointIdList` (INT32[]) как есть
2. Добавить companion-поле с UniqueIds под фичей:

```python
from priceformationcommon.helpers.feature import check_feature, Feature

if check_feature(Feature.ENTITY_SP):
    unique_ids = sbis.OurOrg.ConvertFaceIdsToUniqueIds(sale_point_id_list) if sale_point_id_list else []
    result.Put('SalePointUniqueIds', unique_ids, sbis.FieldType.ftARRAY_TEXT)
```

Для единственного ID (например, `QuestionarySalePointId`):

```python
if check_feature(Feature.ENTITY_SP):
    if questionary_sale_point_id:
        _unique_ids = sbis.OurOrg.ConvertFaceIdsToUniqueIds([questionary_sale_point_id])
        questionary_sp_unique_id = _unique_ids[0] if _unique_ids else None
    else:
        questionary_sp_unique_id = None
    card_type_data.Put('QuestionarySalePointUniqueId', questionary_sp_unique_id, sbis.FieldType.ftSTRING)
```

## Затронутые методы (DiscountCardType)

| BL-метод | Файл | Новое поле |
|---|---|---|
| `ReadDescription` | `read_description.py` | `SalePointItems` (переключен на `listWithBranches` с `unique_ids`) |
| `ReadQuestionary` | `read_questionary.py` | `QuestionarySalePointUniqueId` |
| `ReadNotificationSettings` | `read_notification_settings.py` | `SalePointUniqueIds` в каждом гео-уведомлении |

### read_description.py — listWithBranches

До (баг — строки из @Лицо):
```python
'МассивИД': list(map(str, sale_point_id_list)),
```

После:
```python
unique_ids = sbis.OurOrg.ConvertFaceIdsToUniqueIds(sale_point_id_list) if sale_point_id_list else []
# ...
'МассивИД': unique_ids,
# ...
sbis.Navigation(len(unique_ids), 0, True),
```

### read_notification_settings.py — RecordSet адаптер

При работе с `RecordSet` в гео-уведомлениях нужна адаптация методов:

```python
def _adapt_to_record(record_set):
    if isinstance(record_set, sbis.Record):
        return
    record_set.Remove = record_set.DelCol
    record_set.AddArrayInt32 = record_set.AddColArrayInt32
    record_set.AddString = record_set.AddColString
    record_set.AddArrayText = record_set.AddColArrayText  # добавлено под entity_sp
```

Инициализация поля перед заполнением:
```python
is_entity_sp_enabled = check_feature(Feature.ENTITY_SP)

for _field_name in ['SalePointIdList', 'SalePointListCaption', 'SalePointUniqueIds']:
    if _field_name in geo_notifications.Format():
        geo_notifications.Remove(_field_name)
geo_notifications.AddArrayInt32('SalePointIdList')
geo_notifications.AddString('SalePointListCaption')
if is_entity_sp_enabled:
    geo_notifications.AddArrayText('SalePointUniqueIds')
```

## Паттерн WRITE-side конвертации (geo-уведомления)

Фронтенд под `entity_sp` присылает `SalePointUniqueIds` (composite keys) вместо `SalePointIdList`. Бэкенд конвертирует обратно в целочисленные ID перед сохранением.

**Критическое правило: никогда не перезаписывать `SalePointIdList` пустым результатом конвертации.**

Если `get_ids_by_composite_keys` вернул `[]` (платформенный метод не нашёл запись — например, entity-иерархия ещё не синхронизирована), молчаливая перезапись приводит к потере данных: discount-cards SDK хранит JSON и при пустом `SalePoints` (`if sale_points:`) **молча удаляет уведомление из БД**.

```python
# update_notification_settings.py
for settings in geo_settings:
    if check_feature(Feature.ENTITY_SP) and settings.Get('SalePointUniqueIds'):
        converted_ids = get_ids_by_composite_keys(settings.Get('SalePointUniqueIds'))
        if converted_ids:
            settings.Set('SalePointIdList', converted_ids)
        else:
            # Fallback: оставляем SalePointIdList из входных данных
            warning(
                f'Не удалось конвертировать SalePointUniqueIds в идентификаторы ТП: '
                f'{settings.Get("SalePointUniqueIds")}'
            )
    # ... далее использовать SalePointIdList as-is
```

### Баг 05129409 (2026-05-14)

ТП в гео-уведомлениях пропадала после сохранения и перезагрузки страницы.
Root cause: `get_ids_by_composite_keys` → `[]` → `SalePointIdList = []` → `get_sale_points_location([])` → пустой RecordSet → discount-cards SDK удалял уведомление.
Fix: добавлен defensive check в `update_notification_settings.py:82–90`.

### READ-side: GetDeepestNodesByFaceIds может вернуть пустоту

`get_sale_point_items(sale_point_id_list).ToList('compositeKey')` вернёт `[]` если ТП не является листовым узлом entity-иерархии → `SalePointUniqueIds = []` → фронтенд показывает «ТП не выбрана» (display-only, данные в БД сохранены). Добавлено предупреждение в лог в `read_notification_settings.py:_add_sale_point_info`.

## Паттерн тестирования

```python
from priceformationcommon.helpers.feature import Feature, check_feature
from tests_helpers.test_case import TransactionTestCase, with_feature

UNIQUE_IDS = ['unique-id-1']

@with_feature([Feature.ENTITY_SP])          # прогоняет тест дважды: ON и OFF
class MyTest(TransactionTestCase):

    @patch('sbis.OurOrg.ConvertFaceIdsToUniqueIds', return_value=UNIQUE_IDS)  # нижний = первый арг
    def test_1(self, mock_convert, ...):
        is_entity_sp_enabled = check_feature(Feature.ENTITY_SP)
        # ...
        if is_entity_sp_enabled:
            self.assertEqual(result.Get('SalePointUniqueIds'), UNIQUE_IDS)
```

**Важно — порядок аргументов при `@parameterized.expand` + `@patch`:**

```python
@parameterized.expand([param([True, None])])
@patch('module.method_a')   # верхний
@patch('module.method_b')   # нижний → первый арг после param
def test_1(self, param_data, mock_b, mock_a):
    ...
```

`@parameterized.expand` параметры идут **первыми** после `self`, затем `@patch` моки снизу вверх.

## Мок в тестовом окружении

Метод должен быть объявлен в ORX-моке:
```
tests_new/online/clouds/Online/Mock/OurOrganization/OurOrganization.orx
```

Мок в Python-тестах через `@patch('sbis.OurOrg.ConvertFaceIdsToUniqueIds', return_value=[...])`.
