---
type: concept
title: "Loyalty Stomp Sync Feature Gap"
created: 2026-09-09
updated: 2026-09-09
status: developing
tags:
  - concept
  - loyalty
  - sync
  - offline
  - stomp
  - bugfix
related:
  - "[[Sync-Broker]]"
  - "[[Sync-Broker-Reactive]]"
  - "[[BrokerLoyalty-BonusSettings-Race-Fix]]"
  - "[[BonusSettings-Sync-Restart-Bug]]"
  - "[[Loyalty-Desktop-Broker-Migration]]"
  - "[[DWC-BonusSettings-Events-Migration]]"
---

# Loyalty Stomp Sync Feature Gap

Фича `lty_broker_sync_new3` открывается поюнитно после хф26.4227, а не всем сразу. Стомп-путь синхронизации лояльности её **не проверяет вообще** — подписка на каналы и регистрация обработчиков идут безусловно. Отсюда: на аккаунте с выключенной фичей реактивная синхронизация всё равно работает, а поверх неё работает старый путь синхронизации. По звонку 09.09.2026 решено, что так быть не должно, и это чинят в хф34.

**Код:** `price-formation`, ветка `26.5100/bugfix/aatimoshenko/07204334` от `rc-26.5100`, состояние на 2026-09-09.

---

## Цепочка целиком

### 1. Публикация на онлайне

| Что меняют | Где | Что зовут |
|---|---|---|
| Настройки бонусов | `priceformationonline/loyaltyprograms/bonus/update_settings.py:62` → `set_bonus_settings()` (`priceformationcommon/discount/discount/set_bonus_settings.py:163`) | `commit_after_update()` → `bonus_settings_to_broker()` (`.../bonus/core/history_settings.py:182`) |
| Список ТП настроек бонусов | `.../bonus/core/history_settings.py:264` | `bonus_settings_to_broker(sbis.Bonus.ReadSettings())` |
| Виды цен, промокоды | разные точки | `price_entity_to_broker` / `promo_code_to_broker` |

Все они сходятся в `_send_to_broker()` (`priceformationcommon/core/sync.py:161`):

```python
broker_event = SYNC_BROKER_SENDER.BrokerEvent(table_name, uuid_, ...)
broker_event.SetPublishPolicy(sbis.PublicationPolicy.ppON_REQUEST_FINISH)
event_template = SYNC_BROKER_SENDER.EventTemplate(
    name=EVENT_NAME_PRICE_ENTITY_CHANGED,      # 'loyalty.program.change'
    policy=event.Policy.evON_TRANSACTION_COMMIT,
    channelled=True,
    applications=['mobile', 'offline'],
    clients=[sbis.Session.ClientID()],
)
```

### 2. Канал один на всё

`EVENT_NAME_PRICE_ENTITY_CHANGED = 'loyalty.program.change'` (`core/sync.py:41`) — один канал для настроек бонусов, видов цен и промокодов. Различаются они только именем объекта в событии: `BonusSettings`, `ВидЦены`, `Промокоды`. Практический вывод для диагностики: если по акциям стомпы доезжают, а по настройкам бонусов нет — подписка тут ни при чём, ломается либо публикация, либо маршрутизация на конкретный обработчик.

### 3. Приём в офлайне

```
on_event.py:27  OnEndAllLoadModules → sync_init()  (broker_sync_loyalty.py:97)
                  ├─ SyncManager.AddSync(...) для 4 сущностей
                  └─ SyncBrokerClient.Register(BonusSettingsSync, PromoCodeSync,
                                               PriceEntitySync, CardEmissionSync)   ← строка 112
on_event.py:29,36  desktop.user-authenticated  И  .secondary → PFSync.OnUserAuthenticated
                  └─ подписка на 'discount-cards.changed' и 'loyalty.program.change'
                     (on_user_authenticated.py:22-27)

стомп → BonusSettingsSync.StompHandler (bonus_settings_sync.py:74)
      → sbis.PFSync.BonusSettingsSync() → SyncBrokerClient.Sync(BonusSettingsSync())
      → онлайновый PFSync.BonusSettingsRegularSync → sbis.SyncBroker.GetObjects
      → UpdObjects → sbis.Discount.SetBonusSettings (bonus_settings_sync.py:48)
```

---

## Где именно дыра

Ни `sync_init()`, ни `on_user_authenticated()` не смотрят на `Feature.LTY_BROKER_SYNC` (`lty_broker_sync_new3`, `priceformationcommon/helpers/feature.py:25`). Фича проверяется только в `run_broker_sync_loyalty()` (`broker_sync_loyalty.py:168,177`) — то есть гасит **пул** через SyncManager, но не реактивный путь.

Кузаков Юрий подтвердил это же словами (переписка, 2026-09-08 18:16):

> Да, для стомпов фича не проверяется. А периодическая синка — как в каталоге, раз в 10 мин.

### Почему это опасно, а не просто «лишняя фича работает»

При выключенной фиче в офлайне одновременно живут два писателя в одни и те же таблицы:

| | Фича ON | Фича OFF |
|---|---|---|
| Стомпы | работают | **работают** (не проверяются) |
| Пул настроек бонусов | брокер через SyncManager | старый `sync_settings()` → `_sync_bonus_settings()` → `Discount.SetBonusSettings` (`sync_settings.py:53,75-82`) |
| Пул видов цен | брокер | старый `PFSync.SyncLoyaltyEntities` (`sync_loyalty.py:47-49`) |

