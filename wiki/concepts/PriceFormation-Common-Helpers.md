---
type: concept
title: "PriceFormation Common — Helpers Overview"
updated: 2026-04-13
tags:
  - price-formation
  - helpers
  - python
status: evergreen
related:
  - "[[PriceFormation-Backend-Architecture]]"
  - "[[Wasaby-Python-Patterns]]"
  - "[[Wasaby-RecordSet-Performance]]"
  - "[[Bonus-Programs-Architecture]]"
  - "[[DiscountCard-Subsystem-Overview]]"
  - "[[Saby-Feature-Toggles-API]]"
  - "[[Wasaby-Data-Types]]"
created: 2026-04-13
---

# PriceFormation Common — Helpers Overview

Shared helper modules at `www/service/Модули/PriceFormation.Common/priceformationcommon/helpers/`.

See also: [[PriceFormation-Backend-Architecture]] for the module map, [[DCCommon-Helpers]] for DCCommon-specific utilities.

---

## Type Conversion (`convert.py`, `money.py`, `common.py`)

**convert.py** — null-safe type conversions:
- `float_equal(value_first, value_second, precision=2)` — float comparison with tolerance
- `to_float(value)` — to float, None if None
- `to_int(value)` — to int, None if None

**money.py** — exact arithmetic for monetary values:
- `to_decimal(value, exp=2, rounding=None)` — Decimal with rounding
- `to_money(value, rounding=ROUND_HALF_EVEN)` — round to 2 decimal places
- Types: `Numeric`, `Money` from `priceformationcommon.core.types`

**common.py**:
- `to_uuid(value: str | UUID | None) -> UUID | None` — safe UUID conversion

---

## Logging & Profiling (`logging.py`)

Configuration:
- `PREFIX = 'loyalty'`, `LOG_LEVEL = sbis.LogLevel.llMINIMAL`
- `RECORD_SIZE = RECORD_SET_SIZE = 100`

Functions:
- `log(message, prefix, log_level, bypass_time_limit)` — log message
- `warning(message, prefix, stack_trace)` — warning with stack trace
- `error(message, prefix, stack_trace)` — error with stack trace
- `log_result()`, `log_variable()`, `log_event()`, `log_value()`, `as_str()` — auxiliary helpers

Decorator:
```python
@logging(label='', full=False, with_profiling=False, silent_errors=False, wo_params=False, wo_result=False)
```

---

## Parameter Validation (`assert_param.py`)

Built-in validators:
- `natural_number(value)` — int > 0
- `natural_number_or_none(value)` — int > 0 or None
- `non_zero_number(value)` — non-zero integer
- `non_negative_number(value)` — numeric >= 0
- `any_number(value)` — float/int/Decimal
- `one_of(options)` — one of allowed values
- `list_of_strings()`, `list_of_natural_numbers()`, `list_of_natural_numbers_or_none()`
- `is_uuid(value)` — UUID
- `dict_of()`, `dict_by_key_of()`, `record_of()`, `list_of()` — complex types

Decorators:
```python
@assert_param(**validators)        # custom error
@assert_param_sbis(**validators)   # raises sbis.Error
```

---

## Date & Time (`date_time.py`)

Formats:
- `SERIALIZED_DATE_FORMAT = '%Y-%m-%d'`
- `SERIALIZED_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'`
- `SERIALIZED_DATETIMETZ_FORMAT = '%Y-%m-%d %H:%M:%S.%f%z'`

Key functions:
- `split_date_time(date_time)` — split into date and time
- `to_midnight()` — shift to midnight
- `serialize_date()` / `deserialize_date()` — date serialization
- `serialize_datetime()` / `deserialize_datetime()` — datetime
- `serialize_datetimetz()` / `deserialize_datetimetz()` — datetime + timezone
- `to_servertz()`, `add_servertz()`, `remove_servertz()` — TZ handling
- `get_client_date_time()` — client local time
- `interval_info()` — human-readable date range
- `min_serialized_date()`, `max_serialized_date()` — extremes from date list
- `get_month_len()`, `get_name_of_month()` — month utilities
- `to_datetimetz_format_str()` — normalize TZ string

---

## Record & Data Structures (`record.py`, `dict_utils.py`, `params.py`)

### record.py — sbis.Record / RecordSet creation

