// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

//// Replace this comment with your code.
// while(1){
//     if(KBD != 0){
//         FILL_BLACK();
//     }else{
//         FILL_WHITE();
//     }
// }

(INPUT_KDB)
@KBD
D=M
@FILL_BLACK
D;JNE
@FILL_WHITE
D;JEQ
@INPUT_KDB
0;JMP

(FILL_BLACK)
//i=SCREEN
@SCREEN
D=A
@i
M=D
//if(RAM[i]!=0) goto INPUT_KDB
(LOOP_BLACK)
@i
A=M
D=M
@INPUT_KDB
D;JNE
//RAM[i] = -1
@i
A=M
M=-1
// i++
@i
M=M+1
@LOOP_BLACK
0;JMP

(FILL_WHITE)
//i=SCREEN
@SCREEN
D=A
@i
M=D
//if(RAM[i]=0) goto INPUT_KDB
(LOOP_WHITE)
@i
A=M
D=M
@INPUT_KDB
D;JEQ
//RAM[i] = 0
@i
A=M
M=0
// i++
@i
M=M+1
@LOOP_WHITE
0;JMP