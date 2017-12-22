import Parser
import Extra_functions
Code ="""

include irvine32.inc

B equ ret

.data
a byte 12
Va dword  ? ,203,65
 dword "50h"



.code
F proc uses ghf hfghf fhghf

B
F endp
main proc
L1:
L3: ret
mov eax,  va
jmp L1
call writedec

exit
main endp


END main

"""


P=Parser.Parser(Code)
P.Start()
#print(P.Data_variables)
#print(P.Memory_data_segment)
print(P.Code_segment)
print(P.Labels_names)
print(P.Functions_names)
print(P.Code_Lines)




