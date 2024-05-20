from dataclasses import dataclass
from enum import Enum

ALL_REGISTER = ["r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7", "r8", "r9", "r10", "r11", "r12", "r13", "ar", "ic"]


@dataclass
class RegistersFile(str, Enum):
    R0: None
    R1: None
    R2: None
    R3: None
    R4: None
    R5: None
    R6: None
    R7: None
    R8: None
    R9: None
    R10: None
    R11: None
    R12: None
    R13: None
    AR: None  #address register
    IR: None  #Instruction register

    left_out: None
    right_out: None

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
        self.R13 = 0
        self.AR = 0
        self.IR = {}
        self.right_out = 0

    def latch_register_n(self, number: int, value: int):
        if 0 <= number <= 13:
            setattr(self, f"R{number}", value)
        elif number == 14:
            self.AR = value

    def latch_ir(self, instruction):
        self.IR = instruction

    def sel_left_reg(self, number: int):
        if 0 <= number <= 13:
            self.left_out = getattr(self, f"R{number}")
        elif number == 14:
            self.left_out = self.AR
        elif number == 15:
            self.left_out = self.IR

    def sel_right_reg(self, number: int):
        if 0 <= number <= 13:
            self.right_out = getattr(self, f"R{number}")
        elif number == 14:
            self.right_out = self.AR

    def __str__(self) -> str:
        return self.name


def check_is_register(arg: str) -> bool:
    return arg in ALL_REGISTER
