---
type: concept
title: "Python Localization with rk() (SBIS/Wasaby)"
updated: 2026-04-10
tags:
  - concept
  - python
  - localization
  - wasaby
  - sbis
status: current
related:
  - "[[Python-Code-Standards-SBIS]]"
  - "[[price-formation/_index]]"
created: 2026-04-10
---

# Python Localization with rk() (SBIS/Wasaby)

`rk()` function from `sbis` library for localizing string constants.

---

## Signature

```python
rk(key)                   # translation only
rk(key, number)           # translation + plural form
rk(key, context, number)  # translation + context + plural form
```

**Import:** `rk` comes with `sbis` - no extra imports needed.
```python
from sbis import rk
# or
import sbis; sbis.rk(...)
```

---

## Context

Disambiguates same string with different meanings:

| Context | String | Translation |
|---------|--------|-------------|
| Technical support | Help | Support |
| Medical | Help | Aid |

```python
LogMsg(rk('Помощь', 'Техническая поддержка'))  # → "Support"
```

In translation dict: `"Техническая поддержка@@Помощь": "Support"`

---

## Rules (Critical)

### Do NOT wrap static class variables
```python
# Wrong - translation computed once, won't update
class A:
    message = sbis.rk("мое сообщение")

# Correct - translation applied on every call
class A:
    message = "мое сообщение"
    def get_message():
        return sbis.rk(A.message)
```

### Do NOT concatenate translated strings
Word order varies by language. Use placeholders instead:
```python
# Wrong
raise Error(rk('Ошибка') + ': "' + message + '"')

# Correct - positional
raise Error(rk('Ошибка: "{0}" с кодом {1}').format(message, code))

# Correct - named
raise Error(rk('Ошибка: "{message}" с кодом {code}').format(message=m, code=c))
```
Apply `.format()` **after** `rk()` call. Placeholders must exist in all language translations.

### No leading/trailing whitespace in keys
`'Сохранить'`, `'\nСохранить'`, `'&nbsp;Сохранить'` are treated as different keys.

### Include punctuation inside `rk()`
```python
rk('Ошибка!')      # correct
rk('Удалить?')     # correct
rk('Ошибка') + '!' # wrong
```

---

## Plural Forms

Key format: `"слово(-а,-ов)"` - brackets mark plural variants in translation dict.

```python
rk("запись(-и,-ей)", 1)   # → "запись" / "record"
rk("запись(-и,-ей)", 2)   # → "записи" / "records"
rk("запись(-и,-ей)", 5)   # → "записей" / "records"
rk("запись(-и,-ей)", 1.5) # → "записи" / "records"
```

**Forms by language:**

| Language | Forms | Pattern |
|----------|-------|---------|
| Russian (`ru*`) | 4 | 1 / 2-4 / 5+ / fractional |
| English (`en*`) | 2 | 1 / 2+/fractional |

**Translation dict:**
```json
// ru.json
{ "plural#запись(-и,-ей)": "запись|записи|записей|записи" }

// en.json
{ "plural#запись(-и,-ей)": "record|records" }
```
