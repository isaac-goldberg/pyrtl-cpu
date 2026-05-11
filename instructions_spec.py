import pyrtl

instr_types = {
    "R": 0x33,
    "I": 0x13,
    "B": 0x62,
    "J": 0x6F,
    "custom": 0x73,
}

r_type = [
    {
        "name": "add",
        "f3": 0x0,
        "f7": 0x0,
        "op": lambda a, b: a + b
    },
    {
        "name": "sub",
        "f3": 0x0,
        "f7": 0x20,
        "op": lambda a, b: a - b
    },
    {
        "name": "xor",
        "f3": 0x4,
        "f7": 0x0,
        "op": lambda a, b: a ^ b
    },
    {
        "name": "or",
        "f3": 0x6,
        "f7": 0x0,
        "op": lambda a, b: a | b
    },
    {
        "name": "and",
        "f3": 0x7,
        "f7": 0x0,
        "op": lambda a, b: a & b
    },
    {
        "name": "sll",
        "f3": 0x1,
        "f7": 0x0,
        "op": lambda a, b: pyrtl.shift_left_logical(a, b)
    },
    {
        "name": "srl",
        "f3": 0x5,
        "f7": 0x0,
        "op": lambda a, b: pyrtl.shift_right_logical(a, b)
    },
    {
        "name": "sra",
        "f3": 0x5,
        "f7": 0x20,
        "op": lambda a, b: pyrtl.shift_right_arithmetic(a, b)
    },
    {
        "name": "slt",
        "f3": 0x2,
        "f7": 0x0,
        "op": lambda a, b: pyrtl.signed_lt(a, b)
    },
    {
        "name": "sltu",
        "f3": 0x3,
        "f7": 0x0,
        "op": lambda a, b: a < b
    },
]

i_type = [
    {
        "name": "addi",
        "f3": 0x0,
        "op": lambda a, imm: a + imm,
    },
    {
        "name": "xori",
        "f3": 0x4,
        "op": lambda a, imm: a ^ imm,
    },
    {
        "name": "ori",
        "f3": 0x6,
        "op": lambda a, imm: a | imm,
    },
    {
        "name": "andi",
        "f3": 0x7,
        "op": lambda a, imm: a & imm,
    },
    {
        "name": "slli",
        "f3": 0x1,
        "f7": 0x0,
        "op": lambda a, shamt: pyrtl.shift_left_logical(a, shamt),
    },
    {
        "name": "srli",
        "f3": 0x5,
        "f7": 0x0,
        "op": lambda a, shamt: pyrtl.shift_right_logical(a, shamt),
    },
    {
        "name": "srai",
        "f3": 0x5,
        "f7": 0x20,
        "op": lambda a, shamt: pyrtl.shift_right_arithmetic(a, shamt), 
    },
    {
        "name": "slti",
        "f3": 0x2,
        "op": lambda a, imm: pyrtl.signed_lt(a, imm),
    },
    {
        "name": "sltiu",
        "f3": 0x3,
        "op": lambda a, imm: a < imm,
    }
]

b_type = [
    {
        "name": "beq",
        "f3": 0x0,
        "op": lambda a, b: a == b,
    }
]

j_type = [
    {
        "name": "jal",
    }
]

custom = [
    {
        "name": "ecall",
    }
]