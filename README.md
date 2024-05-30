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

|   Команды   |                                                     Описание команды                                                      |
|:-----------:|:-------------------------------------------------------------------------------------------------------------------------:|
|  `ld a b`   |                                  Загрузка значения из памяти по адресу `b` в регистр `a`                                  |
| `ld a [b]`  |                          Загрузка значения из памяти по адресу, находящемся в `b` в регистр `a`                           |
|  `st a b`   |                                Сохранение значения из регистра `a` в память по адресу `b`                                 |
| `st a [b]`  |                         Сохранение значения из регистра `a` в память по адресу, находящемся в `b`                         |
| `add a b c` |                        Сложение содержимого регситров `b` и `c` и запись результата в регситр `a`                         |
| `sub a b c` |                   Вычитание содержимого из регситра `b` регистра `c` и запись результата в регситр `a`                    |
| `mul a b c` |                       Произведение содержимого регистров `b` и `c` и запись результат в регистр `a`                       |
| `div a b c` |        Целочисленное деление содержимого регситра `b` на содержимое регистра `c` и запись результат в регситр `a`         |
| `mod a b c` |          Деление с остатком содержимого регситра `b` на содержимое регистра `c` и запись результат в регситр `a`          |
|  `cmp a b`  | Сравнение содержимого регистров `a` и `b`, выполнение операции (`a-b`) и выставление флага `zero` по результату сравнения |
|   `inc a`   |                          Инкремент содержимого регистра `a`, то есть увеличение на 1. `a -> a+1`                          |
|   `dec a`   |                          Декремент содержимого регистра `a`, то есть уменьшение на 1. `a -> a-1`                          |
|   `jmp a`   |                                             Безусловный переход на адрес `a`                                              |
|   `jz a`    |                              Условный переход на адрес `a`, если установлен флаг `zero = 1`                               |
|   `jnz a`   |                                    Условный переход на адрес `a`, если флаш `zero = 0`                                    |
|  `in a b`   |                                        Чтение значения из порта `b` в регистр `a`                                         |
|  `out a b`  |                                        Запись содержимого регистра `a` в порт `b`                                         |
|  `mov a b`  |              Загрузка значения из регистра `b` в регистр `a` или прямая загрузка значения `b` в регистр `a`               |
|  `call a`   |                                         Вызов подпрограммы по указанной метке `a`                                         |
|    `ret`    |                                                  Возврат из подпрограммы                                                  |
|    `hlt`    |                                                     Останов программы                                                     |




