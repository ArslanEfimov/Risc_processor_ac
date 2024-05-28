from dataclasses import dataclass

ALL_REGISTER = ["r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7", "r8", "r9", "r10", "r11", "r12"]


@dataclass
class RegistersFile:
    R0: int = None
    R1: int = None
    R2: int = None
    R3: int = None
    R4: int = None
    R5: int = None
    R6: int = None
    R7: int = None
    R8: int = None
    R9: int = None
    R10: int = None
    R11: int = None
    R12: int = None
    BR: int = None
    DR: dict = None  # Instruction register
    left_out = None
    right_out: int = None

    def __init__(self):
        self.R0 = 0
        self.R1 = 0
        self.R2 = 0
        self.R3 = 0
        self.R4 = 0
        self.R5 = 0
        self.R6 = 0
        self.R7 = 0
        self.R8 = 0
        self.R9 = 0
        self.R10 = 0
        self.R11 = 0
        self.R12 = 0
        self.BR = 0
        self.DR = {}
        self.right_out = 0


def check_is_register(arg: str) -> bool:
    return arg in ALL_REGISTER