Старый путь и брокерный пишут одни и те же данные разными механизмами и с разными курсорами. Отсюда формулировка в решении — «может запороть данные клиентам».

---

## Решение (звонок 2026-09-09)

Романова Екатерина, 13:07:

> В звонке обсудили: 1. Стомпы без фичи работать не должны. Чиним ошибку в хф34, потому что может запороть данные клиетам. Проверяем только синку по …

До этого в переписке была противоположная версия (12:41: «стомпы должны работать без фичи с 4100, у нас ошибка на то, что без фичи это не работает»). Звонок её отменил. Итог — фичу надо проверять и в стомп-пути.

---

## Исходный симптом не воспроизвёлся

Заявка была про то, что изменения настроек бонусов не прилетают в офлайн мгновенно после правки в онлайне. Ошибку не завели — 2026-09-09 в 13:42 и 13:49 Романова написала, что перепроверили на двух устройствах у себя и у Куимовой, и глобальные настройки бонусов по стомпу завелись. Логи с онлайна (момент сохранения настроек) запрашивались, но не пришли.

То есть разбор ниже — это разведка по коду без подтверждающих логов, а не установленная первопричина.

---

## Слабые места публикации (остаются, тестами не покрыты)

1. **Событие теряется молча.** `_send_to_broker` отправляет только если `isinstance(uuid_, uuid.UUID)` (`core/sync.py:172`); иначе просто `warning_count += 1`. Сверху `@handle_exceptions` — если `sync_broker_sender` не импортнулся, `SYNC_BROKER_SENDER is None`, и весь вызов схлопывается в одно предупреждение без исключения.

2. **Строка в логе врёт.** `log('Отправлено событие в брокер (…)')` стоит в конце `_send_to_broker` **безусловно** — печатается и когда не отправлено ничего. По её наличию нельзя судить, что событие ушло; смотреть надо на соседнее «Информацию по некоторым записям не удалось внести в сервис истории».

3. **UUID настроек бонусов может быть `None`.** Он генерится один раз в `set_bonus_settings.py:53-54` (`uuid7()`), если его ещё нет. Но `commit_sale_point` публикует по `sbis.Bonus.ReadSettings()`, где дефолт — `'UUID': None` (`get_bonus_settings.py:73`). На аккаунте, где настройки бонусов ни разу не сохраняли через диалог, смена списка ТП уйдёт в брокер с `None` и не опубликуется вовсе.

4. **Подписка и отписка — разные перегрузки.** В `on_user_authenticated.py:26-27` `Unsubscribe(channel)` уходит в неадресную версию SDK, а `Subscribe(channel, 'offline', ClientID, UserID)` — в адресную `Subscribe(client_id, user_id, apps, channel)` (`SBISPlatformSDK/bl-modules/Sync Broker Client Py/sync_broker/sync_broker_wrap.py`). Плюс `PFSync.OnUserAuthenticated` навешан и на `desktop.user-authenticated`, и на `.secondary` (`on_event.py:29,36`) — за логин отрабатывает дважды.

5. **Фолбэка по настройкам бонусов больше нет.** Коммит `f3f14e23b3` (27.08.2026) убрал `_sync_bonus_settings` из `broker_sync_loyalty.py`, а старый пул в `sync_settings.py:53` закрыт фичей. При включённой фиче настройки приезжают только брокером — стомпом либо полной синхронизацией на логине.

Ни `_send_to_broker`, ни `bonus_settings_to_broker`, ни `on_user_authenticated` автотестами не покрыты.

---

## Побочная находка

Зашелвленный фикс из [[BonusSettings-Sync-Restart-Bug]] (PullAll → сброс курсора) в `rc-26.5100` фактически присутствует, только в другой форме: `LoyaltySynchronizer.PullAll()` зовёт `re_sync_method()`, а `BonusSettingsSynchronizer.re_sync_method` — `sbis.PFSync.BonusSettingsReSync()` (`broker_sync_loyalty.py`, классы синхронизаторов). Статус `shelved` на той странице стоит проверить.

---

## Провенанс

- Код `price-formation`, ветка `26.5100/bugfix/aatimoshenko/07204334`, чтение 2026-09-09. Номера строк — на это состояние.
- SDK `SBISPlatformSDK_264200`, `bl-modules/Sync Broker Client Py/`.
- Переписка SBIS `theme_id=01a06241-9678-7943-91cd-0dd0a68cd66b` (фича `lty_broker_sync_new3`, 8 сообщений 08–09.09.2026): Романова Е., Куимова Н., Кузаков Ю.
- Переписка SBIS `theme_id=bbe78433-32d8-4352-8cae-b22fa1844ff7` (3 сообщения 09.09.2026): запрос логов и «всё завелось».
- **Оговорка:** MCP-инструмент отдаёт сообщения диалога обрезанными примерно на 150 символах. Цитаты выше — ровно то, что вернул инструмент; хвосты сообщений не читались и здесь не домысливаются.
- Логов ни с онлайна, ни с кассы не было — код-разведка ничем не подтверждена и не опровергнута.
