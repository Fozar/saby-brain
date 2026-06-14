---
address: c-000018
type: concept
title: "AVIF to PNG Conversion on Windows"
created: 2026-05-18
updated: 2026-05-18
status: current
tags:
  - tooling
  - images
  - windows
  - claude-code
related:
  - "[[SabyGet-Loyalty-Subsystems]]"
  - "[[SabyGet-Landing-Page]]"
---

# AVIF to PNG Conversion on Windows

Практическое руководство: как конвертировать `.avif` файлы в PNG для чтения через Claude Code (Read tool).

## Проблема

Claude Code's Read tool поддерживает PNG/JPG/WebP для vision, но **не умеет читать AVIF визуально** — возвращает бинарные данные.

Obsidian (и другие приложения) часто скачивают и кешируют изображения в AVIF, поэтому эта конвертация нужна регулярно.

## Что НЕ работает на Windows

| Метод | Проблема |
|-------|---------|
| `python3` (Windows Store) | Заглушка — не запускает реальный Python |
| PowerShell WIC `BitmapDecoder.CopyPixels` | Ошибка `0xC00D5212` — нет GPU/HW AV1 декодера |
| PowerShell WIC `RenderTargetBitmap` | Рендерит 0 ненулевых байт (тот же root cause) |
| `pip install pillow-avif-plugin` (Python Store) | Не устанавливается (нет реального pip) |

## Что работает: Python 3.11 + Pillow

Pillow начиная с версии 9.1.0+ включает нативную поддержку AVIF через `libavif`.

### Ключевой момент: использовать `py`, не `python3`

На Windows `python3` — заглушка Microsoft Store. Реальный Python запускается через **`py`** (Python Launcher).

```bash
# Проверить реальный Python
py --version        # Python 3.11.9
py -c "import sys; print(sys.executable)"
# C:\Users\...\Python311\python.exe
```

### Установка Pillow

```bash
py -m pip install pillow
```

### Конвертация одного файла

```bash
py -c "from PIL import Image; Image.open('file.avif').save('file.png')"
```

### Конвертация всех AVIF в директории

```python
# convert_avif.py
from PIL import Image
import os

src_dir = r'C:\path\to\avif\files'
dst_dir = r'C:\Temp'
os.makedirs(dst_dir, exist_ok=True)

for f in os.listdir(src_dir):
    if f.endswith('.avif'):
        src = os.path.join(src_dir, f)
        dst = os.path.join(dst_dir, f.replace('.avif', '.png'))
        try:
            img = Image.open(src)
            img.save(dst, 'PNG')
            print(f'ok: {f} {img.size} {img.mode}')
        except Exception as e:
            print(f'ERR {f}: {e}')
```

```bash
py convert_avif.py
```

### Однострочник для всей папки

```bash
py -c "
from PIL import Image
import os, sys
d = sys.argv[1]
[Image.open(os.path.join(d,f)).save(os.path.join(d,f.replace('.avif','.png'))) for f in os.listdir(d) if f.endswith('.avif')]
print('done')
" C:\path\to\folder
```

## Применение в Claude Code

После конвертации читать через Read tool:

```python
# В сессии Claude Code:
# Read C:\Temp\image_MD5.png  → Claude видит изображение визуально
```

## Контекст возникновения

Обнаружено при ингесте документации SabyGet (2026-05-18): Obsidian скачал изображения с `link.sbis.ru` и сохранил как `*_MD5.avif` в корне vault. Read tool возвращал бинарный `ftypavif`-мусор. Решение через `py` + Pillow разблокировало vision для 8 диаграмм архитектуры и UI-скриншотов.

> [!key-insight] py vs python3 на Windows
> На Windows `python3` = заглушка Microsoft Store (печатает "Python" и выходит). Всегда используй `py` для запуска реального интерпретатора Python. Проверь: `py -c "import sys; print(sys.executable)"` должно вернуть путь в `AppData\Local\Programs\Python`.
