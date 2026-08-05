---
type: synthesis
title: "ExportDiscountCard.PrepareFile — выгрузка карт в Excel без памяти"
address: c-000253
created: 2026-08-05
updated: 2026-08-05
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
  - "[[LRS-Long-Request-Service]]"
  - "[[Wasaby-Long-Running-Operations]]"
  - "[[Wasaby-Platform-Modules]]"
  - "[[File-Transfer-Service]]"
  - "[[PriceFormationOnline-Core]]"
  - "[[Price-Formation-Test-Runner]]"
  - "[[SBIS-Record-Format]]"
---

# ExportDiscountCard.PrepareFile — выгрузка карт в Excel без памяти

Задача **№07076892** (регламент «Ошибка», ответственный Смирнов А.Д., срок 2026-08-08).
Инцидент `6a4cd630aff653d23a7b7db5` от **07.07.2026 13:32 МСК**, prod12 / `online-ru-09` /
`sbis-online-d6-00g`, контейнер `platform-application`, утилизация памяти **50.53**.
Наблюдаемое время метода — **2166 с (~36 мин)**.

Серверные логи инцидента недоступны: `cloud_get_logs` хранит записи **3 суток**, разбор шёл
через месяц. Весь анализ построен на чтении кода.

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

> [!warning] Франшиза считается по-другому
> На франшизных аккаунтах баланс приходит не локальным SQL, а из сервиса `discount-cards`
> по одной карте (см. [[Franchise-Loyalty-Architecture]], [[DiscountCard-Service-API]]).
> Пакетный путь применим **только** при `sbis.PriceFormation.InCloud()` и
> `get_account_franchise().Get('FranchiseRole') is None`; иначе — прежний поштучный расчёт.
> Проверку делает вызывающий код, `get_bonus_balance_batch` её не дублирует.

### 2. Построчная запись файла

Уход с `ms_excel` (модуль **CAOnline**) на платформенный модуль **Excel**,
`excel.light_printer.LightPrinter` в режиме `ConstantMemory`.

```python
printer = LightPrinter({'ConstantMemory': True})
printer.add_sheet(sheet_name)
printer.add_row(header)
for index in range(start, end):
    printer.add_row(_get_row(data, index, fields))
return printer.get_result(self.file_name)
```

Промежуточная матрица не собирается — строки отдаются формирователю по одной. Чтение записи
вынесено в отдельную функцию `_get_row(data, index, fields)`, чтобы ссылка на `rec` не жила
дольше самой строки (см. анти-паттерны RecordSet в [[Wasaby-RecordSet-Performance]]).

### 3. Предохранитель по числу строк

Данные выгрузки до записи всё равно живут в памяти целиком, поэтому поставлен потолок
`_MAX_EXPORT_ROWS = 500000`: сверх него — понятная `sbis.Error`, а не падение по памяти.
Ограничение временное, снимается вместе с переходом на порционную выборку.

## Модуль Excel: что он даёт и где ловушка

Платформенный модуль `Excel` (id `3c456f69-306e-4744-8c7f-8150d782c5bb`) **уже был**
в зависимостях `PriceFormation.Online.s3mod` — подключать ничего не пришлось.

### `LightPrinter` — рабочий API

`Модули бизнес-логики/Excel/excel/light_printer.py`:

