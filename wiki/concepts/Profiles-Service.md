---
type: concept
title: "Сервис Профилей (Profiles Service)"
updated: 2026-04-10
tags:
  - platform
  - wasaby
  - profiles
  - users
status: current
related:
  - "[[Wasaby-Framework]]"
  - "[[Multitenancy-Architecture]]"
  - "[[Wasaby-Profiles-Service]]"
created: 2026-04-10
---

# Сервис Профилей (Profiles Service)

Centralized storage and processing of user personal data across SBIS/Saby. Solves the multitenancy problem: each client has isolated schema, but cross-client user interaction (messaging, document sharing, newsfeed) requires a shared user store.

## Core Concept

In the main service schema: each person = `ЧастноеЛицо`. A user working in multiple accounts has multiple unlinked `ЧастноеЛицо` records.

The Profiles Service introduces **Персона** — a stable, unique identifier for a human across all accounts.
- Corporate users: `Персона ← ЧастноеЛицо` (linked to a specific person record in a client schema)
- Physical persons without a corporate account: Персона without `ЧастноеЛицо`

**Пользователь** (in Profiles Service terms): a combined 64-bit value — upper 32 bits = ClientID, lower 32 bits = PersonID (`@Лицо`).

## Key Terms

| Term | Meaning |
|------|---------|
| Клиент | Schema number in Online DB, or `3` for Inside |
| Лицо | `@Лицо` from `ЧастноеЛицо` table |
| Персона | Profiles Service UUID, unique per human |
| Флаг «ЕстьПользователь» | Has SBIS account (can log in). Distinct from «Пользователь» |
| Публичная должность | Role shown to other organizations (not always = real role) |

## Architecture

Three isolated contours:
- **profiles** (ReadWrite) — write scenarios
- **profiles-ro-any** (ReadOnly) — critical business scenarios without writes
- **profiles-ro-spec** (ReadOnly) — high-load read scenarios

**Local-first query strategy**: most requests are for "local" personas — data fetched from local schema first. Only non-local personas go to the Profiles Service. This minimizes cross-service calls.

**Bi-directional sync** between main service and Profiles Service:
- Main → Profiles: all data from `ЧастноеЛицо` (contacts, work experience, photo metadata)
- Profiles → Main: personal contacts + contacts from other schemas (avoids cross-service calls for full contact info)

**Demo mode**: separate demo service with its own DB.

## Data Stored

1. General info (name, gender, city)
2. Contact data
3. Verified contact data
4. Work experience
5. Personal certificate fingerprints (loaded via Certificate Authority)
6. Profile photo metadata (physical files on FileStorage, served via Previewer)

Each Персона has a personal СБИС Disk root for photos (album «Фото профиля»); the root ID is stored in Profiles Service.

## Code / Repos

- Main service module: **Сервис Профилей online-inside** (for online.sbis.ru)
- Billing module: **Сервис Профилей Биллинг** (for reg.tensor.ru)
- Physical persons module: **Сервис Профилей ФЛ** (for my.sbis.ru)
- Service: **profiles2**

Git:
- `git.sbis.ru/usermngt/profiles`
- `git.sbis.ru/usermngt/profiles2`

Public API: `online.sbis.ru/shared/disk/31bd6721-e745-4ab6-9e18-2e77fdb9e22f`

## Связанные страницы

- [[Wasaby-Profiles-Service]] — Сервис Профилей (платформенная перспектива: типы контактов, права, Demo/ФЛ режимы)
- [[Multitenancy-Architecture]] — мультиарендность: изолированные схемы, маршрутизация
