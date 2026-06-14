---
type: concept
title: "Wasaby Data Types"
updated: 2026-04-10
tags:
  - concept
  - wasaby
  - database
  - sbis
  - types
status: current
related:
  - "[[Wasaby-DB-Access-Patterns]]"
  - "[[Wasaby-Framework]]"
  - "[[Wasaby-RecordSet-Join]]"
created: 2026-04-10
---

# Wasaby Data Types

Reference for the Wasaby platform type system: FieldType enum, temporal types, Decimal/Money, and JSON/HashTable. Covers PostgreSQL, C++, Python, and JavaScript representations.

---

## FieldType Enum (Record Field Types)

Complete reference for `FieldType` values used in `Record` and `RecordSet` field definitions.

### Scalar Types

| Name | FieldType | Description | Notes |
|------|-----------|-------------|-------|
| Int16 | `ftINT16` | Integer [−32 768, 32 767] | Stored internally as Int64 |
| Int32 | `ftINT32` | Integer [−2 147 483 648, 2 147 483 647] | Stored internally as Int64 |
| Int64 | `ftINT64` | Integer [−2^64, 2^64−1] | |
| Float | `ftFLOAT` | Single-precision float | Stored as double |
| Double | `ftDOUBLE` | Double-precision float | |
| Decimal | `ftDECIMAL` | Fixed-precision decimal (alias: `ftMONEY`) | libgmp; up to 1000 digits. Options: precision (default 2), large-decimal flag |
| Text | `ftTEXT` | String | |
| Boolean | `ftBOOLEAN` | Boolean (true/false) | |
| UUID | `ftUUID` | Universally unique identifier | Auto-generates random UUID when no value set |
| XML | `ftXML` | XML data | Identical to ftSTRING; deprecated for new code |
| Binary | `ftBINARY` | Binary data stored directly in field | |
| BLOB | `ftBLOB` | Binary data accessed via `IBlob` interface | Not stored directly |

### Temporal Types

