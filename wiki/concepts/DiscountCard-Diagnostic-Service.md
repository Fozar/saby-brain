---
type: concept
title: "Discount Card Diagnostic Service (discount-cards_diagnostic)"
tags:
  - loyalty
  - discount-cards
  - diagnostic
  - sbis
status: current
related:
  - "[[DiscountCard-Subsystem-Overview]]"
  - "[[Loyalty-Database-Schema]]"
created: 2026-04-10
updated: 2026-04-10
---

# Discount Card Diagnostic Service

Source: `raw/Сервис Диагностика (discount-cards_diagnostic).md` | Domain: [[price-formation/_index]]

Сервис `discount-cards_diagnostic` входит в состав web-приложения `discount-cards`.

## Назначение

1. **Административная панель СДК** — просмотр и изменение статусов/тела задач и запросов
2. **Консьерж (по ТП)**:
   - Информация о применениях промокодов
   - Статистика применений и выдачи эмиссий промокодов

## Типовые выборки

### 1. Получение списка дисконтных карт
Метод: `DiscountCard.GetList/4`

Фильтры:
- ID карты в СДК / в онлайне
- ID типа карты в СДК / в онлайне
- ID аккаунта в онлайне
- Тип (хранимая, онлайна и др.)
- ID персоны
- Признак активности
- Период последнего изменения
- Строка поиска (по ID карты в СДК, в онлайне, номеру, названию)

Сортировка: по ID карты в СДК, по убыванию (курсорная навигация).

### 2. Получение списка типов карт
Метод: `CardType.GetList/4`

Фильтры:
- ID типа карты в СДК / в онлайне
- Тип
- Название
- Признак публикации в SabyGet
- Признаки активности уведомлений (гео, покупки, сгорание бонусов)
- Строка поиска

Сортировка: по ID типа карты в СДК, по убыванию (курсорная навигация).

## Индексы БД

| Индекс | Таблица.Поле | Используется в выборке |
|--------|-------------|----------------------|
| PersonID | Card.PersonID | 1 |
| ClientID | Card.ClientID | 1 |
| CardTemplate | Card.CardTemplate | 1 |
| CardID | Card.CardID | 1 |
| OnlineCardTypeID | Card.OnlineCardTypeID | 1 |
| Number | Card.Number | 1 |
| Description | CardTemplate.Description | 1 |
| ClienID_OnlineCardTypeID | CardType.ClienID_OnlineCardTypeID | 1, 2 |
| Name | CardType.Name | 1, 2 |
| Type | CardType.Type | 2 |
