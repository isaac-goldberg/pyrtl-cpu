import pyrtl
from assembler import assemble

pc = pyrtl.Register(bitwidth=32, name='pc')
reg_file = pyrtl.MemBlock(bitwidth=32, addrwidth=5, name='reg_file', asynchronous=True)

program = assemble("./programs/arithmetic.asm")
i_mem = pyrtl.RomBlock(bitwidth=32, addrwidth=32, romdata=program, name='i_mem', asynchronous=True, pad_with_zeros=True)

instr = i_mem[pc]

opcode = instr[0:7]
rd = instr[7:12]
funct3 = instr[12:15]
rs1 = instr[15:20]
i_imm = instr[20:32]

imm_ext = i_imm.sign_extended(32)

rs1_val = pyrtl.WireVector(32, 'rs1_val')
with pyrtl.conditional_assignment:
    with rs1 == 0:
        rs1_val |= 0
    with pyrtl.otherwise:
        rs1_val |= reg_file[rs1]

# ALU OPERATIONS
alu_out = pyrtl.WireVector(32, 'alu_out')
alu_out <<= rs1_val + imm_ext

reg_write_enable = (rd != 0)
reg_file[rd] <<= pyrtl.MemBlock.EnabledWrite(alu_out, enable=reg_write_enable)

# PC INCREMENTER
pc.next <<= pc + 1

sim_trace = pyrtl.SimulationTrace()
sim = pyrtl.Simulation(tracer=sim_trace)

# CLOCK
for cycle in range(5):
    sim.step({})

# VIEW OUTPUT
sim_trace.render_trace(symbol_len=5, segment_size=1)

print("\n\n----------REGISTER STATES----------")
reg_state = sim.inspect_mem(reg_file)
for i in range(32):
    val = reg_state.get(i, 0)
    if val != 0:
        print(f"Register x{i} = {val}")

if reg_state.get(1, 0) == 15:
    print("\nSuccess! x1 contains the value 15.")