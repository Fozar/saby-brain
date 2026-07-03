---
type: source
title: "Сценарий «Реактивация неактивных клиентов (давно не покупали)» — v1"
created: 2026-07-03
tags:
  - source
  - loyalty
  - customer-journey
  - sabydoc
  - marshruty
  - scenario-design
status: current
related:
  - "[[CustomerJourney-Scenarios-Project]]"
  - "[[Route-Platform-Architecture]]"
  - "[[LoyaltyScenario-ReactivationInactiveClients]]"
  - "[[Выборки-Module]]"
  - "[[Гаврилов-Михаил]]"
  - "[[Loyalty-Product-Overview]]"
  - "[[domains/price-formation/_index]]"
---

# Source: Сценарий «Реактивация неактивных клиентов (давно не покупали)» — v1

**File:** `.raw/Путь клиента/Сценарий -Реактивация неактивных клиентов (давно не покупали)-.sabydoc.pdf`
**Format:** `.sabydoc` export (Saby internal wiki-page format) rendered to PDF, 6 pages, with UI screenshots and a design commentary overlay (green text = answered/settled, red text = open `[Вопрос N]` questions, yellow highlight = "новое окно/макет нужен" TODO markers).
**Project folder:** `Путь клиента` (Customer Journey) — a Saby/Tensor initiative building a generic scenario/marketing-automation engine ("Маршруты") on top of the existing Лояльность (Loyalty) subsystem. See [[CustomerJourney-Scenarios-Project]] for the folder's other (not-yet-ingested) documents.

> [!note] Sibling document — parallel ingest
> A **second, revised version** of this same scenario document is being ingested in parallel by another agent: `.raw/Путь клиента/Сценарий _Реактивация неактивных клиентов (давно не покупали)_МОРОЗОВ правит.pdf` — contains edits/comments from **Морозов**. This source page describes only the v1 (unedited) document. Once the sibling source page exists, diff the two for resolved questions / changed UI / changed business rule and add `[[contradiction]]` callouts where the revised version disagrees with this one. The orchestrator's finalize pass should cross-link both source pages and this note.

## What this document is

A design/discussion doc (not a finished spec) walking through building one concrete scenario — "Reactivation of inactive customers" — inside a new **Сценарии лояльности** (Loyalty Scenarios) UI section, in order to flush out the division of responsibility between three components:

