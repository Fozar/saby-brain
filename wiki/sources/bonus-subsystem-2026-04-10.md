---
type: source
title: Бонусы — Subsystem Documentation
source_files:
  - raw/Бонусы - Описание.md
  - raw/Бонусы - Концепт решения и архитектура.md
  - raw/Бонусы - База данных Бонусов.md
  - raw/Бонусы - Информационная модель.md
  - raw/Бонусы - Алгоритмы и процессы.md
  - raw/Бонусы -Калькулятор бонусных программ. Формула расчета данных.md
ingested: 2026-04-10
tags:
  - loyalty
  - bonuses
  - sbis
  - source
status: ingested
created: 2026-04-10
updated: 2026-04-10
---

# Source: Бонусы Subsystem Documentation

6 files describing the bonus programs subsystem of the SBIS/Saby loyalty system.

## Summary

The bonus subsystem implements accrual and deduction of bonus points within the loyalty system.

**Key entities:**
- `ВидЦены (Тип=5)` — Bonus program (accrual rules)
- `ВидЦены (Тип=40)` — BonusDecRule (deduction rules)
- `ВидЦеныДокумент` — all bonus events (accruals+, spend−, expiry)

**Key insight:** Accrual and deduction are **separate** objects. Bonus balance is calculated dynamically from `ВидЦеныДокумент`.

## Pages Created

- [[Bonus-Programs-Architecture]] — overview, accrual flows, balance calculation, supplementary accrual
- [[BonusDecRule-Info-Model]] — full data model: BonusDecRule, Benefit, ThresholdConditions, TriggerConditions
- [[Bonus-Deduction-Algorithm]] — BONUS_DEC_RULE=40 priority algorithm + calculator formulas

## Pages Updated

- [[Loyalty-Database-Schema]] — added ВидЦены Type=5/40 documentation
