import Parser
import Extra_functions
Code ="""
include irvine32.inc
.data
a dword 20+2,2,3,4,5
.code
F proc 
stc
std
call dumpregs 
call writeint
call crlf
ret
F endp

 main proc

mul 20 30
xchg dword ptr [a+1] ,a

call F
exit
main endp
END main
"""


P=Parser.Parser(Code)
P.Start()
print("Data_variables",P.Data_variables)
print("Memory_data_segment",P.Memory_data_segment)
print("Labels_names",P.Labels_names)
print("Functions_names",P.Functions_names)
print("Instructions",P.Instructions)
print("Code_segment",P.Code_segment)

#print(P.Code_Lines)




