---
type: source
title: "Вложения проекта «Реферальная программа (2 часть)» (2026-08-06)"
updated: 2026-08-06
tags:
  - source
  - price-formation
  - referral
  - sabynet
source_files:
  - "project.sbis.ru/uuid/15d9be83-4971-4f44-987f-023d063ec191/page/project-main (doc_id=544981304)"
status: current
related:
  - "[[ReferralProgram-Part2-Project]]"
  - "[[ReferralProgram-Folders-Priority-Sprint]]"
  - "[[ReferralProgram-ContractorCard-Programs-Tab]]"
  - "[[ReferralProgram-Leads-Section]]"
  - "[[ReferralProgram-SabyNet-Widgets-Redesign]]"
  - "[[ReferralProgram-Offer-Visibility]]"
  - "[[ReferralProgram-Offer-Topics]]"
  - "[[ReferralProgram-SelfJoin]]"
  - "[[ReferralProgram-SabyNet-Offer-Contract]]"
address: c-000271
created: 2026-08-06
---

# Source: вложения проекта «Реферальная программа (2 часть)» (2026-08-06)

Карточка проекта `project.sbis.ru/uuid/15d9be83-4971-4f44-987f-023d063ec191` → `doc_id=544981304` (тип «Проект», у `sbis_resolve_url` ридера нет — тот же двухшаговый путь, что в [[discount-card-design-constructor-attachments-2026-08-06]]). Вложений: 11 верхнего уровня, из них 6 папок; всего разобрано **14 документов**.

## Созданные страницы

- [[ReferralProgram-Part2-Project]] — зонтик: цели ТЗ, карта спринтов, ответственные, что уже реализовано
- [[ReferralProgram-Folders-Priority-Sprint]] — спринт №2 (78 дней): папки/приоритеты/плитки, полная тех. реализация БЛ
- [[ReferralProgram-ContractorCard-Programs-Tab]] — спринт №3 (35,5 дней): `GetListByContractor`, `ContractorHasPrograms`, `CRMNavigationPreload`
- [[ReferralProgram-Leads-Section]] — раздел «Лиды» для обеих ролей
- [[ReferralProgram-SabyNet-Widgets-Redesign]] — разводящая и виджеты (спринты «Разводящая» + «Визуальные изменения» + «Текущее состояние»)
- [[ReferralProgram-Offer-Visibility]] — «Всем кроме» + папки партнёров
- [[ReferralProgram-Offer-Topics]] — темы (теги) офферов
- [[ReferralProgram-SelfJoin]] — самостоятельное присоединение (45 дней, самый свежий спринт)
- [[ReferralProgram-SabyNet-Offer-Contract]] — спринт №4, «Оферта SabyNet»
- Сущности: [[Тихонов-Илья]], [[Кулешов-Дмитрий]]

## Ключевые факты

- **Первоисточник корешков.** Тех. реализация спринта №2 (декабрь 2025) фиксирует переход статистики на `ВидЦеныДокумент` и **отказ от сервиса Маркетинга** — оценка 7 дней. Это исходная постановка всей линии [[ReferralProgram-Stub-Implementation]] → [[ReferralStub-Backfill-Service-Method]] → [[ReferralProgram-RefDealsConvert-Feature]].
- **`LeadSum` нужен ещё в двух методах.** Реализованное сегодня поле ([[ReferralStub-LeadSum-Implementation]]) заказано этим проектом также для `ReferralProgram.GetList` (спринт №2) и `GetListByContractor` (спринт №3), а не только для `GetPartnerList`.
- **Новые БЛ-методы, ещё не в вики**: `ReferralProgram.Move` (по сигнатуре `IndexNumber.Move`), `GetListByContractor`, `ContractorHasPrograms`; фильтр `IsJoined` и поля `Folder`/`FolderName` в существующих.
- **Схема БД под папки не меняется** — иерархия `ВидЦены.Раздел` уже есть.
- **Доступность офферов** — режим «Всем кроме» в `ВидЦеныРасширение.ТипПредоставления` по аналогии с доступностью скидки по клиентам.
- **Курсорная навигация заявок** оценена в 6 дней с явной оговоркой «функционал сложный, заложить ×2 на ошибки» (по опыту `Bonus.GetSaleList`).
- **Масштаб продукта**: 30 аккаунтов-партнёров, 5–7 владельцев.
- Новые лица: [[Тихонов-Илья|Тихонов И.]] (БЛ) и [[Кулешов-Дмитрий|Кулешов Д.]] (UI) на спринте самоприсоединения; Точилова Д. — плановые сметы; Симаков В. — тестирование; Малышев К. А. — UI контрагентов; Притыкин А. — лендинг; Борисевич А. — макет; Мороз Д. — документация.

## Отрицательные результаты (не перечитывать)

- **«Сравнение с конкурентами»** и **«Эксплуатация системы»** — незаполненные корпоративные шаблоны, `lastEditDate` февраль 2025 (до старта проекта). Хранятся не zip-ом, а «голым» JSON — `convert_sabydoc_to_markdown` на них падает с «не является zip-архивом». Тот же вывод, что и по проекту «Дизайн ДК на конструкторе»: эта пара документов в карточках проектов SBIS пустая по умолчанию.
- **Спринт №3 «Приоритеты отображения реф. программ и папки для группировки»** — пустой шаблон концепта.
- **Спринт №5 «Ручное изменение суммы вознаграждения»** — шаблон, содержательного текста две фразы (перенесены в [[ReferralProgram-Part2-Project]]).

## Не обработано

- Две плановые сметы `.pdf` (спринты №2 и №3) — числовые данные по работам перенесены из концептов, отдельно PDF не разбирались.
- Скриншоты `.png` (папки «Раздел Статистика», «Главная страница партнера») и `.url`-ярлыки на Figma.
- Изображения внутри `.sabydoc` сохранены в `*.resources/`, но в вики не переносились.
