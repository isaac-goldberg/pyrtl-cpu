main:
    addi x1, zero, 1
    addi x2, zero, 10
    
    addi x3, zero, 1
    addi x4, zero, 1

    addi x31, zero, 1
    ecall 1
    ecall 1
loop:
    beq x1, x2, exit

    add x5, x3, x4
    add x3, zero, x4
    add x4, zero, x5

    add x31, zero, x5
    ecall 1

    addi x1, x1, 1
    jal x0, loop
exit:
    ecall 10