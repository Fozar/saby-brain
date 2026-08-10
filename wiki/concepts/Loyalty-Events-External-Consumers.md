---
type: concept
address: c-000273
title: "Loyalty-Events-External-Consumers"
created: 2026-08-10
updated: 2026-08-10
tags:
  - dwc
  - loyalty
  - events
  - migration
  - integration
status: developing
related:
  - "[[DWC-Card-Events-Migration]]"
  - "[[DWC-Promocode-Events-Migration]]"
  - "[[DWC-BonusSettings-Events-Migration]]"
  - "[[DWC-Migration-SDK]]"
  - "[[DiscountCard-Subsystem-Overview]]"
  - "[[Тимошенко А.А.]]"
---

# Loyalty-Events-External-Consumers

Удаление событий лояльности при переходе на DWC ломает не только СДК. У части событий есть **потребители за пределами discount-cards**, о которых команда лояльности не знает: подписки живут в чужих репозиториях и на код price-formation никак не ссылаются.

Задача-триггер: **№03266097** — «Удалить код отправки событий на СДК и обращение к фичам т.к. везде перешли на DWC» (ветка `26.6100/feature/aatimoshenko/03266097`, коммит удаляет 14 событий).

---

## Как искать потребителей

Единственный надёжный способ — полнотекстовый поиск имени события по всей кодовой базе Saby (`mcp__saby-search__search_code`), а не по price-formation. Подписка выглядит как строковый литерал в `on_event.py` целевого сервиса и никак не связана с публикующим кодом:

```python
# repo: warehouse/discount-cards — www/DCService/on_event.py
('online.loyalty-card.card-type-data.changed', 'CardType.HandleChangeData'),
```

Проверять надо **каждое** имя события отдельно. Поиск по `rc-26.4100` и `rc-26.5100` даёт одинаковый результат — подписки стабильны между релизами.

---

## Найденные внешние потребители (2026-08-10)

Из 14 удалённых событий 12 слушал только `discount-cards`. Два события имеют **дополнительных** подписчиков:

| Событие | Внешний потребитель | Обработчик | Что делает |
|---------|--------------------|-----------|------------|
| `online.loyalty-card.card-type-data.changed` | `sabyget/core` — `service/SabyGet/on_event.py:32` | `Tasks.EventUpdateBonusFlag` | обновляет флаг бонусов у заведения |
| `online.loyalty-system.promocode-type-data.changed` | `saby-forms/saby-forms` — `service/SabyForms/on_event.py:11` | `Survey.UpdatePromocode` | обновляет виджет промокода в опросе |

Обе подписки после выката 26.6100 перестанут срабатывать **молча** — ошибок не будет, просто перестанут приходить сообщения.

> [!warning] Не трогать при чистке SabyForms
> SabyForms подписан ещё на `online.loyalty-system.promocode-type-survey.linked` / `.unlinked` (`on_event.py:9-10`). Эти события **продолжают публиковаться** из `promocode/core/core.py:863,872` и `promocode/activity/survey.py:72`. При выписывании задачи в SabyForms это надо оговорить явно, иначе снесут лишнее.

---

## Паттерн решения: re-publish своего события из СДК

Переводить внешний сервис на DWC-задачу от price-formation — дорого (им нужен свой DWC-сценарий). Принятый в проекте подход другой: **СДК в своём обработчике публикует собственное событие**, а внешний сервис переезжает на него.

Прецедент уже реализован для SabyGet — `dccore/cardtype/core.py:12`:

```python
def notify_changes(initial_card_type: CardType, updated_card_type: CardType) -> None:
    """Уведомить SabyGet об изменении типа карты"""
    # Уведомляем только при активации/деактивации, изменении срока действия
    # и возможности выдачи карт
    if (
        initial_card_type.enabled != updated_card_type.enabled
        or initial_card_type.public_distribution != updated_card_type.public_distribution
        or initial_card_type.end_date != updated_card_type.end_date
        or initial_card_type.sale_points != updated_card_type.sale_points
    ):
        event.Publish(event.Event(
            name='discount-cards.card-type.changed',
            payload=sbis.Record({
                'ClientID': initial_card_type.client_id,
                'CardTypeID': initial_card_type.online_card_type_id
            }),
            application='sabyget',
            visibility=event.Visibility.evSERVER_ONLY,
            policy=sbis.PublicationPolicy.ppIMMEDIATELY
        ))
```

