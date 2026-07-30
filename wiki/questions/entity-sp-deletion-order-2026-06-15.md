---
type: synthesis
title: "Баг: удаление фичи entity_sp до полного раскатывания"
created: 2026-06-15
updated: 2026-07-30
tags:
  - price-formation
  - discount-cards
  - feature-flags
  - bugfix
  - entity-sp
status: resolved
related:
  - "[[Loyalty-Desktop-Broker-Migration]]"
  - "[[Тимошенко А.А.]]"
  - "[[Feature-Flag-Removal-LOYALTY-IT-NAV]]"
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

---

## Разрешение: повторное удаление фичи, 2026-07-30

Задача [№05144878](https://online.sbis.ru/opendoc.html?guid=c9c3e3ec-efc4-46d0-b2b2-50d4817e28b9&client=3), срок 2026-07-30, статус «В обработке».

### Почему тянулось полтора месяца

Из переписки по задаче:
- 2026-06-05 (день удаления, `1fb3ffbd1c`): Голубь Фёдор сразу возразил — через него прошло «около 10» ошибок под `entity_sp`, «мы тут очень спешим».
- 2026-06-11: Мусохранов Андрей уточнил у Курникова М., успевают ли вообще внедрить фичу, раз её уже удаляют, хотя «она даже нигде не внедрена». Курников ответил: «прямо сейчас спиливать не надо, оставить на конец месяца, ждём исправления ошибок в 3211–3213 от команды [не price-formation]».
- 2026-06-15: откат (см. выше) слит в `rc-26.4100` через `fa95ca0235`.
- 2026-07-27: Лебедева Н. — «с Мишей обсудили, что сделаем (или не сделаем) по отдельной задаче» (про доп. требование — проверка лицензии по композитному ключу на странице настроек ДК).
- Уточнение пользователя (2026-07-30): «Было не готово не в нашей команде, сыпались ошибки под фичей» — то есть блокером была не готовность price-formation, а нестабильность фичи `entity_sp` на стороне другой команды (владельца `entity_sp`/композитных ключей).

### Что изменилось к 2026-07-30

Фича `entity_sp` успела обрасти новым кодом уже поверх восстановленного (реверченного) состояния — `check_feature(Feature.ENTITY_SP)` появился в файлах, которых не было в исходном `1fb3ffbd1c`: отчёты (`report_new_clients`, `useofbonus`, `useofcards`, `useofpromocodes`, `useofpromotion`), `markup/create_item.py`, `promotion/description.py`, `promotion/helpers/conditions.py`, `promotion/update_raw.py`, `discountcardtype/init.py`, и жёсткая проверка в `helpers/license.py` (без фичи — `sbis.Warning`).

**Решение по объёму (подтверждено пользователем):** повторное удаление затрагивает **только** исходные 35 файлов из `1fb3ffbd1c` — ДК, бонусы, промокоды, реферальные бонусы, `helpers/sale_point.py`. Новые места использования флага вне этого списка — зона ответственности их авторов, не трогались.

Параллельно Марков А.В. в тот же день (2026-07-30, `dcc13b9df6`) переудалил фронтовую часть на новой ветке `26.5100/bugfix/05144878_feature_del` от актуального `rc-26.5100` — подтверждает, что команда синхронно переигрывает старый откат именно в 5100.

### Механика повторного удаления (бэкенд)

```bash
git checkout -b 26.5100/bugfix/aatimoshenko/05144878_feature_del rc-26.5100
git revert -n fa95ca0235   # revert-коммит, которым в июне откатили 1fb3ffbd1c
# 2 конфликта — код успел эволюционировать за 1.5 месяца
```

`git revert` самого revert-коммита (`fa95ca0235`) — рабочий приём для «откатить откат», но он ломается там, где код после отката продолжал жить своей жизнью:

- **`bonus/update_settings.py`** — после `fa95ca0235` кто-то упростил проверку лицензии (убрал fallback на `old_sale_point_list`). Наивный revert предлагал старый (до-упрощения) вариант тела функции. Разрешение: убрать только `check_feature(Feature.ENTITY_SP) and` из условия, тело оставить в актуальном (упрощённом) виде.
- **`promocode/update.py`** — после `fa95ca0235` добавили переменную `promo_code_type` (рефакторинг повторных `.Get('Type')`), вызов `promo_code_to_broker(...)`, и полностью новый блок записи `SalePointList` в историю через `promocode_folder_history`/`promocode_item_history` (заменил старые `PromoCodeHistory`/`on_after_update_history`), сам блок целиком под `check_feature(Feature.ENTITY_SP)` без `else`. Разрешение: сохранить весь новый код, убрать только feature-guard (условие стало безусловным).

**Правило для похожих ситуаций:** если `git revert` конфликтует спустя длительное время, конфликт почти всегда означает «код-получатель мутировал независимо от флага». Наивно брать сторону старого (pre-revert) коммита нельзя — теряется весь параллельный рефакторинг. Разрешать нужно вручную: взять актуальную структуру кода, убрать именно feature-guard, тело/поведение оставить как есть.

### Верификация перед коммитом

- `grep` по всем застейдженным файлам на `ENTITY_SP`/`check_feature` — чисто, утечек нет
- `py_compile` всех 33 изменённых `.py` — ОК
- `.orx` (XML) после auto-merge — валидны (`xml.etree.ElementTree.parse`)

Коммит: `930d0b1dc9` — "Удалена фича entity_sp и ДК, бонусов, реферальных бонусов, промокодов", ветка `26.5100/bugfix/aatimoshenko/05144878_feature_del`, не запушено на момент записи.
