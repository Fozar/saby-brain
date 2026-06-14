---
type: concept
title: "Промокоды — Информационная модель"
updated: 2026-04-10
tags:
  - loyalty
  - promocode
  - info-model
  - price-formation
status: current
related:
  - "[[Promocode-Subsystem-Overview]]"
  - "[[Loyalty-Database-Schema]]"
  - "[[BonusDecRule-Info-Model]]"
created: 2026-04-10
---

# Промокоды — Информационная модель

Navigation: [[Promocode-Subsystem-Overview]] | [[Loyalty-Database-Schema]]

---

## Иерархия прикладных объектов

```
PromoCode (абстрактный)
├── PromoCodePublic       (Тип=5, общий)
├── PromoCodeIndividual   (Тип=6, индивидуальный)
├── PartnerPromoCode      (Тип=7, партнёрский)
└── PromoCodeForActivity  (Тип=8, за активность)

PromoCodeEmission  — эмиссия (выпуск) промокодов
PromoCodeItem      — экземпляр промокода (конкретная карта)
PromoCodeDesign    — служебный тип настроек отображения
```

---

## PromoCode (базовый абстрактный объект)

| Поле | Тип | Описание |
|------|-----|----------|
| Name | String | Название промокода |
| IsActive | Boolean | Доступен к использованию |
| Type | Enum | 5-Общий, 6-Индивидуальный, 7-Партнёрский, 8-За активность |
| Promotion | Акция | Связанная акция (условия применения) |
| SalesPointList | ТочкаПродаж[] | Точки продаж |

---

## PromoCodePublic (Общий, Тип=5)

Дополнительные поля:

| Поле | Тип | Описание |
|------|-----|----------|
| Code | String | Код промокода |
| ApplyLimit | Integer | Максимально допустимое число применений |
| OncePerClient | Boolean | Только единоразовое применение на одного клиента |
| Design | ДизайнПромокода | Настройки отображения |

---

## PromoCodeForActivity (За активность, Тип=8)

| Поле | Тип | Описание |
|------|-----|----------|
| Amount | Integer | Лимит выдачи |
| SubType | Enum | Способ выдачи: 1-Покупка, 2-Опрос, 4-Отзыв, 8-Регистрация |
| NumberFormat | НастройкиГенерации | Правила генерации кодов |
| ConditionData | УсловияЗаПокупку | Критерии выдачи |
| InterviewList | Опрос[] | Опросы (для SubType=2) |
| NotificationEnabled | Boolean | Отправка уведомлений о выдаче |
| Notification | Рассылка | Рассылка уведомлений |

---

## PromoCodeEmission (Эмиссия промокодов)

| Поле | Тип | Описание |
|------|-----|----------|
| PromoCode | Промокод | Головной промокод |
| GenerationType | Enum | Способ создания экземпляров |
| ReleaseDate | Date | Дата создания эмиссии |
| ExpirationPeriod | Integer | Срок действия (в днях) |
| NumberFormat | НастройкиГенерации | Настройки генерации |
| Broadcast | Рассылка | Документ рассылки клиентам |

---

## PromoCodeItem (Экземпляр промокода)

| Поле | Тип | Описание |
|------|-----|----------|
| PromoCodeEmission | Эмиссия\|Промокод | Родительская эмиссия |
| Code | String | Конкретный код |
| ReleaseDate | Date | Дата создания |
| Client | Контрагент | Владелец экземпляра |

---

## НастройкиГенерацииПромокодов (NumberFormat)

| Поле | Тип | Описание |
|------|-----|----------|
| Prefix | String | Префикс кода |
| AllowedSymbols | Enum | Both / Numbers / LatinUpperLetters |
| Length | Integer | Длина кода |
| Type | Enum | QR / EAN8 / EAN13 |

---

## УсловияЗаПокупку (ConditionData)

Ключевые поля условий выдачи промокода:

| Поле | Описание |
|------|----------|
| Clients / ExcludedClients | Белый/чёрный список клиентов |
| DiscountCards | Требуется дисконтная карта определённого типа |
| OnBirthday | За N дней до/после дня рождения |
| FirstOrder | За первый заказ |
| Regions / ExcludedRegions | Геозависимость |
| Period | Дата/время/дни недели+месяца |
| SalesPoints | Конкретные точки продаж |
| ForDelivery | 0-нет, 1-самовывоз, 2-курьер, 3-оба |
| PaymentType | 1-нал, 2-карта, 3-зарплата, 4-QR, 5-интернет |
| Nomenclature | Конкретные товары |
| SaleType | 0-оптом, 1-розница |
| SaleSum | Минимальная сумма покупки |
| NomenclatureCount | Минимальное количество |

---

## ПериодСрабатывания

StartDate/EndDate + StartTime/EndTime + DaysOfWeek + DaysOfMonth — полный контроль временного окна выдачи.

---

## ДизайнПромокода

- **DesignData** (НастройкаАспекта) — настройки для кошелька мобильного устройства
- **PromoPage** (НастройкаАспекта) — настройки вида промо-страницы промокода