| Name | FieldType | Description | Notes |
|------|-----------|-------------|-------|
| Date | `ftDATE` | Date `'dd.mm.yyyy'` | Defaults to current date when no value |
| Time | `ftTIME` | Time of day `'hh:mm:ss.μs'` | Defaults to current time when no value |
| DateTime | `ftDATETIME` | Absolute timestamp | Options: default-now flag, without-timezone flag. See [[#Temporal Types]] |
| TimeInterval | `ftTIMEINTERVAL` | Duration without fixed start/end | E.g., "3 days 7 hours" |

### Compound Types

| Name | FieldType | Description | Notes |
|------|-----------|-------------|-------|
| Enum | `ftENUM` | Number from a limited set | Dictionary defines allowed values + labels |
| Flags | `ftFLAGS` | Up to 32 boolean flags (true/false/unset) | Dictionary maps flag indices 0–31 to labels; gaps allowed |
| Identifier | `ftIDENTIFIER` | (ObjectType: string, ObjectId: Int64) pair | ObjectType may be empty |
| Link | `ftLINK_N_TO_1` | FK reference to another DB table | Stored as Int64; linked table name in format options |
| Record | `ftRECORD` | Nested Record | Different rows in a RecordSet may hold differently-formatted nested Records |
| RecordSet | `ftRECORDSET` | Nested RecordSet | Different rows may hold differently-formatted nested RecordSets |
| HashTable | `ftHASH_TABLE` | JSON as parsed DOM tree | See [[#JSON / HashTable Type]] |
| File | `ftRPC_FILE` | RpcFile object | |

### Array Types

All array types hold variable-length arrays; any element may be NULL.

| FieldType | Element Type |
|-----------|-------------|
| `ftARRAY_INT16` | Int16 |
| `ftARRAY_INT32` | Int32 |
| `ftARRAY_INT64` | Int64 |
| `ftARRAY_FLOAT` | Float |
| `ftARRAY_DOUBLE` | Double |
| `ftARRAY_DECIMAL` | Decimal (options: precision, large-decimal flag) |
| `ftARRAY_TEXT` | String |
| `ftARRAY_BOOLEAN` | Boolean |
| `ftARRAY_DATE` | Date |
| `ftARRAY_TIME` | Time |
| `ftARRAY_DATETIME` | DateTime (option: without-timezone flag) |
| `ftARRAY_TIMEINTERVAL` | TimeInterval |
| `ftARRAY_UUID` | UUID |

### Bridge Types (Python)

Used for organizing the C++/Python "bridge" pattern in list methods.

| FieldType | Holds |
|-----------|-------|
| `ftSORTING` | `SortingList` — sort request for list methods |
| `ftNAVIGATION` | `Navigation` — pagination/cursor request |
| `ftNAVIGATION_RESULT` | `NavigationResult` — pagination metadata (has-more, next cursor) |

---

## Temporal Types

The platform defines four temporal types. All are timezone-unaware except `DateTime with timezone`.

### Date

Calendar date without timezone.

| Layer | Type |
|-------|------|
| PostgreSQL | `date` |
| C++ | `sbis::Date` |
| Python | `datetime.date` |

> [!note] Year range
> C++ implementation supports years 1400–10000 only.

### Time

Point in day (00:00:00.000000 – 23:59:59.999999), microsecond precision. No timezone.

| Layer | Type |
|-------|------|
| PostgreSQL | `time without time zone` |
| C++ | `sbis::Time` |
| Python | `datetime.time` |

### TimeInterval

Duration without fixed start/end (e.g., "2 days, 3 hours"). Only unambiguously computable intervals are used.

| Layer | Type |
|-------|------|
| PostgreSQL | `interval` |
| C++ | `sbis::TimeInterval` |
| Python | `datetime.timedelta` |

### DateTime — With Timezone

Use when exact event time matters (sales, report submissions). Stored as UTC in DB.

| Layer | Type | Detail |
|-------|------|--------|
| PostgreSQL | `timestamp with time zone` | Stored as UTC+0 |
| C++ | `sbis::DateTime` | Converted to app-server timezone on read |
| Python | `datetime.datetime` | Converted to app-server timezone on read |
| JS client | ISO 8601 with offset | Converted to browser timezone on deserialization |

**Example:** Client in Vladivostok (UTC+10) submits a report at 09:12:07 local.
- DB stores: `2016-05-20 23:12:07 UTC+0`
- App server in Tashkent (UTC+5) reads: `2016-05-21 04:12:07` (no TZ suffix — it's always the server's known zone)
- Browser in Vladivostok sees: `2016-05-21T09:12:07.000+1000`

> [!key-insight] The absolute moment never changes — only the representation shifts per layer.

### DateTime — Without Timezone

No conversions at any layer. The value is stored and returned as-is.

| Layer | Type |
|-------|------|
| PostgreSQL | `timestamp without time zone` |
| C++ | `sbis::DateTime` |
| Python | `datetime.datetime` |

```python
r = Record()
r.AppendField('DateTimeWithoutTimezone', FieldType.ftDATETIME, FormatOptions.foWITHOUT_TIMEZONE)
```

---

## Decimal / Money Type

Fixed-precision decimal number. Use for financial data and any value requiring exact decimal representation.

> [!note] Money = Decimal
> `Money` is an alias for `Decimal`, kept for backwards compatibility. They are identical.

### Platform Representations

| Layer | Type |
|-------|------|
| PostgreSQL | `numeric` |
| SQLite | Stored as string |
| Python | `decimal.Decimal` |
| C++ | `sbis::Decimal` (via libgmp) |

### Decimal vs Double

| Parameter | double | Decimal |
|-----------|--------|---------|
| Storage | Binary floating point (IEEE 754) | Integer + decimal scale factor |
| Exact decimal representation | No (0.3 ≈ 0.2999…) | Yes |
| Max significant digits | ~15 | Unlimited (C++: memory; PG: 131072 integer, 16383 fractional) |
| Fractional digits | Variable/uncontrolled | Fixed by precision setting |
| Direct equality comparison | Unsafe | Safe |
| Speed | Fast (hardware FPU) | Slow (software, heap allocation) |
| Special values | −0, NaN, ±∞ | NaN (except C++ where invalid ops throw) |

> [!key-insight] Never use `double` for financial calculations. Use `Decimal`.

### Precision

- `precision > 0` — fixed digits after decimal; values are rounded HALF-UP.
- `precision = 0` — no fractional part.
- `precision < 0` — auto-precision (unlimited, grows as needed during arithmetic).

### Serialization

By default, `Decimal` serializes as `double` in RPC calls — which loses precision for large values (> 15 digits). Use the **Large decimal** flag to serialize as string instead.

### Python API

Special methods for `Large decimal` variant:

| Class | Method |
|-------|--------|
| `RecordFormat`, `Record` | `AddBigMoney`, `AddArrayBigMoney` |
| `RecordSet` | `AddColBigMoney`, `AddColArrayBigMoney` |

### C++ Usage Examples

```cpp
// Fixed precision 5
Decimal d(static_cast<Decimal::DecimalPrecision>(5));
// From string, precision 2 (default)
Decimal d1(L"123.456E-10");
// From double, auto-precision
Decimal d7(3.14159f, Decimal::AutoPrecision);

// Arithmetic: result precision = max(a.prec, b.prec)
Decimal a(L"1"_sv, 3), b(2., 4);
auto c = a + b;  // precision 4

// Precision is irreversible
d.SetPrecision(3);  // rounds to 3 digits
d.SetPrecision(6);  // pads, but 3-digit rounding already applied
```

---

## JSON / HashTable Type

Corresponds to `ftHASH_TABLE` in FieldType. A hash table (key→value map) stored as a parsed JSON DOM.

### Platform Representations

| Layer | Type |
|-------|------|
| PostgreSQL | `jsonb` (supported since PG 9.4+) |
| C++ | `AnyValue` (wraps: `nullptr`, `bool`, `int`, `String`, `MixedArray`, `HashTable`) |
| Python | `str` |
| JavaScript | `{}` — keys translate to native JS types |

### C++ Types

- **`AnyValue`** — polymorphic value container (`IS_NULL`, `IS_BOOL`, `IS_INT`, `IS_FLOAT`, `IS_TEXT`, `IS_OBJECT`, `IS_ARRAY`).
- **`HashTable`** — associative array. Constructed with `HashKey(L"key") = value` syntax. Throws `HashKeyNotFoundException` for missing keys.
- **`MixedArray`** — indexed array of AnyValue.

```cpp
HashTable ht(HashKey(L"a") = 123, HashKey(L"b") = L"asd");
ht[L"a"];  // 123
ht[L"c"];  // throws HashKeyNotFoundException

MixedArray arr(1, 2, HashTable(HashKey(L"key") = L"val"));
arr[2][L"key"];  // "val"
```

### JavaScript / Frontend

For frontend interaction with hash-table fields, use:
- `Types/entity:Record` — wraps data as a table row.
- `Types/entity/adapter/Sbis` — adapter for SBIS-JSON format (serialized RecordSet/Record from business logic).

```js
var rec = new Record({ format: {foo: 'object'}, adapter: new Adapter() });
rec.set('foo', {bar: 'baz'});
```

---

## Cross-References

- See [[Wasaby-DB-Access-Patterns]] for how types flow through queries.
- See [[Wasaby-RecordSet-Join]] for joining RecordSets using typed fields.
- See [[Loyalty-Database-Schema]] for real-world usage of these types in SBIS loyalty DB.
