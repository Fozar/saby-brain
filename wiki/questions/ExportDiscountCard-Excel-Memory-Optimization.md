---
type: synthesis
title: "ExportDiscountCard.PrepareFile — выгрузка карт в Excel без памяти"
address: c-000253
created: 2026-08-05
updated: 2026-09-03
tags:
  - loyalty
  - discount-cards
  - performance
  - memory
  - excel
  - price-formation
  - sbis
status: developing
question: "Почему ExportDiscountCard.PrepareFile съедает память контейнера и работает 36 минут, и как выгружать карты в Excel с ограниченным потреблением памяти?"
answer_quality: solid
related:
  - "[[PromoCode-Generation-Memory-Optimization]]"
  - "[[Bonus-GetTotalBalance-Local-Card-Scan-Memory]]"
  - "[[DiscountCard-Subsystem-Overview]]"
  - "[[Bonus-Programs-Architecture]]"
  - "[[Franchise-Loyalty-Architecture]]"
  - "[[DiscountCard-Service-API]]"
  - "[[GetClientListWithStats-Franchise-PersonalAccount-Zero-Balance-SDK]]"
  - "[[LRS-Long-Request-Service]]"
  - "[[Wasaby-Long-Running-Operations]]"
  - "[[Wasaby-Platform-Modules]]"
  - "[[File-Transfer-Service]]"
  - "[[PriceFormationOnline-Core]]"
  - "[[Price-Formation-Test-Runner]]"
  - "[[SBIS-Record-Format]]"
---

# ExportDiscountCard.PrepareFile — выгрузка карт в Excel без памяти

Задача **№07076892** (регламент «Ошибка», ответственный Смирнов А.Д.).
Инцидент `6a4cd630aff653d23a7b7db5` от **07.07.2026 13:32 МСК**, prod12 / `online-ru-09` /
`sbis-online-d6-00g`, контейнер `platform-application`, утилизация памяти **50.53**.
Наблюдаемое время метода — **2166 с (~36 мин)**.

Серверные логи инцидента недоступны: `cloud_get_logs` хранит записи **3 суток**, разбор шёл
через месяц. Весь анализ построен на чтении кода.

> [!note] Две итерации реализации
> **2026-08-05** — разбор и первая реализация под веху 4100, затем перенесена (веха **26.5100**,
> согласовано с Омельяненко 05.08, веху поставил Чудинов).
> **2026-09-03** — переделано на `rc-26.5100` после напоминания Федько («значительная» ошибка
> живёт с июля). Итог отличается от августовского в трёх местах, они помечены ниже.
> Ветка не коммичена, на стенде не проверялась.

## Пять слоёв одной причины

`ExportDiscountCard.PrepareFile` (`priceformationonline/discountcard/exportdiscountcard/`)
потребляет память и время линейно от числа карт аккаунта, причём независимо сразу по пяти местам:

| # | Место | Что происходит |
|---|---|---|
| 1 | `_sql_get_discount_cards_data` | все дисконтные карты аккаунта одним запросом, **без лимита** |
| 2 | `prepare_data` | бонусный баланс считается **на каждую карту отдельно** — ~5 запросов в БД на карту |
| 3 | `dump_data_to_disk` | все строки собираются в промежуточную python-матрицу |
| 4 | `ms_excel.write2file_xlsx` | книга xlsx строится **целиком в памяти** (`xlsxwriter.Workbook(bio)` без `constant_memory`) |
| 5 | `rf.SetData(bio.getvalue())` | готовый zip **дублируется** при отдаче |

Слои 2 и 4 доминируют. Пять копий данных живут одновременно, отсюда и выход за предел контейнера.

Пять запросов на карту — это `get_discount_card`, `sql_get_discount_list_by_card_type`,
`get_franchise`, при необходимости `get_client_person_uuid` и `sql_get_bonus_operations`.
На аккаунте в сотни тысяч карт получается несколько сотен тысяч запросов.

