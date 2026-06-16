---
type: concept
title: "ReferralProgram Data Model"
created: 2026-06-16
updated: 2026-06-16
tags:
  - referral-program
  - price-formation
  - data-model
  - sabynet
status: developing
related:
  - "[[SabyBank-RKO-Referral]]"
  - "[[ReferralProgram-Stub-Implementation]]"
---

# ReferralProgram — модель данных и архитектура

Реферальная программа (оффер) — объект в таблице `ВидЦены`. Принадлежность к SabyNet-конфигурации (Реф. Сети / БизнесГруппе) определяется **иерархией разделов**, а не прямым FK.

---

## Схема данных

```
БизнесГруппа (SabyNet-конфигурация = "Реф. Сеть")
    └── Раздел (папка в ВидЦены) — создаётся при первой программе в группе
            └── ВидЦены (= реф. программа, e.g. "Т-банк")
                    Атрибуты.ReferralProgram.AdObject      → ID корневого источника
                    Атрибуты.ReferralProgram.AdObjectUUID  → UUID корневого источника
                    └── ВидЦеныВидКарты → ВидКарты (эмиссия реф. кодов)
                                                └── Карта (реф. код партнёра)
                                                        Лицо = @Лицо партнёра
                                                        Атрибуты.ReferralProgram.AdObject → @AdObject партнёрского источника

AdObject (маркетинговая система — внешняя)
    └── Корневой источник программы (ad_object_uuid)
            └── Источники партнёров (один на каждого Join)
                    access_data_guid      = ID БизнесГруппы  ← единственная жёсткая ссылка
                    access_data_client_id = ClientID партнёра
                    @AdObject             → цифра в utm_rfcid
```

---

## Реферальная ссылка

`utm_rfcid=3_25770347` декодируется как `{account_number}_{@AdObject партнёрского источника}`.

Функция сборки — `compute_referral_link` в `core.py`:
```python
referral_code = f'{account_number}_{source_id}'  # source_id = @AdObject
```

При миграции программы `@AdObject` источника партнёра **не меняется** → ссылка остаётся живой.

---

## Почему `access_data_guid` — единственная жёсткая ссылка на БизнесГруппу в источнике

В таблице `ВидЦены` нет поля «БизнесГруппа» — принадлежность идёт через иерархию `Раздел`. В AdObject-источниках нет понятия иерархии разделов, поэтому ID группы пишется явно в `access_data_guid` при `Join`:

```python
# join.py:74
source = get_or_create_source(
    ...,
    parent_uuid=str(referral_program.ad_object_uuid),  # под корневым источником программы
    access_data_guid=referral_business_group.id,        # ← жёсткая ссылка на БизнесГруппу
    access_data_client_id=partner_client_id,
)
```

Остальные связи косвенные:
- Источник висит в иерархии под корнем реф. сети (`parent_uuid`)
- Реф. программа принадлежит группе через `Раздел` ВидЦены

---

## Ключевые классы (price-formation)

| Класс | Файл | Роль |
|---|---|---|
| `ReferralProgram` | `core.py` | Объект реф. программы, маппинг ВидЦены |
| `ReferralProgramRepository` | `core.py` | CRUD в БД (`Создать`, `Записать`, `Прочитать`) |
| `ReferralBusinessGroup` | `core.py` | Обёртка над БизнесГруппой, `folder_id` |
| `ReferralProgramField` | `core.py` | Константы имён полей |

`ReferralProgram.folder` = `ВидЦены.Раздел` — через этот атрибут меняется принадлежность к сети.

---

## Миграция программы между Реф. Сетями (задача 06096778)

Задача: перенос оффера Т-банк из одной Реф. Сети Тензора в другую.

**Что нужно перепривязать:**

1. **Источник партнёра** (Соков М.) — перебить `access_data_guid` на ID новой БизнесГруппы + пересчитать агрегаты. `@AdObject` остаётся — ссылка виджета не ломается.

2. **ВидЦены** (Тимошенко А.) — сменить `Раздел` на папку новой БизнесГруппы:
   ```python
   rp = ReferralProgramRepository.read(referral_program_id)
   rp.folder = ReferralBusinessGroup.create(new_bg_id, BusinessGroupRole.VENDOR).folder_id
   ReferralProgramRepository.update(rp)
   ```

3. **Метод-обёртка** (Тимошенко А.) — вызов (1) + (2) в одной транзакции, доступен из JS-консоли. Вход: `referral_program_id` + `new_business_group_id`.

**Задача 2 — флаг неактивных программ** (Тимошенко А.):
- Флаг: `Атрибуты.ReferralProgram.IsActive = false`
- Фильтр по флагу добавляется в SQL WHERE в `get_list`, `get_stats_helpers`, `get_joinable_list`, `get_partner_list`
- Метод простановки флага вызывается из JS-консоли

**Реалистичная оценка:** ~0.5–1 день на все задачи Тимошенко А. (не 3.5 дня — каждая задача это 1–3 строки логики в новом файле).

---

## Методы выборки (точки для фильтра по IsActive)

- `get_list.py` → `_sql_get_referral_program_list` — основной список
- `get_stats.py` → `sql_get_price_stats` в `get_stats_helpers.py`
- `get_joinable_list.py` — программы доступные к подключению
- `get_partner_list.py` — список партнёров
