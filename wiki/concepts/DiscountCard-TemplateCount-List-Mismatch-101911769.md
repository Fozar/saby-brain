---
type: concept
title: "Ромашка в дизайне ДК: счётчик и список шаблонов расходятся (№101911769)"
created: 2026-10-29
updated: 2026-10-29
status: developing
tags: [price-formation, discount-cards, test-stand, bugfix]
related:
  - "[[DiscountCard-Design-Constructor-Architecture]]"
---

# Ромашка в дизайне ДК: счётчик и список шаблонов расходятся

## Задача
Ошибка на стенде №101911769, doc_id 631264537, веха 26.6100.
https://dev.saby.ru/opendoc.html?guid=01a15541-3f40-75ef-8330-9358f8aa103a&client=3
Автор Чудинов И.А. С 29.10 выполнение у Тимошенко А.А. Перенос срока на 28.11 согласуется.
fix-online, тип карты 6328. При открытии «Дизайн» появляется список с одной плиткой и бесконечной загрузкой.
Лебедева в передаче: DiscountCardType.GetTemplateCount вернул 2, GetTemplateList — 1.

## Где остановились
Анализ готов. Расхождение условий отбора находится в discount-cards, в методах CardType.GetTemplateCount/GetTemplateList.
Price-formation проксирует счётчик, при единственном элементе списка возвращает формат карточки.
Код не меняли. Рекомендация: передать владельцу методов СДК / согласовать исправление с Кузаковым Ю.

## Что выяснено по коду
- В price-formation get_template_count.py:31 возвращает результат CardType.GetTemplateCount (для участника франшизы отдельная ветка, здесь FranchiseRole=null).
- В discount-cards www/DCService/dcservice/online/cardtype/get_template_count.py счётчик ограничен только ClientID и CardTypeID.
- get_template_list.py в СДК дополнительно исключает черновики и требует ApplicationKey без dc_design_new, либо SiteId под фичей.
- В price-formation get_template_list.py:49–51 единственная запись заменяется результатом DiscountCardTemplate.Read: ThemeData вместо ThemeScreen.
- client/LoyaltyOnline/DiscountCardType/RegistryNew/DesignList/PrefetchConfig.ts:56–58 выбирает страницу одного дизайна только при счётчике 1.
- Плитка _designList/DesignList.wml:96 использует ThemeScreen.
- Исходный sbislogz содержит receivedState серверной предзагрузки, который semantic JSON конвертера не сохраняет. Проверен оригинальный архив.
- В receivedState designList: одна запись @Template=591210, 19 полей, ThemeData есть, ThemeScreen отсутствует; reportFeature.dc_design_new=false; размер страницы 30, навигация не объясняет расхождение.
- Скриншот подтверждает одну плитку с ромашкой, название «Основной7». Консоль не содержит ошибки, объясняющей симптом.
- Оба локальных репозитория находятся в ветках линейки 26.6100; конкретную скрытую запись СДК не читали, поэтому неизвестно, отсекается ли она по черновику или ApplicationKey.
- Серверные логи от 19.10 старше срока хранения 3 дня; не запрашивались.

## Решения и почему
Исправление требуется в СДК: счётчик и список должны учитывать одинаковые условия доступности шаблонов.
Правку в чужом репозитории не начинали; передача задачи и сообщения коллегам не выполнялись.

## Открытые вопросы
Какое условие исключает вторую запись у типа 6328 — требует чтения данных СДК.

## Roadmap
- Согласовать владельца исправления в СДК.
- Проверить одинаковый отбор при включённой и выключенной dc_design_new, включая черновики.
- На fix проверить тип 6328: открытие одного дизайна; также проверить тип с несколькими дизайнами.

## Ссылки
- Задача: https://dev.saby.ru/opendoc.html?guid=01a15541-3f40-75ef-8330-9358f8aa103a&client=3
- Ветка/MR по ошибке не создавались.