Вызывается из обоих обработчиков: `CardType.HandleChangeData:200` и `PromocodeType.HandleChangeData:145`.

SabyGet **уже подписан** на `discount-cards.card-type.changed` (`on_event.py:19` → `Tasks.EventByDiscountCard`), но другим обработчиком — для сброса кэша. Переезд `Tasks.EventUpdateBonusFlag` на это же событие сводится к правке одной строки у них.

### Аналог для SabyForms (реализован 2026-08-10)

Добавлено в `dccore/cardtype/core.py` + вызов в `PromocodeType.HandleChangeData`:

```python
def notify_promocode_type_changes(updated_promocode_type: CardType) -> None:
    """Уведомить SabyForms об изменении выпуска промокода"""
    event.Publish(event.Event(
        name='discount-cards.promocode-type.changed',
        payload=sbis.Record({
            'ClientID': updated_promocode_type.client_id,
            'PromocodeTypeID': updated_promocode_type.online_card_type_id
        }),
        application='saby-forms',
        ...
    ))
```

---

## Поле `application` в event.Event

`application` — псевдоним приложения-адресата, в чей адрес публикуется событие. Пустая строка = online. Известные значения из discount-cards: `sabyget`, `sabyget-service`, `smsc_service`.

Для SabyForms корректное значение — **`saby-forms`**, подтверждается их же константой:

```python
# saby-forms/saby-forms — service/SabyForms/Events/__init__.py:18
EVENT_APPLICATION_NAME = "saby-forms"
```

Определение поля — докстринг `publish_to_users` в том же файле: «Псевдоним приложения, в адрес которого публикуется событие».

---

## Разница в семантике при переезде

Новое событие СДК **не эквивалентно** старому событию Онлайна. При выписывании задач внешним командам это надо проговаривать:

1. **Payload другой.** Было — RecordSet изменений с полным набором полей; стало — `Record{ClientID, CardTypeID}` / `Record{ClientID, PromocodeTypeID}`. Потребителю придётся дозапрашивать данные.
2. **Условия срабатывания уже.** `notify_changes` шлёт только при изменении `enabled` / `public_distribution` / `end_date` / `sale_points`, а старое событие — при любом изменении данных типа карты.
3. **Не срабатывает при создании.** Вызов обёрнут в `if current_card_type is not None` — событие уходит только при обновлении. Для сценариев вроде «первый бонусный тип карты у аккаунта» это дыра, которую надо явно обсуждать с потребителем.

---

## Ответственные (из `responsible` в .orx)

| Сервис | Метод | Ответственный |
|--------|-------|--------------|
| SabyGet | `Tasks.EventUpdateBonusFlag` (`SabyGetDWC.orx:875`) | Исламов А.И. (`dcb50614-519a-4f45-9904-2918f79e17ba`) |
| SabyGet | `Establishment.EventUpdateBonusFlag` (`SabyGet.orx:8790`) | Никитин Е.С. (`df56a420-8ade-413d-9a3b-d9ea82702f0e`) |
| SabyForms | `Survey.UpdatePromocode` (`SabyForms.orx:2892`) | Антонов А.А. (`a6718d27-391b-40ee-b428-f3ec50149fbb`) |

`responsible` в .orx — владелец метода, а не обязательно текущий состав команды. Перед выпиской перепроверять.

---

## Ключевые файлы

| Файл | Роль |
|------|------|
| `discount-cards www/DCService/on_event.py` | подписки СДК; 14 строк удалены в 03266097 |
| `discount-cards www/DCCore/dccore/cardtype/core.py` | `notify_changes`, `notify_promocode_type_changes` |
| `discount-cards www/DCService/dcservice/online/cardtype/handle_change_data.py:200` | вызов `notify_changes` |
| `discount-cards www/DCService/dcservice/online/promocodetype/handle_change_data.py:145` | вызов `notify_changes` + `notify_promocode_type_changes` |
| `sabyget/core service/SabyGet/on_event.py:32` | подписка, требующая переезда |
| `saby-forms/saby-forms service/SabyForms/on_event.py:11` | подписка, требующая переезда |
