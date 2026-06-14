---
address: c-000135
created: 2026-06-14
updated: 2026-06-14
type: concept
title: "Wasaby PDF Transformer — конвертация PDF в PDF/A"
tags:
  - wasaby
  - middleware
  - pdf
  - conversion
  - backend
status: current
related:
  - "[[Wasaby-HTML-Converter]]"
  - "[[Wasaby-File-Transfer]]"
sources:
  - ".raw/wasaby.Backend/Middleware/Преобразование PDF/Публичное API.sabydoc"
---

# Wasaby PDF Transformer

Сервис преобразования PDF-документов к стандартам ISO (PDF/A).

> Для конвертации HTML → PDF используйте [[Wasaby-HTML-Converter]] (`PdfConverter.*`).

## API

### PDFTransformer.ConvertPDFToPDFA/2

Конвертация PDF в PDF/A-2.

```python
# Параметры:
# Document   — File (RpcFile исходного PDF)
# Conformance — String (уровень соответствия)

result = sbis.BLObject("PDFTransformer").Invoke("ConvertPDFToPDFA/2",
    Document=rpc_file,
    Conformance="Level2B"  # возвращает File с результатом
)
```

### PDFTransformer.ConvertPDFToPDFA/3

Конвертация PDF в PDF/A-3. Добавляет параметр `Prevalidate` (Boolean).

```python
result = sbis.BLObject("PDFTransformer").Invoke("ConvertPDFToPDFA/3",
    Document=rpc_file,
    Conformance="Level3B",
    Prevalidate=True  # предварительная валидация; возвращает File или Null
)
```

## Уровни соответствия (Conformance)

`Level1A`, `Level1B`, `Level2A`, `Level2B`, `Level2U`, `Level3A`, `Level3B`, `Level3U`, `Level4`, `Level4E`, `Level4F`

## Ошибки

| Ошибка | Причина | Решение |
|--------|---------|---------|
| "Файл повреждён или имеет неподдерживаемый формат" | Нарушена структура PDF | — |
| "Документ защищён паролем" | PDF с паролем | — |

## Связанные страницы

- [[Wasaby-HTML-Converter]] — HTML → PDF (PdfConverter)
- [[Wasaby-File-Transfer]] — передача больших файлов
