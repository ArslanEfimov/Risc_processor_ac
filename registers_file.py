from dataclasses import dataclass
from enum import Enum

ALL_REGISTER = ["r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7", "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15"]


@dataclass
class Register(str, Enum):
    R0: "r0"
    R1: "r1"
    R2: "r2"
    R3: "r3"
    R4: "r4"
    R5: "r5"
    R6: "r6"
    R7: "r7"
    R8: "r8"
    R9: "r9"
    R10: "r10"
    R11: "r11"
    R12: "r12"
    R13: "r13"
    R14: "r14"
    R15: "r15"

    def __str__(self) -> str:
        return self.name


def check_is_register(arg: str) -> bool:
    return arg in ALL_REGISTER
