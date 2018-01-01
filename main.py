import Parser
Code ="""
INCLUDE Irvine32.inc

.data
a byte 2,20
 word   lengthof a +1 dup(25),
        30+3,0
.code


F proc 
pushad

mov eax,2
mov ebx,33
mov ecx,00
call dumpregs
call crlf
popad
ret
F endp

main proc
    mov eax,50
    mov bl,20
    mul bl
call dumpregs
	exit
main endp
end main



"""


Input_File="""
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
print("State",P.State)
print("Output_File",P.Output_File)
#print(A)