- `create_record_format(format_def, field_name_list, name_format)` — RecordFormat
- `create_record(record_format, default_values, with_own_record_format, skip_missing_fields)` — Record
- `create_record_with_format(record_data)` — from FormattedDataDef
- `get_or_add_field()`, `set_or_create_fields()`, `update_record_fields()` — field manipulation
- `get_filter_conditions()`, `build_record_with_path()` — filter construction
- Types:
  - `FormatDef = List[Tuple[str, sbis.FieldType]]`
  - `FormattedDataDef = List[Tuple[str, sbis.FieldType, Optional[Any]]]`

> [!tip] Performance
> Prefer `rec = rs.AddRow()` (no args) + `rec.Fill({'Field': val})` to eliminate IField churn. See [[Wasaby-RecordSet-Performance]].

### dict_utils.py — dictionary utilities

- `update_dict(base, add)` — shallow merge (recursive for dict values)
- `deepmerge(base, add)` — deep merge without depth limit
- `deepget(base, keys, default, value_type)` — get nested value
- `safe_deepget()` — safe version with default
- `deepset(base, keys, value, del_if_none)` — set nested value
- `deepdel()` — delete nested + clean empty parents
- `deepclean()` — remove empty values
- `deephas()` — check key presence
- `batch_dict(base, batch_size)` — split into batches
- `group_by(iterable, key)` — group by key
- `replace_key()` — rename keys
- `to_json()`, `from_json()` — JSON with Decimal support
- `uuid_to_json()` — UUID → JSON string
- Class `DecimalEncoder(json.JSONEncoder)` — Decimal encoder

### params.py — parameter management

- Class `UserParams(id_)` — user parameters: `get()`, `set()`, `delete()`
- Class `GlobalParams(id_)` — global client parameters: `get()`, `set()`

---

## List Method Utilities (`list_method.py`)

Classes:
- `ListIteratorWrapper` — ListIterator wrapper; callbacks: `result_callback`, `init_callback`, `after_iteration_callback`
- `TreeType(Enum)` — tree display modes
- `Spread(Enum)` — spread modes

Decorators / functions:
- `@entries()` — compute ENTRY_PATH for registries
- `@selection()` — mass selection support
- `@multi_root_navigation()` — multi-section navigation
- `normalize_params()` — normalize list method parameters
- `call_in_batches()` — call in portions (10K limit)
- `call_in_batches_with_cursor()` — batches with cursor navigation
- `get_list_with_iterator()` — get results via ListIterator
- Type `ListMethodType` — callable type for list methods

---

## Sales Point & Location (`sales_point.py`, `location.py`, `source.py`)

### sales_point.py

- `get_sales_point_list(additional_filters, sort, navigation)` — get sale points
- `get_sale_points_by_warehouses(warehouse_list)` — warehouses → sale points
- `get_warehouses_by_sale_points(sale_point_list)` — sale points → warehouses
- `get_default_sale_point(sale_point_list, with_org_name)` — default sale point

### source.py

- `SourceVectorFormat = tuple[int|None, int|None, int|None, int|None]`
- `get_source_id_by_vector(source_vector)` — vector → ID (e.g. "130/250")
- `read_source_hierarchy_up(source_list)` — source hierarchy upward (cloud)

---

## Roles & Rights (`roles.py`, `rights.py`)

### roles.py

- `FULL_ACCESS_LEVEL = 4`
- `get_all_roles_list()` — all roles
- `get_user_roles_list(user)` — user roles
- `check_roles(discount_list)` — check rights on discounts
- Class `Role(id_, name, description)` — role: `get_id()`, `get_name()`, `get_description()`
- SQL: `_SQL_GET_PRICE_ENTITY_ROLES` — roles for price entity types

---

## JSON & String Utilities (`json_wrapper.py`, `str_utils.py`)

### json_wrapper.py

- `UUIDEncoder(json.JSONEncoder)` — UUID → hex string
- Class `JsonWrapper(str_json='')`: `set_value()`, `get_value()`, `get_values()`, `__str__()`, `__eq__()`

### str_utils.py

