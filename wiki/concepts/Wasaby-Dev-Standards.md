---
address: c-000105
created: 2026-06-14
updated: 2026-06-14
type: concept
title: "Wasaby Backend Dev Standards"
tags:
  - wasaby
  - standards
  - development
  - backend
status: current
related:
  - "[[Wasaby-SQL-Standard]]"
  - "[[Wasaby-Python-Standard]]"
  - "[[Wasaby-Cpp-String-Standard]]"
sources:
  - ".raw/wasaby.Backend/Стандарты разработки/Стандарты разработки.sabydoc"
---

# Wasaby Backend Dev Standards

Стандарты разработки бэкенда Wasaby Framework. Определяют правила оформления кода, именования, review и качества.

## Разделы

| Язык/тема | Wiki-страница |
|-----------|---------------|
| Python | [[Wasaby-Python-Standard]] |
| C++ (строки) | [[Wasaby-Cpp-String-Standard]] |
| SQL | [[Wasaby-SQL-Standard]] |

## Инструменты статического анализа

- **Radon** — цикломатическая сложность Python-кода
- **Pylint** — замечания PEP-8 и стиль
- **Genie** → "Inspect code" → "Code Review" для анализа прямо из IDE

> [!key-insight] Code review scoring
> Итоговая оценка = 5 − штраф Radon − штраф Pylint − штраф за грубые ошибки
> Минимальный приемлемый балл фиксируется командой, но типично ≥ 3.

## Ссылки

- [Стандарт Python](https://link.sbis.ru/article/87b7fb1e-9c3d-4c4e-b23b-bc3af2745ea1)
- [Стандарт C++](https://link.sbis.ru/article/d8b5ef49-e1f6-4bfc-8c53-16fddc63dcf8)
- [Стандарт SQL](https://link.sbis.ru/article/f29d268f-9bc3-4b74-ba80-69dc2d19f64e)
