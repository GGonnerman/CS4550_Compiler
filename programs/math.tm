 0: LDC  6,1(0)
 1: ST   6,6(6)   ; Store current top
 2: LDA  5,1(6)   ; Update status
* Do some math to get correct return addr (uses top reg but restores it)
 3: LDC  6,3(0)
 4: ADD  6,6,7
 5: ST   6,0(5)   ; Store the return address
 6: LDA  6,6(5)   ; Set the new top pointer
 7: LDC  7,21(0)  ; Jump to main
 8: OUT  4,0,0    ; Printing main return value
 9: HALT 0,0,0
*
* Function: print
*
10: ST   1,1(5)
11: ST   2,2(5)
12: ST   3,3(5)
13: LD   2,-1(5)  ; Load argument
14: OUT  2,0,0    ; Print value
* Nothing to do with return value
15: LD   1,1(5)
16: LD   2,2(5)
17: LD   3,3(5)
18: LD   6,5(5)   ; Restore top pointer
19: LD   5,4(5)   ; Restore status pointer
20: LD   7,2(6)   ; Restore program counter
*
* Function: main
*
21: ST   1,1(5)
22: ST   2,2(5)
23: ST   3,3(5)
24: LDC  4,182(0) ; Loading literal
25: ST   4,8(5)
26: LDC  4,277(0) ; Loading literal
27: ST   4,9(5)
28: LD   2,8(5)   ; Loading first temp value
29: LD   1,9(5)   ; Loading second temp value
30: MUL  4,2,1    ; Adding the two vaules and put into return
31: ST   4,-1(5)
32: LD   1,1(5)
33: LD   2,2(5)
34: LD   3,3(5)
35: LD   6,5(5)   ; Restore top pointer
36: LD   5,4(5)   ; Restore status pointer
37: LD   7,1(6)   ; Restore program counter
