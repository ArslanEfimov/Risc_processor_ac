from dataclasses import dataclass
from enum import Enum

ALL_REGISTER = ["r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7", "r8", "r9", "r10", "r11", "r12"]


@dataclass
class RegistersFile:
    R0 = 0
    R1 = 0
    R2 = 0
    R3 = 0
    R4 = 0
    R5 = 0
    R6 = 0
    R7 = 0
    R8 = 0
    R9 = 0
    R10 = 0
    R11 = 0
    R12 = 0
    BR = 0
    DR = {}  # Instruction register
    left_out = 0
    right_out = 0

    def __str__(self) -> str:
        return self.value


def check_is_register(arg: str) -> bool:
    return arg in ALL_REGISTER
