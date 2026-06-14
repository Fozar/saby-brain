---
type: concept
title: "Discount Card Service API (discount-cards)"
tags:
  - loyalty
  - discount-cards
  - api
  - sbis
status: current
related:
  - "[[DiscountCard-Subsystem-Overview]]"
  - "[[DiscountCard-Algorithms-Processes]]"
  - "[[Loyalty-Public-API]]"
created: 2026-04-10
updated: 2026-04-10
---

# Discount Card Service API

Source: `raw/API подсистемы.md` | Domain: [[price-formation/_index]]

Расположение сервиса:
- Пользовательское API: `private.sbis.ru/discount-cards/service/`
- Админское API: `private.sbis.ru/discount-cards_diagnostic/service/` и `cloud.sbis.ru/discount-cards_diagnostic/service/`

---

## Пользовательское API (Card.*)

Работает только с **активными** картами, принадлежащими текущей персоне (из сессии).

| Метод | Описание |
|-------|----------|
| `Card.Save` | Создать/обновить хранимую ДК. При наличии PK — обновляем, иначе создаём |
| `Card.Delete` | Отключить хранимую ДК (пометить неактивной) |
| `Card.GetList` | Список активных ДК персоны. Поддерживает фильтры: Keys, ClientID, SalePoint, ShopID, SearchString |
| `Card.Read` | Одна активная ДК по идентификатору |
| `Card.GetOwnerList` | Список UUID владельцев активных карт онлайна |
| `Card.GetSalePointCardInfo` | Инфо о ТП: ECardInfo (можно ли выдать карту), BonusesInfo (баланс бонусов) |
| `Card.GetWallet` | Wallet-образ карты онлайна (ссылка на .pkpass в FileTransfer) |
| `Card.GetListV2` | Список активных карт персоны (расширенный, v4+) |
| `Card.ReadV2` | Активная карта текущего пользователя по ID |
| `Card.GetPass` | Электронный образ карты онлайна для текущего пользователя |

### Card.Save — поля
- `Card` (Integer|None) — PK (при обновлении)
- `Number` (String) — номер карты (обязателен при создании)
- `FrontImg`, `BackImg` — фото карты
- `TemplateID` (Integer) — PK шаблона (с 20.2100)
- `EmissionBarCode` (String) — тип штрихкода
- `CreationDate` (DateTime)
- `Attributes` (String) — доп. атрибуты карты

### Card.GetList — возвращаемые поля
`Key`, `Number`, `EmissionBarCode`, `Attributes`, `CanBeAddedToWallet`, `Template` (ID, Name, StripImageUrl, ShopUUID, Aliases, LogoUrl, BackgroundColor, TextColor), `Name`, `FrontImg`, `BackImg`, `LastUpdated`, `CreationID`, `ClientID`, `WalletSerialNumber`, `EmissionName`, `DiscountValue`, `ExpireCardDate`, `IsExpired`, `SalesPointList`, `Bonuses` (AvailableBalance, NextExpirationDate, NextExpirationSum, MaxPaymentPercent)

### Коды ошибок (Card.*)

| Код | Описание |
|-----|----------|
| 1000 | Карта была удалена ранее |
| 1010 | Удаление невозможно, непредвиденная ошибка |
| 1020 | Не удалось получить персону |
| 1030 | Ошибка при обработке карты из сервиса |
| 1040 | Ошибка при обработке карты из онлайна |
| 1050 | Дата последнего обновления карты > переданного |
| 1060 | Переданы не все обязательные поля |
| 1070 | Не все обязательные поля содержат значения |
| 1080 | Проблема при сохранении изображения |
| 1090 | Карта с таким идентификатором отсутствует |
| 1100 | Карта принадлежит другой персоне |
| 1110 | Удаление карты онлайна запрещено |
| 1120 | Изменение основных данных карты онлайна запрещено |
| 1150 | Неподдерживаемый тип штрих-кода |

---

## Шаблоны дисконтных карт

### Пользовательское API
| Метод | Описание |
|-------|----------|
| `Company.GetList` / `CardTemplate.GetList` (с 20.7100) | Список активных шаблонов. Фильтры: SearchString, ИдО |

Возвращает: ID, Name, Logo, LogoID, TrueLogo, Aliases, Shop, BackgroundColor, TextColor

### Админское API
| Метод | Описание |
|-------|----------|
| `CardTemplate.GetList` | Все шаблоны (активные и неактивные). Фильтры: ИдО, ShopID, Enabled, SearchString |
| `CardTemplate.Read` | Один шаблон по ИдО. Включает Strip, Logo, BackgroundColor, TextColor, TypeBarCode |
| `CardTemplate.Save` | Создать/обновить шаблон |

---

## Админское API (Card.*)

Работает с **любыми** картами в сервисе (без ограничений по персоне).

| Метод | Описание |
|-------|----------|
| `Card.Save` (admin) | Дополнительные поля: Company/CompanyName, PersonID (обязателен при создании) |
| `Card.Delete` (admin) | Пометить неактивной (не требует проверки персоны) |
| `Card.GetList` (admin) | Полный список карт. Фильтры: Number, SearchString, Enabled, ClientID, Card, CardID, Type (1=хранимые, 2=онлайна), ShopID, SalePoint |
| `Card.Read` (admin) | Одна карта по идентификатору |
| `Card.ReadV2` | Активная карта по ID |
| `Card.GetDetails/1`, `Card.GetDetails/2` | Детальная информация о карте |

### Поля Card.GetList (admin)
`Card`, `Number`, `Enabled`, `PersonID`, `Attributes`, `ClientID`, `CardID`, `ShopID`, `Company`, `CompanyName`, `CompanyImage`, `TemplateID`, `TemplateLogoUrl`, `TemplateLogoID`, `TemplateName`, `FrontImg`, `BackImg`, `LastUpdated`, `CreationDate`

---

> [!note] Связь с Loyalty-Public-API
> `Card.GetListV2`, `Card.ReadV2`, `Card.GetPass` также описаны в [[Loyalty-Public-API]] в разделе карт.