1. **Лояльность** (Loyalty subsystem — existing PriceFormation.Online domain, this team)
2. **Маршруты** (Routes/Customer Journey platform — new, being built, ownership of most UI chrome is *assumed* by the doc's authors but explicitly unconfirmed)
3. **Выборки** (Selections/segmentation module — separate team, owned by **Миша Гаврилов**)

The bulk of the document is a numbered walkthrough of the scenario-builder UI, each step annotated with `[Вопрос N]` — an open question about who (which BL method, which component, which team) is responsible for that piece of UI or logic. Very few of these questions have settled answers in v1; those that do are marked in green.

## Business rule being modeled

> Ежедневно отбираем клиентов, кто не покупал последние 30 дней. Начисляем 100 бонусов и отправляем письмо, ждём покупки до 10 дней; если есть покупка — отправляем письмо «спасибо».

Full walkthrough, configured example values (100 bonus points, 10-day wait, sample "Ресторан Мили" tenant used for email templates, sample client pass timeline with a real purchase example: order 9247 ₽ containing "GUESS NOELLE 8 TOP ZIP" 3499₽ + "Туфли Dino Ricci Select 39 Коричневый" 5748₽) — see [[LoyaltyScenario-ReactivationInactiveClients]].

General scenario-builder architecture extracted from this walkthrough (menu structure, scenario types, general settings, condition-builder, flow-graph editor block types, event catalog, execution/scheduling model, open ownership questions) — see [[Route-Platform-Architecture]].

## Screenshots described (page → content)

- **p.1** — Left nav flyout under «Скидки и акции»: Бонусы / Промокоды / Реферальная система / Дисконтные карты / **Сценарии**. Сценарии list view: totals header (Проходы 8 276, В работе 2 924), list of scenario cards (Давно не покупали, Письмо с напоминанием, Брошенная корзина, День рождения, Бонусы при регистрации, Уведомление о начислении, Первая покупка, Сезонное зимнее обувь). Below: monthly stats table per scenario (Проходы/Выбывшие/Купившие/Сумма). A "Настройки" (Settings) modal: "Клиент попадает в сценарий не чаще [30] дн" (toggle **Ограничить срабатывание**, on by default) + "Режим тишины" (toggle, on by default, description: "Срабатывание сценарии будет приостановлено в указанные промежутки времени в часовом поясе клиента").
- **p.2** — "Создать сценарий" type picker: **По событию** / **Периодический** / **Разовый**. "Запуск сценария" dialog: schedule row ("Срабатывает Ежедневно 12:00") + condition builder ("Условие какое?", И/ИЛИ operators) with a long field palette: Покупали, Не покупали, Что, Где, Физлица (Пол, Возраст, День рождения), Владельцы карт, Без, Кол-во бонусов, Когда, Количество, Число покупок, Сумма, С последней покупки прошло, Есть телефон, Email. Two condition steps shown being added: "Физлица Есть Email" then "Не было покупок".
- **p.3** — Condition "Когда" set to "За последние 30 дн". Saved scenario card view — tabs: Описание / Этапы / Схема / Проходы / Статистика. Description tab shows: Условия старта (Срабатывает Ежедневно 12:00; Условие Физлица Есть Email + Не было покупок: За последние 30 дн), Цели block (empty, "+" to add), Клиенты list (sample rows: Олег, Загребова Елена — with mini status icons and amounts). Схема (flow-diagram) tab: start flag node + "+" node-type picker (Действие / Условие / Ожидание). Action picker opened, "Начислить бонусы" selected.
- **p.4** — Action config panel "Начислить бонусы" → "Начислить [100] 5" (points field). Action-add submenu: Начислить бонусы, Назначить скидку, Выдать промокод, **Отправить**, Перенести в папку, Добавить тег, Выполнить код. "Отправить" config: channel "Отправить по e-mail", From "Ресторан Мили", subject/body "Заберите ваши бонусы! Подарок от нас: 100 бонусов уже ждут вас в личном кабинете!". Node-type picker again, "Ожидание" (Wait) selected → schema shows "Начислить 100Б, отправить Email" node. Wait-block config: "Ждём [10] дней", И/ИЛИ condition rows, empty "Событие какое?" + "Время вышло" branches.
- **p.5** — Event picker (opened from the Wait block's "Событие какое?" row): grouped tree — Лояльность; Клиент (Оптовая покупка, Действия с карточкой клиента, **Розничная покупка** ✓ selected); Посетитель сайта → Вход на сайт; Корзина (Добавлен товар, Брошенная корзина, Заказ создан/изменен, Продукт добавлен в избранное, Окончание сессии); Бронирование; Запись. Wait block finalized: "Ожидание покупки 10 дней", branch "Розничная покупка → [переход]" / "Время вышло → [переход]". Second "Отправить" action block (thank-you email) configured identically to the first, trigger "Клиент совершил покупку". Final schema: flag → Действие (Начислить 100Б, отправить Email) → Ожидание (10 дней, branches Розничная покупка / Время вышло) → Действие (Отправить Email). Scenario card header shows Тип сценария "По расписанию", Цели block populated with sample placeholder goals ("Промо-акция сработала", "Отказался от покупки"), Клиенты list with more rows (Олег, Загребова Елена, Екатерина, Александрова Николай, Егор, Обручев Сергей, Наталия, Новосельцев Валентин) — sample/mock data, not real customers.
- **p.6** — "Проходы" (Passes/runs) tab: list of run records grouped by node reached (Ожидание покупки 10... / Отправить Email), with per-record counts. Клиент-detail "карточка прохода" for **Загребова Елена** (+7 (960) 123-45-67, esagrebova@email.ru): timestamped timeline — 19 авг "Клиент отобран" (Физлица: Есть Email, Не было покупок: За последние 30 дн) → "Начислить 100Б, отправить Email" (текст письма) → "Ожидание покупки 10 дней" → 20 авг "Есть покупка" (заказ 9 247 ₽: "Туфле GUESS NOELLE 8 TOP ZIP" 3 499 ₽ + "Туфли Dino Ricci Select 39 Коричневый" 5 748 ₽) → "Отправить Email" ("Спасибо, что выбираете нас! Поделиться впечатлением на magazin.ru") → "Промо-акция сработала за 1 д". Bottom-right "Статистика" panel is a yellow-highlighted "новый макет" placeholder — not designed yet; required metrics listed in body text: кол-во помещённых/прошедших/купивших, сумма начисленных баллов, кол-во отправленных писем, кол-во и сумма покупок.

## Key open questions (unresolved in v1, red-flagged by the doc's authors)

> [!question] Ownership boundaries — not settled in this version
> - Which BL method/component renders the left folder tree and right scenario list of «Сценарии лояльности»?
> - How/by whom is a new "Loyalty" scenario type registered into the Маршруты platform's type list?
> - Who owns general settings storage/UI (re-entry cooldown, quiet mode) — Лояльность, per the authors' working assumption, but unconfirmed?
> - Can Loyalty query which unfinished route/scenario instances a given client (`@Лицо`) is currently enrolled in?
> - Who owns the scenario card CRUD, the clients registry (**no mockup exists yet**), and the Цели (Goals) block — authors lean "either omit or take Маршруты's default as-is"?
> - Where/how is the saved selection ID (from Выборки) persisted and threaded through to the scenario dialog?
> - Who builds/renders the flow-scheme (Схема) editor, the block-type/action/event pickers, the Проходы registry and pass-detail card? Authors' working assumption: **Маршруты платформа** for all of these — not yet confirmed by that team.
> - What BL-method signature/format must Loyalty expose for Маршруты to call on schedule ("прикладной метод")? In which field of the scenario card is it registered?
> - How does Loyalty push run-time metadata (e.g., purchase details) into Маршруты's statistics at event-fire time — via what API?
> - What is the spec for the "авто-проходчик" (auto-walker) that executes consecutive non-waiting steps in one pass?

## Provenance note

This is a **product/architecture design discussion document**, not a finalized technical spec — most content is proposals and open questions rather than settled decisions. Treat facts here as "as understood by the document's authors at time of writing," subject to revision by the sibling Морозов-edited version and later ТЗ documents in the same `Путь клиента` folder (`Техническое задание.pdf`, `Концептуальное решение*.pdf`, `Блоки для сценариев лояльности.pdf`, `Список УсловийДействий.pdf`, `События-действия для сценариев лояльности.sabydoc.pdf` — not yet ingested).
