main:
    addi t0, zero, 0
    addi t1, zero, 10
    
    addi t2, zero, 1
    addi t3, zero, 1

    addi a0, zero, 1
    ecall 1
    ecall 1
loop:
    beq t0, t1, exit

    add t4, t2, t3
    add t2, zero, t3
    add t3, zero, t4

    add a0, zero, t4
    ecall 1

    addi t0, t0, 1
    jal zero, loop
exit:
    ecall 10