import logging
import re
import sys

from exeptions import RegisterNotFoundError, ValueNotFoundError
from isa import AddressingType, Instruction, Opcode, Term, Variables, write_code
from registers_file import check_is_register

SECTION_DATA = "section .data:"
SECTION_TEXT = "section .text:"


def remove_comments(program_code):
    """Удалить все комментарии из кода."""
    return re.sub(r";.*", "", program_code)


def remove_whitespace(program_code):
    line = program_code.strip()
    cleaned_line = re.sub(r"\s+", " ", line)
    return cleaned_line


def clean_code(program_code):
    code_lines = program_code.splitlines()
    code_lines = [line for line in code_lines if line != ""]
    code_lines_without_comments = map(remove_comments, code_lines)
    clean_code_lines = "\n".join(map(remove_whitespace, code_lines_without_comments))
    return clean_code_lines


def check_is_number(line: str) -> bool:
    """Проверить, является ли строка целым числом."""
    return bool(re.match(r"^-?\d+$", line))


def check_is_string(line: str) -> bool:
    return bool(re.fullmatch(r"^(\".*\")|(\'.*\')$", line))


def translate_section_data(line_data, variables: Variables, address):
    lines = line_data.splitlines()
    for line in lines:
        name, value = map(str.strip, line.split(":", 1))
        if check_is_number(value):
            value = int(value)
            variables[name] = Variables(name, value, address, False)
            address += 1
        elif check_is_string(value):
            chars_array = list(value)
            chars_array = chars_array[1:-1]
            unicode_chars_array = [ord(char) for char in chars_array] + [0]  # в конце 0 терминатор
            variables[name] = Variables(name, unicode_chars_array, address, False)
            address += len(unicode_chars_array)
        elif value.startswith("resb"):
            size = value.split(" ")[1]
            char_buffer = [0] * int(size)
            variables[name] = Variables(name, char_buffer, address, False)
            address += len(char_buffer)
        else:
            address_reference = variables[value].address
            variables[name] = Variables(name, address_reference, address, True, value)
            address += 1

    return variables, address


def parse_arg_and_address_type_for_ld_st(variables: Variables, arg: str):
    label_ref = ""
    if arg in variables.keys():
        label_ref = arg
        arg = variables[arg].address
        address_type = AddressingType.IMMEDIATE.value
    elif arg[0] == "[" and arg[-1] == "]" and arg[1:-1] in variables.keys():
        label_ref = arg[1:-1]
        arg = variables[arg[1:-1]].address
        address_type = AddressingType.INDIRECT.value
    else:
        raise ValueNotFoundError(f"Variable {arg} is not found")
    return arg, address_type, label_ref


def translate_ld_and_st(line_command: str, opcode: str, instr_memory: list[Instruction], variables: Variables, address):
    register = line_command.split(" ")[1]
    if check_is_register(register):
        register_number = register[1:]
        arg = line_command.split(" ")[2]
        arg, arg_type, label_ref = parse_arg_and_address_type_for_ld_st(variables, arg)
        instr_memory.append(
            Instruction(opcode, [register_number, arg], arg_type, Term(address, label_ref, f"{opcode} command"))
        )
    else:
        raise RegisterNotFoundError(f"{register} does not exist")


def translate_binop(line_command: str, opcode: str, instr_memory: list[Instruction], address):
    register = line_command.split(" ")[1]
    register_number = register[1:]
    arg1 = line_command.split(" ")[2]
    arg2 = line_command.split(" ")[3]
    if check_is_register(arg1) and check_is_register(arg2):
        arg1 = arg1[1:]
        arg2 = arg2[1:]
        instr_memory.append(
            Instruction(
                opcode,
                [register_number, arg1, arg2],
                AddressingType.REGISTER.value,
                Term(address, "", f"{opcode} command"),
            )
        )
    else:
        if not check_is_register(arg1):
            raise RegisterNotFoundError(f"{arg1} does not exist")
        if not check_is_register(arg2):
            raise RegisterNotFoundError(f"{arg2} does not exist")