- `int_as_str(value, hide_zero, no_group_separator)` — integer with separators
- `money_as_str(value, hide_zero, no_group_separator)` — money with 2 decimal places
- `percent_as_str(value, hide_zero, no_group_separator)` — percentages
- `masked_number(value)` — card number mask (last 4 digits)
- `short_person_name(value)` — "Lastname F.O."
- `short_person_name_from_list(value_list)` — from list
- `tuple_for_sql(tpl)` — tuple for SQL query

---

## Nomenclature (`nomenclature.py`)

- `get_nom_name(nom_id_list)` — nomenclature names
- `get_nom_base_unit(nom_id_list)` — base units
- `FilterArchival` — archival filter constants
- `FilterServiceFolder` — service folder filter constants
- `GetNomenclatureListType` — enumeration method type

---

## Advanced Utilities

### wrappers.py

- `@handle_exceptions()` — catch exceptions, log, return None
- `@on_transaction_commit()` — execute after transaction commit
- `run_with_password_and_warning()` — execute only with password
- `async_call_on_commit()` — async call on transaction completion
- `@sql_timeout(seconds=5, default_value=None)` — limit SQL execution time

### lock.py

- `INT_MAX = 2147483647`
- `AdvisoryLockMode` — TRY / WAIT
- Class `AdvisoryLockDecorator(lock_name, lock_id_extractor)` — lock decorator
- `lock_id_getter_factory()` — lock ID getter factory by document type
- `advisory_lock()` — PostgreSQL advisory lock for concurrent access
- `create_loyalty_lock_transaction()` — context manager: lock + transaction

### feature.py

- `Feature` — feature names (ENTITY_SP, REGION_COUNTRY, LOYALTY_IMPROVE, …)
- `check_feature(name, offline_name, with_offline)` — check feature enabled
- `is_feature_on(name)` — check flag

See also: [[Saby-Feature-Toggles-API]] for full feature flag API.

### cloud.py

- `_SALE_CLOUD_OP_TIMEOUT_DEFAULT = 3000` (ms)
- `get_cloud_ep(with_cloud_timeout)` — get cloud endpoint
- `get_sale_cloud_op_timeout()` — configured timeout
- `add_cloud_data_error_messages()`, `get_cloud_data_error_messages()` — cloud error messages
- `@cloud_call()` — decorator for cloud method calls

### franchise.py

- `FRANCHISE_CONFIGURATION = 'bcd58727-5adf-40cf-b441-23cd57b9df54'`
- `FranchiseRole` — OWNER=1, FRANCHISEE=2
- `get_account_owned_franchise_ids()` — franchises where account is owner
- `is_current_account_franchise_owner()` — check owner role
- `get_owner_account_id(franchise_uuid)` — online account ID of owner
- `get_account_franchise()` — role + UUID of current franchise

### environment.py

- `is_test_environment()` — test/pre/pre-test environment?

---

## Price Configuration (`price/core/settings.py`, `price/core/rounding.py`)

### settings.py

- `RoundingSettings(type, thresholds, auto_pl)` — rounding config namedtuple
- Class `PriceSettings`:
  - `ROUNDING_UP=0`, `ROUNDING_DOWN=1`, `ROUNDING_ARITHMETIC=2`, `ROUNDING_NULL=3`
  - `get()`, `_get_rounding()`
- `get_price_settings()` — load from global params
- `UnitType`, `PaymentType` — enumerations

### rounding.py

- `rounding(prices, rounding_settings)` — apply rounding to price list
- `_round_price(price, threshold_list)` — round one price
- `_get_round_value(price, threshold_list)` — determine rounding step
- Mapping: UP→ROUND_UP, DOWN→ROUND_DOWN, ARITHMETIC→ROUND_HALF_UP

---

## Related Pages

- [[PriceFormation-Backend-Architecture]] — module map showing where helpers/ sits
- [[DCCommon-Helpers]] — DCCommon-specific helpers (barcode, encryption, bonus balance)
- [[Wasaby-Python-Patterns]] — sbis.Error/Warning, CreateTransaction patterns
- [[Wasaby-RecordSet-Performance]] — Record/RecordSet optimization patterns
- [[Wasaby-Data-Types]] — FieldType enum, Decimal/Money vs double
- [[Saby-Feature-Toggles-API]] — full Feature flag API
- [[Bonus-Programs-Architecture]] — bonus balance calculation context
- [[DiscountCard-Subsystem-Overview]] — discount card context for barcode/encryption usage