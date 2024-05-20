import logging
from dataclasses import dataclass

from isa import Opcode, MACHINE_WORD_MAX_VALUE, MACHINE_WORD_MIN_VALUE, MEMORY_SIZE
from registers_file import RegistersFile

ALU_OPCODE_BINARY_HANDLERS: dict = {
    Opcode.ADD: lambda left, right: int(left + right),
    Opcode.SUB: lambda left, right: int(left - right),
    Opcode.MUL: lambda left, right: int(left * right),
    Opcode.DIV: lambda left, right: int(left / right),
    Opcode.MOD: lambda left, right: int(left % right),
    Opcode.CMP: lambda left, right: int(left - right),
}

ALU_OPCODE_INC_DEC: dict = {
    Opcode.INC: lambda left: left + 1,
    Opcode.DEC: lambda left: left - 1,
}


@dataclass(frozen=True)
class Port:
    value: int


STDIN: int = Port(0)
STDOUT: int = Port(1)


class ALU:
    flag_z = None

    def __init__(self):
        self.flag_z = 0

    def perform(self, opcode: Opcode, left: int, right: int):
        if opcode in ALU_OPCODE_BINARY_HANDLERS:
            handler = ALU_OPCODE_BINARY_HANDLERS[opcode]
            value = handler(left, right)
        elif opcode in ALU_OPCODE_INC_DEC:
            handler = ALU_OPCODE_INC_DEC[opcode]
            value = handler(left)
        value = self.handle_overflow(self, value)
        self.set_flag(self, value)
        return value

    def set_flag(self, value: int):
        self.flag_z = int(value == 0)

    @staticmethod
    def handle_overflow(self, value: int):
        if value >= MACHINE_WORD_MAX_VALUE:
            return value - MACHINE_WORD_MAX_VALUE
        if value <= MACHINE_WORD_MIN_VALUE:
            return value + MACHINE_WORD_MAX_VALUE
        return value


class IO_CONTROLLER:
    ports = None

    def __init__(self, ports: dict[Port, list[int]]):
        self.ports = ports

    def read(self, port: Port):
        if port in self.ports:
            logging.debug("IN %s", 0)
            return 0
        value = self.ports[port].pop(0)
        logging.debug('IN: %s - "%s"', value, chr(value))
        return value

    def write(self, port: Port, value):
        self.ports[port].append(value)


class DataPath:
    def __init__(self, memory, io_controller: IO_CONTROLLER):
        self.memory = memory
        self.io_controller = io_controller
        self.register_file = RegistersFile
        self.pc = 0
        self.alu: ALU = ALU()
        self.memory_size = MEMORY_SIZE

    def signal_latch_pc(self, value: int):
        self.pc = value

    def read_memory(self, address: int):
        assert address < self.memory_size, f"There is no cell with index in memory {address}"
        return self.memory[address]

    def write_memory(self, address: int, value: int):
        assert address < self.memory_size, f"There is no cell with index in memory {address}"
        self.memory[address] = value


class ControlUnit:
    current_instruction = None

    def __init_(self, data_path: DataPath):
        self.data = data_path
        self.current_instruction: Opcode = None
        self.instruction_executors = {

        }

    def decode_instruction(self):
        instr_out = self.data_path.read_memory(self.data_path.pc)
        self.current_instruction = Opcode(instr_out.get("Opcode"))
        return self.current_instruction

    def execute(self):
        current_instruction = self.decode_instruction(self)
        self.data_path.register_file.latch_ir(current_instruction)
        execute_instruction = self.instruction_executors[current_instruction]
        execute_instruction()
