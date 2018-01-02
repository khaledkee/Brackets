import Parser
Code ="""

; Code start
; don't use readdec
include Irvine32.inc

.data

.code

main proc
mov edx, 0
MOV ESI, 0
call readint
MOV DL, AL
cmp dl, 100
ja z
cmp dl, 1
jl z
JE A
MOV BL, 2
MOV CL, 3
L1:
MOV AL, DL
DIV BL
CMP AH, 0
je next
mov AL, DL
MUL CL
INC AX
NEXT :
mov DL, AL
INC ESI
MOV EAX, 0
CMP DL, 1
JNE L1
A :
MOV EAX, ESI
CALL WRITEINT
z :
exit

main endp

END main

; End of code



"""

Input_File="""11
"""

###########Code,Max_Instructions,Max_Memory

P=Parser.Parser(Code, 1000, 1000, Input_File)


A=P.Start()
# return [Instructions,Memory,Output_File] | False | TL | ML

print("Data_variables",P.Data_variables)
print("Memory_data_segment",P.Memory_data_segment)
print("Labels_names",P.Labels_names)
print("Functions_names",P.Functions_names)
print("Instructions",P.Instructions)
print("Code_segment",P.Code_segment)
print("Registers",P.Registers)
print("Stack_segment",P.Stack_segment)
print("Stack_segment",P.Stack_segment.__len__())
print("Memory_data_segment",P.Memory_data_segment.__len__())
print("State",P.State)
print("Output_File",P.Output_File)
print(A)















