import pyrtl
from assembler import assemble
from instructions import *
from program import get_program

pc = pyrtl.Register(bitwidth=32, name='pc')
reg_file = pyrtl.MemBlock(bitwidth=32, addrwidth=5, name='reg_file', asynchronous=True)

# program = assemble("./matrix.asm")
program = assemble(get_program())
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
i_imm = instr[20:32]
i_imm_ext = i_imm.sign_extended(32)
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

# used by custom instructions
ecall_code = instr[20:32]
# ---------------------------------------------------------

rs1_val = pyrtl.WireVector(32, 'rs1_val')
rs2_val = pyrtl.WireVector(32, 'rs2_val')
with pyrtl.conditional_assignment:
    with rs1 == 0: rs1_val |= 0
    with pyrtl.otherwise: rs1_val |= reg_file[rs1]
    with rs2 == 0: rs2_val |= 0
    with pyrtl.otherwise: rs2_val |= reg_file[rs2]

pc_plus_4 = pc + 4

# ALU execution, R and I type instructions
alu = pyrtl.WireVector(32, "alu")
with pyrtl.conditional_assignment:
    for ins in r_type_instructions:
        with (opcode == instruction_types["R"]) & (ins["f7"] == funct7) & (ins["f3"] == funct3):
            alu |= ins["op"](rs1_val, rs2_val)

    for ins in i_type_instructions:
        if "f7" in ins: # bitshifts use funct7
            with (opcode == instruction_types["I"]) & (ins["f3"] == funct3) & (ins["f7"] == funct7):
                alu |= ins["op"](rs1_val, shamt)
        else:
            with (opcode == instruction_types["I"]) & (ins["f3"] == funct3):
                alu |= ins["op"](rs1_val, i_imm_ext)
                
    with opcode == instruction_types["J"]:
        alu |= pc_plus_4

    with pyrtl.otherwise: alu |= 0
reg_write_enable = (rd != 0) & (opcode != instruction_types["B"])
reg_file[rd] <<= pyrtl.MemBlock.EnabledWrite(alu, enable=reg_write_enable)

# PC modifying, J and B type instructions
do_branch = pyrtl.WireVector(1)
with pyrtl.conditional_assignment:
    for ins in b_type_instructions:
        with (opcode == instruction_types["B"]) & (ins["f3"] == funct3):
            do_branch |= ins["op"](rs1_val, rs2_val)
    with pyrtl.otherwise:
        do_branch |= 0

next_pc = pyrtl.WireVector(32)
with pyrtl.conditional_assignment:
    with (opcode == instruction_types["B"]) & (do_branch == 1):
        next_pc |= pc + b_imm_ext
    with opcode == instruction_types["J"]:
        next_pc |= pc + j_imm_ext
    with pyrtl.otherwise:
        next_pc |= pc_plus_4
pc.next <<= next_pc

sim_trace = pyrtl.SimulationTrace()
sim = pyrtl.Simulation(tracer=sim_trace)

# clock
MAX_TICKS = 1000000
i = 0
print_activated = False
while True:
    if i >= MAX_TICKS:
        print("max clock cycles of ", MAX_TICKS, "exceeded, shutting down program")
        break
    
    sim.step({})
    reg_states = sim.inspect_mem(reg_file)
    
    opcode_state = sim.inspect(opcode)
    if opcode_state == instruction_types["custom"]:
        ecall_code_state = sim.inspect(ecall_code)
        if ecall_code_state == 1:
            print(reg_states.get(10, 0))
        elif ecall_code_state == 2:
            print()
        elif ecall_code_state == 10:
            break
    
    i += 1

debugging = False
if debugging:
    sim_trace.render_trace(symbol_len=5, segment_size=1)
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
