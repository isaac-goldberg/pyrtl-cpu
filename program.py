import random

def r():
    return random.randint(0, 255)

tasks = []
for i in range(50):
    tasks.append(f"""addi s0, zero, {r()}
addi s1, zero, {r()}
addi s2, zero, {r()}
addi s3, zero, {r()}

addi s4, zero, {r()}
addi s5, zero, {r()}
addi s6, zero, {r()}
addi s7, zero, {r()}

mul t0, s0, s4
mul t1, s1, s6
add a0, t0, t1
ecall 1

mul t0, s0, s5
mul t1, s1, s7
add a0, t0, t1
ecall 1
ecall 2

mul t0, s2, s4
mul t1, s3, s6
add a0, t0, t1
ecall 1

mul t0, s2, s5
mul t1, s3, s7
add a0, t0, t1
ecall 1
ecall 2""")

def get_program():
    return "\n".join(tasks) + "\necall 10"