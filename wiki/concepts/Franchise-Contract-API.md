---
type: concept
title: "Franchise Contract API (FranchiseContract.*)"
tags:
  - franchise
  - api
  - sbis
  - loyalty
  - discount-cards
status: current
related:
  - "[[DiscountCard-Service-API]]"
  - "[[DiscountCard-Subsystem-Overview]]"
  - "[[Loyalty-Public-API]]"
  - "[[Loyalty-Product-Overview]]"
  - "[[ReferralDeals-System]]"
created: 2026-04-10
updated: 2026-04-10
---

# Franchise Contract API

Source: `raw/API Франшизы.md` | Domain: [[domains/price-formation/_index]]

External API of the Franchise module in SBIS/Saby. All methods are under the `FranchiseContract` namespace and operate against an agency/franchise contract (агентский договор / договор обслуживания).

---

## API Methods Overview

### Lifecycle Handlers

These handle events on the contract itself (status transitions of the invitation/contract):

| Method | Description |
|--------|-------------|
| `FranchiseContract.OnAccept` | Handler called when an invitation in an agency contract is accepted |
| `FranchiseContract.OnRestore` | Handler called when an agency contract is restored |
| `FranchiseContract.OnTerminate` | Publishes a local franchise event about invitation status change |

**Parameters:**
- `OnAccept` — document ID, parameters object
- `OnRestore` — event data object
- `OnTerminate` — document ID

---

### Operator Management

Operators are users (persons) attached to a service contract. All methods take at minimum a document ID.

| Method | Description |
|--------|-------------|
| `FranchiseContract.AddOperator` | Add a single operator to a franchise contract |
| `FranchiseContract.AddOperators` | Add multiple operators to a franchise contract (batch) |
| `FranchiseContract.DelOperator` | Remove an operator from a service contract |
| `FranchiseContract.HasOperators` | Check whether the contract has any operators |
| `FranchiseContract.OperatorList` | List of users on a service contract |
| `FranchiseContract.OperatorsData` | Get operator roles for a service contract |
| `FranchiseContract.SetOperatorAccess` | Block/unblock an operator in the client's personal cabinet (ЛК) |

**Parameters:**

| Method | Params |
|--------|--------|
| `AddOperator` | document ID, person ID |
| `AddOperators` | document ID, list of person IDs |
| `DelOperator` | document ID, person ID |
| `HasOperators` | document ID |
| `OperatorList` | document ID |
| `OperatorsData` | document ID, list of user profile IDs |
| `SetOperatorAccess` | document ID, person ID, block flag (Boolean) |

---

### Data Retrieval

| Method | Description |
|--------|-------------|
| `FranchiseContract.PointSalesList` | Enriched list of sales points (точки продаж) by contract ID |
| `FranchiseContract.AccessData` | Access data for an agency contract by portal ID |

**Parameters:**
- `PointSalesList` — document ID
- `AccessData` — portal ID (note: different parameter type from operator methods — uses portal ID, not document ID)

---

## Key Design Notes

- **Document ID vs Portal ID:** The vast majority of methods accept a document ID (`Идентификатор документа`) as their primary key. `AccessData` is the exception — it takes a portal ID (`Идентификатор портала`).
- **Batch vs single operator:** `AddOperator` and `AddOperators` differ only in that the latter accepts a list of person IDs.
- **OperatorsData** returns role information and requires both document ID and a list of user profile IDs — richer than `OperatorList` which returns just the user list.
- **SetOperatorAccess** blocks/unblocks within the client ЛК specifically (not a global block).
- API completeness per knowledge base: **100%** as of 2 Nov 2025.

---

## Related Concepts

- [[Franchise-Loyalty-System]] — business overview: Owner/Participant model, sync mechanics, single client base
- [[Franchise-SabyNet-Subsystem]] — SabyNet configuration layer: regulations, operator workflow, no-KPI mode
- [[Franchise-Loyalty-Architecture]] — DB schema additions (FranchiseUUIDList, FranchiseRole, GroupId)
- [[DiscountCard-Service-API]] — similar operator/access pattern in the discount card subsystem
- [[ReferralDeals-System]] — another contract-centric API in the same domain
- [[Loyalty-Public-API]] — broader public API surface of the loyalty platform
- [[Loyalty-In-Products]] — which products support franchise features