> [!key-insight] Классический N+1 плюс небуферизованная запись
> Ни один из пяти слоёв не «медленный» сам по себе — каждый нормален на десятках строк.
> Проблема ровно в том, что ни один не имеет потолка, и все пять умножаются на число карт.
> Тот же паттерн разбирался в [[PromoCode-Generation-Memory-Optimization]] и
> [[Bonus-GetTotalBalance-Local-Card-Scan-Memory]].

## Решение

### 1. Бонусный баланс пачками, без дублирования логики

Список бонусных программ определяется **типом карты**, а типов в аккаунте единицы. Значит карты
группируются по типу (`COALESCE("ВидКарты"."Раздел", "ВидКарты"."@ВидКарты")`) и считаются
пачками по 1000 — один запрос на пачку вместо запроса на карту.

Параллельный запрос писать не нужно: существующий `sql_get_bonus_operations`
(`priceformationcommon/discountcard/core/get_bonus_balance.py`) расширен **необязательным**
`card_id_list`. Директивы шаблонизатора переключают ветку, одиночный вызов не меняется:

```sql
/* {% ifnotnull card_id_list %} */
PED."Карта" AS "CardId",
/* {% end if %} */
...
/* {% ifnull card_id_list %} */
PED."Карта" = !card_id
/* {% end if %} */
/* {% ifnotnull card_id_list %} */
PED."Карта" = ANY(!card_id_list::INT[])
/* {% end if %} */
```

`CardId` добавляется и в `ORDER BY` **первым** — это позволяет разложить общий поток операций
по картам одним проходом (`_split_operations_by_card`, генератор) без сортировки в памяти.
Сам расчёт баланса (`calculate_bonus_balance`) остаётся общий — иначе логику пришлось бы
править в двух местах.

Публичная точка входа — `get_bonus_balance_by_cards(card_id_list, bonus_id_list) -> dict[int, Decimal]`.
Карты без операций возвращаются с нулевым балансом, поэтому вызывающему не нужен отдельный проход
по «пустым».

### 2. Франшиза — тоже пачками (изменено 2026-09-03)

> [!key-insight] Франшизность — свойство **типа карты**, а не карты
> `get_franchise` (`discountcard/loyaltycard/core/franchise.py:34`) для `DiscountCard` проверяет
> две вещи: франшизен ли аккаунт (`get_account_franchise`) и франшизен ли `card_type_id`
> (`get_card_type_franchise_info`). Значит группировка по типу карты, сделанная ради списка
> бонусных программ, **уже** разделяет франшизные и нефраншизные карты — отдельного прохода
> не нужно.

Внутри франшизного типа карты остаётся поштучное условие из
`_get_bonus_balance_core`: в СДК идут только карты, у владельца которых есть персона
(`get_client_person_uuid`, принимает список). Оно и разрезает список надвое
(`_split_by_balance_source`).

Франшизные карты берут баланс через `Card.GetBonusBalanceByCards` СДК (`Online.orx:283`,
`dcservice/online/card/franchise/get_bonus_balance_by_cards.py`) пачками по 1000 UUID.

> [!warning] Это денормализованное поле, а не пересчёт
> `GetBonusBalanceByCards` читает колонку `Card."BonusBalance"` в БД СДК — то есть отдаёт
> сохранённый баланс, тогда как поштучный `_get_dc_bonus_balance_rs` запрашивает операции и
> считает заново. Для отчёта это принято сознательно; расхождение возможно, и оно того же рода,
> что разбиралось в [[GetClientListWithStats-Franchise-PersonalAccount-Zero-Balance-SDK]]
> (там `BonusBalance=0` лежал прямо в БД СДК).
>
> Августовский вариант оставлял франшизу поштучной — тогда на франшизном аккаунте с сотнями
> тысяч карт исходная проблема сохранялась бы. Сейчас N+1 убран полностью.

### 3. Построчная запись файла

