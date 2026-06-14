---
address: c-000108
created: 2026-06-14
updated: 2026-06-14
type: concept
title: "Wasaby C++ String Standard (StringView / String / StackString)"
tags:
  - wasaby
  - standards
  - cpp
  - strings
  - backend
  - performance
status: current
related:
  - "[[Wasaby-Dev-Standards]]"
sources:
  - ".raw/wasaby.Backend/Стандарты разработки/Стандарт разработки на C++/Стандарт разработки на C++.sabydoc"
  - ".raw/wasaby.Backend/Стандарты разработки/Стандарт разработки на C++/Работа со строками.sabydoc"
  - ".raw/wasaby.Backend/Стандарты разработки/Стандарт разработки на C++/Использование StringView_String_StackString.sabydoc"
---

# Wasaby C++ String Standard

Три основных класса Wasaby Framework для работы со строками: `StringView`, `String`, `StackString`. Выбор зависит от сценария использования.

## Сводная таблица — когда что использовать

| Сценарий | Класс |
|----------|-------|
| Функция только читает строку | `StringView` |
| Глобальная строковая константа | `StringView` (L"..."_sv) |
| Метод сохраняет строку в поле класса | `String` |
| Конструктор/фабрика создаёт объект по строке | `String` (move) |
| Построить короткоживущую строку из частей | `StackString` + `StringBuilder` |
| Конкатенация в цикле / форматирование | `StringBuilder` / `Format` |

## StringView / BinaryStringView

Read-only ссылка на непрерывный буфер символов. Не владеет данными.

**Плюсы:**
- Бесплатное копирование (копируется только указатель + длина)
- Бесплатные операции `substr`, `trimmed`
- Абстрагирует от способа хранения: принимает `std::string`, `String`, `StackString`, `wchar_t*`

**Ограничения:**
- Read-only — нельзя модифицировать данные
- Нет `c_str()` — строка **не** null-terminated
- **Нельзя хранить дольше источника** — если строка-источник уничтожена, StringView инвалиден

```cpp
// Правильно: константа на этапе компиляции, нет аллокаций
static const StringView DOCUMENTS_TABLE = L"Документы"_sv;

// Правильно: параметр только для чтения
void Exec(StringView query) {
    internal_c_driver_exec(query.data(), query.size());
}
```

## String

Аналог `std::wstring`. Владеет данными, аллоцирует на куче.

Используется когда:
- Метод **сохраняет** строку в поле класса
- Конструктор/фабрика принимает строку по значению → move

```cpp
class Foo {
public:
    void SetName(String name) {
        mName = std::move(name);  // move — без лишнего копирования
    }
private:
    String mName;
};
```

## StackString / BinaryStackString

`String`-подобная строка со **стековым буфером** + автоматический переход в кучу при переполнении.

Используется для **построения короткоживущей строки** из частей.

```cpp
// Оптимальный паттерн: нет аллокаций, безопасно при больших строках
StackString<256> url;
Format(url, L"http://%1%/api_v%2%/%3%/?%4%"_sv, domain, api_version, method, params);
DoHttpRequest(StringView(url));
// url удаляется сразу после — данные не нужны дальше
```

## StringBuilder

Конкатенация без промежуточных аллокаций. Превосходит `std::stringstream`:
- Нет локалей → быстрее
- Нет внутренних аллокаций → меньше фрагментации кучи
- Пишет сразу в переданный контейнер (String, StackString, `std::vector<char>`)

```cpp
WStringBuilder query;
query << L"SELECT FROM"_sv << table << L" LIMIT "_sv << count;
SqlQuery(query.Get());   // Get() — ссылка без копирования
```

```cpp
BinaryStackString<512> redis_command;
MakeStringBuilder(redis_command)
    << "GET"_sv << Encoded(Encoding::UTF8, key);
```

## ToString / Format / FormatByContext

| Функция | Назначение |
|---------|------------|
| `ToString(val)` | Преобразование значения в строку |
| `ToString(str, val)` | Дозапись строкового представления в `str` |
| `Format(str, L"template %1%"_sv, arg)` | Форматирование по шаблону (плейсхолдеры `%1%`, `%2%`, …) |
| `FormatByContext(text, context)` | Подстановки `{{имя_переменной}}` из Context-объекта (для БЛ) |
| `FormatFromRecord(format, rec)` | **Deprecated** — использовать `FormatByContext` |

### Format vs boost::format

Wasaby `Format` предпочтительнее: не раздувает бинарники, предсказывает и резервирует размер буфера, работает через `ToString`.

```cpp
// Без аллокаций (StackString)
StackString<256> query;
Format(query, L"SELECT FROM %1% LIMIT %2%"_sv, table, count);

// С одной аллокацией (String)
String query = Format(L"SELECT FROM %1% LIMIT %2%"_sv, table, count);
```

## FromString

Парсинг строк → типизированные значения.

```cpp
int val = FromString<int>(sv.substr(pos).trimmed());

// Hex-модификатор
Int hexVal = FromString<Hex<Int32>>(str);  // парсит 0xABС, ABC и т.п.
```

## Расширение

Кастомная стрингификация: специализация `Stringify<MyType>` с методом `ToString(Allocator<wchar_t>&, const MyType&)`.  
Кастомный парсинг: специализация `DeStringify<MyType>` с методом `FromString(StringView)`.
