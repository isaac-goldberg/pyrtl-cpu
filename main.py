import pyrtl
from assembler import assemble
from instructions_spec import *

pc = pyrtl.Register(bitwidth=32, name='pc')
reg_file = pyrtl.MemBlock(bitwidth=32, addrwidth=5, name='reg_file', asynchronous=True)

program = assemble("./arithmetic.asm")
i_mem = pyrtl.RomBlock(bitwidth=32, addrwidth=32, romdata=program, name='i_mem', asynchronous=True, pad_with_zeros=True)

instr = i_mem[pc]

# ---------------------------------------------------------
# INSTRUCTION DECODING
# ---------------------------------------------------------
# used by all
opcode = instr[0:7]

# used by R and I
rd = instr[7:12]
funct3 = instr[12:15]
rs1 = instr[15:20]

# used by R
rs2 = instr[20:25]
funct7 = instr[25:32]

# used by I
i_imm_ext = instr[20:32].sign_extended(32)
# ---------------------------------------------------------

rs1_val = pyrtl.WireVector(32)
rs2_val = pyrtl.WireVector(32)
with pyrtl.conditional_assignment:
    with rs1 == 0: rs1_val |= 0
    with pyrtl.otherwise: rs1_val |= reg_file[rs1]
    with rs2 == 0: rs2_val |= 0
    with pyrtl.otherwise: rs2_val |= reg_file[rs2]

# ALU EXECUTE
alu = pyrtl.WireVector(32)

with pyrtl.conditional_assignment:
    for ins in r_type:
        with (opcode == instr_types["R"]) & (ins["f7"] == funct7) & (ins["f3"] == funct3):
            alu |= ins["op"](rs1_val, rs2_val)

    for ins in i_type:
        with (opcode == instr_types["I"]) & (ins["f3"] == funct3):
            alu |= ins["op"](rs1_val, i_imm_ext)

    with pyrtl.otherwise: alu |= 0

reg_write_enable = (rd != 0)
reg_file[rd] <<= pyrtl.MemBlock.EnabledWrite(alu, enable=reg_write_enable)

# PC INCREMENTER
pc.next <<= pc + 1

sim_trace = pyrtl.SimulationTrace()
sim = pyrtl.Simulation(tracer=sim_trace)

# CLOCK
for _ in range(5):
    sim.step({})

# VIEW OUTPUT
sim_trace.render_trace(symbol_len=5, segment_size=1)
print("\n---------------------REGISTER STATES---------------------")
reg_state = sim.inspect_mem(reg_file)
for i in range(32):
    val = reg_state.get(i, 0)
    if val != 0:
        print(f"x{i} = {val}")

if reg_state.get(1, 0) == 15:
    print("\nSuccess! x1 contains the value 15.")