Уход с `ms_excel` (модуль **CAOnline**) на платформенный модуль **Excel**,
`excel.light_printer.LightPrinter` в режиме `ConstantMemory`.

```python
printer = LightPrinter({'ConstantMemory': True})
for sheet_name, first_row, last_row in self._get_sheets(len(data)):
    printer.add_sheet(sheet_name)
    printer.add_row(headers)
    for position in range(first_row, last_row):
        record = data[position]
        printer.add_row([_prepare_cell(record.Get(fld)) for fld in fields])
return printer.get_result(self.file_name)
```

Промежуточная матрица не собирается — строки отдаются формирователю по одной. Ссылка на запись
живёт внутри одной итерации, формат набора при этом не меняется (анти-паттерны RecordSet —
[[Wasaby-RecordSet-Performance]]).

Разбивка по листам вынесена в `_get_sheets(rows_count) -> [(имя, первая строка, за последней)]`;
пороги прежние — один лист до 2^16 строк, дальше по 50 000 с суффиксом `(0k-50k)`.

### 4. Потолок по числу строк — убран (изменено 2026-09-03)

Августовский вариант ставил `_MAX_EXPORT_ROWS = 500000` с понятной `sbis.Error` сверх лимита.
**Снято по решению Тимошенко** при переделке: лишнее видимое поведение для аккаунтов, которые
сейчас как-то, но выгружаются.

Следствие: данные выборки по-прежнему живут в памяти целиком (слой 1 не тронут). Убраны слои
2–5, потолка нет. Полное снятие ограничения по памяти — вариант B ниже.

## Модуль Excel: что он даёт и где ловушка

Платформенный модуль `Excel` (id `3c456f69-306e-4744-8c7f-8150d782c5bb`) **уже был**
в зависимостях `PriceFormation.Online.s3mod:13` — подключать ничего не пришлось.

### `LightPrinter` — рабочий API

`Модули бизнес-логики/Excel/excel/light_printer.py` (сверено на `rc-26.5100`):

