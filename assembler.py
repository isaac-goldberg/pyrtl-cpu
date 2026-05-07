import re
from instructions_spec import *

isa_map = {}
def add_type(char, instrs):
    for instr in instrs:
        new_dict = {
            "type": char,
            "opcode": instr_types[char],
        }
        for key, value in instr.items():
            if key != "name" and key != "op":
                new_dict[key] = value
        isa_map[instr["name"]] = new_dict
add_type("R", r_type)
add_type("I", i_type)

def load(filename):
    with open(filename, "r") as file:
        return file.read()

def assemble(filename):
    asm_code = load(filename)
    
    # named registers map
    registers = {
        'zero': 0, 'ra': 1, 'sp': 2, 'gp': 3, 'tp': 4,
        't0': 5, 't1': 6, 't2': 7, 's0': 8, 'fp': 8, 's1': 9,
        'a0': 10, 'a1': 11, 'a2': 12, 'a3': 13, 'a4': 14, 'a5': 15, 'a6': 16, 'a7': 17,
        's2': 18, 's3': 19, 's4': 20, 's5': 21, 's6': 22, 's7': 23, 's8': 24, 's9': 25, 's10': 26, 's11': 27,
        't3': 28, 't4': 29, 't5': 30, 't6': 31
    }
    for i in range(32): 
        registers[f'x{i}'] = i

    program = {}
    lines = [line.strip() for line in asm_code.split('\n') if line.strip()]

    for idx, line in enumerate(lines):
        line = re.split(r'[#;]', line)[0].strip()
        if not line: continue

        parts = re.split(r'[,\s]+', line.lower())
        inst_name = parts[0]
        
        if inst_name not in isa_map:
            print(f"Warning: Instruction {inst_name} not supported.")
            continue

        info = isa_map[inst_name]
        rd = registers[parts[1]]
        rs1 = registers[parts[2]]

        opcode = instr_types[info["type"]]

        if info['type'] == 'R':
            # funct7, rs2, rs1, funct3, rd, opcode
            rs2 = registers[parts[3]]
            machine_code = (info['f7'] << 25) | (rs2 << 20) | (rs1 << 15) | (info['f3'] << 12) | (rd << 7) | opcode
            
        elif info['type'] == 'I':
            # imm, rs1, funct3, rd, opcode
            imm = int(parts[3], 0) & 0xFFF # 12 bits for imm
            machine_code = (imm << 20) | (rs1 << 15) | (info['f3'] << 12) | (rd << 7) | opcode

        program[idx] = machine_code

    return program