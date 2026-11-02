path = "/mnt/c/Users/aa.timoshenko/PycharmProjects/claude-obsidian/wiki/concepts/PromoCode-Design-Constructor.md"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

bad = """## Доработка: обновление ID шаблона сайта дизайна (02.11)

- **Лебедева, 02.11 11:07:** «Замени пожалуйста ид шаблона на b8f7fd80-ca26-4e9e-b384-5b14ddb6e3f9, и закроем задачу».
- В  константа  заменена с  на .
- Тесты  (6 тестов) и тесты создания/чтения/обновления промокодов (10 тестов) прошли успешно.
- Ветка , коммит .
- Оформлен регламентный Merge Request в СБИС: https://online.sbis.ru/opendoc.html?guid=01a19b65-1912-77c5-a4c8-258d432d5647&client=3, GitLab MR !153436, !153437, !153438 (приложение online)."""

good = """## Доработка: обновление ID шаблона сайта дизайна (02.11)

- **Лебедева, 02.11 11:07:** «Замени пожалуйста ид шаблона на b8f7fd80-ca26-4e9e-b384-5b14ddb6e3f9, и закроем задачу».
- В `core.py` константа `PROMOCODE_SITE_TEMPLATE_ID` заменена с `94345145-2493-428e-bf2b-dee75f09e962` на `b8f7fd80-ca26-4e9e-b384-5b14ddb6e3f9`.
- Тесты `tests_priceformationonline.loyaltyprograms.promocode.design_site.CreateDesignSite` (6 тестов) и тесты создания/чтения/обновления промокодов (10 тестов) прошли успешно.
- Ветка `26.6100/feature/aatimoshenko/09234630_site_template`, коммит `be5d709dc8`.
- Оформлен регламентный Merge Request в СБИС: https://online.sbis.ru/opendoc.html?guid=01a19b65-1912-77c5-a4c8-258d432d5647&client=3, GitLab MR !153436, !153437, !153438 (приложение online)."""

if bad in text:
    text = text.replace(bad, good)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("FIXED")
else:
    print("BAD NOT FOUND")