def translate_mov_and_cmp(line_command: str, opcode: str, instr_memory: list[Instruction], address):
    register = line_command.split(" ")[1]
    register_number = register[1:]
    arg = line_command.split(" ")[2]
    address_type = AddressingType.REGISTER.value
    if check_is_register(register):
        if opcode == Opcode.MOVE:
            if arg.startswith("#"):
                address_type = AddressingType.IMMEDIATE.value
        arg = arg[1:]
        instr_memory.append(
            Instruction(opcode, [register_number, arg], address_type, Term(address, "", f"{opcode} command"))
        )
    else:
        raise RegisterNotFoundError(f"{register} does not exist")


def translate_inc_and_dec(line_command: str, opcode: str, instr_memory: list[Instruction], address):
    register = line_command.split(" ")[1]
    register_number = register[1:]
    if check_is_register(register):
        instr_memory.append(
            Instruction(
                opcode, [register_number], AddressingType.REGISTER.value, Term(address, "", f"{opcode} command")
            )
        )
    else:
        raise RegisterNotFoundError(f"{register} does not exist")


def translate_in_out(line_command: str, opcode: str, instr_memory: list[Instruction], address):
    register = line_command.split(" ")[1]
    register_number = register[1:]
    number_port = 0
    if check_is_register(register):
        if opcode == Opcode.OUT:
            number_port = 1
        instr_memory.append(
            Instruction(
                opcode,
                [register_number, number_port],
                AddressingType.PORT_ADDRESSING.value,
                Term(address, "", f"{opcode} command"),
            )
        )
    else:
        raise RegisterNotFoundError(f"{register} does not exist")


def translate_jumps_and_call(line_command: str, opcode: str, instr_memory: list[Instruction], address, labels):
    label = line_command.split(" ")[1]
    if label in labels:
        arg = labels[label]
        instr_memory.append(
            Instruction(opcode, [arg], AddressingType.IMMEDIATE.value, Term(address, f"{label}", f"{opcode} command"))
        )
    else:
        raise ValueNotFoundError(f"Label {label} does not exist")


def translate_section_text(lines_text, variables: Variables, address, instr_memory: list[Instruction], labels):
    lines_text = lines_text.splitlines()
    for line in lines_text:
        opcode = line.split(" ")[0]
        if opcode in [Opcode.LD, Opcode.ST]:
            translate_ld_and_st(line, opcode, instr_memory, variables, address)
            address += 1
        elif opcode in [Opcode.ADD, Opcode.SUB, Opcode.MUL, Opcode.DIV, Opcode.MOD]:
            translate_binop(line, opcode, instr_memory, address)
            address += 1
        elif opcode in [Opcode.CMP, Opcode.MOVE]:
            translate_mov_and_cmp(line, opcode, instr_memory, address)
            address += 1
        elif opcode in [Opcode.INC, Opcode.DEC]:
            translate_inc_and_dec(line, opcode, instr_memory, address)
            address += 1
        elif opcode in [Opcode.JMP, Opcode.JZ, Opcode.JNZ, Opcode.CALL]:
            translate_jumps_and_call(line, opcode, instr_memory, address, labels)
            address += 1
        elif opcode in [Opcode.IN, Opcode.OUT]:
            translate_in_out(line, opcode, instr_memory, address)
            address += 1
        elif opcode in Opcode.RET:
            instr_memory.append(
                Instruction(opcode, "", AddressingType.NON_ADRESSABLE.value, Term(address, "", f"{opcode} command"))
            )
            address += 1
        elif opcode in Opcode.HLT:
            instr_memory.append(
                Instruction(opcode, "", AddressingType.NON_ADRESSABLE.value, Term(address, "", f"{opcode} command"))
            )
    return instr_memory


def saved_all_labels_and_delete(lines_text, address):
    lines_text = lines_text.splitlines()
    labels = {}
    for line in lines_text:
        if line.startswith("."):
            labels[line[0:-1]] = address
            lines_text.remove(line)
        address += 1

    return labels, "\n".join(lines_text)


