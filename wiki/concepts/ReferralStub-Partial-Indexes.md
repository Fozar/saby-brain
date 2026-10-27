---
type: concept
title: "Корешки: частичные индексы ReferralStub и ReferralStubEffectiveDate (№08052923)"
created: 2026-10-07
updated: 2026-10-27
status: developing
tags:
  - price-formation
  - referral-program
  - sabybank
  - sql-index
  - tech-design
related:
  - "[[ReferralStub-Stats-Index-Questions]]"
  - "[[SabyBank-Stub-Rewards-Calculation]]"
  - "[[ReferralProgram-GetPartnerList-Stub-Stats]]"
  - "[[ReferralProgram-GetLeadPeriodList-Stub-Mode]]"
  - "[[ReferralProgram-RefDealsConvert-Feature]]"
  - "[[zvonok-musohranov-timoshenko-2026-07-23]]"
---

# Корешки: индексы под запросы по корешкам

Задача в разработку №08052923 ([ссылка](https://online.sbis.ru/opendoc.html?guid=019fd0b4-8c8d-7848-a285-61aad8837ee5&client=3)), автор и ответственный Тимошенко, заведена 05.08.2026 из диалога с Мусохрановым ([диалог](https://dev.sbis.ru/page/dialog/019f91f8-c334-7182-866e-64f44f21dee3)). Веха 26.6100, срок 28.11.2026. Критерий: индекс в 26.6100, MR влит. В 26.5100 индекс штатно не добавить: там нет конвертации БД.

Продолжение вопросов из [[ReferralStub-Stats-Index-Questions]].

## Где остановились (27.10)

- Ветка перебрана: один коммит `2a2901d145` (вместо `90eb0af5`). Предикат обоих индексов уже сужен до `"ТипСвязи" IS NOT NULL AND "EffectiveDate" IS NOT NULL` (вопрос 2 ниже закрыт кодом, в диалоге с Мусохрановым предложено 12.10), PK из `ReferralStub` убран (индекс: ВидЦены, ДатаВремя DESC). В запросы по `ДатаВремя` добавлен `EffectiveDate IS NOT NULL`.
- Коммит большой (12 файлов, +309/-142), предложено разбить, чтобы ревьюеру было проще. Делится на независимые части: индексы (.dicx) + мелкие правки `GetStubList`/`GetPartnerList`/LeadCount; `GetList`; `GetStats`+`GetStatsByPartner` (общий `get_stats_helpers.py`); Price в `GetLeadPeriodList`. Порядок выката не важен: без индексов запросы работают как раньше, индексы без новых запросов просто не используются.
- Варианты: A, 4 MR (рекомендую); B, 3 MR; C, 2 MR (индексы отдельно, запросы вместе). Каждая часть идёт в две ветки (6100 и 6200). **Ждёт выбора Тимошенко.** Текущие !151204/!151205 станут первой частью.

### 27.10, вечер: разбиение сделано в рабочей папке

Решено (Тимошенко): в !151204 оставить только основное, остальное в отдельную ветку. Основное: два индекса + опознание корешка по `ТипСвязи` и `EffectiveDate IS NOT NULL` в `GetStubList`, `GetPartnerList`, LeadCount в `GetLeadPeriodList`. Второй MR: `GetList`, `GetStats`/`GetStatsByPartner`, Price в `GetLeadPeriodList`.
- `rc-26.6100` ушёл вперёд (MR !151204/!151205 оба с конфликтом, одна ветка на оба), полный коммит при переносе конфликтует в `get_list.py` и `get_stats_helpers.py`.
- Worktree `D:/dev/wt08052923`: ветка MR сброшена на `rc-26.6100` и собрана заново из основного (не закоммичено, не запушено); полный старый коммит `2a2901d145` лежит в локальной ветке `26.6100/feature/aatimoshenko/08052923_queries`. Тесты не прогнаны: стенда для этой папки нет (`D:/dev/test_build/wt08052923`), нужна «Сборка online».
- В теле MR (документ №09291202) «Что сделано» и «Что протестировать» надо переписать под основное, тексты предложены в чате.

## Состояние на 07.10

- Ветка `26.6100/feature/aatimoshenko/08052923`, один коммит `90eb0af5` «Частичные индексы под корешки и правка запросов реф. программ под них».
- MR [!151204](https://git.sbis.ru/warehouse/price-formation/-/merge_requests/151204) в `rc-26.6100` и [!151205](https://git.sbis.ru/warehouse/price-formation/-/merge_requests/151205) в `rc-26.6200`. Задача MR №09291202, сервис online (конвертация БД).
- 29.09 Омельяненко пропустил, Мусохранов вернул с вопросом: зачем в индексе PK `@ВидЦеныДокумент`. 30.09 Тимошенко ответил в MR (курсор GetStubList), снова на ревью у Мусохранова с 30.09, ответа нет.
- 28.09 было совещание «Обсуждение индекса для корешков» (doc_id 624426474), итогов в вики нет.

## Таблица и индексы

Корешки лежат в `ВидЦеныДокумент` (`PriceFormation.Online.dicx`, ответственный Мусохранов). Корешок: `ВидЦены` = реф. программа, `Карта` = реф. код партнёра, `ДатаВремя` = дата создания заявки, `EffectiveDate` = дата статуса (обязательна в CreateStub/UpdateStub, ВНР тоже заполняют), `ТипСвязи` = 10/15/20, `OperationId` = UUID заявки.

`ТипСвязи` заполнен не только у корешков: 2 (агрегат по реализации розницы, `write_aggregates.py`), 3 (агрегат за месяц), 4 (бонусы за отзыв), 5 (агрегат по реализации партнёра, `import_aggregates.py`). У 2/3/5 `EffectiveDate` пустой, у 4 заполнен.

Что уже было до MR: `ВидЦены` (ВидЦены, ДатаВремя), `Карта` (Карта, ДатаВремя DESC), `OperationId`, `BonusesEffectiveDate` (ВидЦены, EffectiveDate DESC, PK DESC) с предикатом `Бонусы IS NOT NULL AND EffectiveDate IS NOT NULL`. Под отбор успешных заявок по `EffectiveDate` без `Бонусы` индекса не было: GetPartnerList и GetStats читали всю историю программы.

Что добавляет MR:

| Индекс | Колонки | Предикат | Для чего |
|---|---|---|---|
| `ReferralStub` | ВидЦены, ДатаВремя DESC, @ВидЦеныДокумент DESC | `"ТипСвязи" IS NOT NULL` | реестр корешков (курсор), счётчики всех заявок |
| `ReferralStubEffectiveDate` | ВидЦены, EffectiveDate DESC | `"ТипСвязи" IS NOT NULL` | успешные заявки и вознаграждения по дате статуса |

`null_keys="0"` в SBIS даёт к предикату `(col1 IS NOT NULL OR col2 IS NOT NULL ...)` (проверено по DDL на тестовой БД, индекс `PriceListDoc`), так что агрегаты с заполненным `ВидЦены` в оба индекса попадают.

## Какие запросы какой индекс берут (ветка MR)

| Метод | Отбор | Индекс |
|---|---|---|
| GetStubList | ВидЦены, ТипСвязи IS NOT NULL, ДатаВремя или EffectiveDate, курсор (ДатаВремя, PK) DESC | ReferralStub |
| GetList, LeadCount по программе | ВидЦены, ТипСвязи IS NOT NULL, ДатаВремя | ReferralStub |
| GetList, Price | ВидЦены, Бонусы IS NOT NULL, ДатаВремя | ВидЦены |
| GetList на партнёре | Карта + ДатаВремя | Карта |
| GetStats / GetStatsByPartner, Price и LeadCount | Карта + ДатаВремя (LATERAL по карте) | Карта |
| GetStats, PositiveLeadCount | ВидЦены IN (программы группы), ТипСвязи = 15, EffectiveDate | ReferralStubEffectiveDate |
| GetPartnerList, LeadCount/LeadSum | ВидЦены, ТипСвязи IS NOT NULL, ДатаВремя | ReferralStub |
| GetPartnerList, PositiveLeadCount | ВидЦены, ТипСвязи = 15, EffectiveDate | ReferralStubEffectiveDate |
| GetPartnerList, Price в режиме корешков | ВидЦены, Бонусы > 0, ТипСвязи IS NOT NULL, EffectiveDate | ReferralStubEffectiveDate или BonusesEffectiveDate |
| GetLeadPeriodList, Price корешков | ВидЦены, Бонусы > 0, ТипСвязи IS NOT NULL, EffectiveDate | ReferralStubEffectiveDate или BonusesEffectiveDate |
| GetLeadPeriodList, LeadCount | ВидЦены, ТипСвязи IS NOT NULL, ДатаВремя | ReferralStub |
| CreateInvoice | программы группы, Бонусы > 0, EffectiveDate | BonusesEffectiveDate |
| ReadStub, UpdateStub, проверка дубля в CreateStub, HandleSourceChanged | OperationId | OperationId |
| SetStubPrice | ВидЦены, PK = ANY, ТипСвязи = 15 | PK |
| CreateStubsFor* (ВНР, разово) | ВидЦены, OperationId IS NOT NULL | ВидЦены |

Правки запросов в MR, чтобы индексы заработали: GetStubList опознаёт корешок по `ТипСвязи IS NOT NULL` вместо `OperationId IS NOT NULL`; GetList считает по программе через LATERAL, а не по всей таблице; в GetStats убран общий LEFT JOIN с OR, каждый показатель отдельным подзапросом; в GetLeadPeriodList ветки корешков и посетителей разведены через UNION ALL (в ветке посетителей `ТипСвязи IS NULL`, двойного учёта нет).

## Открытые вопросы

1. **PK в `ReferralStub`** (Мусохранов). Нужен для курсора GetStubList: у корешков из ВНР по сделкам `ДатаВремя` одинаковая за день (полночь). Вариант: дозапрашивать время сделки в ВНР и убрать PK. Без PK Postgres досортирует только строки с одинаковой датой.
2. **Предикат шире, чем нужно.** В июле предлагался `"ТипСвязи" IS NOT NULL AND "EffectiveDate" IS NOT NULL`, чтобы отрезать агрегаты 2/3/5. В MR остался только `ТипСвязи IS NOT NULL`. На тестовой БД агрегатов единицы (схема на 5 млн строк: 74 строки с типом 2, 97 с типом 3), на крупных розничных аккаунтах тип 2 пишется на каждую реализацию по каждой акции. Если сузить: для `ReferralStubEffectiveDate` правка только в .dicx (отбор по `EffectiveDate` сам доказывает `IS NOT NULL`); для `ReferralStub` в запросы по `ДатаВремя` надо добавить `"EffectiveDate" IS NOT NULL`. `ТипСвязи >= 10` в предикате хуже: из `ТипСвязи = !param` планировщик это не всегда выведет.
3. **PositiveLeadCount в GetStats** считается одним проходом по всем программам группы, даже на партнёре (замечание reviewbot без ответа). Через карту было бы хуже: индекс `Карта` без `EffectiveDate`, читалась бы вся история карты. Стоит ответить в MR.
4. **Price в GetStats по `ДатаВремя`, а в GetLeadPeriodList и GetPartnerList по `EffectiveDate`** (замечание reviewbot). Так было и до MR, в задачу не входит, но расхождение виджета и разбивки по месяцам остаётся.
5. Размер и время построения на крупных аккаунтах не замерены. Мусохранов предлагал гонять на большой БД.
