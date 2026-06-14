---
type: concept
address: c-000071
title: "SonarQube + STAN Linter Setup"
tags:
  - linters
  - sonarqube
  - stan
  - eslint
  - stylelint
  - prettier
  - git-hooks
  - code-quality
status: current
related:
  - "[[Linter-Standarization-Project]]"
  - "[[Python-Code-Standards-SBIS]]"
created: 2026-05-18
updated: 2026-05-18
---

# SonarQube + STAN Linter Setup

Техническая инструкция по подключению ESLint, Stylelint, Prettier и SonarQube к репозиториям Wasaby.

---

## Полный порядок подключения

1. Замена комментариев TSLint → ESLint
2. Генерация отчёта об ошибках
3. Исправление ошибок
4. Отключение pre-receive хуков (старые: `check_js`, `check_ts`)
5. Подключение pre-commit хуков (опционально)
6. Подключение SonarQube

---

## 1. Замена комментариев TSLint → ESLint

```bash
# Клонировать репозиторий dev-tools
git clone https://git.sbis.ru/sbis/dev-tools
cd dev-tools
npm i

# Создать config.json:
{
  "system": { "rootDir": "C:\\linters\\repos", "logsDir": "C:\\linters\\logs" },
  "repositories": {
    "input": ["https://git.sbis.ru/your/repo.git"],
    "rcBranch": "rc-26.3100",
    "workBranch": "feature/tslint-to-eslint-comments",
    "commit": { "message": "Convert TSLint comments -> ESLint comments" }
  },
  "script": { "target": "tsLintToESLint" }
}

node cli.js --config=./config.json
```

---

## 2. Настройка package.json

```jsonc
// Удалить: eslint, stylelint, tslint из dependencies/devDependencies
// Удалить: --tslint флаги
// Удалить файлы: tslint.json, .eslintrc, .stylelintrc.json

// Добавить в "scripts":
"prepare": "wasaby-cli loadProject && wasaby-cli initTSEnv && wasaby-cli initGitHooks",
"lint:fix": "eslint . --fix",
"lint:debug": "eslint . -o eslintResult.log --no-color --quiet",
"lint:css:fix": "stylelint \"**/*.{css,less}\" --fix",
"lint:css:debug": "stylelint \"**/*.{css,less}\" -o stylelintResult.log --no-color",
"prettier": "prettier --write ."

// Добавить в "wasaby-cli":
"ESLint": {
  ".ts": { "@typescript-eslint/no-floating-promises": "error" }
}
```

---

## 3. Прогон авто-фикса

```bash
npm i
npm run lint:fix
npm run lint:css:fix
npm run prettier
```

---

## 4. Генерация отчёта (Jenkins)

URL: `http://ci.sbis.ru/job/code_reviewer/build?delay=0sec`  
- `review_git_url` — папка для сканирования  
- `stan_mode` — `sonar2`

---

## 5. Отключение pre-receive хуков

Написать поручение Александру Меряшину: отключить хуки `check_js` и `check_ts` для репозитория.

---

## 6. Подключение pre-commit хуков

```json
// В package.json → "wasaby-cli":
"preCommitHooks": ["Prettier", "ESLint", "Stylelint"]
```

При коммите с ошибками — коммит отменяется.

---

## 7. Подключение SonarQube

**Только после мержа реквеста с исправлениями.**

Написать поручение Сахаревичу Сергею: включить SonarQube в режиме **sonar2** для репозитория.

> [!key-insight] Режимы СТАН
> - **lint** — используется при ревью кода (более строгий)
> - **sonar2** — используется при добросках (авто-разворот при blocker/error/fault/warning)
> - Дублирование кода (duplicate) — не заворачивает при sonar2, накапливается

---

## Игнорирование ошибок

### JS/TS (ESLint)

```js
// eslint-disable-next-line <rule1>, <rule2>   — следующая строка
/* eslint-disable <rule1>, <rule2> */           — весь файл с этого места
```

