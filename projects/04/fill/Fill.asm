// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.
// infinite loop
(LOOP)
    // check keyboard input
    @KBD
    D = M

    // set i
    @i
    M = 0
    // if KBD is 0, go white
    @WHITE
    D;JEQ
    // if KBD is not 0, go black
    @BLACK
    D;JNE

    // white
    (WHITE)
        @i
        D = M   // get diff
        @SCREEN
        A = A + D   // get address
        M = 0       // get white
        @i
        M = M + 1   // i++
        D = M
        // check if i is less or equal with 8191
        @8191
        D = D - A
        @WHITE
        D;JLE
        // go to the start
        @LOOP
        0;JMP
        
    // black
    (BLACK)
        @i
        D = M   // get diff
        @SCREEN
        A = A + D   // get address
        M = -1       // get black
        @i
        M = M + 1   // i++
        D = M
        // check if i is less or equal with 8191
        @8191
        D = D - A
        @BLACK
        D;JLE
        // go to start
        @LOOP
        0;JMP
