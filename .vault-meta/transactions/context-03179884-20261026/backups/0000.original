---
type: concept
title: "Удаление и скрытие клиента: свои обработчики событий для дисконтных карт"
created: 2026-10-07
updated: 2026-10-07
status: developing
tags:
  - discountcard
  - crm
  - events
  - contractor
  - tech-design
related:
  - "[[PromoCode-Registry-Search-By-Code]]"
  - "[[DiscountCard-GetListWithStats-SDK-Call-Loop]]"
---

# Удаление и скрытие клиента: свои обработчики событий для дисконтных карт

Задача в разработку №03179884 ([ссылка](https://online.sbis.ru/opendoc.html?guid=1b6ce09e-ef5b-4a0d-8f0b-da3ad2ca7865&client=3)), автор Лукьянов Н.Л. (Клиенты), заведена 17.03.2026. Веха 26.6100, срок 28.11.2026. Исполнитель в карточке пока Омельяненко: переназначить на Тимошенко он обещал после утверждения плана у Федько (переписка 06.10). Критерий приёмки: «Реализовано согласно задаче».

**Запрос.** Сейчас CRM сама проверяет наши карты и сама зовёт наш `DiscountCard.OnDestroyClient` при удалении и скрытии клиента. Лукьянов просит забрать эту логику к нам и подписаться на события контрагентов самим.

## Как сейчас (CRM, `crm/core`, ветка rc-26.6100)

Модуль «Активные продажи», `on_event.py` строки 102-123:

| Событие | Обработчик CRM | Что делает для карт |
|---|---|---|
| `online.contractor.deleting.allow` | `CRMClients.AllowDeletePhysic` (`activesales/crmclients/helpers.py:32`) | Для `Type = 2` и заполненного `Entrepreneur` запрос `HAS_SALE_OR_DOCS_OR_EMPLOYEE` (`templates.py`). Наш кусок (если загружен `PriceFormation.Online`): есть ли в `ВидЦеныДокумент` по картам клиента операции без `Sale`, без `Документ`, с `ДатаВремя` не NULL и меньше infinity |
| `online.contractor.deleting.deleted` | `CRMClients.DeleteClientHandlerForRec` (`handlers.py:37`) | `DiscountCard.OnDestroyClient([Entrepreneur])`, тип не проверяет |
| `online.contractor.deleting.deleted` | `CRMClients.DeletePhysic` (`editor.py:142`) | Удаляет `ЧастноеЛицо`, если `Тип = 4` |
| `contractor.hide` | `CRMClients.DeleteClientHandler` (`editor.py:116`) | По `@Лицо` контрагента берёт `Entrepreneur` для `Type = 2` и зовёт `OnDestroyClient` |

## Контракты событий (публикует `contragents/online`)

- `online.contractor.deleting.allow`: `LocalPublishRecord`, в обработчик идёт запись контрагента (`@Лицо`, `Entrepreneur`, `Type` enum, `UUID`, `Название`, `НеОтображается` и др., см. `delete.py::_prepare_delete`). Ответ: Record с полем `Allowed` (bool). Удаляют, только если все вернули True или None (`permissibility.py::can_delete`), иначе контрагента скрывают.
- `online.contractor.deleting.deleted`: та же запись, публикуется после `Contractor.DeleteInBaseSql` (`delete.py:362`). Для ИП и КФХ (`Type` 1, 3) до события уже вызван `PrivateFace.Delete`.
- `contractor.hide`: только `@Лицо` контрагента (int). Публикуется из удаления, когда удалять нельзя (`delete.py:769`), и из ручного скрытия в реестре (`set_display.py:157`).
- `Type`: 0 организация, 1 ИП, 2 физ. лицо, 3 КФХ, 4 гос. инспекция, 5 группа компаний (`contragents/common`, `ContractorKind`).

## Что у нас

- `DiscountCard.OnDestroyClient` (`priceformationonline/discountcard/discountcard/on_destroy_client.py`): берёт карты с `Карта.Лицо` = частное лицо клиента. У настоящих карт (тип CARD, ECARD) ставит `Заблокировано = True` и `Лицо = NULL` через `RetailDiscountCard.Update` (уходит уведомление в сервис ДК). У служебных персональных карт (без эмиссии) сохраняет ид. клиента в `Атрибуты.Client.ClientId`.
- `Карта.Лицо` ссылается на `Лицо` с `on_delete = 2` (по всей видимости обнуление ссылки). Для обычных карт там частное лицо (`Контрагент.Entrepreneur`), для партнёрских промокодов там `@Лицо` контрагента (`has_partner_activity.py`).
- Подписки модуля: `PriceFormation.Online/on_event.py`, `event.SetLocalCallback` в `OnEndAllLoadModules`. Приоритета у подписок нет, от CRM модуль не зависит (`PriceFormation.Online.s3mod`).

## Тех. решение

Три новых метода в `DiscountCard.orx` (category Handle, trusted_only) и подписки в `on_event.py`. Код в `discountcard/discountcard/handle_client_delete.py`:

1. `DiscountCard.HandleClientDeletingAllow(Contractor) -> Record{Allowed}`: тот же запрос по операциям, что был у CRM. Только для `Type = 2` с заполненным `Entrepreneur`, иначе True. Права на удаление клиента по-прежнему проверяет CRM.
2. `DiscountCard.HandleClientDeleted(Contractor)`: `on_destroy_client([Entrepreneur])`, как у CRM, без проверки типа.
3. `DiscountCard.HandleClientHide(ContractorId)`: `Entrepreneur` из `Контрагент` по `@Лицо` и `Type = 2`, затем `on_destroy_client`.

Совместимость: пока CRM не убрала свои вызовы, всё выполнится дважды. Это безопасно: проверка просто дублируется, а второй `OnDestroyClient` уже не найдёт настоящих карт (у них `Лицо = NULL`), служебным картам повторно запишет тот же ид. Порядок выката: сначала мы, потом CRM убирает свой кусок запроса и оба вызова `OnDestroyClient`. Сам `OnDestroyClient` оставляем, пока его зовёт CRM.

## Открытые вопросы

1. **Порядок с `CRMClients.DeletePhysic`** (Лукьянову). Наш обработчик `deleted` ищет карты по `Карта.Лицо`. Если `DeletePhysic` отработает раньше, ссылка обнулится и карты останутся незаблокированными и без владельца. Порядок локальных подписок между модулями ничем не гарантирован, сейчас это везение (так и сказано в задаче). Варианты: CRM удаляет частное лицо после всех обработчиков `deleted` (отдельным шагом или событием); или нам дают событие до удаления частного лица.
2. **Отвязка при скрытии** (Лукьянову, Омельяненко). Сейчас при скрытии карта и блокируется, и отвязывается от клиента, хотя клиента потом могут восстановить (`contractor.recover`), в коде на это TODO. Можно при скрытии только блокировать, а отвязывать при удалении. Это меняет поведение, поэтому в заготовке оставлено как было.
3. **Вне задачи**: партнёрские промокоды (`Карта.Лицо` = контрагент) при удалении клиента не обрабатываются ни сейчас, ни в заготовке. Франшиза тоже: карты ищутся только в своём аккаунте.

## Состояние

- Worktree `D:/dev/wt03179884`, ветка `26.6100/feature/aatimoshenko/03179884` от `origin/rc-26.6100`, не закоммичено.
- Изменено: `DiscountCard.orx` (3 метода), `PriceFormation.Online/on_event.py` (3 подписки), новый `handle_client_delete.py`, тесты `tests/tests_priceformationonline/discountcard/discountcard/handle_client_delete.py` (9 тестов, не запускались). pylint 10/10.
- От CRM (Лукьянов) после нашего выката: убрать кусок `pf_module` из `HAS_SALE_OR_DOCS_OR_EMPLOYEE` и вызовы `OnDestroyClient` из `delete_client_handler` и `delete_client_handler_rec`.
