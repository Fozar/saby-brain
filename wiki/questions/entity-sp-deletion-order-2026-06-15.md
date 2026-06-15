---
type: synthesis
title: "Баг: удаление фичи entity_sp до полного раскатывания"
created: 2026-06-15
updated: 2026-06-15
tags:
  - price-formation
  - discount-cards
  - feature-flags
  - bugfix
  - entity-sp
status: developing
related:
  - "[[Loyalty-Desktop-Broker-Migration]]"
  - "[[Тимошенко А.А.]]"
---

# Баг: удаление фичи entity_sp до полного раскатывания

## Симптом

На стенде `online-inside_26.4100` при создании типа дисконтной карты (Бизнес → Скидки и акции → Дисконтные карты → «+») не подтягивается точка продаж в диалог. Задача: [№06108231](https://online.sbis.ru/opendoc.html?guid=019eb177-8bf7-7fe9-a0b2-45ea6e6da9e0&client=3).

## Корневая причина

Коммит `1fb3ffbd1c` («Удалена фича entity_sp и ДК, бонусов, реферальных бонусов, промокодов», 2026-06-05) удалил guard-проверки `check_feature(Feature.ENTITY_SP)` из 35 файлов Python.

В `get_list.py` типов ДК это выглядело так — до удаления:

```python
is_entity_sp_enabled = check_feature(Feature.ENTITY_SP)
...
if is_entity_sp_enabled:
    sale_point_items = sbis.НашаОрганизация.listWithBranches(...)  # новый формат
else:
    sale_point_info = sbis.DiscountCardDesign.GetSalePointInfo(...)  # старый формат
```

После удаления код безусловно вызывает `listWithBranches`. Но на pretест-стенде фича `entity_sp` **не включена для всех** — фронтенд ждёт `SalePointInfo` (старый формат), получает `null`, точка продаж не отображается.

## Ключевой принцип (Михель Витольд)

> «По идее фича сначала должна включаться на всех, и только потом удаляться. А на претесте она не на всех включена.»

**Правило**: удалять фичу (убирать feature-flag guards) можно только после того, как фича включена на 100% аудитории на всех стендах. Иначе пользователи без фичи получают сломанный путь выполнения.

## Связанный фронтовый откат

Параллельно Марков А.В. создал откат фронтовых изменений (`79e9357235`):
- Коммит `ec3415058a` — revert фронтендной части
- Ветка: `26.4100/bugfix/05144878_feature_revert`
- Статус 2026-06-15: не слит в `rc-26.4100`

## Фикс

```bash
git checkout -b 26.4100/bugfix/06108231_entity_sp_revert origin/rc-26.4100
git revert 1fb3ffbd1c --no-commit
git commit
```

Revert чистый (нет конфликтов), 35 файлов, 317 вставок / 120 удалений — симметрично оригинальному коммиту.

Затронутые модули: `discountcard/discountcardtype`, `dcservice/servicediscountcard`, `loyaltyprograms/bonus`, `loyaltyprograms/promocode`, `loyaltyprograms/promotion`, `loyaltyprograms/referralbonus`, `helpers/sale_point`.

## Тесты

| Директория | Результат |
|---|---|
| `discountcard/discountcardtype` | 180 OK, 4 skipped, 1 pre-existing import error |
| `loyaltyprograms/bonus` | 165 OK, 1 skipped |
| `loyaltyprograms/referralbonus` | 52 OK, 11 skipped |
| `loyaltyprograms/promocode` | 128 OK, 4 skipped, 1 pre-existing import error |

Pre-existing import errors — `ModuleNotFoundError: No module named 'tests_priceformationonline'` в test-runner окружении, не связаны с фиксом.
