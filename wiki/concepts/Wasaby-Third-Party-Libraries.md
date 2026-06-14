---
address: c-000118
created: 2026-06-14
updated: 2026-06-14
type: concept
title: "Wasaby: Подключение сторонних библиотек (Python / C++)"
tags:
  - wasaby
  - backend
  - python
  - cpp
  - libraries
  - build
  - conan
status: current
related:
  - "[[Wasaby-BL-Objects]]"
  - "[[Wasaby-Python-Standard]]"
sources:
  - ".raw/wasaby.Backend/Инструменты разработки/Использование сторонних библиотек/Подключение сторонних библиотек Python.sabydoc"
  - ".raw/wasaby.Backend/Инструменты разработки/Использование сторонних библиотек/Подключение сторонних библиотек С++.sabydoc"
---

# Wasaby: Подключение сторонних библиотек

> [!warning] Согласование обязательно
> Перед использованием любой сторонней библиотеки необходимо получить согласование по внутренней инструкции. Только после согласования можно подключать библиотеку в модули.

## Python

**Репозиторий**: `git.sbis.ru/third-party/python`  
**Pip-репозиторий**: `repo-dev.mgmt.tensor.ru/#browse/browse:pypi-repo`

### Порядок подключения

1. **Создать рецепт сборки** (`setup.py`) в корне репозитория с исходным кодом библиотеки
2. **Оформить поручение** на добавление пакета в pip-репозиторий (на отдел сборки)
3. **Добавить ресурс** в `.s3mod` файл модуля в Genie:

```xml
<resources>
  <resource
    architecture="all"
    compiler="all"
    deployment_root="service_root"
    link_type="all"
    name="microdbf"
    os="all"
    type="python_library"
  />
</resources>
```

- `name` — имя библиотеки (как в pip)
- `deployment_root` — всегда `service_root` для типа `python_library`

4. **Использовать** в коде как обычно:
```python
import microdbf
```

Скачивание из pip происходит при сборке дистрибутива → папка `python_libraries` в корне образа сервиса.

## C++

**Репозиторий**: `git.sbis.ru/third-party`  
**Пакетный менеджер**: Conan  
**Рецепты**: `git.sbis.ru/third-party/conan-recipes`  
**Jenkins**: `platform-jenkins.sbis.ru/view/third-party-libs/`

### Порядок подключения

1. Отдел сборки создаёт репозиторий в группе `third-party` с ветками по версиям платформы (`rc-22.7200`, `rc-23.1000`, …)
2. Добавить рецепт сборки в `conan-recipes` → Jenkins запускает централизованную сборку
3. В `CMakeLists.txt` — два шага:

```cmake
# 1. Загрузка и установка путей
sbis_conan_run(
    SBIS_REQUIRES
        my-library
        openssl
        zlib
    SBIS_CONAN_ARGS
        IMPORTS
            "lib, *.dll -> ${CMAKE_BINARY_DIR}/bin"
            "lib, *.dylib -> ${CMAKE_BINARY_DIR}/bin"
            "lib, *.so -> ${CMAKE_BINARY_DIR}/bin"
)

# 2. Добавление зависимости к таргету
sbis_use_library("my-library")
```

- `SBIS_REQUIRES` — список имён библиотек; версия регулируется SDK
- `IMPORTS` — копирует `.dll/.so/.dylib` в `bin/` для тестов и jinnee
- `sbis_use_library` — добавляет include-пути и флаги сборки к текущему таргету (`sbis_create_project`)

## Связанные страницы

- [[Wasaby-BL-Objects]] — модули, в которых подключаются библиотеки
- [[Wasaby-Unit-Testing]] — тесты используют те же ресурсы модуля
