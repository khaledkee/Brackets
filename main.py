import Parser
import Extra_functions
Code ="""
include irvine32.inc
.data
a byte "hello world",0
.code
F proc 

call dumpregs 
;call writeint
;call crlf
;call writedec
ret
F endp

 main proc
 mov dl, 64
shr  dl, 3

 
L :




call F
;loop L
;call F

exit
main endp
END main
"""

############# mov     shift    xchg     loop     jmp    add   neg    flags



#################

###########Code,Max_Instructions,Max_Memory
P=Parser.Parser(Code,1000,1000)

P.Start()
# return True | False | TL | ML

print("Data_variables",P.Data_variables)
print("Memory_data_segment",P.Memory_data_segment)
print("Labels_names",P.Labels_names)
print("Functions_names",P.Functions_names)
print("Instructions",P.Instructions)
#print("Code_segment",P.Code_segment)
print("State",P.State)

#print(P.Code_Lines)








