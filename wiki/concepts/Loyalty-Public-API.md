---
type: concept
title: "Loyalty Public API"
updated: 2026-04-10
tags:
  - loyalty
  - api
  - dcservice
  - price-formation
  - sbis
status: current
related:
  - "[[Loyalty-Database-Schema]]"
  - "[[Loyalty-Cloud-Config]]"
  - "[[price-formation/_index]]"
created: 2026-04-10
---

# Loyalty Public API

Public API for the SBIS loyalty system. Full documentation: [wi.sbis.ru BL kaizen](https://wi.sbis.ru/docs/bl/kaizen/d09d92ec-6340-4f46-94f5-b940488a1a81/).

Branded card template API: [API Брендбук](https://wi.sbis.ru/docs/bl/kaizen/8b2d23d7-4f1d-4fb1-a190-8476cbec96e1/).

---

## API Groups

1. **Loyalty on sales** — get sale data, assign and calculate loyalty
2. **Loyalty in SabyGet** — public info for end customers about their loyalty participation
3. **Multifunctional** — reference data and info for systems using loyalty programs

---

## SalePoint API

| Method | Description |
|---|---|
| `SalePoint.GetBalance` | Get bonus and card info available to a person at sale points |
| `SalePoint.GetPromocodes` | Get individual and purchase-reward promo codes active at a sale point |
| `SalePoint.CanCreateECard` | Check if card can be issued at the sale point (affects % icon display) |

---

## Card API (Saby Get)

| Method | Description |
|---|---|
| `Card.GetListV2` | Get list of available cards (used for venue registry, bonus display) |
| `Card.ReadV2` | Read one card (same format as GetListV2) |
| `Card.Save/1`, `Card.Save/2` | Create stored card |
| `Card.Delete/1`, `Card.Delete/2` | Delete stored card |
| `Card.GetPass` | Get e-card image |
| `Card.GetOwnerList` | Get card owners |
| `Card.ReloadCardInfoWithData` | Update card info in DCService from provided data |
| `Card.GetPassFromOnline` | Get e-card image from online |

---

## CardTemplate API

| Method | Description |
|---|---|
| `CardTemplate.GetList` | Get list of templates for stored cards |
| `CardTemplate.Read` | Read online template |
| `CardTemplate.Save` | Save online template |

---

## CardType API

| Method | Description |
|---|---|
| `CardType.SetNotificationSettings` | Configure notifications |
| `CardType.GetNotificationSettings` | Get notification settings |

---

## Promocode API

| Method | Description |
|---|---|
| `Promocode.Get` | Get promo code |
| `Promocode.GetList` | Get all active promo codes for user |
| `Promocode.Read` | Get detailed promo code info |
| `Promocode.GetNumber` | Get count of active promo codes |
| `PromocodeType.ReadAspectSettings` | Read promo code type aspect settings |
| `PromocodeType.ReadByUuid` | Read promo code type by UUID |
| `PromocodeEmission.GetStatistics` | Get promo code emission statistics |

---

## LoyaltyProgram API

| Method | Description |
|---|---|
| `LoyaltyProgram.Join` | Join a loyalty program via venue (used in SabyGet) |

---

## Pass API (DCService)

| Method | Description |
|---|---|
| `Pass.CreatePromocode` | Create promo code pass |
| `Pass.CreateCertificate` | Create Apple Wallet + Google Pay e-images for certificate |
| `Pass.SendMessages` | Send messages (mailing) |
| `Pass.CancelMessages` | Cancel unsent messages |
| `Pass.GetOwners` | Get users who own e-card images (for mailing targeting) |

---

## Online Service API (Online → DCService)

| Method | Description |
|---|---|
| `ServiceDiscountCard.GetCardPartialInfo` | Return partial card info by ID |
| `ServiceDiscountCard.GetCardIds` | Return all named discount card IDs for local schema |

---

## Barcode Type Reference

Unified barcode type registry (sources: online, mobile Saby Get, web Saby Get):

`aztec`, `codabar`, `code128`, `code39`/`barcode39`, `code39mod43`, `code93`, `datamatrix`, `ean13`, `ean8`, `interleaved2of5`, `itf`, `itf14`, `maxicode`, `pdf417`, `pdf417qrcode`, `rss14`, `rssexpanded`, `upca`, `upce`, `upceanextension`, `qrcode`, `custom`

Note: `barcode39` comes from online; `custom` = untyped number for online cards.

---

## Google Pay Image URL Handling

On test environments, card template image URLs (`Strip`, `Logo`) from internal sources (online, retail, presto, etc.) must be rewritten before creating Google Pay passes. Google's server cannot access internal test URLs.

**Fix**: Replace `online|presto|retail|salon|resto` in domain with `webhook`.

Example: `pre-test-online.sbis.ru/...` → `pre-test-webhook.sbis.ru/...`

This rewrite happens server-side when forming Google Pay creation requests.

---

## Questionary

`Questionary` object in DCService — handles discount card issuance form. See: [wi.sbis.ru DCService Questionary](https://wi.sbis.ru/docs/bl/objects/f12ed72c-483d-4ce5-bdb7-1779eb4def63/Questionary/).

---

## Client Cleanup

| Method | Description |
|---|---|
| `Clients.DeleteDemoClientData` | Delete Demo client data from DCService |