| Элемент | Поведение |
|---|---|
| `LightPrinter(options)` | `options` — обычный `dict`. `{'ConstantMemory': True}` → `workbook_options['constant_memory'] = True`; иначе → `in_memory = True` (стр. 53–57) |
| вывод | `sbis.TmpFile()`, не `BytesIO` — zip не дублируется в памяти (стр. 59) |
| `add_sheet(name)` | `_validate_sheet_name`: обрезка до 31 знака, вырезание `[]:*?/\`, авто-суффикс `(N)` при повторе |
| `add_row(values, merge_ranges=None, style=None, data_types=None)` | `data_types` управляет только числовым форматом ячейки |
| `get_result(file_name)` | `RpcFile`, `SetName(sbis.try_rk2(file_name) + '.xlsx')` (стр. 220) — расширение добавляется само, как и в `write2file_xlsx` |

> [!info] Тело `add_row` не прочитано
> `gitlab_file_read` отдаёт только первые 100 строк файла, а `saby-search` возвращает по одной
> строке на совпадение. Строки 100–215 `light_printer.py` восстановить не удалось, поэтому
> августовский тезис «значения пишутся как есть, без `str()`» **не перепроверен**.
> В реализации это обошли: `_prepare_cell` приводит значение к строке (`'' if None else str(v)`),
> ровно как делал `write_xlsx.py:27`.

### Почему БЛ-метод `sbis.Excel.*` не подошёл

Правильный рефлекс — звать платформу через `sbis.<Объект>.<Метод>`, а не импортировать python
чужого модуля. Здесь это **не сработало** (разбор от 2026-08-05, в сентябре не перепроверялся).

Единственный синхронный БЛ-метод, отдающий файл, — `Excel.SaveToFile(Data, Fields, Titles,
HierarchyField, FileName, Options) -> RPCFILE`. Его тело зовёт `excel_utils.save_recordset(...,
options=Options)` → `RecordSetToExcel.__init__`, а там (`excel/printer/rs_printer.py:77`):

```python
self.round_fields = self.options.get("RoundFields", None)
```

`Options` объявлен как `RECREFERENCE` и приходит как `sbis.Record`. У `sbis.Record.get()`
сигнатура **без аргументов** — метод оставлен для совместимости и «ничего не делает»
(`Record.pyi:736`, см. [[SBIS-Record-Format]]).

> [!key-insight] `Excel.SaveToFile` несовместим с любым непустым `Options`
> Непустой `Options` роняет метод по `TypeError` ещё в конструкторе. А с `Options=None`
> включается `in_memory=True` (`rs_printer.py:44`) — то есть книга снова целиком в памяти,
> ровно то, от чего уходим. Метод пригоден только для маленьких выгрузок.

Методы, которые `Options` разбирают правильно — `Excel.Save` / `Excel.SaveList` через
`save_custom` (`excel/export.py:83`, там `options = options.as_dict() if options else {}`) —
требуют **списочного БЛ-метода с навигацией**. Это отдельная архитектура выгрузки
(см. «Что дальше», вариант B).

Отсюда решение: прямой импорт `excel.light_printer.LightPrinter` — в том же стиле, в котором
раньше импортировался `ms_excel.write_xlsx`, но из модуля, уже объявленного в зависимостях,
и с обычным `dict` вместо `Record` в опциях.

## Побочные находки

- **`ms_excel` делал все ячейки текстовыми** (`write_xlsx.py:27` — `str(value)`), суммы
  в выгрузках не складывались в Excel. Соблазн починить это заодно при переходе на `LightPrinter`
  **отклонён**: смена типа ячеек видима внешним потребителям файла, а регламент «Ошибка»
  запрещает расширять фикс без согласования. `_prepare_cell` сохраняет прежнее поведение —
  файл остаётся байт-в-байт того же вида. Отдельная задача, если понадобится.
- **`ExportPersonalBalance` запускает чужой экспорт.** `export_personal_balance.py:32` ставит
  `self._lrs_task_method = 'ExportDiscountCard.PrepareFile'` — ВНР-выгрузка персонального
  баланса поднимает выгрузку дисконтных карт. Баг реальный, **не исправлен**.
- **`ExportPersonalBalance.prepare_data` — тот же N+1** (`export_personal_balance.py:53-55`,
  `get_bonus_balance` в цикле по персональным счетам). В задачу не входит, сообщено отдельно.
- **Причина скипа `TestExportPromocode` отпала.** Тест помечен `@test_new_skip` именно потому,
  что `ms_excel` тянет модуль CAOnline с полутора десятками зависимостей, которых нет в тестовом
  проекте. После перехода на `Excel` это условие снято — расскипать можно отдельной задачей.
- **Модуль `Excel` в тестах замокан.** В тестовом проекте от него только
  `tests_new/online/clouds/Online/Mock/Excel/Excel.s3mod` — описание без python. Формирование
  файла автотестами не покрывается **в принципе**, мок `excel.light_printer` в юнит-тестах
  обязателен, проверка реального файла — только руками на стенде.

## Затронутый код (редакция 2026-09-03)

Пять файлов, ~444 строки добавлено / ~37 удалено:

- `priceformationcommon/discountcard/core/get_bonus_balance.py` — `card_id_list`
  в `sql_get_bonus_operations`, новые `get_bonus_balance_by_cards` и `_split_operations_by_card`
- `priceformationonline/discount/core/export.py` — базовый класс `ExportData`: `LightPrinter`,
  построчная запись, `_get_sheets`, `_prepare_cell`
- `priceformationonline/discountcard/exportdiscountcard/export_discount_card.py` —
  `_get_bonus_balance` (группировка по типу), `_get_franchise_card_type_id_list`,
  `_split_by_balance_source`, `_get_account_bonus_balance`, `_get_dc_bonus_balance`,
  `CardUUID` / `ClientId` / `CardTypeId` в SQL
- `tests/tests_priceformationcommon/discountcard/core/get_bonus_balance.py` —
  `GetBonusBalanceByCardsTest` (4 теста)
- `tests/tests_priceformationonline/discountcard/exportdiscountcard/prepare_file.py` —
  мок `excel.light_printer` вместо `ms_excel`, `test_bonus_balance_by_card_type`

Августовские имена (`get_bonus_balance_batch`, `_fill_bonus_balance`, `_get_indexes_by_card_type`,
`_get_row`, `_MAX_EXPORT_ROWS`) в сентябрьской редакции **не используются** — при поиске по
истории задачи это может путать.

> [!tip] Служебные поля и порядок операций над RecordSet
> SQL выгрузки отдаёт `CardUUID`, `ClientId`, `CardTypeId` только ради расчёта баланса.
> Их `DelCol` делается **до** `AddColMoney('Bonuses')` и до цикла заполнения: менять формат
> набора можно только когда не осталось живых ссылок на его записи. Публичный результат
> `prepare_data` при этом не изменился — старый тест сравнения `as_list()` прошёл без правок.

## Проверка

- pylint **10.00/10** по трём продуктовым файлам (конфиг jinnee/Stan).
- `tests_priceformationcommon/discountcard` — **523 OK**.
- `tests_priceformationcommon/.../get_bonus_balance` — **264 OK** (включая 16 новых, `with_feature`
  прогоняет оба состояния флагов `bonus_hold` / `lty_recentbonushold`).
- `tests_priceformationonline/discountcard/exportdiscountcard` — **2 OK**.

> [!warning] Базовый уровень падений в `tests_priceformationonline/discountcard`
> Пакет целиком даёт **705 тестов, 14 падений**: `discountcard.create_ext` (license, коды
> 64002/64003 против `-1`), `pfsync.get_emission` (8 ошибок), загрузка
> `discountcardtype.create`. Тот же набор воспроизводится на чистом дереве (704 теста) —
> сверено прогоном под `git stash`. Проверять свою правку по «FAILED» в этом пакете нельзя,
> нужен дифф со стешем.

Формирование файла (`LightPrinter`) и франшизная ветка (`Card.GetBonusBalanceByCards`)
автотестами **не покрыты** — только ручная проверка на стенде.

## Почему задача пережила две вехи

Правка выходит за рамки локальной починки одного метода:

1. **Затронут базовый класс всех выгрузок** — от `ExportData` наследуются ещё выгрузка
   промокодов и выгрузка персонального баланса.
2. **Сменился модуль формирования файла**, и автотестами он не покрывается — нужна ручная
   проверка на стенде по всем трём выгрузкам.
3. **Правится общий SQL бонусного баланса.** `get_bonus_balance` используется далеко за
   пределами выгрузки: это баланс, которым клиент расплачивается. Ошибка здесь бьёт по деньгам,
   а не по отчёту.

Инцидент при этом не блокирующий: выгрузка на больших аккаунтах и сейчас недоступна,
ухудшения от переноса нет. Пункты про смену типа ячеек и про жёсткий лимит строк, бывшие
в августовском списке причин переноса, **сняты** — оба поведения решено не менять.

## Что дальше

> [!open-question] Вариант B — порционная выборка
> Полный уход от сборки данных в памяти: переход на платформенный итеративный экспорт
> (`Excel.SaveList` / `save_custom` с курсорной пагинацией, см. [[CursorNavigation-Mechanism]]).
> Требует превращения выгрузки в списочный БЛ-метод. Согласовано как **отдельная задача**.

Открыто также: чинить ли `ExportPersonalBalance._lrs_task_method` и его N+1 здесь или заводить
отдельно; стоит ли поднимать поломанный `Excel.SaveToFile` перед владельцами модуля `Excel`;
приемлемо ли для отчёта денормализованное `Card."BonusBalance"` на франшизных аккаунтах.
