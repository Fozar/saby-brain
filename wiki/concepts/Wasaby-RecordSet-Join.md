---
type: concept
title: "Wasaby RecordSet Join"
updated: 2026-04-10
tags:
  - concept
  - wasaby
  - database
  - sbis
status: current
related:
  - "[[Wasaby-DB-Access-Patterns]]"
  - "[[Wasaby-Data-Types]]"
  - "[[Wasaby-Framework]]"
created: 2026-04-10
---

# Wasaby RecordSet Join

In-memory join of multiple `RecordSet` objects using the `Query` fluent API. Supports INNER, LEFT, and RIGHT joins, field selection, and field aliasing — mirroring SQL semantics without a DB round-trip.

Available in both C++ and Python.

---

## Query API

```cpp
// C++
class Query {
    Query& On(std::map<String, String> const& key_map);      // join condition: left_field → right_field
    Query& FromLeft(Vector<JKey>::type const& keys);          // select fields from left set
    Query& FromRight(Vector<JKey>::type const& keys);         // select fields from right set
    Query& InnerJoin(RecordSet const& left, RecordSet const& right);
    Query& LeftJoin (RecordSet const& left, RecordSet const& right);
    Query& RightJoin(RecordSet const& left, RecordSet const& right);
    // Cascade: join result with another set
    Query& InnerJoin(RecordSet const& other);
    Query& LeftJoin (RecordSet const& other);
    Query& RightJoin(RecordSet const& other);
    RecordSet Select();   // execute and return result
};

class JKey {
    JKey(String field);                    // include field as-is
    JKey(String origin, String renamed);   // include field, rename in result
};
```

```python
# Python equivalents
Query().On({"A": "B"}).InnerJoin(left, right).Select()
Query().On({"A": "B"}).FromRight(["D"]).InnerJoin(left, right).Select()
Query().On({"A": "B"}).FromRight([sbis.JKey("D", "E")]).InnerJoin(left, right).Select()
```

---

## Default Behavior

If neither `FromLeft()` nor `FromRight()` is called, **all fields from both sets** appear in the result.

---

## InnerJoin

Returns only rows with matching keys in both sets.

```cpp
// C++ — all fields
Query().On({ { L"A", L"B" } }).InnerJoin(left, right).Select()
// Python
Query().On({"A": "B"}).InnerJoin(left, right).Select()
```

**Select one field from right set:**
```cpp
Query().On({ { L"A", L"B" } }).FromRight({ { L"D" } }).InnerJoin(left, right).Select()
Query().On({"A": "B"}).FromRight(["D"]).InnerJoin(left, right).Select()
```

**Select field with rename:**
```cpp
Query().On({ { L"A", L"B" } }).FromRight({ { L"D", L"E" } }).InnerJoin(left, right).Select()
Query().On({"A": "B"}).FromRight([sbis.JKey("D", "E")]).InnerJoin(left, right).Select()
```

---

## LeftJoin

Returns all rows from the left set; right-side fields are NULL when no match.

```cpp
Query().On({ { L"A", L"B" } }).LeftJoin(left, right).Select()
Query().On({"A": "B"}).LeftJoin(left, right).Select()
```

**Select field from right with rename:**
```cpp
Query().On({ { L"A", L"B" } }).FromRight({ { L"B", L"E" } }).LeftJoin(left, right).Select()
Query().On({"A": "B"}).FromRight([sbis.JKey("B", "E")]).LeftJoin(left, right).Select()
```

---

## RightJoin

Returns all rows from the right set; left-side fields are NULL when no match.

```cpp
Query().On({ { L"A", L"B" } }).RightJoin(left, right).Select()
Query().On({"A": "B"}).RightJoin(left, right).Select()
```

---

## Cascade Joins

Chain a third (or more) set onto the result of a prior join:

```cpp
Query()
    .On({ { L"A", L"B" } }).InnerJoin(left, right)
    .On({ { L"C", L"D" } }).LeftJoin(third)
    .Select()
```

---

## Field Selection Summary

| Call | Effect |
|------|--------|
| Neither `FromLeft` nor `FromRight` | All fields from both sets |
| `FromLeft(["X"])` | Only field X from left + all from right |
| `FromRight(["Y"])` | Only field Y from right + all from left |
| `FromRight([JKey("Y", "Z")])` | Field Y from right renamed to Z |
| Both `FromLeft` and `FromRight` | Only specified fields from each set |

---

## Cross-References

- See [[Wasaby-DB-Access-Patterns]] for how RecordSets are obtained from DB queries.
- See [[Wasaby-Data-Types]] for FieldType reference (types of fields in joined RecordSets).
