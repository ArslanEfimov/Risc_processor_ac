from __future__ import annotations
import logging
import sys
from dataclasses import dataclass

from exeptions import EndIterationError, ValueNotFoundError
from isa import MACHINE_WORD_MAX_VALUE, MACHINE_WORD_MIN_VALUE, MEMORY_SIZE, AddressingType, Opcode, read_code
from registers_file import RegistersFile

INSTRUCTION_COUNT = 15000
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

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


STDIN: Port = Port(0)
STDOUT: Port = Port(1)


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
        value = self.handle_overflow(value)
        self.set_flag(value)
        return value

    def set_flag(self, value: int):
        self.flag_z = int(value == 0)

    @staticmethod
    def handle_overflow(value: int):
        if value > MACHINE_WORD_MAX_VALUE:
            return value % MACHINE_WORD_MAX_VALUE
        if value < MACHINE_WORD_MIN_VALUE:
            return value % abs(MACHINE_WORD_MIN_VALUE)
        return value

    @staticmethod
    def get_arg(left: dict) -> int:
        if "arg" in left:
            return left.get("arg")
        raise ValueNotFoundError("ArgumentNotFound")


class IoController:
    ports = None

    def __init__(self, ports: dict[Port, list[int]]):
        self.ports = ports

    def read(self, port: Port):
        if port not in self.ports:
            logging.debug("IN %s", 0)
            return 0
        value = self.ports[port].pop(0)
        if value == 0:
            logging.debug('IN: %s - "%s"\n', value, "")
        else:
            logging.debug('IN: %s - "%s"\n', value, chr(value))
        return value

    def write(self, port: Port, value):
        if 0 <= value <= 127:
            logging.debug('OUT << "%s"\n', chr(value))
        else:
            logging.debug("OUT << %s\n", value)
        self.ports[port].append(value)


class DataPath:
    memory: list = None
    io_controller: IoController = None
    registers: RegistersFile = None
    pc: int = None
    sp: int = None
    alu: ALU = None
    memory_size: int = None

    def __init__(self, memory, io_controller: IoController):
        self.memory = [0 for i in range(MEMORY_SIZE + 1)]
        for i in range(len(memory)):
            self.memory[i] = memory[i]
        self.io_controller = io_controller
        self.register_file = RegistersFile()
        self.pc = 0
        self.sp = MEMORY_SIZE
        self.alu: ALU = ALU()
        self.memory_size = MEMORY_SIZE + 1

    def signal_latch_pc(self, value: int):
        self.pc = value

    def signal_latch_sp(self, value: int):
        self.sp = value

    def signal_read_memory(self, address: int):
        assert address < self.memory_size, f"There is no cell with index in memory {address}"
        return self.memory[address]

    def signal_write_memory(self, address: int, value: int):
        assert address < self.memory_size, f"There is no cell with index in memory {address}"
        if address == self.sp:
            self.memory[address] = value
        else:
            self.memory[address]["data_section"] = value

    def signal_latch_reg_number(self, number: int, value: int):
        if 0 <= number <= 12:
            setattr(self.register_file, f"R{number}", value)
        if number == 13:
            self.register_file.BR = value

    def signal_latch_dr(self, instruction):
        self.register_file.DR = instruction

    def sel_left_out(self, number: int):
        if 0 <= number <= 12:
            self.register_file.left_out = getattr(self.register_file, f"R{number}")
        if number == 13:
            self.register_file.left_out = self.register_file.BR
        if number == 14:
            self.register_file.left_out = self.register_file.DR
        if number == 16:
            self.register_file.left_out = self.pc

    def sel_right_out(self, number: int):
        if 0 <= number <= 12:
            self.register_file.right_out = getattr(self.register_file, f"R{number}")
        if number == 13:
            self.register_file.left_out = self.register_file.BR


