# Simple risc processor
- Ефимов Арслан Альбертович, P3232
- lisp -> asm | risc | neum | hw | instr | struct | stream | port | cstr | prob2 | cache
- Упрощенный вариант:
- asm | risc | neum | hw | instr | struct | stream | port | cstr | prob2 |

## Язык программирования
Синтаксис в расширенной БНФ:

```ebnf
<program> ::= <data_section> "\n" <text_section>

<data_section> ::= "section" "." "data" ":" [comment] "\n" {data}
<text_section> ::= "section" "." "text" ":" [comment] "\n" {instruction}

<data> ::= <identifier> ":" <data_value>

<data_value> ::= | <number>
                 | <string>
                 | "resb" <positive_integer>
                 | [<comment>]
                 
<instruction> ::= | ld <register> <address>
                  | st <register> <address>
                  | add <register> <register> <register>
                  | sub <register> <register> <register>
                  | mul <register> <register> <register>
                  | div <register> <register> <register>
                  | mod <register> <register> <register>
                  | cmp <register> <register> 
                  | inc <register> 
                  | dec <register>
                  | jmp <label>
                  | jz <label>
                  | jnz <label>
                  | in <register> <port>
                  | out <register> <port>
                  | mov <register> <argument>
                  | call <label>
                  | ret
                  | hlt
                  | <label_definition>
                  | [<comment>]

<digit> ::= [0-9]

<port> ::= "0" | "1"

<address> ::= "[" <identifier> "]" | <identifier>

<identifier> ::= <letter> { <letter> | <digit> }

<positive_integer> ::= <digit> { <digit> }

<number> ::= ["-"] <positive_integer>

<letter> ::= [a-zA-Z]

<comment> ::= ";" { <any symbol except "\n"> }

<argument> ::= <register> | #<number>

<register> ::= "r" <positive_integer>

<label> ::= "." <identifier>

<label_definition> ::= <label> ":"

<string> ::= "\"" { <character> } "\""

<character> ::= <letter> | <digit> | <special_char>

<special_char> ::= "." | "," | ";" | ":" | "!" | "?" | "'" | "(" | ")" | "[" | "]" | "{" | "}" | "+" | "-" | "*" | "/" | "=" | "<" | ">" | " " | "\t"
```

Команды:

| Команды     |                                                     Описание команды                                                      |
|:------------|:-------------------------------------------------------------------------------------------------------------------------:|
| `ld a b`    |                                  Загрузка значения из памяти по адресу `b` в регистр `a`                                  |
| `ld a [b]`  |                          Загрузка значения из памяти по адресу, находящемся в `b` в регистр `a`                           |
| `st a b`    |                                Сохранение значения из регистра `a` в память по адресу `b`                                 |
| `st a [b]`  |                         Сохранение значения из регистра `a` в память по адресу, находящемся в `b`                         |
| `add a b c` |                        Сложение содержимого регситров `b` и `c` и запись результата в регситр `a`                         |
| `sub a b c` |                   Вычитание содержимого из регситра `b` регистра `c` и запись результата в регситр `a`                    |
| `mul a b c` |                       Произведение содержимого регистров `b` и `c` и запись результат в регистр `a`                       |
| `div a b c` |        Целочисленное деление содержимого регситра `b` на содержимое регистра `c` и запись результат в регситр `a`         |
| `mod a b c` |          Деление с остатком содержимого регситра `b` на содержимое регистра `c` и запись результат в регситр `a`          |
| `cmp a b`   | Сравнение содержимого регистров `a` и `b`, выполнение операции (`a-b`) и выставление флага `zero` по результату сравнения |
| `inc a`     |                          Инкремент содержимого регистра `a`, то есть увеличение на 1. `a -> a+1`                          |
| `dec a`     |                          Декремент содержимого регистра `a`, то есть уменьшение на 1. `a -> a-1`                          |
| `jmp a`     |                                             Безусловный переход на адрес `a`                                              |
| `jz a`      |                              Условный переход на адрес `a`, если установлен флаг `zero = 1`                               |
| `jnz a`     |                                    Условный переход на адрес `a`, если флаш `zero = 0`                                    |
| `in a b`    |                                        Чтение значения из порта `b` в регистр `a`                                         |
| `out a b`   |                                        Запись содержимого регистра `a` в порт `b`                                         |
| `mov a b`   |              Загрузка значения из регистра `b` в регистр `a` или прямая загрузка значения `b` в регистр `a`               |
| `call a`    |                                         Вызов подпрограммы по указанной метке `a`                                         |
| `ret`       |                                                  Возврат из подпрограммы                                                  |
| `hlt`       |                                                     Останов программы                                                     |

Память выделяется статически при запуске модели, видимость данных -- глобальная. Виды литералов -- строковые и целочисленные

## Организация памяти
- Память соответствует фон Неймановской архитектуре
- Размер машинного слова - 32 бита.
- Модель включает в себя 15 регистров
- Все инструкции фиксированной длины
```text

           memory
+----------------------------+
| 00 : jmp n                 |
| 01 : data                  |
| 02 : ...                   |
| 03 : ...                   |
| n  : program start         | 
|                            |
|           ...              |
|                            |
|           ...              |
+----------------------------+
```
- Ячейка `0` соответствует инструкции `jmp`, осуществляющая переход на адрес первой инструкции в программе
- С ячейки памяти `1` начинается секция `.data`. Переменные могут быть четырех типов:
    - `Строковые` -- под которые отводится `n+1` ячеек памяти, где последняя (доп. символ) -- `нуль-терминатор`
    - `Целочисленные` -- под них отводится одна ячейка памяти
    - `Ссылочные` -- указывают на адрес другой переменной, под них отводится одна ячейка памяти
    - `Буферные` -- под них отводится `n` последовательных ячеек памяти, где `n` - значение из запроса на выделение [`resb n`]
