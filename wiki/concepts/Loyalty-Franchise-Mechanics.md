---
type: concept
title: "Loyalty BL — Franchise Event Mechanics"
updated: 2026-04-10
tags:
  - loyalty
  - franchise
  - algorithms
  - sbis
  - price-formation
status: current
related:
  - "[[Franchise-Loyalty-Architecture]]"
  - "[[Franchise-Loyalty-System]]"
  - "[[Loyalty-Database-Schema]]"
  - "[[Акции-Subsystem-Overview]]"
  - "[[Promocode-Subsystem-Overview]]"
  - "[[Bonus-Programs-Architecture]]"
  - "[[price-formation/_index]]"
created: 2026-04-10
---

# Loyalty BL — Franchise Event Mechanics

Source: `raw/Алгоритмы и процессы.md` | Domain: [[price-formation/_index]]

Documents the **event-driven lifecycle handling** within the Loyalty Business Logic layer (БЛ Лояльности) for franchise operations. Complements [[Franchise-Loyalty-Architecture]] (DB schema) and [[Franchise-Loyalty-System]] (business overview).

---

## Events БЛ Лояльности Subscribes To

The Loyalty BL subscribes to five franchise lifecycle events:

| Event | Trigger |
|-------|---------|
| `online.agent_contract.create_portal` | Social network group created |
| `online.agent_contract.archive_portal` | Social network group archived ("sent to archive") |
| `online.agent_contract.restore_portal` | Social network group restored from archive |
| `online.franchise_contract.accepted` | Account joins a franchise contract as franchisee |
| `online.franchise_contract.terminated` | Franchise contract terminated |

---

## Event Handler: create_portal (Owner)

When a social network group is created, in the **owner's account**:

1. A `ВидЦены` record is created — serves as the franchise folder for **Акции** (promotions).
2. A `ВидКарты` record is created — serves as the franchise folder for **Промокоды** (promo codes).

These records are called **franchise loyalty folders** (франшизные папки лояльности). The `ВидЦены` record is considered primary.

Attributes written:
```json
{ "FranchiseRole": 1, "AgentGroupFolder": true }
```

- The presence of such a ВидЦены record is the **authoritative signal** that an account participates in a franchise.
- `FranchiseRole` enables fast role determination without recomputing.

For all loyalty entities belonging to the group, `ВидЦеныРасширение.GroupId` is set to the group's identifier.

---

## Event Handler: franchise_contract.accepted (Franchisee/Participant)

Same folder creation logic as for the owner, except:

```json
{ "FranchiseRole": 2, "AgentGroupFolder": true }
```

- `FranchiseRole: 2` marks franchise entities as **read-only** — participants cannot edit or independently use them.
- Actual franchise promotions and promo codes only appear in the participant's account via **synchronization** (not immediately on join).

---

## Event Handler: archive_portal / franchise_contract.terminated

When a group is archived or a contract terminated:

1. Franchise folder records are **deleted**.
2. All franchise entities in the account are **deactivated**.
3. `FranchiseRole` attributes are **preserved** on deactivated records.

> [!design-note]
> Preserving `FranchiseRole` after deactivation ensures former participants cannot edit or reuse franchise entities post-disconnection, without needing a separate freeze mechanism.

---

## Promotion Assignment to Franchise

When a promotion or promo code is assigned the condition **"Партнёрам"** (to partners):
- The corresponding `ВидЦены` / `ВидКарты` is moved into the franchise folder.
- This is done by setting `*.Раздел` to the franchise folder record's ID.

---

## Synchronization: Owner → Participants

Franchise promotions flow from the Owner account to Participant accounts via synchronization. Three documented processes (referenced in source via sequence diagrams, images not captured):

1. **Подключение нового участника** — connect a new participant.
2. **Отключение от франшизы** — disconnect from franchise.
3. **Синхронизация данных от Владельца к Участникам** — data sync from Owner to all Participants.

See synchronization details in [[Franchise-Loyalty-System#Синхронизация данных]].

---

## Bonus Operations in Franchise Context

Source references (sequence diagrams not captured) for two bonus processes:

1. **Получение бонусного баланса** — bonus balance retrieval across franchise accounts.
2. **Списание и начисление бонусов** — bonus deduction and accrual.

For general bonus mechanics see [[Bonus-Programs-Architecture]] and [[Bonus-Deduction-Algorithm]].

---

## Related Pages

| Page | What it covers |
|------|---------------|
| [[Franchise-Loyalty-System]] | Business overview: Owner/Participant model, single client base, sync button UI |
| [[Franchise-Loyalty-Architecture]] | DB schema: FranchiseUUIDList, GroupId, ВидЦеныЛица.ТипЛица |
| [[Franchise-Contract-API]] | External API: FranchiseContract.* methods |
| [[Franchise-SabyNet-Subsystem]] | SabyNet configuration layer, operator workflow |
| [[Loyalty-Database-Schema]] | ВидЦены Атрибуты: FranchiseRole, AgentGroupFolder fields |
