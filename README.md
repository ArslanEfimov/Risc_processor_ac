# risc_machine
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