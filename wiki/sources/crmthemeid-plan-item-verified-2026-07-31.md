---
type: source
address: c-000241
title: "Пункт плана: ReferralProgram.GetCRMThemeId реализован в 26.4200, проверен на схеме Тензора"
source_type: sbis_dialog
created: 2026-07-31
updated: 2026-07-31
tags:
  - price-formation
  - referral-program
  - implementation
  - verified
status: current
related:
  - "[[ReferralProgram-CRMThemeId-By-Referral-Code]]"
  - "[[Тимошенко А.А.]]"
---

# Пункт плана: ReferralProgram.GetCRMThemeId реализован и проверен

Источник: `raw/Диалоги SBIS/3067c623-6ace-4ec5-b355-b36794ae2f7a.md` (theme_id `3067c623-6ace-4ec5-b355-b36794ae2f7a`), 2026-07-31.

Тимошенко сдаёт пункт плана: в **26.4200** реализован метод `ReferralProgram.GetCRMThemeId` — получение идентификатора темы отношений по источнику реферального кода партнёра (параметр `AdObject`, INTEGER — развилка формата входа из [[ReferralProgram-CRMThemeId-By-Referral-Code]] закрыта в пользу `@AdObject`). Приложен пример вызова из консоли (`Types/source`, `SbisService`, contract `ReferralProgram`).

Маранов В.Ф. (постановщик задачи №07164990) просит [[Красавин Михаил|Красавина М.]] проверить, что метод можно позвать «на схеме тензора» — то есть в контексте вызова в аккаунте Тензора, как и требовалось по ответам Мусохранова от 2026-07-28 (см. [[ReferralProgram-CRMThemeId-By-Referral-Code]] §«Ответы получены»). Красавин подтверждает в течение часа: «метод работает без ошибок».

> [!key-insight] Задача №07164990 закрыта практической проверкой
> Это первое прямое подтверждение работоспособности метода в целевом контексте вызова (аккаунт Тензора) — окончательно снимает открытую развилку №2 («нужен ли `CreateMultitenantEndpointByClientId`») в [[ReferralProgram-CRMThemeId-By-Referral-Code]]: метод отработал без ошибок в том виде, в каком реализован, без явного указания на использование multitenancy-обёртки в источнике.
