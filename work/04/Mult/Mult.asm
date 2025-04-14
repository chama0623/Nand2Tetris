// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
// The algorithm is based on repetitive addition.

//// Replace this comment with your code.
//i=0
@0
D=A
@i
M=D

// R2 = 0
@R2
M=D

(LOOP)
// if(i==R0) goto END
    @R0
    D=M
    @i
    D=D-M
    @END
    D;JEQ

    //R2 += R1
    @R2
    D=M
    @R1
    D=D+M
    @R2
    M=D

    // i++
    @i
    D=M
    @1
    D=D+A
    @i
    M=D
    // jump to LOOP
    @LOOP
    0;JMP

(END)
//END
@END
0;JMP