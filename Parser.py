
class Parser:
    Code = ""
    Code_Lines = []
    Special_Symbols="~!@#$%^&*()+=/-,{}<:>?[]\|"
    Digits="0123456789"
    Special_Names=[
        "include","equ","proc","endp","end","ret","exit",
        "type","sizeof","lengthof","ptr","dup"]
    Data_types=[
        "byte", "sbyte", "word", "sword", "dword", "sdword"
    ]
    Special_Names_no_Operands=[
        "pushad", "popad", "pushfd", "popfd", "cbw",
        "cwd", "cdq", "cld", "std", "stc", "clc"
    ]
    Special_Names_one_Operands=[
        "call", "jmp", "neg", "inc", "dec", "loop", "push",
        "pop", "test", "je", "jz", "jne", "jnz", "ja", "jnbe",
        "jg", "jnle", "jae", "jnb", "jge", "jnl", "jb", "jnae",
        "jl", "jnge", "jbe", "jna", "jle", "jng", "mul", "imul",
        "div", "idiv", "rep", "repe", "repz", "repne", "repnz"

    ]
    Special_Names_two_Operands=[
        "movsb","movsw","movsd","cmpsb","cmpsw","cmpsd",
        "scasb","scasw","scasd","stosb","stosw","stosd",
        "lodsb","lodsw","lodsd","sbb","acd","shl","shr",
        "sal","sar","rol","ror","rcl","rcr","mov","movsx",
        "movzx","add","sub","xchg","xor","and","or","cmp"
    ]
    Registers=[
        "eax","ebx","ecx","edx",
        "ebp","esp","esi","edi",
        "eip","ax","bx","cx","dx",
        "al","ah","bl","bh","ch",
        "cl","dh","dl"
    ]
    Data_variables={}
    Memory_data_segment=[]

    def __init__(self,Code):
        self.Code =Code

    def Start(self):
        self.Split_to_Lines()
        if self.Remove_constants()==False:
            print("syntax error")
            return
        else:
            X=0#self.Build_Memory()
            ####################################

    def Split_to_Lines(self):
        Line = []
        Word = ""
        Stak=""
        Comment = False
        String = False
        for i in range(0, len(self.Code)):
            if self.Code[i] == '\n':
                if Word != '':
                    Line.append(Word)
                if Line.__len__() != 0:
                    self.Code_Lines.append(Line)
                    if Line.__len__()>=2:
                        if Line[0].lower()=="end":
                            break
                Word = ""
                Line=[]
                Comment = False
                String = False
            elif Comment==False:
                if self.Code[i] == ' ':
                    if String==False:
                        if Word != "":
                            if Word != '':
                                Line.append(Word)
                                Word = ""
                    else:
                        Word += self.Code[i]
                elif self.Code[i] != ' ':
                    if self.Code[i]=='"':
                        if String==False:
                            if Word!="":
                                if Word != '':
                                    Line.append(Word)
                            Word='"'
                            String=True
                        elif Word[0] == self.Code[i]:
                            String=False
                            Word += self.Code[i]
                            if Word != '':
                                Line.append(Word)
                                Word = ""
                        else:
                            Word += self.Code[i]
                    elif self.Code[i]=='\'':
                        if String==False:
                            if Word!="":
                                if Word != '':
                                    Line.append(Word)
                            Word='\''
                            String=True
                        elif Word[0]==self.Code[i]:
                            String=False
                            Word += self.Code[i]
                            if Word != '':
                                Line.append(Word)
                                Word = ""
                        else:
                            Word += self.Code[i]
                    else:
                        if String==True:
                            Word += self.Code[i]
                        else:
                            if self.Code[i]==';':
                                Comment==True
                            elif self.Special_Symbols.__contains__(self.Code[i])==True:
                                if Word != '':
                                    Line.append(Word)
                                    Line.append(self.Code[i])
                                    Word = ""
                                else:
                                    Line.append(self.Code[i])
                            else:
                                Word += self.Code[i]


        return self.Code_Lines

    def Remove_constants(self):
        i = 0
        while (i < len(self.Code_Lines)):
            if len(self.Code_Lines[i]) > 2:
                if self.Code_Lines[i][1].lower() == "equ":
                    if self.Check_is_valid(self.Code_Lines[i][0])==False:
                        return False
                    else:
                        for j in range(0, len(self.Code_Lines)):
                            if j != i:
                                if self.Code_Lines[j].__contains__(self.Code_Lines[i][0]) == True:
                                    Index = self.Code_Lines[j].index(self.Code_Lines[i][0])
                                    for k in range(0, len(self.Code_Lines[i]) - 2):
                                        self.Code_Lines[j].insert(Index + k, self.Code_Lines[i][k + 2])
                                    self.Code_Lines[j].remove(self.Code_Lines[i][0])


                    self.Code_Lines.remove(self.Code_Lines[i])
                    continue
            i = i + 1
        return True

    def Check_is_valid(self,String):
        if self.Special_Names.__contains__(String.lower()) == True:
            return False
        elif self.Special_Names_no_Operands.__contains__(String.lower()) == True:
            return False
        elif self.Special_Names_one_Operands.__contains__(String.lower()) == True:
            return False
        elif self.Special_Names_two_Operands.__contains__(String.lower()) == True:
            return False
        elif self.Data_types.__contains__(String.lower()) == True:
            return False
        elif self.Registers.__contains__(String.lower()) == True:
            return False
        elif String.__contains__('"') == True:
            return False
        elif String.__contains__('\'') == True:
            return False
        elif String.__contains__('.') == True:
            return False
        elif String[0].isdecimal() == True:
            return False
        if self.Data_variables.__len__()>0:
            if self.Data_variables.__contains__(String)==True:
                return False
        return True

    def Build_Memory(self):
        Comma=False
        if (self.Code_Lines[0].__len__() == 2)&(self.Code_Lines[0][0].lower() == "include")&(self.Code_Lines[0][1].lower() == "irvine32.inc"):
            self.Code_Lines.remove(self.Code_Lines[0])
            i=0
            while(i<self.Code_Lines.__len__()):
                if (self.Code_Lines[i].__len__()==1)&(self.Code_Lines[i][0].lower()==".data"):
                    self.Code_Lines.remove(self.Code_Lines[i])
                    while (i < self.Code_Lines.__len__()):
                        if (self.Code_Lines[i].__len__()==1)&(self.Code_Lines[i][0].lower()==".code"):
                            i = i + 1
                            break
                        elif (self.Code_Lines[i].__len__()==1)&(self.Code_Lines[i][0].lower()==".data"):
                            self.Code_Lines.remove(self.Code_Lines[i])
                        else:
                            tmp=self.Check_data_line(self.Code_Lines[i],Comma)
                            if tmp==0:
                                return False
                            elif tmp==1:
                                Comma=False
                            else:
                                Comma=True
                            self.Code_Lines.remove(self.Code_Lines[i])
                else:
                    i=i+1
        else:
            return False

        return True

    def Check_data_line(self,Line,Comma):
        tmp_memory=[]
        if Comma==False:
            if self.Check_is_valid(Line[0])==False:
                return  0
            else:
                if Line.__len__()>1:
                    if self.Data_types.__contains__(Line[1].lower())==True:
                        for i in range(2,len(Line)):
                            A=10
                            #################
                    else:
                        return  0
                else:
                    return 0
        else:
            A=10##############
        return 0