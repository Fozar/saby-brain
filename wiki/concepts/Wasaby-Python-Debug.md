---
address: c-000126
created: 2026-06-14
updated: 2026-06-14
type: concept
title: "Wasaby Python Debugging — VSCode и PyCharm"
tags:
  - wasaby
  - debugging
  - python
  - vscode
  - pycharm
  - devtools
status: current
related:
  - "[[Wasaby-Memray]]"
  - "[[Wasaby-Unit-Testing]]"
sources:
  - ".raw/wasaby.Backend/Отладка/Отладка Python/Отладка Python.sabydoc"
  - ".raw/wasaby.Backend/Отладка/Отладка Python/Отладка Python в VS Code.sabydoc"
  - ".raw/wasaby.Backend/Отладка/Отладка Python/Отладка Python через IDE PyCharm, Python Remote Debug.sabydoc"
---

# Wasaby Python Debugging

Отладка Python на локальных стендах — через VSCode (`sbis_root`) или PyCharm Professional (Python Remote Debug).

## VS Code (через sbis_root)

### Требования

- VS Code или VS Code Insiders
- Расширение Python для VSCode
- `sbis_root` утилита (входит в стенд)

### Структура каталогов

```
# Linux
/development/billing/stand/        ← стенд
/development/debug/debug.py        ← скрипты отладки

# Windows
/billing/stand/
/debug/debug.py
```

### Скрипт отладки (debug.py)

```python
import sbis_root as sbis
print(sbis)
```

### Проставление сессии

```python
# 1. Установить ID пользователя
user_id = ...
auth_obj = sbis.AuthByUserID(user_id)
sid = auth_obj.GetSessionId()
sbis.Session.Set(sbis.WebServerContextKey.icsSESSION_ID, sid)

# 2. Для online — указать схему БД
sbis.SetCurrentSearchPath(f"'_{sid[:8]}',public")

# 3. Если нужна персона пользователя
prof_guid = '00000000-0000-0000-0000-000000000000'  # UUID персоны
sbis.Session.AddOrReplaceHeader("x-spid", prof_guid)
```

Альтернатива: взять `sid` из браузера через DevTools.

### Конфигурация отладчика (.vscode/launch.json)

**Windows:**
```json
{
  "version": "0.2.0",
  "configurations": [{
    "name": "Python: Текущий файл",
    "type": "python",
    "request": "launch",
    "stopOnEntry": false,
    "python": "<путь к python>",
    "program": "${file}",
    "cwd": "${workspaceFolder}/loader.py",
    "env": { "PYTHONPATH": "." },
    "envFile": "${workspaceFolder}/loader.env",
    "debugOptions": ["RedirectOutput"],
    "console": "internalConsole",
    "pythonPath": "<путь к python>"
  }]
}
```

**Linux** (добавить `LD_LIBRARY_PATH`):
```json
"env": {
  "PYTHONPATH": ".",
  "LD_LIBRARY_PATH": ".<путь к библиотекам gcc>"
}
```

---

## PyCharm Professional (Remote Debug)

> [!warning] Последняя допустимая версия PyCharm — **2022.3.3**. Более новые версии использовать нельзя (нет лицензий JetBrains).

### Установка

```bash
# Версия pydevd-pycharm должна совпадать с версией сборки PyCharm (Help → About)
pip install pydevd-pycharm==.8836.43

# На Linux/Docker (использовать Python стенда, не системный)
/opt/python3.11/bin/python3.11 -m ensurepip
/opt/python3.11/bin/python3.11 -m pip install pydevd-pycharm==.8836.43
```

### Настройка конфигурации

1. В PyCharm: Add Configuration → "+" → Python Remote Debug
2. Указать свободный порт (debug server будет его слушать)
3. Опционально: флаг **Share** (конфигурация доступна во всех проектах)
4. **Path mappings** — не заполнять при локальной отладке (работает только при реально удалённом коде)
5. Запустить debug server

### Внедрение в код

Скопировать строки из консоли PyCharm после запуска debug server:
```python
import pydevd_pycharm
pydevd_pycharm.settrace('localhost', port=<PORT>, stdoutToServer=True, stderrToServer=True)
```

Вставить в нужную точку кода. После подключения работают обычные breakpoints.

### Особенности

- Можно отлаживать стенд с локальной и серверной БД
- Указав IP/порт debug server другого разработчика, он сможет отлаживать ваш стенд
- Если debug server упал во время отладки — перезапустить стенд

---

## Связанные страницы

- [[Wasaby-Memray]] — профилировщик памяти (после отладки)
- [[Wasaby-Unit-Testing]] — юнит-тесты без живого стенда
