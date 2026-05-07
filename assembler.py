import re

def load(filename):
    with open(filename, "r") as file:
        return file.read()

def assemble(filename):
    asm_code = load(filename)
    
    registers = {f'x{i}': i for i in range(32)}
    registers.update({'zero': 0, 'ra': 1, 'sp': 2, 'gp': 3, 'tp': 4, 't0': 5, 't1': 6, 't2': 7})

    isa_map = {
        'addi': {'opcode': 0x13, 'funct3': 0x0}
    }

    program = {}
    lines = [line.strip() for line in asm_code.split('\n') if line.strip()]

    for idx, line in enumerate(lines):
        line = re.split(r'[#;]', line)[0].strip()
        if not line:
            continue

        # Clean up the line and split by whitespace/commas
        parts = re.split(r'[,\s]+', line.lower())
        inst = parts[0]
        rd = registers[parts[1]]
        rs1 = registers[parts[2]]
        imm = int(parts[3], 0)  # Supports both decimal and 0x hex input

        if inst in isa_map:
            conf = isa_map[inst]
            
            # RISC-V i-type instruction:
            # [ imm[11:0] (12b) | rs1 (5b) | funct3 (3b) | rd (5b) | opcode (7b) ]
            
            imm &= 0xFFF
            
            machine_code = (imm << 20) | (rs1 << 15) | (conf['funct3'] << 12) | (rd << 7) | conf['opcode']
            program[idx] = machine_code

    return program
