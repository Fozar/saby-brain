---
type: concept
title: "Wasaby DB Access Patterns"
updated: 2026-04-10
tags:
  - concept
  - wasaby
  - database
  - sbis
  - postgresql
status: current
related:
  - "[[Wasaby-Framework]]"
  - "[[Multitenancy-Architecture]]"
  - "[[Python-Code-Standards-SBIS]]"
created: 2026-04-10
---

# Wasaby DB Access Patterns

Platform-level database access for C++ and Python on Wasaby backend. Five distinct patterns.

---

## 1. Synchronous Queries

### IStatement (Low-level)

```python
# Python
stmt = sbis.GetConnectedDatabase().CreateStatement()
stmt.SetParam(1, "Ivan")
result = stmt.Exec('select * from "Пользователь" where "Логин" = $1')
```

- Parameters are **positional** (start from 1), not named.
- `ClearParams()` resets all params.
- Returns `ICursor` or null (for DML).
- Can pass a `RecordFormat` to coerce result types (needed for platform types like Перечисляемое).
- Can pass `StopToken` to cancel on demand.

> [!key-insight] SQLite quirk
> For INSERT/UPDATE/DELETE on SQLite, you must iterate the cursor with `Next()` until null — otherwise the query is never actually executed.

### SqlQuery (High-level)

```python
res = SqlQuery('select * from "Пользователь" where "Логин" = $1', "Ivan")
# With specific DB:
res = SqlQuery(GetConnectedDatabase("users"), 'select * from ...', "Ivan")
```

One-liner API. Returns `RecordSet`. Accepts optional `IDatabase`, `RecordFormat`, and `StopToken`.

---

## 2. Asynchronous Queries

```python
# Python — must use `with` for RAII
with statement.AsyncQuery('SELECT ... FROM ...') as async_result:
    cursor = async_result.Next()
```

```cpp
// C++
auto async_result = statement->AsyncQuery(L"SELECT ...");
```

### Wait patterns

| Method | Behavior |
|--------|----------|
| `Wait()` | Block until ready (no timeout) |
| `WaitFor(duration)` | Returns false if timeout exceeded |
| `WaitUntil(deadline)` | Returns false if deadline passed |
| `WaitForAll(...)` | Wait for all results in a range |
| `WaitForAny(...)` | Wait for first ready result |
| Python: `sbis.WaitForAllQueries([...])` | All results |
| Python: `sbis.WaitForAnyQuery([...])` | First ready cursor |

### Key constraints

- **One active async query per connection** — attempting a second query blocks (deadlock risk).
- **Never save IAsyncQueryResult beyond the BL method scope** — may block another method using the same connection from the DB manager.
- **Python**: always wrap in `with` (RAII on GC is unreliable).
- **Async returns all multi-statement results** (unlike sync which returns only the last).
- **Cancel()** is best-effort — server may already be done.
- Supported only for **PostgreSQL** (since platform v21.2000).

---

## 3. LISTEN/NOTIFY (PostgreSQL Pub/Sub)

PostgreSQL built-in message bus. ACID-transactional delivery. Max message body: 8000 chars.

### Sending

```python
SqlQuery('NOTIFY my_channel, $1', notify_message)
# Or use pg_notify for dynamic channel names:
stmt.Exec("select pg_notify($1, $2)")
```

### Subscribing (Python)

```python
with sbis.GetConnectedDatabase().Listen(channel_name) as listener:
    notify = listener.Next()                                   # wait forever
    notify = listener.Next(timedelta(milliseconds=100))        # wait up to 100ms
    notify = listener.Next(datetime.now() + timedelta(...))    # wait until deadline
    if notify:
        sbis.LogMsg(notify.Message())
```

### INotify methods

| C++ | Python | Returns |
|-----|--------|---------|
| `ChannelName()` | `Channel()` | Channel name |
| `Message()` | `Message()` | Message body (may be empty) |
| `ProcessId()` | `Pid()` | Server process ID |

### Constraints