- Переменные располагаются в памяти также последовательно, так, как прописаны в коде
- С ячейки памяти `n` начинается секция `.text`. В ней последовательно расположены инструкции

Регистры:
```text
+----------------------------+
|         Registers          |
+----------------------------+
|            r0              |
+----------------------------+
|            r1              |
+----------------------------+
|            r2              |
+----------------------------+
|            r3              |
+----------------------------+
|            r4              |
+----------------------------+
|            r5              |
+----------------------------+
|            r6              |
+----------------------------+
|            r7              |
+----------------------------+
|            r8              |
+----------------------------+
|            r9              |
+----------------------------+
|            r10             |
+----------------------------+
|            r11             |
+----------------------------+
|            r12             |
+----------------------------+
|            r13 - BR        |
+----------------------------+
|            r14 - DR        |
+----------------------------+

```
- Регистры `r0-r12` общего назначения и они могут быть использованы программистом как угодно
- Регистр `r13` -- это буферный регистр `BR`, используется для сохранения `PC` во время адресных инструкций `ld` и `st` (не доступен программисту)
- Регистр `r14` -- это регистр данных `DR`, в него сохраняются считанные инструкции (не доступен программисту)
- Регистры находятся в регистровом файле `RegistersFile`

## Система команд
- Машинное слово -- 32 бита
- Доступ к памяти осуществляется по адресу, находящемся в регистре `PC` -- programm counter. Установка адреса реализуется следующими способами:
    - Увеличение `PC` на `1`
    - Непосредственно из самого `ALU`
- Поддерживаются следующие виды адресации:
  - Абсолютная
  - Косвенная
  - Регистровая
  - Портовая

Также команда может быть безадресной
  
- Ввод-вывод осуществляется как поток токенов, port-mapped, управление вводом-выводом осуществляется с помощью `IO_CONTROLLER`.
Чтение происходит в регистр, запись также происходит из регистра.
- Поток управления:
  - Условные и безусловные переходы (`jz`, `jnz`, `jmp`)
  - Если инструкция это не переход, то после нее инкрементируем `PC`
- Способ кодирования инструкций - `struct`, использование `json` формата

## Набор инструкций
- Декодирование инструкций выполняется за `1` такт
- Выборка операнда или адреса зависит от типа адресации:
    - Прямая адресация - `2` такта
    - Косвенная адресация - `3` такта

| **Мнемоника** | Кол-во тактов | Описание                                                                                 |
|:-------------:|:-------------:|:-----------------------------------------------------------------------------------------|
|     `ld`      |      `2`      | Загружает значение из памяти по адресу в регистр                                         |
|     `st`      |      `2`      | Сохраняет значение из регистра в память по адресу                                        |
|     `add`     |      `2`      | Складывает значение двух регистров и сохраняет в третий                                  |
|     `sub`     |      `2`      | Вычитает значение одного регистра из другого и сохраняет в третий                        |
|     `div`     |      `2`      | Целочисленно делит значение одного регистра из другого и сохраняет в третий              |
|     `mul`     |      `2`      | Умножает значение одного регистра из другого и сохраняет в третий                        |
|     `mod`     |      `2`      | Делит с остатком значение одного регистра из другого и сохраняет в третий                |
|     `cmp`     |      `2`      | Сравнивает значения двух регистров путем вычитания и выставляет флаг `zero`              |
|     `inc`     |      `2`      | Увеличивает значение регистра на `1`                                                     |
|     `dec`     |      `2`      | Уменьшает значение регистра на `1`                                                       |
|     `jmp`     |      `1`      | Безусловный переход по адресу метки                                                      |
|     `jz`      |      `1`      | Условный переход по адресу метки, если `zero` == 1                                       |
|     `jnz`     |      `1`      | Условный переход по адресу метки, если `zero` == 0                                       |
|     `in`      |      `2`      | Прочитать значение по указанному порту в регистр                                         |
|     `out`     |      `2`      | Записать значение по указанному порту из регистра                                        |
|     `mov`     |      `2`      | Загрузка значения из регистра в регистр или непосредственная загрузка значения в регистр |
|    `call`     |      `3`      | Вызов подпрограммы, значение `PC` на вершину стека                                       |
|     `ret`     |      `2`      | Возврат из подпрограммы, возврщаем из вершины стека `PC`                                 |
|     `hlt`     |      `0`      | Останов программы                                                                        |

## Способ кодирования инструкций
- Машинный код сериализуется в список JSON.
- Один элемент списка - одна инструкция.

Пример:
```text
[
    {
        "opcode": "jz", 
        "arg": 4, 
        "addressing": 0, 
        "term": [
            6, 
            ".end", 
            "jz command"
        ]
    }
]
```
где:
- `opcode` -- строка с кодом операции
- `arg` -- аргумент инструкции (может отсутствовать)
- `addressing` -- тип адресации инструкции
- `term` -- кортежи для удобного восприятия машинного кода
    - `term[0]` -- индекс инструкции в памяти
    - `term[1]` -- метки, которые присутствуют в командах перехода
    - `term[2]` -- комментарии (опционально)
  
Типы данных в модуле [isa](./isa.py), где:

- `Opcode` -- перечисление кодов оперций;
- `Term` -- структура для описания фрагментов кода

## Транслятор
