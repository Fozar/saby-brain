---
type: concept
title: "Franchise (Saby Net) Subsystem"
updated: 2026-04-10
tags:
  - franchise
  - sabynet
  - loyalty
  - price-formation
  - configuration
status: current
related:
  - "[[Loyalty-In-Products]]"
  - "[[Loyalty-Product-Overview]]"
  - "[[ReferralDeals-System]]"
  - "[[Акции-Subsystem-Overview]]"
  - "[[Bonus-Programs-Architecture]]"
  - "[[Franchise-Loyalty-Architecture]]"
  - "[[price-formation/_index]]"
created: 2026-04-10
---

# Franchise (Saby Net) Subsystem

The Franchise subsystem is a **separate configuration** of the Saby Net application, built on the same core mechanisms. It enables franchise networks to manage loyalty, promotions, and bonus programs across multiple venues operating in different accounts.

Source: internal SBIS knowledge base, Oct 2025.

---

## Key Characteristics

| Feature | Franchise behavior |
|---|---|
| Application | Saby Net (отдельная конфигурация) |
| Регламент | Custom regulation with **reduced field set** |
| Операторы | Supported (operator workflow) |
| KPI settings | **Not available** |
| Statistics | Specific data recorded to statistics |
| Bonus programs/promotions | Shared across all franchise venues, even in different accounts |

---

## Differentiating Features vs Standard Saby Net

1. **Custom regulation (регламент)** — fewer fields than the standard document flow regulation.
2. **Operator workflow** — franchise deals with operators, not just self-service.
3. **No KPI settings** — simplified management layer.
4. **Statistics fixation** — specific franchise-relevant events are recorded separately.
5. **Shared loyalty across accounts** — bonus programs and акции can be configured once and applied to venues in different Saby accounts. This is the primary value-add for franchise networks.

---

## Shared Bonus Programs and Promotions

The key loyalty feature of franchise: a single bonus program and promotion set configured at the franchise level applies uniformly across all connected venues, regardless of which Saby account they operate under.

Reference: [loyalty/knowledge](https://link.sbis.ru/loyalty/knowledge)

For how loyalty applies at POS see [[Loyalty-Sale-Application]].
For bonus program mechanics see [[Bonus-Programs-Architecture]].
For акции subsystem see [[Акции-Subsystem-Overview]].

---

## Code Artifacts

| Artifact | Repo / Path |
|---|---|
| Visual representation config | `edo/edo-client` → `rc-25.1234` → `regulation_config.py` L356 (UUID: `af72a752-e57e-4706-881d-7f3efbb0a536`) |
| Regulation JSON (standard) | `edo/regulation-json` → `rc-25.3100` → `REGL_Договор_франшизы_2ea37571...regl.json` |
| Regulation JSON (incoming) | `edo/regulation-json` → `rc-25.3100` → `REGL_Договор_франшизы__входящий__1ba8e7de...regl.json` |
| App configuration | `engine/appconfiguration-datapackage` → `rc-25.3100` → `bcd58727-5adf-40cf-b441-23cd57b9df54.cfg` |

---

## Relations

- [[Loyalty-In-Products]] — franchise support is noted as a cross-cutting concern for loyalty features; most mechanisms support franchise. Exceptions: накопительные подарочные акции and пороговые акции (in progress).
- [[ReferralDeals-System]] — deals/referral system that operates within SabyNet, used by franchise owners.
- [[Loyalty-Product-Overview]] — Saby Net listed in product integrations table with role "Franchise network: shared loyalty, bonus balances across accounts".
