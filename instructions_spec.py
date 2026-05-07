import pyrtl

instr_types = {
    "R": 0b0110011,
    "I": 0b0010011,
}

r_type = [
    {
        "name": "add",
        "f7": 0b0000000,
        "f3": 0b000,
        "op": lambda a, b: a + b
    },
    {
        "name": "sub",
        "f7": 0b0100000,
        "f3": 0b000,
        "op": lambda a, b: a - b
    },
    {
        "name": "sll",
        "f7": 0b0000000,
        "f3": 0b001,
        "op": lambda a, b: pyrtl.shift_left_logical(a, b)
    },
    # "slt": {
    #     "f7": 0b0000000,
    #     "f3": 0b010,
    #     "op": lambda a, b: 1 if a < b else 0
    # },
    # "sltu": {
    #     "f7": 0b0000000,
    #     "f3": 0b011,
    #     "op": lambda a, b: 1 if (a & 0xFFFFFFFF) < (b & 0xFFFFFFFF) else 0
    # },
    # "or": {
    #     "f7": 0b0000000,
    #     "f3": 0b110,
    #     "op": lambda a, b: a | b
    # },
    # "and": {
    #     "f7": 0b0000000,
    #     "f3": 0b111,
    #     "op": lambda a, b: a & b
    # },
    # "xor": {
    #     "f7": 0b0000000,
    #     "f3": 0b100,
    #     "op": lambda a, b: a ^ b
    # },
    # "srl": {
    #     "f7": 0b0000000,
    #     "f3": 0b101,
    #     "op": lambda a, b: pyrtl.shift_right_logical(a, b)
    # },
    # "sra": {
    #     "f7": 0b0100000,
    #     "f3": 0b101,
    #     "op": lambda a, b: a >> (b & 0x1F)
    # },
]

i_type = [
    {
        "name": "addi",
        "f3": 0b000,
        "op": lambda a, imm: a + imm,
    },
]

# format: (f3): operation(a, imm)
# i_type = {
#     0b000: lambda a, imm: a + imm, # addi
#     0b111: lambda a, imm: a & imm, # andi
#     0b110: lambda a, imm: a | imm, # ori
#     0b100: lambda a, imm: a ^ imm, # xori
#     0b010: lambda a, imm: a < imm, # slti
#     0b011: lambda a, imm: a < imm, # sltiu
#     # Shifts
#     # 0b001: lambda a, imm: a << (imm & 0b11111),                     # SLLI
#     # 0b101: lambda a, imm: a >> (imm & 0b11111) if (imm & 0b100000) == 0 else a.signed_right_shift(imm & 0b11111),   # SRLI / SRAI
# }