---
type: concept
title: "Wasaby Shared Future"
address: c-000033
created: 2026-05-22
updated: 2026-05-22
tags:
  - wasaby
  - performance
  - concurrency
  - python
  - cpp
status: current
related:
  - "[[Wasaby-App-Optimization]]"
  - "[[Wasaby-DB-Access-Patterns]]"
  - "[[SBIS-Internal-API-Methods]]"
  - "[[Python-Code-Standards-SBIS]]"
---

# Wasaby Shared Future

Механизм параллельного выполнения удалённых запросов (к БД, BL-методам) в Wasaby Framework. Доступен на Python и C++. Снижает суммарное время ожидания с суммы времён до времени самого долгого запроса.

> [!key-insight] Ключевой принцип
> Параллельно запускать нужно только **удалённые** запросы (к БД, RPC). Для мелких вычислений накладные расходы превысят выигрыш.

---

## Python API

Через класс `sbis.BLObject`, метод `FutureInvoke()`.

```python
# Запускаем три запроса параллельно
result1 = BLObject('Тест').FutureInvoke('Запрос1')  # 1 сек
result2 = BLObject('Тест').FutureInvoke('Запрос2')  # 2 сек
result3 = BLObject('Тест').FutureInvoke('Запрос3')  # 3 сек

# .get() блокирует до готовности результата
return result1.get().Size() + result2.get().Size() + result3.get().Size()
# Итого: 3 секунды вместо 6
```

`FutureInvoke()` возвращает объект `sbis.FutureObject`. Метод `.get()` возвращает результат, если готов, иначе ждёт.

## C++ API

Через класс `bl::Object`, метод `Invoke<sbis::shared_future<T>>()`.

```cpp
auto result1 = bl::Object(L"Тест").Invoke<sbis::shared_future<RecordSet>>(L"Запрос1"),
     result2 = bl::Object(L"Тест").Invoke<sbis::shared_future<RecordSet>>(L"Запрос2"),
     result3 = bl::Object(L"Тест").Invoke<sbis::shared_future<RecordSet>>(L"Запрос3");

return result1.get().Size() + result2.get().Size() + result3.get().Size();
```

---

## Прикладной паттерн: порядок вызовов

Оптимальный порядок — запускать **самый медленный** метод первым, `.get()` самого быстрого вызывать первым. Так минимизируется время ожидания в `.get()`.

```python
for one_doc in result:
    # Запускаем в порядке: медленный → быстрый
    future_contacts = BLObject('СвязьПапок').FutureInvoke('КонтрагентЕстьЛиКонтакты', ...)
    future_monitor  = BLObject('СвязьПапок').FutureInvoke('ПользователиНаКонтроле', ...)
    future_connect  = BLObject('СвязьПапок').FutureInvoke('ПолучитьСвязанныеДокументыИТипы', ...)

    # .get() в порядке: быстрый → медленный
    one_doc.СвязанныеДокументы        = future_connect.get()
    one_doc.ПользователиНаКонтроле    = future_monitor.get()
    one_doc.КонтрагентЕстьЛиКонтакты = future_contacts.get()
```

---

## Ограничение 1: лимит потоков

По умолчанию — **16 параллельных потоков** FutureInvoke. Регулируется настройкой облака:
> `Ядро.Сервер приложений.МаксимальноеКоличествоВнутреннихПотоков`

Поведение при превышении лимита:
- Вызов выполняется **синхронно** в текущем потоке (как обычный `Invoke()`)
- Когда поток освобождается, следующий вызов снова уходит в пул
- Максимальный параллелизм: 17 потоков (16 + основной)
- В худшем случае: всё сводится к одному потоку (если 16 медленных + 1 ещё медленнее синхронный)

> [!warning] Риск при цикле
> При вызове `FutureInvoke` в цикле над большим массивом — часть вызовов автоматически становится синхронной. Не создаёт `boost_resource_error`, но снижает эффективность параллелизма. Для таких случаев — см. [[#ParallelTasks]].

## Ограничение 2: ожидание при выходе из метода

Если BL-метод завершается, не получив результаты всех запущенных `FutureInvoke`, платформа **автоматически дожидается** их завершения перед отдачей ответа. Это предотвращает «висячие» потоки.

```cpp
sbis::shared_future<bool> res = Object(L"My").Invoke<sbis::shared_future<bool>>(L"Test");
if (!some_condition())
    return false;  // платформа дождётся завершения "My.Test" перед отдачей ответа
```

## Ограничение 3: отдельное соединение с БД

Метод, вызванный через `FutureInvoke`, выполняется в **отдельном соединении** и **отдельной транзакции**. Ему **недоступны** незафиксированные изменения основного потока.

---

## ParallelTasks

Класс для гибкого управления набором параллельных задач. Решает главный недостаток `FutureInvoke` в цикле: освободившийся поток сразу берёт следующую задачу, не ожидая завершения текущего потока.

| Метод | Описание |
|-------|----------|
| `AddTask(functor)` | Добавить произвольный функтор |
| `AddInvoke('Объект.Метод', args)` | Добавить локальный RPC-вызов |
| `Launch()` | Запустить всё и дождаться завершения |

**Python:**
```python
pt = sbis.ParallelTasks()
pt.AddTask(lambda: 42)
pt.AddTask(lambda: "hello, world")
pt.AddInvoke('Тест.Эхо', 'test')
futures = pt.Launch()
# futures[0].Get() == 42
# futures[1].Get() == "hello, world"
# futures[2].Get() == "test"
```

**C++ (краткая форма):**
```cpp
auto func1 = []() -> int { return 5; };
auto func2 = []() -> String { return L"Hello"_s; };
auto [f1, f2] = blcore::LaunchParallelTasks(func1, func2);
// f1.Get() == 5
```

---

## Прочие особенности

- Все параметры передаются в поток **по значению** (копируются). В C++ при передаче указателя — обеспечить потокозащищённость переменной.
- Исключения в дочернем потоке **пробрасываются** в основной при вызове `.get()`.
- В дочерний поток передаются **потокозависимые настройки** (например, стратегия сообщений об ошибках).
- Рекомендуется выполнять другие вычисления **между** запуском `FutureInvoke` и вызовом `.get()`.
- Подробно о future-механизме: [boost documentation](http://www.boost.org/doc/libs/1_53_0/doc/html/thread/synchronization.html#thread.synchronization.futures)

---

## Связанные темы

- [[Wasaby-App-Optimization]] — обзор оптимизации БЛ-слоя
- [[Wasaby-DB-Access-Patterns]] — синхронные и асинхронные запросы к БД
- [[SBIS-Internal-API-Methods]] — внутренние BL-методы (`ПунктПлана`, `СлужЗап`)
- [[Python-Code-Standards-SBIS]] — стандарты кода Python в Wasaby