| Элемент | Поведение |
|---|---|
| `LightPrinter(options)` | `options` — обычный `dict`. `{'ConstantMemory': True}` → `workbook_options['constant_memory'] = True`; иначе → `in_memory = True` |
| вывод | `sbis.TmpFile()`, не `BytesIO` — zip не дублируется в памяти |
| `add_sheet(name)` | `_validate_sheet_name`: обрезка до 31 знака, вырезание `[]:*?/\` |
| `add_row(values)` | значения пишутся **как есть**, без `str()` |
| `get_result(file_name)` | `RpcFile` через `SetStream`, расширение `.xlsx` добавляется само |

### Почему БЛ-метод `sbis.Excel.*` не подошёл

Правильный рефлекс — звать платформу через `sbis.<Объект>.<Метод>`, а не импортировать python
чужого модуля. Здесь это **не сработало**, и причина неочевидна.

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

- **`ms_excel` делал все ячейки текстовыми.** `write_xlsx.py:27` прогонял каждое значение через
  `str(value)` — суммы в выгрузках не складывались в Excel. Переход на `LightPrinter` это чинит
  попутно: значения пишутся сырыми, `sbis.Money = Decimal`, а `xlsxwriter 0.9.3` держит `Decimal`
  в `num_types`. Изменение видимое для пользователя — файлы могут разбираться внешними
  инструментами на стороне клиентов.
- **`ExportPersonalBalance` запускает чужой экспорт.** `export_personal_balance.py:32` ставит
  `self._lrs_task_method = 'ExportDiscountCard.PrepareFile'` — ВНР-выгрузка персонального
  баланса поднимает выгрузку дисконтных карт. Баг реальный, **не исправлен**: расширять фикс
  без согласования регламент «Ошибка» запрещает.
- **Причина скипа `TestExportPromocode` отпала.** Тест помечен `@test_new_skip` именно потому,
  что `ms_excel` тянет модуль CAOnline с полутора десятками зависимостей, которых нет в тестовом
  проекте (комментарий в `tests_priceformationonline/loyaltyprograms/exportpromocode/prepare_file.py`
  прямо называет вариантом решения «заменить библиотеку ms_excel на другую»). После перехода
  на `Excel` это условие снято — расскипать можно отдельной задачей.
- **Модуль `Excel` в тестах замокан.** В тестовом проекте от него только
  `tests_new/online/clouds/Online/Mock/Excel/Excel.s3mod` — описание без python. Формирование
  файла автотестами не покрывается **в принципе**, мок `excel.light_printer` в юнит-тестах
  обязателен, проверка реального файла — только руками на стенде.

## Затронутый код

Четыре файла, ~300 строк добавлено / ~31 удалено:

- `priceformationonline/discount/core/export.py` — базовый класс `ExportData`: `LightPrinter`,
  построчная запись, `_MAX_EXPORT_ROWS`, `_get_row`
- `priceformationcommon/discountcard/core/get_bonus_balance.py` — `card_id_list`
  в `sql_get_bonus_operations`, новые `get_bonus_balance_batch` и `_split_operations_by_card`
- `priceformationonline/discountcard/exportdiscountcard/export_discount_card.py` —
  `_fill_bonus_balance` (пачки + франшизная ветка), `_get_indexes_by_card_type`,
  `CardTypeId` в SQL
- `tests/tests_priceformationonline/discountcard/exportdiscountcard/prepare_file.py` —
  мок `excel.light_printer` вместо `ms_excel`, два регрессионных теста

Проверка: pylint **10.00/10** по продуктовым файлам; 3 теста экспорта, 345 тестов
`tests_priceformationcommon/discountcard`, 156 тестов бонусных балансов — все OK.

> [!tip] Как устроен тест эквивалентности
> `test_bonus_balance_batch_matches_by_card`: 6 карт в 2 эмиссиях (значит 2 группы по типу),
> `_CARD_BATCH_SIZE` подменён на 2 — проверяется в том числе граница пачки, а поштучный
> `_fill_bonus_balance_by_card` подменён на `side_effect=AssertionError`. Без этой подмены
> откат на поштучную ветку заставил бы тест сравнивать её саму с собой и тест бы «проходил».

## Почему перенесено на дальнюю веху

Правка выходит за рамки локальной починки одного метода:

1. **Затронут базовый класс всех выгрузок**, а не только карты — от `ExportData` наследуются
   ещё выгрузка промокодов и выгрузка персонального баланса.
2. **Сменился модуль формирования файла**, и автотестами он не покрывается (см. выше) —
   нужна ручная проверка на стенде по всем трём выгрузкам.
3. **Меняется содержимое ячеек** — числа вместо текста, видимо для внешних потребителей файла.
4. **Правится общий SQL бонусного баланса.** `get_bonus_balance` используется далеко за
   пределами выгрузки: это баланс, которым клиент расплачивается. Ошибка здесь бьёт по деньгам,
   а не по отчёту.
5. **Появилось новое поведение — жёсткий лимит строк.** Аккаунты, где выгрузка сейчас
   отрабатывает медленно, могут начать получать ошибку; порог надо подтвердить на объёмах.

Инцидент при этом не блокирующий: выгрузка на больших аккаунтах и сейчас недоступна,
ухудшения от переноса нет.

## Что дальше

> [!open-question] Вариант B — порционная выборка, снятие лимита
> Полный уход от сборки данных в памяти: переход на платформенный итеративный экспорт
> (`Excel.SaveList` / `save_custom` с курсорной пагинацией, см. [[CursorNavigation-Mechanism]]),
> после которого `_MAX_EXPORT_ROWS` убирается. Требует превращения выгрузки в списочный
> БЛ-метод. Согласовано как **отдельная задача**, не в 4100.

Открыто также: чинить ли `ExportPersonalBalance._lrs_task_method` здесь или заводить отдельно;
стоит ли поднимать поломанный `Excel.SaveToFile` перед владельцами модуля `Excel`.
