jal x0, main

main:
    addi x1, zero, 1
    addi x2, zero, 1000
loop:
    beq x1, x2, exit
    addi x1, x1, 1
    jal x0, loop
exit:
    addi x31, x31, 10