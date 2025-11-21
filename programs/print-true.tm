 0: LDC  6,1(0)
 1: ST   6,6(6)  ; Store current top
 2: LDA  5,1(6)  ; Update status
* Do some math to get correct return addr (uses top reg but restores it)
 3: LDC  6,3(0)
 4: ADD  6,6,7
 5: ST   6,0(5)  ; Store the return address
 6: LDA  6,6(5)  ; Set the new top pointer
 7: LDC  7,21(0) ; Jump to main
 8: OUT  4,0,0   ; Printing main return value
 9: HALT 0,0,0
*
* Function: print
*
10: ST   1,1(5)
11: ST   2,2(5)
12: ST   3,3(5)
13: LD   2,-1(5) ; Load argument
14: OUT  2,0,0   ; Print value
* Nothing to do with return value
15: LD   1,1(5)
16: LD   2,2(5)
17: LD   3,3(5)
18: LD   6,5(5)  ; Restore top pointer
19: LD   5,4(5)  ; Restore status pointer
20: LD   7,2(6)  ; Restore program counter
*
* Function: main
*
21: ST   1,1(5)
22: ST   2,2(5)
23: ST   3,3(5)
24: LDC  2,1(0)
* Calling print
25: ST   5,6(6)  ; Store current status
26: ST   6,7(6)  ; Store current top
27: ST   2,1(6)  ; Load value from register into arg slot
28: LDA  5,2(6)  ; Update status
* Do some math to get correct return addr (uses top reg but restores it)
29: LDC  6,3(0)
30: ADD  6,6,7
31: ST   6,0(5)  ; Store return address
32: LDA  6,6(5)  ; Restore top reg to its real value
33: LDC  7,10(0)
* Returning from print
34: LDC  2,0(0)
* Calling print
35: ST   5,6(6)  ; Store current status
36: ST   6,7(6)  ; Store current top
37: ST   2,1(6)  ; Load value from register into arg slot
38: LDA  5,2(6)  ; Update status
* Do some math to get correct return addr (uses top reg but restores it)
39: LDC  6,3(0)
40: ADD  6,6,7
41: ST   6,0(5)  ; Store return address
42: LDA  6,6(5)  ; Restore top reg to its real value
43: LDC  7,10(0)
* Returning from print
44: LDC  4,1(0)  ; Loading literal
45: ST   4,7(5)
46: ST   4,-1(5)
47: LD   1,1(5)
48: LD   2,2(5)
49: LD   3,3(5)
50: LD   6,5(5)  ; Restore top pointer
51: LD   5,4(5)  ; Restore status pointer
52: LD   7,1(6)  ; Restore program counter
