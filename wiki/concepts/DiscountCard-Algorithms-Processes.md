---
type: concept
title: "Discount Card Service — Algorithms & Processes"
tags:
  - loyalty
  - discount-cards
  - algorithms
  - sbis
status: current
related:
  - "[[DiscountCard-Subsystem-Overview]]"
  - "[[DiscountCard-Service-API]]"
  - "[[PassUpdater-Service]]"
created: 2026-04-10
updated: 2026-04-10
---

# Discount Card Service — Algorithms & Processes

Source: `raw/Алгоритмы и процессы.md` | Domain: [[price-formation/_index]]

## Доступность сервиса ДК для внешних вызовов

Сервис ДК ограниченно доступен для внешних вызовов через **облегчённую систему прав** (light-right).

**Разрешённые домены:**
- `online.sbis.ru`
- `api.sabyget.ru`

**Разрешённые методы:**
```
Card.Delete/1, Card.Delete/2
Card.GetDetails/1, Card.GetDetails/2
Card.GetListV2/4
Card.GetPass/2
Card.ReadV2/1
Card.Save/1, Card.Save/2
CardTemplate.GetList/4
Pass.GetDownloadURL/2
CardType.NeedToUpdatePasses/1
Pass.CreateCertificate/3
Card.GetDesign/2
```

## Работа с конфиденциальными данными

Методы, работающие с конф. данными (имена клиентов, покупки, частота, суммы), настроены так, чтобы данные **не попадали в логи в открытом виде**. Шифруются с помощью EncryptData.

**Расшифровка логов (Python):**
```python
base64.b64decode(
    sbis.EncryptData.DecryptDataByKey('encoded_string', 'encrypt_key')
).decode('utf-8')
```

**Методы с конф. данными в discount-cards:**
Questionary.CreateCard, Questionary.VerifyPhone, Pass.GetDownloadURL, Wallet.GetUpdated, Card.Delete/1-2, Card.GetDetails/1-2, Card.GetListV2, Card.GetPass, Card.ReadV2, Card.Save/1-2, CardTemplate.GetList

**Методы с конф. данными в pass-updater:**
Wallet.DisableRegistrationOnUpdate, Wallet.RegistrationOnUpdate, Wallet.Get, Wallet.GetSerialNumber, Wallet.InitiateUpdate

## Сценарии с конф. данными

1. **Saby Get**: реестр карт, просмотр карты, получение образа, создание/удаление кастомной карты
2. **Online**: уведомления, получение образа по QR, обновление образов, управление подпиской на обновления
3. **Сервис рассылок**: массовые рассылки на AW-образы

## Сценарии межсервисного взаимодействия

| Сценарий | Участники |
|----------|-----------|
| Начисление бонусов на ДК в продаже | online ↔ СДК ↔ SabyGet |
| Обновление статистики по ДК | online → СДК |
| Запланированное изменение бонусного баланса (сгорание, отложенное начисление) | Планировщик → СДК |
| Выдача ДК через анкету (старая/новая) | online → СДК → pass-updater |
| Выдача ДК с рассылкой и получением эл. образа | online → СДК → Сервис рассылок → APN/Google |
| Выдача промокодов | online → СДК |
| Рассылка промокодов | СДК → Сервис рассылок |
| Отправка гео-уведомлений (Apple) | СДК → APN |
| Начисление бонусов на праздник | Планировщик → СДК |

## Синхронизация данных из онлайна в СДК

Сущности для поддержания актуальности: **Карта онлайна**, **Тип карты онлайна**.

**3 механизма синхронизации:**
1. `Card.ReloadCardInfoWithData` — основные данные карты (не статистика), синхронно (для старой анкеты)
2. Брокер синхронизации — асинхронная синхронизация
3. Планировщик `RequestCardsDataFromOnline` — регулярный запрос данных из онлайна

## Формирование электронных образов

### Apple Wallet
- Архив `.pkpass` — цифровой аналог карты для iOS (Apple Wallet)
- Подписывается сертификатом Pass Type ID + WWDR
- Устройство регистрируется в pass-updater после установки образа
- Дальнейшее обновление через APN (Apple Push Notification Service)

**Ссылки на внешние ресурсы:**
- passkit-generator: генерация сертификатов
- Apple Developer: WWDR-сертификат (`AppleWWDRCAG4.cer`)
- Apple documentation: Walletpasses API (pass.json, .pkpass, обновление)

### Google Pay
- JWT-образ для Android
- pass-updater напрямую обращается к Google API
- Шаблон (класс) + экземпляр (объект) по Google Wallet Loyalty API

## Подсистема прав

Внешние вызовы только с разрешённых доменов + только указанных методов (облегчённая система прав, light-right). Подробнее: [[DiscountCard-Service-API]]