- **One subscriber per channel per connection.** Duplicate `Listen()` on same channel → exception until previous `INotifyListener` is freed.
- Local queue limit: `MAX_PENDING_NOTIFIES = 50`. Older messages are dropped on overflow.
- Subscription lifetime: `Listen()` → `UNLISTEN` or connection close.

---

## 4. Bulk Operations (ITableCopier)

Copies large volumes of data in one operation. Supports **PostgreSQL** and **SQLite** (with restrictions).

```python
copier = sbis.CreateTableCopier(fmt)
```

| Method | Direction | Notes |
|--------|-----------|-------|
| `Get(output, options, filter?)` | DB → stream | Full table or filtered |
| `GetByQuery(query, cb, options)` | DB → callback chunks | SELECT-based |
| `Put(input, options)` | stream → DB | Opens/closes session automatically |
| `AddRecord()` + `Flush()` | record → DB | Buffered insert |
| `operator<<` (C++) | value → DB | Field-by-field streaming |

**Formats:** `TableCopyFormat.Text`, `TableCopyFormat.Binary`, `TableCopyFormat.CSV`

> [!key-insight] SQLite restriction
> `Get`, `GetByQuery`, `Put` are NOT supported for SQLite. Use `AddRecord` + `Flush` or `operator<<`.

`SetCopyInMode(TableCopyInMode::InsertOrReplace)` — upsert mode for C++.

---

## 5. SQL Templates

System for parameterized, conditional SQL queries stored as text. Avoids SQL injection risk.

### Core classes

| Class | Purpose |
|-------|---------|
| `Template` | Parse once, reuse many times (thread-safe after parse) |
| `TemplateExecutor` | Holds a Template ref + bound params |
| `QueryStorage` | Module-relative template files, shared settings, caching |

### Named parameters

```sql
-- Default prefix: !
SELECT * FROM "Клиент" WHERE "@Клиент" = !account AND "Имя" = !name
-- Double prefix to escape: !! → !
```

Custom prefix via preamble: `--meta prefix=@`

### Conditional constructs

| Construct | Condition |
|-----------|-----------|
| `{% ifdef param %}...{% endif %}` | param is set |
| `{% ifnotnull param %}...{% endif %}` | param is set and not NULL |
| `{% ifndef param %}...{% endif %}` | param is not set |
| `{% ifnull param %}...{% endif %}` | param is NULL |
| `{% iftrue param %}` / `{% iffalse param %}` | boolean value |
| `{% = param %}` | `=!param` or `IS NULL` (NULL-aware equality) |
| `{% ifequal param "literal" %}` | equality to string literal |

### Lists

| Shorthand | Equivalent |
|-----------|------------|
| `{% where all %}` | `begin="where(" sep=")and(" end=")"` |
| `{% where any %}` | `begin="where(" sep=")or(" end=")"` |
| `{% set %}` | `begin=set sep=,` |
| `{% group all/any %}` | grouped condition block |

```sql
{% where all %}
{% item ifnotnull partner %}
  kkt."Partner" = !partner
{% enditem %}
{% item ifnotnull region %}
  kkt."Region" = !region
{% enditem %}
{% endwhere %}
```

### QueryStorage

```python
storage = sbis.QueryStorage('ModuleName', 'sql/subdir')
result = storage.Query('query_name', param1=val1, param2=val2)
```

- Loads `.sql` files relative to module root.
- Caches parsed `Template` objects — no re-parsing.
- Shared static params and prefix settings for the whole group.

> [!key-insight] Performance rule
> Always cache `Template` objects in **static** class/function attributes. Parsing is expensive; parsing the same template on every call is a bug.

### Python API functions

- `QueryByTemplate(tmpl, params...)` → RecordSet
- `QueryRecordByTemplate` → single Record
- `QueryRowByTemplate` → single Row
- `QueryScalarByTemplate` → single value

### Nested templates

`TemplateExecutor` can be passed as a parameter to another `TemplateExecutor`. Executed lazily on substitution. Copied on pass — safe to reuse with different params.
