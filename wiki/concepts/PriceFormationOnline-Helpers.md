---
type: concept
title: "PriceFormationOnline — Helpers"
tags: [price-formation, helpers, python, online]
status: evergreen
related:
  - "[[PriceFormation-Common-Helpers]]"
  - "[[PriceFormation-Backend-Architecture]]"
  - "[[Wasaby-Python-Patterns]]"
  - "[[Loyalty-Sale-Application]]"
  - "[[LRS-Long-Request-Service]]"
created: 2026-04-10
updated: 2026-04-10
---

# PriceFormationOnline — Helpers

Хелперы специфичные для онлайн-модуля: `www/service/Модули/PriceFormation.Online/priceformationonline/helpers/`

## Context & State Management

### `context_storage.py` — контекстное хранилище (автор: Голубь Ф.С.)

Хранение данных привязанное к контексту исполнения (ContextVar). Поддерживает вложенные контекстные менеджеры.

**`StorageObject[T]` (dataclass)**:
- `context_depth: int` — уровень вложенности
- `context_data: T` — хранимые данные

**`ContextStorage[T]` (Generic, context manager)**:
- `_context_var: ClassVar[ContextVar[StorageObject] | None] = None`
- `set_data(value: T)` — установить значение
- `__enter__` / `__exit__` — поддержка `with`-блока
- `_get_raw_data() -> T` — внутренний геттер
- Sentinel: `_EMPTY_CONTEXT = object()`

### `warning_context.py` — агрегация ConfirmWarning (автор: Голубь Ф.С.)

Контекстный менеджер для накопления `ConfirmWarning`-исключений: перехватывает их внутри блока, агрегирует и выбрасывает при выходе из внешнего контекста.

**`ConfirmWarningStorageObject` (dataclass)**:
- `warnings: dict[int, list[ConfirmWarning]]` — по коду ошибки
- `force_codes: set[int]` — коды, которые игнорировать
- `add_warning(warning)` — добавить

**`ReadOnlyConfirmWarningStorageObject` (dataclass)**:
- `warnings: MappingProxyType[int, list[ConfirmWarning]]`
- `force_codes: frozenset[int]`

**`ConfirmWarningContext(ContextStorage)`**:
- `__init__(force_codes: list[int] | None = None)`
- `has_warnings: bool` — есть накопленные?
- `force_warning_check()` — явно проверить и выбросить
- `try_add_warning(warning)` — добавить в контекст
- `get_data() -> ReadOnlyConfirmWarningStorageObject`
- `_aggregate_warnings() -> ConfirmWarning` — агрегация с приоритетом
- `_IS_AGGREGATED_KEY = '_is_aggregated'`
- Зависит от: `ConfirmWarningCode`, `ConfirmWarning`, `context_storage`

---

## Licensing (`license.py`)

Управление лицензиями лояльности и привязка к торговым точкам.

**Константы**:
- `MAIN_LICENSE_ID = 'LOYALTY_PROGRAM'`
- `SALE_POINT_LICENSE_ID = 'DISCOUNTS_PS'`
- `SALE_POINT_LICENSE_BALANCE_ID = 'DISCOUNTS_PS_BALANCE'`
- `LICENSE_WARNING_CODE = 64002`
- `ALL_SALE_POINTS_WARNING_CODE = 64003`

**`SalePointLicenseState` (NamedTuple)**:
- `active_list: List[int]` — ТП с активной лицензией
- `unlicensed_list: List[int]` — ТП без лицензии
- `on_credit_list: List[int]` — ТП с лицензией в кредит

**`SalePointLicenseRestrictionInfo` (NamedTuple)**:
- `is_available: bool` — можно продолжать?
- `restriction_config: Optional[dict]` — конфиг окна
- `display_restriction_config: Optional[dict]` — что показать пользователю

**`LicenseCheckResult`** — Record с полями: `IsAvailable`, `RestrictionConfig`, `DisplayRestrictionConfig`, `UnlicensedSalePointIdList`, `OnCreditSalePointIdList`, `IsAllSalePoints`, `Reason`

