---
type: source
title: "tests_new/README.md — Unit Test Framework for price-formation"
source_path: "price-formation/tests_new/README.md"
ingested: 2026-04-11
tags:
  - price-formation
  - testing
  - unit-tests
  - pycharm
  - cmake
  - wasaby
status: ingested
related:
  - "[[PriceFormation-Test-Framework]]"
  - "[[PriceFormation-Backend-Architecture]]"
  - "[[Saby-Feature-Toggles-API]]"
created: 2026-04-11
updated: 2026-04-11
---

# Source: tests_new/README.md

**Date ingested:** 2026-04-11
**Source:** `price-formation/tests_new/README.md`
**Language:** Russian
**Topic:** Unit testing framework setup, build, and test-writing guide for the price-formation loyalty/pricing system.

---

## Summary

README для системы юнит-тестов лояльности. Описывает три тестовых проекта (Desktop, Online, OnlineWithDiscountCore), утилиту `test_manager.py`, процесс сборки через cmake/ninja/test_framework, настройку PyCharm, и правила написания тестов (моки методов и таблиц, sbis_feature, skip-декораторы).

---

## Pages Created / Updated

- Created: [[PriceFormation-Test-Framework]]
- Updated: [[PriceFormation-Backend-Architecture]] — added link to test framework
- Updated: [[concepts/_index]] — added test framework entry
- Updated: [[domains/price-formation/_index]] — added test section

---

## Key Facts Extracted

1. Три тестовых проекта: `Desktop`, `Online`, `OnlineWithDiscountCore` (требует дополнительных зависимостей — ядро расчёта).
2. `test_manager.py` — утилита в корне репо, автоматизирует: проверку окружения, загрузку зависимостей, сборку, запуск проекта.
3. Зависимость от `pnt-toolbox` — должен лежать рядом с `price-formation` (sibling-репозиторий).
4. Сборка: cmake + ninja (не genie, не дистрибутив); SDK версии должен соответствовать ветке.
5. Git симлинки обязательны на Windows: `git config --global core.symlinks true` + перезапуск компьютера после установки SDK.
6. Рабочая директория тестов: `<build_dir>/price-formation/tests/<project>/run`.
7. Мок методов → `TestLoyalty.orx`; мок таблиц → `TestLoyalty.dicx` (изменение dicx требует пересборки).
8. `sbis_feature` отсутствует в тестовом проекте — всегда мокировать через `@enable_features([...])`.
9. `@with_feature` — классовый декоратор, прогоняет с обоими состояниями флага.
10. `@test_new_skip` — для тестов, которые не могут работать в тестовой среде.
11. Контактное лицо по вопросам: Ушаков Тимофей (Т.Л.).