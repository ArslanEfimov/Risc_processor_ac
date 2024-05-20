import json
from collections import namedtuple
from enum import Enum

MACHINE_WORD_SIZE = 32
MACHINE_WORD_MAX_VALUE = 2 ** (MACHINE_WORD_SIZE - 1) - 1
MACHINE_WORD_MIN_VALUE = -(2 ** (MACHINE_WORD_SIZE - 1))
MEMORY_SIZE = 2048

class Opcode(str, Enum):
    LD: str = "ld"
    ST: str = "st"
    ADD: str = "add"
    SUB: str = "sub"
    MUL: str = "mul"
    DIV: str = "div"
    MOD: str = "mod"
    CMP: str = "cmp"
    INC: str = "inc"
    DEC: str = "dec"
    JMP: str = "jmp"
    JZ: str = "jz"
    IN: str = "in"
    OUT: str = "out"
    JNZ: str = "jnz"
    MOVE: str = "mov"
    HLT: str = "hlt"

    def __str__(self) -> str:
        """Переопределение стандартного поведения `__str__` для `Enum`: вместо
               `Opcode.INC` вернуть `increment`.
               """
        return str(self.value)


class Variables:
    def __init__(self, name: str, value: list[int] | int, address: int, has_it_reference):
        self.name = name
        self.value = value
        self.address = address
        self.has_it_reference = has_it_reference

    def __str__(self) -> str:
        return f"{self.name}: {self.value} (Address: {self.address})"


class Term(namedtuple("Term", "line label comment")):
    """
    terms
    """


class AddressingType(Enum):
    IMMEDIATE: int = 0
    INDIRECT: int = 1
    REGISTER: int = 2
    NON_ADRESSABLE: int = 3
    PORT_ADDRESSING: int = 4


class Instruction:
    def __init__(self, opcode: Opcode, args: list[str], address_type: int, term: Term):
        self.opcode = opcode
        self.args = args
        self.address_type = address_type
        self.term = term

    def __str__(self):
        return f"opcode: {self.opcode}, args: {' '.join(map(str, self.args))}, addressing: {self.address_type}, term: ({self.term})"


def write_code(filename, code):
    """Записать машинный код в файл."""
    with open(filename, "w", encoding="utf-8") as file:
        buf = []
        for instr in code:
            buf.append(json.dumps(instr))
        file.write("[" + ",\n ".join(buf) + "]")


def read_code(filename):
    """Прочесть машинный код из файла.
    """
    with open(filename, encoding="utf-8") as file:
        code = json.loads(file.read())

    for instr in code:
        # Конвертация строки в Opcode
        if "opcode" in instr:
            instr["opcode"] = Opcode(instr["opcode"])

        # Конвертация списка term в класс Term
        if "term" in instr:
            assert len(instr["term"]) == 3
            instr["term"] = Term(instr["term"][0], instr["term"][1], instr["term"][2])

    return code