**Функции**:
- `get_sale_point_license_state(sale_point_id_list)` → `SalePointLicenseState` — `sbis.License.CheckByConsumers`
- `get_sale_point_license_restriction_info(unlicensed_count, on_credit_count)` → UI-конфиг
- `bind_sale_point_license(sale_point_id_list, reason)` — привязать лицензию (свободную или в кредит)
- `raise_license_error(restriction_config)` — выбросить `sbis.Warning`
- `check_sale_point_license(sale_point_id_list=None) -> LicenseCheckResult` — проверить лицензию; демо-аккаунты обрабатываются отдельно
- `process_sale_point_license_check_result(check_result, ignore_warning_code_list)` — обработать результат (привязка / варнинг)
- `unbind_sale_point_license(sale_point_id_list)` — отвязать (только тестовые среды)

---

## Business Groups (`business_group.py`)

Работа с бизнес-группами (франшизы, группы вендоров).

**Константы**: `ROOT_FOLDER_ATTRIBUTE_NAME = 'AgentGroupFolder'`

**`MemberStatus`**: `ACCEPTED=1`, `SENT=2`, `DECLINED=3`
**`BusinessGroupRole`**: `VENDOR=1`, `AGENT=2`

**`BusinessGroupFolder` (ABC)**:
- `root_folder_id: int | None`
- `TABLE_NAME: str`
- `get_folder_list(group_class, group_id_list)` → `sbis.RecordSet`
- `get_folder_by_id(group_class, entity_id)` → `sbis.Record | None`
- `create_folder(group, group_role, group_name)` → `sbis.Record` (abstract)

Конкретные реализации:
- **`PriceEntityBusinessGroupFolder`** — `TABLE_NAME = 'ВидЦены'`
- **`CardTypeBusinessGroupFolder`** — `TABLE_NAME = 'ВидКарты'`

**`BusinessGroup` (ABC)**:
- Свойства: `id`, `type`, `name`, `role`, `folder_id`
- `get_by_folder_id(folder_id)` → `Self | None`
- `get_member_list(member_contractor_id, member_account_id, invite_status)` → `sbis.RecordSet`
- `get_member_contractor(member_client_id)` → `tuple[int|None, str]`
- `get_client_id_by_contractor(contractor_id)` → `int | None`
- `get_list(group_id_list)` → `list[Self]`
- `create(group_id, group_role, group_name)` → `Self`
- `get_user_role()` → `tuple[UUID, str] | None`
- `TYPE: UUID`, `FOLDER_CLASS: BusinessGroupFolder`, `FOLDER_ATTRIBUTE_NAME: str`
- `_CONTRACT_OBJECT = sbis.AgentContract`

**`Socnet`** (helper):
- `get_group_name(group_id)`, `get_group_type(group_id)`, `get_group_owner_client_id(group_id)`

---

## Sale Points (`sale_point.py`)

- `get_sale_point_list(is_online_call, only_in_spp, sale_point_id_list, include_additional)` → `sbis.RecordSet` (поля: Company, Name, NormName; `SalesPoint.ListFull`, страницы по 100)
- `get_sale_point_id_list(include_additional, sale_point_id_list, only_in_spp)` → `List[int]`
- `get_spp_id_by_sale_point(sale_point_id_list)` → `Dict[int, int]`
- `get_spp_uuid_by_sale_point(sale_point_id_list)` → `Dict[int, int]`
- `get_sale_point_items(sale_point_id_list, max_items)`:
  - `Feature.ENTITY_SP` включён → `OurOrg.listWithBranches` (составные ключи)
  - Иначе → `PriceFormation.SalesPointTree`

---

## Nomenclature (`nomenclature.py`, автор: Литвинцева М.А.)

- `get_preload_nomenclature_info(nom_id_list, additional_fields, additional_filters, sort, navigation, method_type)`:
  - Авто-добавляет поля: `Name`, `ServiceFolder`, `Deleted`
  - Фильтрует по `Archival=2` (не архив)
  - Делегирует в `priceformationcommon.helpers.nomenclature.get_nomenclature_list`

---

## External Services

### `marketing.py` — интеграция с CRM / маркетинг-сервисом

**`SourceType`**: `REFERRAL_PROGRAM=70`, `REFERRAL_CODE=71`
**`SourceStatus`**: `PUBLISHED=1`, `UNPUBLISHED=2`, `UNDER_MODERATION=3`, `FAILED_MODERATION=4`, `DELETED=5`, `MIXED=0`
**`SiteType`**: EXT_SITE=0, SITE_BUILDER=1, SABYGET_RU=2, N_SBIS_RU=3, SURVEY=4, MENU=5, DELIVERY=6, WEBINAR=7, FEEDBACK=8, ONLINE_DEMO=9, WIDGET_IFRAME=10, SABYSERVICE=11, YANDEX_METRIKA=21

