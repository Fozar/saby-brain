---
type: concept
title: "Python Code Standards (SBIS/Wasaby)"
updated: 2026-04-10
tags:
  - concept
  - python
  - code-standards
  - sbis
  - wasaby
status: current
related:
  - "[[price-formation/_index]]"
  - "[[Python-Localization-rk]]"
created: 2026-04-10
---

# Python Code Standards (SBIS/Wasaby)

PEP-8 based with Wasaby-specific exceptions. Source: `docs/prompts/code_standarts.md`.

---

## Exceptions from PEP-8

**Line length:** max 120 characters (PEP-8 default is 79).

**Method naming:** CamelCase is allowed for BL object methods and platform methods used in Python:
```python
Account.ListOfCertificatesAndApplications(myfilter)
sbis.BLObject("Account").Invoke("ListOfCertificatesAndApplications", myfilter)
```

---

## Formatting Rules

**Indentation:** 4 spaces per level. Wrapped elements: align with opening delimiter OR use double indent for function parameters.

**Blank lines:** 2 lines between top-level definitions (functions, classes); 1 line between methods inside class.

**Imports:** one package per line; at file top (after comments/docstrings, before globals); absolute paths preferred; wildcard imports (`from sbis import *`) are **forbidden**.

**Quotes:** programmer's choice for single-line strings. Multiline strings: always triple double quotes (`"""`).

---

## Spacing Rules

**Sequences:** spaces only after comma or colon in dicts. OK around slice operators.

**Constructs:** no space before colon in conditionals; no space between function name and parentheses; no extra spaces in assignments.

**Operators:** always single spaces around: assignment (`=`, `+=`, etc.), comparison (`==`, `<`, `>`, `!=`, `<=`, `>=`, `in`, `not in`, `is`, `is not`, `and`, `or`, `not`). For mixed-priority ops: lower priority gets spaces, higher priority does not.

**Function arguments:**
```python
# No space for default value
def complex(real, imag=0.0): ...

# Space when type annotation present
def munge(sep: AnyStr = None): ...
def munge() -> AnyStr: ...
```

---

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Packages | lowercase, no underscores preferred | `mypkg` |
| Modules | lowercase, underscores OK | `my_module` |
| Classes | CamelCase | `MyClassName` |
| Exceptions | CamelCase + `Error` suffix | `MyError` |
| Functions/methods | snake_case | `my_method_name` |
| Non-public methods | `_` prefix | `_internal` |
| Private methods | `__` prefix | `__private` |
| Constants | UPPER_SNAKE_CASE | `MAX_OVERFLOW` |
| `self` | always first arg of instance method | |
| `cls` | always first arg of class method | |

> Exception: `sbis` module methods use CamelCase.

---

## Comments

1. Each file starts with its purpose description.
2. All classes and methods must be commented.
3. Forced bad code: add link to Task/Bug that tracks the fix.
4. API documentation: use docstrings.

**Inline comments:** start with `#`, at least 2 spaces before `#`, 1 space after. Same indent level as the code.

```python
x = x + 1  # compensate for boundary  (correct)
```
