addi s0, zero, 1
addi s1, zero, 2
addi s2, zero, 3
addi s3, zero, 4

addi s4, zero, 5
addi s5, zero, 6
addi s6, zero, 7
addi s7, zero, 8

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