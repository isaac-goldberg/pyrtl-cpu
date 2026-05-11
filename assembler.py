import re
from instructions import *
from abi import registers

isa_map = {}
def add_type(char, instrs):
    for instr in instrs:
        new_dict = {
            "type": char,
            "opcode": instruction_types[char],
        }
        for key, value in instr.items():
            if key != "name" and key != "op":
                new_dict[key] = value
        isa_map[instr["name"]] = new_dict

add_type("R", r_type_instructions)
add_type("I", i_type_instructions)
add_type("B", b_type_instructions)
add_type("J", j_type_instructions)
add_type("custom", custom_instructions)

def load(filename):
    with open(filename, "r") as file:
        return file.read()

def assemble(filename):
    asm_code = load(filename)
    for i in range(32): 
        registers[f"x{i}"] = i

    program = {}
    lines = [line.strip() for line in asm_code.replace("$", "").split("\n") if line.strip()]

    labels = {}
    instructions = []
    pc = 0

    # first pass for symbols
    for line in lines:
        # remove comments
        line = re.split(r"[#;@]", line)[0].strip()
        if not line: continue

        # labels
        if ":" in line:
            label_part, instr_part = line.split(":", 1)
            labels[label_part.strip().lower()] = pc
            line = instr_part.strip()
            if not line: continue

        parts = re.split(r"[,\s]+", line.lower())
        parts = [p for p in parts if p] # remove empty strings
        instructions.append((pc, parts))
        pc += 4

    # second pass for instructions
    for pc, parts in instructions:
        idx = pc // 4
        inst_name = parts[0]
        
        if inst_name not in isa_map:
            print(f"Warning: Instruction {inst_name} not supported.")
            continue

        info = isa_map[inst_name]
        opcode = instruction_types[info["type"]]

        if info["type"] == "R":
            # format: add rd, rs1, rs2
            rd = registers[parts[1]]
            rs1 = registers[parts[2]]
            rs2 = registers[parts[3]]
            
            machine_code = (info["f7"] << 25) | (rs2 << 20) | (rs1 << 15) | (info["f3"] << 12) | (rd << 7) | opcode
        elif info["type"] == "I":
            # format: addi rd, rs1, imm
            rd = registers[parts[1]]
            rs1 = registers[parts[2]]
            imm_field = 0
            
            if "f7" in info: # bitshifts use funct7
                shamt = int(parts[3], 0) & 0x1F
                f7 = info.get("f7", 0) 
                imm_field = (f7 << 5) | shamt
            else:
                imm_field = int(parts[3], 0) & 0xFFF
                
            machine_code = (imm_field << 20) | (rs1 << 15) | (info["f3"] << 12) | (rd << 7) | opcode
        elif info["type"] == "B":
            # format: beq rs1, rs2, label
            rs1 = registers[parts[1]]
            rs2 = registers[parts[2]]
            target = parts[3]
            
            if target in labels:
                offset = labels[target] - pc
            else:
                offset = int(target, 0)
                
            offset = offset & 0x1FFE
            imm_12 = (offset >> 12) & 0x1
            imm_11 = (offset >> 11) & 0x1
            imm_10_5 = (offset >> 5) & 0x3F
            imm_4_1 = (offset >> 1) & 0xF
            
            machine_code = (imm_12 << 31) | (imm_10_5 << 25) | (rs2 << 20) | (rs1 << 15) | (info["f3"] << 12) | (imm_4_1 << 8) | (imm_11 << 7) | opcode
        elif info["type"] == "J":
            # format: jal rd, label
            rd = registers[parts[1]]
            target = parts[2]
            
            if target in labels:
                offset = labels[target] - pc
            else:
                offset = int(target, 0)
            
            offset = offset & 0x1FFFFFE
            imm_20 = (offset >> 20) & 0x1
            imm_19_12 = (offset >> 12) & 0xFF
            imm_11 = (offset >> 11) & 0x1
            imm_10_1 = (offset >> 1) & 0x3FF
            
            machine_code = (imm_20 << 31) | (imm_10_1 << 21) | (imm_11 << 20) | (imm_19_12 << 12) | (rd << 7) | opcode
        elif info["type"] == "custom":
            # format: ecall code
            code = parts[1]
            code = int(code) & 0xFFF
            
            machine_code = (code << 20) | opcode
        
        program[idx] = machine_code

    return program