def convert_data_to_json(variables: Variables, json_code):
    for variable in variables.values():
        if isinstance(variable.value, int) and not variable.has_it_reference:
            json_code.append({"data_section": variable.value, "term": Term(variable.address, "", "int var")})
        elif isinstance(variable.value, list):
            for idx, val in enumerate(variable.value):
                json_code.append({"data_section": val, "term": Term(variable.address + idx, "", "char")})
        else:
            json_code.append({"data_section": variable.value, "term": Term(variable.name_reference, "", "pointer var")})
    return json_code


def convert_text_to_json(instructions: list[Instruction], json_code):
    for instruction in instructions:
        opcode = instruction.opcode
        if opcode in [Opcode.LD, Opcode.ST, Opcode.MOVE, Opcode.CMP, Opcode.IN, Opcode.OUT]:
            register = instruction.args[0]
            arg = instruction.args[1]
            address_type = instruction.address_type
            term = instruction.term
            json_code.append(
                {"opcode": opcode, "register": register, "arg": arg, "addressing": address_type, "term": term}
            )
        elif opcode in [Opcode.ADD, Opcode.SUB, Opcode.MUL, Opcode.DIV, Opcode.MOD]:
            register0 = instruction.args[0]
            register1 = instruction.args[1]
            register2 = instruction.args[2]
            address_type = instruction.address_type
            term = instruction.term
            json_code.append(
                {
                    "opcode": opcode,
                    "register0": register0,
                    "register1": register1,
                    "register2": register2,
                    "addressing": address_type,
                    "term": term,
                }
            )
        elif opcode in [Opcode.INC, Opcode.DEC]:
            register = instruction.args[0]
            address_type = instruction.address_type
            term = instruction.term
            json_code.append({"opcode": opcode, "register": register, "addressing": address_type, "term": term})
        elif opcode in [Opcode.JMP, Opcode.JZ, Opcode.JNZ, Opcode.CALL]:
            arg1 = instruction.args[0]
            address_type = instruction.address_type
            term = instruction.term
            json_code.append({"opcode": opcode, "arg": arg1, "addressing": address_type, "term": term})
        elif opcode in [Opcode.HLT, Opcode.RET]:
            address_type = instruction.address_type
            term = instruction.term
            json_code.append({"opcode": opcode, "addressing": address_type, "term": term})


def translate(program_code):
    clean_code_lines = clean_code(program_code)
    section_data_begin_idx = clean_code_lines.find(SECTION_DATA) + len(SECTION_DATA) + 1
    section_text_begin_idx = clean_code_lines.find(SECTION_TEXT)
    section_data = clean_code_lines[section_data_begin_idx:section_text_begin_idx]
    section_text = clean_code_lines[section_text_begin_idx + (len(SECTION_TEXT) + 1) :]
    variables_data = {}
    instructions = []
    address = 1
    json_machine_code = []
    variables_data, address = translate_section_data(section_data, variables_data, address)

    json_machine_code.append(
        {
            "opcode": Opcode.JMP,
            "arg": address,
            "addressing": AddressingType.IMMEDIATE.value,
            "term": Term(0, ".text", "jmp to instructions"),
        }
    )

    labels, section_text = saved_all_labels_and_delete(section_text, address)
    try:
        instructions = translate_section_text(section_text, variables_data, address, instructions, labels)
    except (ValueNotFoundError, RegisterNotFoundError) as e:
        logging.warning(e)
        return {}
    convert_data_to_json(variables_data, json_machine_code)
    convert_text_to_json(instructions, json_machine_code)
    return json_machine_code


def main(source_file, target_file):
    with open(source_file, encoding="utf-8") as f:
        code = f.read()
    json_machine_code = translate(code)
    write_code(target_file, json_machine_code)
    print(f"source LoC: {len(code.splitlines())}, code instr: {len(json_machine_code)}")


if __name__ == "__main__":
    assert len(sys.argv) == 3, "Usage: python translator.py <source_file> <target_file>"
    _, source_file, target_file = sys.argv
    main(source_file, target_file)
    print("----Translation finished!----")