class ControlUnit:
    data_path: DataPath = None
    current_instruction = None
    _tick: None

    def __init__(self, data_path: DataPath):
        self.data_path = data_path
        self.current_instruction: Opcode = None
        self._tick = 0

    def __repr__(self):
        # Преобразование всех значений в строки для корректного форматирования
        ticks_str = str(self._tick)
        pc_str = str(self.data_path.pc)
        opcode = str(self.data_path.register_file.DR.get("opcode"))
        br_str = str(self.data_path.register_file.BR)
        sp_str = str(self.data_path.sp)
        z_flag_str = str(self.data_path.alu.flag_z)
        r0 = str(self.data_path.register_file.R0)
        r1 = str(self.data_path.register_file.R1)
        r2 = str(self.data_path.register_file.R2)
        r3 = str(self.data_path.register_file.R3)
        r4 = str(self.data_path.register_file.R4)
        r5 = str(self.data_path.register_file.R5)
        r6 = str(self.data_path.register_file.R6)
        r7 = str(self.data_path.register_file.R7)
        r8 = str(self.data_path.register_file.R8)
        r9 = str(self.data_path.register_file.R9)
        r10 = str(self.data_path.register_file.R10)
        r11 = str(self.data_path.register_file.R11)
        r12 = str(self.data_path.register_file.R12)

        state_repr = (
            "TICK: {:3} | PC {:3} | BR: {:3} | DR: {:3} | SP {:3} | Z_FLAG: {:1} \n | R0: {:2} | R1: {:2} | R2: {:2} "
            "| R3: {:2} | R4: {:2} | R5: {:2} | R6: {:2} | R7: {:2} | R8: {:2} | R9: {:2} | R10: {:2} | R11: {:2} | "
            "R12: {:2} | \n"
        ).format(
            ticks_str, pc_str, br_str, opcode, sp_str, z_flag_str, r0, r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12
        )
        return f"{state_repr}"

    def tick(self):
        self._tick += 1

    def decode_and_execute_instruction(self):
        execute_instruction_handler: dict = {
            Opcode.LD: self.handle_execute_load,
            Opcode.ST: self.handle_execute_store,
            Opcode.ADD: self.handle_execute_math_operation,
            Opcode.SUB: self.handle_execute_math_operation,
            Opcode.DIV: self.handle_execute_math_operation,
            Opcode.MUL: self.handle_execute_math_operation,
            Opcode.CMP: self.handle_execute_cmp,
            Opcode.MOD: self.handle_execute_math_operation,
            Opcode.INC: self.handle_execute_inc_and_dec,
            Opcode.DEC: self.handle_execute_inc_and_dec,
            Opcode.MOVE: self.handle_execute_mov,
            Opcode.IN: self.handle_execute_in,
            Opcode.OUT: self.handle_execute_out,
        }
        # read MEM(PC)
        instr_out = self.data_path.signal_read_memory(self.data_path.pc)
        self.current_instruction = Opcode(instr_out.get("opcode"))
        self.data_path.signal_latch_dr(instr_out)
        self.tick()
        if self.decode_and_execute_control_flow_instruction():
            return
        handler_execute = execute_instruction_handler[self.current_instruction]
        handler_execute()

    def decode_and_execute_control_flow_instruction(self):
        flag_execute = False
        if self.current_instruction in Opcode.JMP:
            self.handle_execute_jmp()
            flag_execute = True
        elif self.current_instruction in Opcode.JZ:
            self.handle_execute_jz()
            flag_execute = True
        elif self.current_instruction in Opcode.JNZ:
            self.handle_execute_jnz()
            flag_execute = True
        elif self.current_instruction in Opcode.CALL:
            self.handle_execute_call()
            flag_execute = True
        elif self.current_instruction in Opcode.RET:
            self.handle_execute_ret()
            flag_execute = True
        elif self.current_instruction in Opcode.HLT:
            self.handle_execute_hlt()
        return flag_execute

    def handle_operand_fetch(self):
        # сохраняем PC в BR
        self.data_path.sel_left_out(16)
        self.data_path.signal_latch_reg_number(13, self.data_path.register_file.left_out)
        self.tick()
        # кладем операнд из DR в PC
        self.data_path.sel_left_out(14)
        self.data_path.signal_latch_pc(self.data_path.alu.get_arg(self.data_path.register_file.left_out))
        self.tick()
        if self.data_path.register_file.DR.get("addressing") == AddressingType.INDIRECT.value:
            address = self.data_path.signal_read_memory(self.data_path.pc).get("data_section")
            self.data_path.signal_latch_pc(address)
            self.tick()

    def handle_execute_load(self):
        self.handle_operand_fetch()
        data = self.data_path.signal_read_memory(self.data_path.pc).get("data_section")
        self.data_path.signal_latch_reg_number(int(self.data_path.register_file.DR.get("register")), data)
        self.tick()
        # BR -> PC+1
        self.data_path.sel_left_out(13)
        self.data_path.signal_latch_pc(self.data_path.register_file.left_out + 1)
        self.tick()
        logging.debug("%s", self.__repr__())

    def handle_execute_store(self):
        self.handle_operand_fetch()
        register = int(self.data_path.register_file.DR.get("register"))
        self.data_path.sel_left_out(register)
        self.data_path.signal_write_memory(self.data_path.pc, self.data_path.register_file.left_out)
        self.tick()
        self.data_path.sel_left_out(13)
        self.data_path.signal_latch_pc(self.data_path.register_file.left_out + 1)
        self.tick()
        logging.debug("%s", self.__repr__())

    def handle_execute_math_operation(self):
        opcode = self.data_path.register_file.DR.get("opcode")
        reg1 = int(self.data_path.register_file.DR.get("register1"))
        reg2 = int(self.data_path.register_file.DR.get("register2"))
        self.data_path.sel_left_out(reg1)
        self.data_path.sel_right_out(reg2)
        result_operation = self.data_path.alu.perform(
            opcode, self.data_path.register_file.left_out, self.data_path.register_file.right_out
        )
        reg0 = int(self.data_path.register_file.DR.get("register0"))
        self.data_path.signal_latch_reg_number(reg0, result_operation)
        self.tick()
        self.data_path.signal_latch_pc(self.data_path.pc + 1)
        self.tick()
        logging.debug("%s", self.__repr__())

    def handle_execute_cmp(self):
        opcode = self.data_path.register_file.DR.get("opcode")
        reg0 = int(self.data_path.register_file.DR.get("register"))
        reg1 = int(self.data_path.register_file.DR.get("arg"))
        self.data_path.sel_left_out(reg0)
        self.data_path.sel_right_out(reg1)
        self.data_path.alu.perform(
            opcode, self.data_path.register_file.left_out, self.data_path.register_file.right_out
        )
        self.tick()
        self.data_path.signal_latch_pc(self.data_path.pc + 1)
        self.tick()
        logging.debug("%s", self.__repr__())

    def handle_execute_inc_and_dec(self):
        opcode = self.data_path.register_file.DR.get("opcode")
        register = int(self.data_path.register_file.DR.get("register"))
        self.data_path.sel_left_out(register)
        result = self.data_path.alu.perform(opcode, self.data_path.register_file.left_out, None)
        self.data_path.signal_latch_reg_number(register, result)
        self.tick()
        self.data_path.signal_latch_pc(self.data_path.pc + 1)
        self.tick()
        logging.debug("%s", self.__repr__())

    def handle_execute_mov(self):
        addressing = self.data_path.register_file.DR.get("addressing")
        register = int(self.data_path.register_file.DR.get("register"))
        if addressing == AddressingType.REGISTER.value:
            register2 = int(self.data_path.register_file.DR.get("arg"))
            self.data_path.sel_left_out(register2)
            self.data_path.signal_latch_reg_number(register, self.data_path.register_file.left_out)
            self.tick()
        else:
            self.data_path.sel_left_out(14)
            self.data_path.signal_latch_reg_number(
                register, int(self.data_path.alu.get_arg(self.data_path.register_file.left_out))
            )
            self.tick()
        self.data_path.signal_latch_pc(self.data_path.pc + 1)
        self.tick()
        logging.debug("%s", self.__repr__())

    def handle_execute_hlt(self):
        logging.debug("%s", self.__repr__())
        raise EndIterationError()

    def handle_execute_jmp(self):
        self.data_path.sel_left_out(14)
        self.data_path.signal_latch_pc(self.data_path.alu.get_arg(self.data_path.register_file.left_out))
        self.tick()
        logging.debug("%s", self.__repr__())

    def handle_execute_jz(self):
        if self.data_path.alu.flag_z == 1:
            self.data_path.sel_left_out(14)
            self.data_path.signal_latch_pc(self.data_path.alu.get_arg(self.data_path.register_file.left_out))
            self.tick()
        else:
            self.data_path.signal_latch_pc(self.data_path.pc + 1)
            self.tick()
        logging.debug("%s", self.__repr__())

    def handle_execute_jnz(self):
        if self.data_path.alu.flag_z == 0:
            self.data_path.sel_left_out(14)
            self.data_path.signal_latch_pc(self.data_path.alu.get_arg(self.data_path.register_file.left_out))
            self.tick()
        else:
            self.data_path.signal_latch_pc(self.data_path.pc + 1)
            self.tick()
        logging.debug("%s", self.__repr__())

    def handle_execute_call(self):
        self.data_path.signal_write_memory(self.data_path.sp, self.data_path.pc)
        self.tick()
        self.data_path.signal_latch_sp(self.data_path.sp - 1)
        self.tick()
        self.data_path.sel_left_out(14)
        self.data_path.signal_latch_pc(self.data_path.alu.get_arg(self.data_path.register_file.left_out))
        self.tick()
        logging.debug("%s", self.__repr__())

    def handle_execute_ret(self):
        self.data_path.signal_latch_sp(self.data_path.sp + 1)
        self.tick()
        address_ret = self.data_path.signal_read_memory(self.data_path.sp)
        self.data_path.signal_latch_pc(address_ret + 1)
        self.tick()
        logging.debug("%s", self.__repr__())

    def handle_execute_in(self):
        self.data_path.sel_left_out(14)
        port = Port(int(self.data_path.alu.get_arg(self.data_path.register_file.left_out)))
        register = int(self.data_path.register_file.DR.get("register"))
        if port == STDIN:
            self.data_path.signal_latch_reg_number(register, self.data_path.io_controller.read(port))
            self.tick()
            self.data_path.signal_latch_pc(self.data_path.pc + 1)
            self.tick()
        logging.debug("%s", self.__repr__())

    def handle_execute_out(self):
        self.data_path.sel_left_out(14)
        port = Port(int(self.data_path.alu.get_arg(self.data_path.register_file.left_out)))
        register = int(self.data_path.register_file.DR.get("register"))
        if port == STDOUT:
            self.data_path.sel_left_out(register)
            self.data_path.io_controller.write(port, self.data_path.register_file.left_out)
            self.tick()
            self.data_path.signal_latch_pc(self.data_path.pc + 1)
            self.tick()
        logging.debug("%s", self.__repr__())


def simulation(code, user_input: list[int]):
    io_o = IoController({STDIN: user_input, STDOUT: []})
    data_path = DataPath(code, io_o)
    control_unit = ControlUnit(data_path)

    instruction_counter = 0
    try:
        while instruction_counter < INSTRUCTION_COUNT:
            instruction_counter += 1
            control_unit.decode_and_execute_instruction()
    except (EndIterationError, ValueNotFoundError):
        pass

    return data_path.io_controller.ports[STDOUT], instruction_counter, control_unit._tick


def main(machine_code, file_user_input):
    code = read_code(machine_code)
    user_input: list[int]
    with open(file_user_input) as f:
        file_line = f.read()
        user_input = [ord(c) for c in file_line] + [0]

    output, instruction_count, ticks = simulation(code, user_input)
    if isinstance(output, list) and all(isinstance(i, int) and 0 <= i <= 127 for i in output):
        print("".join([chr(c) for c in output]))
    else:
        print("\n".join([str(c) for c in output]))
    print(f"Instruction count: {instruction_count}, ticks: {ticks}")


if __name__ == "__main__":
    source_file = sys.argv[1]
    file_user_input = sys.argv[2]
    main(source_file, file_user_input)
