 .data
    res DW 0
    subs DW 0
    mult DW 0
    precio DW 0
    promedio DW 0
calcula:
    PUSH bp
    MOV bp, sp
    MOV AX, [bp+4]
    MOV BX, [bp+6]
    MOV AX, BX
    MOV [bp-2], AX
    MOV AX, [bp-2]
    POP bp
    RET
resta:
    PUSH bp
    MOV bp, sp
    MOV AX, [bp+4]
    SUB AX, 15
    MOV [bp-2], AX
    MOV AX, [bp-2]
    POP bp
    RET
multiplicar:
    PUSH bp
    MOV bp, sp
    POP bp
    RET
mult:
    PUSH bp
    MOV bp, sp
    MOV AX, [bp-2]
    POP bp
    RET
precio:
    PUSH bp
    MOV bp, sp
    POP bp
    RET
promedio:
    PUSH bp
    MOV bp, sp
    MOV AX, 10
    MOV [bp-2], AX
    MOV AX, 20
    MOV [bp-2], AX
    MOV AX, [bp+4]
    MOV BX, [bp+6]
    MOV AX, BX
    MOV [bp-2], AX
    POP bp
    RET
fin:
    MOV AX, 0x4C00
    INT 21H