### CSS/Less (Stylelint)

```css
/* stylelint-disable-next-line <rule1> */   — следующая строка
/* stylelint-disable <rule1> */             — весь файл с этого места
```

> [!warning] Stylelint баг
> Inline-игнорирование одной строки в Stylelint иногда отключает проверку всего файла.
> Предпочтительно: игнорировать конкретное правило для конкретной строки отдельной строкой комментария.

---

## Распространённые ошибки

### JS: no-undef (глобальные переменные в тестах)

```js
/* global assert, sinon */  // добавить в начало файла
```

`requirejs` → заменить на `require`.

### CSS: комментарии через //

В CSS только `/* ... */`. Комментарии `//` ломают парсер ESLint/Stylelint — меняй на `/* */`.

### CSS: no-descending-specificity

Перенести блок с тяжёлым селектором ниже по файлу, а не переносить много слабых.

### Stylelint: автофикс не исправляет всё

Прогонять `npm run lint:css:fix` несколько раз до полного устранения ошибок.

---

## Справочник линтеров

### Маппинг уровней ошибок → уровни СТАН

| Линтер | Уровень линтера | Уровень СТАН | Блокирует ревью? |
|---|---|---|---|
| **stan-bl / xlint** | blocker | blocker | да |
| | error | error | да |
| | fault | fault | да |
| | warning | warning | нет (выписывается ошибка) |
| | diagnostic | diagnostic | нет (не выписывается) |
| **pylint** | Fatal, Error | error | да |
| | Warning, Convention, Refactor | warning | нет |
| | Information | diagnostic | нет |
| **radon** (сложность) | F, E, D | warning | нет |
| | C, B, A | — | нет |
| **eslint** | error | error | да |
| | warn | warning | нет |
| **stylelint** | error | error | да |
| | warning | warning | нет |
| **eslintcc** (сложность) | F, E, D | diagnostic | нет |
| | C, B, A | — | нет |
| **prettier** | — | — | не СТАН, только форматирование |

### Стадии проверки по линтерам

| Линтер | IDE | Genie/jinnee | SonarQube MR | pre-commit | pre-receive | Доброска |
|---|---|---|---|---|---|---|
| stan-bl / xlint | — | + | + (≥blocker) | — | + `check_tmpl` | + |
| pylint | + (плагин) | + | + | — | + `check_python` / `check_python_orx_syntax` | + |
| radon | — | + | + (F,E,D) | — | + `check_python` (F) | + (F,E) |
| eslint | + (встроен) | + | + | + | — | + |
| stylelint | + (встроен) | + | + | + | — | + |
| eslintcc | — | + | — | — | — | — |
| prettier | + (встроен) | — | — | + | — | — |

### Кол-во правил по режимам СТАН

| Линтер | lint | sonar | sonar2 |
|---|---|---|---|
| stan-bl | **больше** | меньше | меньше |
| pylint | все | все | все |
| radon | все | все | все |
| eslint | **больше** | меньше | меньше (+ .tsx файлы) |
| stylelint | **больше** | меньше | меньше |
| eslintcc | нет | нет | нет |
| xlint | много | много | много |

### Соответствие режимов СТАН инструментам

| Инструмент | Режим СТАН |
|---|---|
| Genie / jinnee | lint (Code Review) |
| SonarQube до 2023 | sonar |
| SonarQube 2023+ | **sonar2** |

> [!key-insight] Почему lint строже sonar2
> lint — более полный набор правил, используется при ревью кода в Genie/jinnee.
> sonar2 — подмножество правил для проверки добросок. Часть ошибок (дублирование, eslintcc) при sonar2 не заворачивается и накапливается со временем.

---

## Связанные страницы

- [[Linter-Standarization-Project]] — проект подключения линтеров (завершён 04.05.2026)
- [[Python-Code-Standards-SBIS]] — стандарты Python-кода