Функции:
- `get_or_create_source(name, status, type_id, description, parent_uuid, ext_id, access_data_guid, access_data_client_id, url)` → `dict` с `@AdObject` и `AdObjectUUID`
- `delete_source_by_ext_id(ext_ids, type_ids)`
- `get_source_by_ext_id(ext_ids, type_ids)` → `sbis.RecordSet`
- `add_ad_objects_to_referral_code(referral_program_ad_object, ad_objects)` → `bool`
- `get_site_list_without_stats(site_types, site_ids)` → RecordSet (SiteId, SiteUrl)
- `get_sales_sources_stats(type_name, places, date_begin, date_end)` → RecordSet (Place, AdObject, Qty, Sum, Positive, PositiveSum)
- `get_sales_sources_lead_info(lead_id, agent_group_id)` → `sbis.Record`
- `get_source_detail(date_from, date_to, client, site_id, redirect_source, redirect_source_by_site)` → RecordSet (RedirectSource, UniqCust, UniqCustLead, AvgTime) — `ConsumerStats.GetSourceDetail/4`

### `url.py` — короткие URL и CDN (автор: Михайленко Е.А.)

- `get_short_urls(url_list, without_expiration)` → `Optional[List[str]]` — url-shortener сервис
- `_get_short_link_create_params(url_list, without_expiration, name)` → RecordSet/Record
- `update_short_url(short_url, new_original_url)` — обновить (ShortLink.Update возвращает None всегда)
- `delete_short_url(short_url_list, original_url_list)` — удалить по короткому или оригинальному
- `get_original_url(short_url)` → `str | None`
- `restore_short_url(short_url, original_url, skip_check)` — восстановить удалённый
- `get_url_at_online_host(url)` → URL на online.sbis.ru
- `get_relative_cdn_url(url)` → `Optional[str]` — относительный путь CDN-ресурса
- Примечание: `.` исключена из паттерна коротких ссылок (проблемы с мессенджером)

### `lrs.py` — Long Request Service (автор: Постнов С.А.)

**`LongRequestHandler`**:
- `__init__(request_name, request_description, task_description, task_method, show_result=True, auto_close_on_end=False)`
- `run(*params)` — запустить долгую операцию
- `commit_task(request, task)` — зафиксировать задачу в LRS
- `create_task()` — создать задачу с настройками

### `events.py` — события лояльности (автор: Литвинцева М.А.)

- `send_event_loyalty_changed(**id_lists)` — событие об изменении программ лояльности
  - Параметры: `promotion_list`, `promo_code_list`, `discount_card_list`
  - Публикует: `online.loyalty-system.{loyalty_name}.update`
  - Маппинг: promotion_list→promotion, promo_code_list→promo-code, discount_card_list→card-type

---

## UI & Media

### `color.py` — цветовые утилиты

**`RGBA` (dataclass)**: `red`, `green`, `blue`, `alpha` (0-255)
**`HSLA` (dataclass)**: `hue`, `sat`, `light`, `alpha`

Функции:
- `get_color_with_opacity(hex_color, opacity=100)` → hex с прозрачностью
- `get_gradient(hex_color_1, hex_color_2, angle, boundary, opacity=100)` → CSS linear-gradient
- `hex_to_rgb(rgb_hex)` → `Tuple[int, int, int]`
- `hex_to_rgba(rgb_hex)` → `RGBA`
- `rgba_to_hsla(rgba)` → `HSLA`
- `hex_to_hsla(rgb_hex)` → `HSLA`
- `color_is_dark(hex_color)` → `bool` — по формуле яркости
- `change_color_brightness(hex_color, factor)` → hex с изменённой яркостью
- `remove_transparency_and_gradient(color)` → первый цвет из градиента
- `_round_math(value, ndigits)` — математическое округление (совместимость с JS)

### `image.py` — изображения и превью (автор: Михайленко Е.А.)

- `resize_image(url, target_size, method='m', result_type='')` → `sbis.RpcFile | str`
  - Путь: `/previewer/{method}/{size_path}{path}`
- `get_file_by_url(url, service_address)` → `sbis.RpcFile`
  - Заголовки: `X-SBISSessionID`, `X-Uniq-ID`
