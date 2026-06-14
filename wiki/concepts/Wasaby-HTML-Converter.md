---
address: c-000132
created: 2026-06-14
updated: 2026-06-14
type: concept
title: "Wasaby HTML Converter (converter_html / webshot)"
tags:
  - wasaby
  - middleware
  - pdf
  - conversion
  - backend
status: current
related:
  - "[[Wasaby-File-Transfer]]"
  - "[[Wasaby-BL-Calls]]"
sources:
  - ".raw/wasaby.Backend/Сервисы общего назначения/Приложения семейства Converter Html и Webshot/Техническая документация/API сервиса конвертации HTML.sabydoc"
---

# Wasaby HTML Converter

Три сервиса конвертации:

| Сервис | Назначение | Модуль |
|--------|-----------|--------|
| `converter_html` | HTML → PDF | `PdfConverter.*` |
| `converter_big_html` | Большие HTML → PDF | `BigPdfConverter.*` |
| `webshot` | URL/HTML → изображение | `ImageConverter.*` |

## PDF конвертер (converter_html)

### Основные методы

| Метод | Описание |
|-------|----------|
| `PdfConverter.ConvertHtml(file)` | HTML RpcFile → PDF (параметры по умолчанию: A4, 10мм отступы, портрет) |
| `PdfConverter.ConvertHtml(file, params)` | HTML RpcFile → PDF с параметрами |
| `PdfConverter.ConvertUrl(url)` | URL → PDF |
| `PdfConverter.ConvertUrl(url, params, cookies)` | URL → PDF с параметрами и куки |
| `PdfConverter.ConvertHtmlFromFileTransfer(params, control_info)` | HTML из file-transfer → PDF |
| `PdfConverter.ConvertHtmlToFileTransfer(guid, section, params)` | HTML → PDF → file-transfer |
| `PdfConverter.ConvertManyHtml(params, files)` | Много HTML → один PDF |
| `PdfConverter.ConvertMultiHtml(files, params)` | Много HTML → много PDF |
| `PdfConverter.ConvertTiffToPdfByGuid(file)` | TIFF → PDF по GUID |

Private-варианты (`Private*`) — для доступа к приватной зоне.

### Параметры ConvertHtml(file, params)

```python
params = sbis.Record()
params["PageSize"] = "A4"            # или PageWidth/PageHeight в мм
params["PageLandscape"] = False       # альбомная ориентация
params["PageOrientation"] = 0         # 0=авто, 1=портрет, 2=альбом, 3=авто без разбивки
params["margin"] = "default"          # "default"(10мм), "minimum"(5мм), "none"(0мм)
params["PageTopMargin"] = "10"        # или PageBottomMargin/PageRightMargin/PageLeftMargin
params["FirstPageTemplate"] = "..."   # шаблон колонтитулов первой страницы
params["OddPageTemplate"] = "..."     # нечётные страницы
params["EvenPageTemplate"] = "..."    # чётные страницы
params["FirstPageNumber"] = 1         # нумерация с N
params["FontCompression"] = True      # сжатие шрифтов в PDF
params["Timeout"] = 60               # таймаут (сек), по умолчанию по размеру файла
params["NeedPdfA"] = False           # формат PDF/A
params["ErrorIfNoFile"] = True        # исключение при ошибке (иначе пустой файл)
params["fileName"] = "report.pdf"     # имя выходного файла
```

### Прокси-модуль (PDF.Save)

Для сохранения отчёта в PDF из BL:
```python
PDF.Save(
    MethodName,    # метод БЛ для построения отчёта
    Filter,        # фильтр
    Fields,        # поля
    Sorting,       # сортировка
    Titles,        # заголовки
    HierarchyField,
    FileName,      # имя файла
    Pagination,
    PageLandscape,
    Sync           # синхронный/асинхронный режим
)
```

## Webshot (ImageConverter)

Конвертация URL или HTML в изображение (PNG/JPEG).

| Метод | Описание |
|-------|----------|
| `ImageConverter.ConvertUrl(url)` | URL → изображение |
| `ImageConverter.ConvertUrl(url, params, cookies)` | URL → изображение с параметрами |
| `ImageConverter.ConvertHtml(file, params)` | HTML → изображение |
| `ImageConverter.ConvertUrlMultiElements(url, params, cookies)` | Захват нескольких элементов |
| `ImageConverter.ConvertUrlToDisk(url, params, cookies)` | URL → изображение на диск |

### Delayed Print (для динамического контента)

При использовании `delayedPrint=true` в params:

```javascript
// JS на конвертируемой странице:
window.tensor.waitPrint()   // вызывать каждые ≤5 сек во время загрузки контента
window.tensor.startPrint()  // вызвать, когда страница готова к захвату
window.tensor.abortPrint()  // вызвать при ошибке построения страницы
```

Таймауты:
- Нет вызова `waitPrint()` или `startPrint()` в течение 30 секунд → конвертация прервана
- Нет вызова `waitPrint()` или `startPrint()` в течение 5 секунд после предыдущего `waitPrint()` → прервана

## Большой PDF конвертер (converter_big_html)

Для очень больших документов:
```python
BigPdfConverter.ConverterBigHtml(guid)
BigPdfConverter.ConverterBigHtml(guid, params)
BigPdfConverter.ConvertHtml(file, params)
```

## Связанные страницы

- [[Wasaby-File-Transfer]] — `ConvertHtmlFromFileTransfer` / `ConvertHtmlToFileTransfer`
- [[Wasaby-BL-Calls]] — вызов методов конвертера
