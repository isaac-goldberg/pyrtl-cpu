import pyrtl
from assembler import assemble
from instructions_spec import *

pc = pyrtl.Register(bitwidth=32, name='pc')
reg_file = pyrtl.MemBlock(bitwidth=32, addrwidth=5, name='reg_file', asynchronous=True)

program = assemble("./arithmetic.asm")
i_mem = pyrtl.RomBlock(bitwidth=32, addrwidth=32, romdata=program, name='i_mem', asynchronous=True, pad_with_zeros=True)

word_addr = pyrtl.concat(pyrtl.Const(0, 2), pc[2:32])
instr = i_mem[word_addr]

# ---------------------------------------------------------
# INSTRUCTION DECODING
# ---------------------------------------------------------
# used by all
opcode = instr[0:7]

# used by R, I, B, J
rd = instr[7:12]
funct3 = instr[12:15]
rs1 = instr[15:20]

# used by R, B
rs2 = instr[20:25]
funct7 = instr[25:32]

# used by I
i_imm_ext = instr[20:32].sign_extended(32)
shamt = rs2 # alias

# used by B
imm_12 = instr[31:32]
imm_11 = instr[7:8]
imm_10_5 = instr[25:31]
imm_4_1 = instr[8:12]
b_imm_13 = pyrtl.concat(imm_12, imm_11, imm_10_5, imm_4_1, pyrtl.Const(0, 1))
b_imm_ext = b_imm_13.sign_extended(32)

# used by J
j_imm_20 = instr[31:32]
j_imm_19_12 = instr[12:20]
j_imm_11 = instr[20:21]
j_imm_10_1 = instr[21:31]
j_imm_21 = pyrtl.concat(j_imm_20, j_imm_19_12, j_imm_11, j_imm_10_1, pyrtl.Const(0, 1))
j_imm_ext = j_imm_21.sign_extended(32)
# ---------------------------------------------------------

rs1_val = pyrtl.WireVector(32, 'rs1_val')
rs2_val = pyrtl.WireVector(32, 'rs2_val')
with pyrtl.conditional_assignment:
    with rs1 == 0: rs1_val |= 0
    with pyrtl.otherwise: rs1_val |= reg_file[rs1]
    with rs2 == 0: rs2_val |= 0
    with pyrtl.otherwise: rs2_val |= reg_file[rs2]

pc_plus_4 = pc + 4

# ALU execution
alu = pyrtl.WireVector(32, 'alu')
with pyrtl.conditional_assignment:
    for ins in r_type:
        with (opcode == instr_types["R"]) & (ins["f7"] == funct7) & (ins["f3"] == funct3):
            alu |= ins["op"](rs1_val, rs2_val)

    for ins in i_type:
        if "f7" in ins: # bitshifts differentiated by funct7
            with (opcode == instr_types["I"]) & (ins["f3"] == funct3) & (ins["f7"] == funct7):
                alu |= ins["op"](rs1_val, shamt)
        else:
            with (opcode == instr_types["I"]) & (ins["f3"] == funct3):
                alu |= ins["op"](rs1_val, i_imm_ext)
                
    with opcode == instr_types["J"]:
        alu |= pc_plus_4

    with pyrtl.otherwise: alu |= 0

reg_write_enable = (rd != 0) & (opcode != instr_types["B"])
reg_file[rd] <<= pyrtl.MemBlock.EnabledWrite(alu, enable=reg_write_enable)

# PC incrementing or branching
take_branch = pyrtl.WireVector(1)

with pyrtl.conditional_assignment:
    for ins in b_type:
        with (opcode == instr_types["B"]) & (ins["f3"] == funct3):
            take_branch |= ins["op"](rs1_val, rs2_val)
    with pyrtl.otherwise:
        take_branch |= 0

next_pc = pyrtl.WireVector(32, 'next_pc')
with pyrtl.conditional_assignment:
    with (opcode == instr_types["B"]) & (take_branch == 1):
        next_pc |= pc + b_imm_ext
    with opcode == instr_types["J"]:
        next_pc |= pc + j_imm_ext
    with pyrtl.otherwise:
        next_pc |= pc_plus_4

pc.next <<= next_pc

sim_trace = pyrtl.SimulationTrace()
sim = pyrtl.Simulation(tracer=sim_trace)

# clock
MAX_STEPS = 1000000
i = 0
while True:
    if i >= MAX_STEPS:
        break
    
    sim.step({})
    reg_states = sim.inspect_mem(reg_file)
    if reg_states.get(31, 0) == 10: # graceful exit code
        break
    i += 1

# view output
# sim_trace.render_trace(symbol_len=5, segment_size=1)
print("---------------------REGISTER STATES---------------------")
reg_state = sim.inspect_mem(reg_file)
for i in range(32):
    val = reg_state.get(i, 0)
    if val == 0: continue
    
    if val & (1 << 31):
        signed_v = val - (1 << 32)
    else:
        signed_v = val
    
    print(f"x{i} = {signed_v}")
