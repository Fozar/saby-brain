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

### 27.10, ночь: запросы разбиты на два MR

Решение (Тимошенко): вариант 1. Второй MR сокращён до `GetList`, `GetStats` вынесен в третий, Price мастер-фильтра (`GetLeadPeriodList`) из задачи убран (для него есть индекс `BonusesEffectiveDate`, без замера на большой базе не трогаем).
- **MR 2, только `GetList`:** ветка `26.6100/feature/aatimoshenko/08052923_queries`, коммит `366ee19462` (код +32/-20 и тесты), документ doc_id 632817944, !153094-!153096. Тесты пакета `referralprogram`: 438 OK.
- **MR 3, только `GetStats`/`GetStatsByPartner`:** ветка `..._stats`, коммит `4da80e8f6f` (в основном `get_stats_helpers.py` +106/-137), документ doc_id 632820933 ([ссылка](https://online.sbis.ru/opendoc.html?guid=01a17ca7-f30e-7f6c-b997-cb71145938f9&client=3)), !153097-!153099. Тесты 438 OK. Урезать до 40 строк не вышло: если вынести только успешные заявки, а основной join оставить, счётчики задваиваются (на одну карту несколько строк join), поэтому каждый показатель считается своим подзапросом.
- Старые коммиты сохранены локально: `backup/08052923-full` (`2a2901d145`), `backup/08052923-queries-v1` (`a3ee53ce9d`).
- Поле «Что тестировать» в документе 632817944 осталось от большой версии (реестр программ, виджет, мастер-фильтр), его нужно сократить до реестра «Реферальные программы». Тела («Что сделано») всех трёх документов правит Тимошенко.
- Стенд остался запущенным: `D:/dev/t08052923/test_build/price-formation`, код читается из `D:/dev/t08052923/price-formation`.

### 27.10, поздний вечер: второй MR оформлен, но признан слишком большим

Ветка `26.6100/feature/aatimoshenko/08052923_queries` (коммит `a3ee53ce9d`), собрана заново от свежего `rc-26.6100`, MR независим от первого. Внутри `GetList` (+32/-20), `GetStats`/`GetStatsByPartner` (+106/-137 в `get_stats_helpers.py`), Price в `GetLeadPeriodList` (+42/-23), тесты около 145 строк. MR-документ второго MR: doc_id 632817944 ([ссылка](https://online.sbis.ru/opendoc.html?guid=01a17c97-0e91-7910-a0bd-bc5f691e7b39&client=3)), GitLab !153094 (rc-26.6100), !153095, !153096. Старый полный коммит сохранён в локальной ссылке `backup/08052923-full`. Пакет `referralprogram`: 440 тестов OK, с рефакторингом №10271344 и первым MR сливается чисто (`git merge-tree`).

- **Решение (Тимошенко, 27.10):** изменения «гигантские», сделать аккуратнее и проще. Предложены варианты: A (рекомендую) два небольших MR: `GetList` как есть + урезанный `GetStats` (только успешные заявки по дате статуса отдельным подзапросом, около 40 строк), а Price мастер-фильтра убрать из задачи; B один урезанный MR; C три MR без сокращения. **Ждёт выбора.**
- Price мастер-фильтра (UNION ALL) под вопросом: для него уже есть индекс `BonusesEffectiveDate`, а переписывание породило замечание бота про задвоение. Без замера на большой базе не утверждаем, что оно лишнее.
- При переносе на свежий rc в `rc` уже есть новый расчёт Price в статистике (корешки по `EffectiveDate`, посетители по `ДатаВремя`, SabyBank только корешки), он учтён. Тест `test_price_by_status_date_under_feature` падал из-за теста: `create_stub_test_data()` не возвращал программу, корешок на 150 был без `ВидЦены`; хелпер теперь возвращает программу (исправление в ветке второго MR).
- Рефакторинг №10271344 (MR !153076-!153078, не влит) переименовывает `get_stats_helpers.py` в `core/stats.py` (99%), правки второго MR переедут сами.
- Новое замечание ревьюбота в !151204 (Medium: `EffectiveDate IS NOT NULL` не во всех счётчиках заявок, `GetStats`/`GetList`) закрывается вторым MR. Ответ в тред не писал.
- Название: в реферальной программе вознаграждение называем `price`, слово `reward` в новом коде не используем. Мой псевдоним `rewards` в подзапросе Price мастер-фильтра заменён на `price` (правка в рабочей папке, не закоммичена; при варианте A уйдёт вместе с самим Price). Старые `reward` в `rc` (`_save_lead_reward`, тесты) не мои.
- Тела обоих MR-документов («Что сделано», «Что протестировать») правит Тимошенко сам, инструмент заполняет только «Что тестировать».

### 27.10, вечер: замечание ревьюбота по тестам

Ревьюбот (Low): условие `EffectiveDate IS NOT NULL` не покрыто тестом. Добавлены 3 теста (строка с типом связи, но без даты статуса не попадает в реестр `GetStubList`, в LeadCount `GetPartnerList` и `GetLeadPeriodList`). Проверено, что без условия все 3 падают. Влито amend в тот же коммит, теперь `630d2beec5` (было `8678c2ec8e`), пакет `referralprogram` 441 тест OK, push с force-with-lease. Открытой остаётся ветка Мусохранова про PK в индексе: ответ уже в MR (PK убран 13.10), ждёт его реакции.

### 27.10, вечер: основное запушено

Коммит `8678c2ec8e` на свежем `rc-26.6100` запушен в ветку MR (force-with-lease), 6 файлов +38/-5. Тесты на нормальном стенде: 3 класса (64) и весь пакет `referralprogram` (438), OK. Остальное (`GetList`, `GetStats`/`GetStatsByPartner`, Price в `GetLeadPeriodList`) ждёт переноса с `2a2901d145` на свежий rc в локальной ветке `26.6100/feature/aatimoshenko/08052923_queries` (конфликты в `get_list.py` и `get_stats_helpers.py`). Тело MR (док. №09291202) Тимошенко правит сам, тексты даны в чате.

### 27.10, вечер: разбиение сделано в рабочей папке

Решено (Тимошенко): в !151204 оставить только основное, остальное в отдельную ветку. Основное: два индекса + опознание корешка по `ТипСвязи` и `EffectiveDate IS NOT NULL` в `GetStubList`, `GetPartnerList`, LeadCount в `GetLeadPeriodList`. Второй MR: `GetList`, `GetStats`/`GetStatsByPartner`, Price в `GetLeadPeriodList`.
- `rc-26.6100` ушёл вперёд (MR !151204/!151205 оба с конфликтом, одна ветка на оба), полный коммит при переносе конфликтует в `get_list.py` и `get_stats_helpers.py`.
- Worktree `D:/dev/t08052923/price-formation` (перенесён из `D:/dev/wt08052923`): ветка MR сброшена на `rc-26.6100` и собрана заново из основного (не закоммичено, не запушено); полный старый коммит `2a2901d145` лежит в локальной ветке `26.6100/feature/aatimoshenko/08052923_queries`. Стенд собирается из этой папки (`tm -project online`, сборка `D:/dev/t08052923/test_build/price-formation`). Первый прогон на `D:/dev/wt08052923` ничего не доказал: облако тестов берёт код по пути `../price-formation`, а в `D:/dev` это ссылка на `pf-26.61`, т.е. стенд исполнял чужой код (новый тест `test_ignores_rows_without_link_type` честно упал: `2 != 1`). Поэтому папка перенесена в `D:/dev/t08052923/price-formation`, рядом ссылка `pnt-toolbox`.
- После правки `get_lead_period_list.py` (LeadCount получил `EffectiveDate IS NOT NULL`) прогон трёх классов (GetStubListTest, GetPartnerList, GetLeadPeriodList) надо повторить на нормальном стенде; коммит и push с `--force-with-lease` только после зелёного прогона и «ок».
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
