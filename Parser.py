import Extra_functions


class Parser:
    Code = ""
    Code_Lines = []
    Special_Symbols="~!@#$%^&*()+=/-,{}<:>?[]\|"
    Digits="0123456789"
    Special_Names=[
        "include","equ","proc","endp","end","uses"
        "type","sizeof","lengthof","ptr","dup","offset"]
    Data_types=[
        "byte", "sbyte", "word", "sword", "dword", "sdword"
    ]
    Irvine32_functions=[
        "crlf","readchar","readdec","readstring","readint","writechar","writedec","writestring","writeint","dumpregs"
    ]
    Special_Names_no_Operands=[
        "pushad", "popad", "pushfd", "popfd", "cbw",
        "cwd", "cdq", "cld", "std", "stc", "clc","ret","exit"
    ]
    Special_Names_one_Operands=[
        "call", "jmp", "neg", "inc", "dec", "loop", "push",
        "pop", "je", "jz", "jne", "jnz", "ja", "jnbe",
        "jg", "jnle", "jae", "jnb", "jge", "jnl", "jb", "jnae",
        "jl", "jnge", "jbe", "jna", "jle", "jng", "mul", "imul",
        "div", "idiv", "rep", "repe", "repz", "repne", "repnz"

    ]
    Special_Names_two_Operands=[
        "movsb","movsw","movsd","cmpsb","cmpsw","cmpsd",
        "scasb","scasw","scasd","stosb","stosw","stosd",
        "lodsb","lodsw","lodsd","sbb","acd","shl","shr",
        "sal","sar","rol","ror","rcl","rcr","mov","movsx",
        "movzx","add","sub","xchg","test","xor","and","or","cmp"
    ]
    Registers={
        "eax":0,"ecx":0,"edx":0,"ebx":0,
        "esp":0,"ebp":0,"esi":0,"edi":0,
        "eip":0,"ax":0,"bx":0,"cx":0,"dx":0,
        "al":0,"ah":0,"bl":0,"bh":0,"ch":0,
        "cl":0,"dh":0,"dl":0
    }
    Flags={"cf":0,"of":0,"sf":0,"ac":0,"pf":0,"zf":0,"df":0}
    Data_variables={}
    Memory_data_segment=[]
    Code_segment=[]
    Stack_segment = []
    Functions_names={}
    Labels_names={}
    Opened_function=""
    Use_Uses=[]
    Data_type_for_comma=0
    Instructions=0
    Max_Memory=0
    Max_Instructions=0
    State=""
    Input_File=""
    Input_File_index=0
    Output_File=""

    def __init__(self,Code,Max_Instructions,Max_Memory,Input_File):
        self.Input_File=Input_File
        Code=Code.replace('\t','   ')
        self.Code =Code.lower()
        self.Max_Instructions=Max_Instructions
        self.Max_Memory=Max_Memory

    def Start(self):
        if self.Split_to_Lines()!=False:
            if self.Remove_constants() == False:
                #print("syntax error")
                return False

            else:
                if self.Build_Memory()==False:
                    if self.State!="":
                        return self.State
                    #print("syntax error")
                    return False
                else:
                    if self.Build_code_segment() == False:
                        if self.State != "":
                            return self.State
                        #print("syntax error")
                        return False
                    else:
                        if self.Start_Code() == False:
                            if self.State != "":
                                return self.State
                            #print("syntax error")
                            return False
                        else:
                            return [self.Instructions,self.Memory_data_segment.__len__()+self.Stack_segment.__len__(),self.Output_File]
        else:
           # print("syntax error")
            return False

        return True

    def Split_to_Lines(self):
        Line = []
        Word = ""
        Comment = False
        String = False
        for i in range(0, len(self.Code)):
            if self.Code[i] == '\n':
                if Word != '':
                    if (String == True) & (Word[0] != Word[Word.__len__() - 1]):
                        return False
                    Line.append(Word)
                if Line.__len__() != 0:
                    self.Code_Lines.append(Line)
                    if Line.__len__()>=2:
                        if Line[0]=="end":
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
                                Comment=True

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
                if self.Code_Lines[i][1] == "equ":
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
        if self.Special_Names.__contains__(String) == True:
            return False
        elif self.Special_Names_no_Operands.__contains__(String) == True:
            return False
        elif self.Special_Names_one_Operands.__contains__(String) == True:
            return False
        elif self.Special_Names_two_Operands.__contains__(String) == True:
            return False
        elif self.Data_types.__contains__(String) == True:
            return False
        elif self.Registers.__contains__(String) == True:
            return False
        elif self.Irvine32_functions.__contains__(String) == True:
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
        if self.Functions_names.__len__()>0:
            if self.Functions_names.__contains__(String)==True:
                return False
        if self.Labels_names.__len__()>0:
            if self.Labels_names.__contains__(String)==True:
                return False
        return True

    def Type(self,String):
        if (String=="byte")|(String=="sbyte"):
            return 1
        elif (String=="word")|(String=="sword"):
            return 2
        else:
            return 4

    def Check_is_valid_data(self,String):
        if self.Data_variables.__len__()>0:
                if self.Data_variables.__contains__(String) == True:
                    return self.Data_variables[String]
        try :
            String+=0
            return -2
            raise Exception("String")
        except Exception:
            if ((String[0] == String[len(String) - 1]) & (String[0] == '"')) | (
                (String[0] == String[len(String) - 1]) & (String[0] == "\'")):
                return -3
        return -1

    def Build_Memory(self):
        Comma=False
        if (self.Code_Lines[0].__len__() == 2)&(self.Code_Lines[0][0] == "include")&(self.Code_Lines[0][1] == "irvine32.inc"):
            self.Code_Lines.remove(self.Code_Lines[0])
            i=0
            while(i<self.Code_Lines.__len__()-1):
                if (self.Code_Lines[i].__len__()==1)&(self.Code_Lines[i][0]==".data"):
                    self.Code_Lines.remove(self.Code_Lines[i])
                    while (i < self.Code_Lines.__len__()-1):
                        if (self.Code_Lines[i].__len__()==1)&(self.Code_Lines[i][0]==".code"):
                            i = i + 1
                            break
                        elif (self.Code_Lines[i].__len__()==1)&(self.Code_Lines[i][0]==".data"):
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
            if Comma==True:
                return False
        else:
            return False

        return True

    def Save_in_Memory(self,Type,tmp_memory):
        for i in range(0,len(tmp_memory)):
            if self.Max_Memory<self.Memory_data_segment.__len__():
                self.State="ML"
                return False
            try:
                tmp_memory[i][0] += 0
                if tmp_memory[i][0]<0:
                    tmp_memory[i][0]=pow(2,Type)+tmp_memory[i][0]
                if tmp_memory[i][0]<0:
                    return False
                tmp=str(hex(tmp_memory[i][0]))[2:]
                if tmp.__len__()*4>Type:
                    return False

                for j in range(0,int(Type/8)):
                    if tmp=="":
                        self.Memory_data_segment.append("00")
                    elif tmp.__len__()>1:
                        self.Memory_data_segment.append(tmp[len(tmp)-2]+tmp[len(tmp)-1])
                        tmp=tmp[:-2]
                    else:
                        self.Memory_data_segment.append('0' + tmp[len(tmp) - 1])
                        tmp = tmp[:-1]
                continue
                raise Exception("String")
            except Exception:
                string=tmp_memory[i][0]
                string=string[:-1]
                string = string[1:]
                for j in range(0,len(string)):
                    tmp = str(hex(ord(string[j])))[2:]
                    for k in range(0, int(Type / 8)):
                        if tmp == "":
                            self.Memory_data_segment.append("00")
                        elif tmp.__len__() > 1:
                            self.Memory_data_segment.append(tmp[len(tmp) - 2] + tmp[len(tmp) - 1])
                            tmp = tmp[:-2]
                        else:
                            self.Memory_data_segment.append('0' + tmp[len(tmp) - 1])
                            tmp = tmp[:-1]

       # print("Memory_data_segment  ",self.Memory_data_segment)
        return True

    def Search_lable(self,address):
        ret=False
        for i in self.Labels_names:
            if self.Labels_names[i]==address:
                return True
        return ret

    def Jmp_X(self,String):


        if String=="jmp":
            return True
        elif (String=="je")|(String=="jz"):
            if self.Flags["zf"]==1:
                return True
            return False
        elif (String=="jne")|(String=="jnz"):
            if self.Flags["zf"]==0:
                return True
            return False
        elif (String=="ja")|(String=="jnbe")|(String=="jg")|(String=="jnle"):
            if self.Flags["sf"]==self.Flags["of"]:
                return True
            return False
        elif (String=="jb")|(String=="jnae")|(String=="jl")|(String=="jnge"):
            if self.Flags["sf"]!=self.Flags["of"]:
                return True
            return False
        elif (String=="jae")|(String=="jnb")|(String=="jge")|(String=="jnl"):
            if self.Flags["sf"]==self.Flags["of"]:
                return True
            elif self.Flags["zf"]==1:
                return True
            return False
        elif (String=="jbe")|(String=="jna")|(String=="jle")|(String=="jng"):
            if self.Flags["sf"]!=self.Flags["of"]:
                return True
            elif self.Flags["zf"]==1:
                return True
            return False
        elif (String=="loop"):
            self.Neg_inc_dec('dec',[['ecx']])
            if self.Flags["zf"]==1:
                return False
            return True

    def Irvine32(self,String):
        #"","","","","readint","","","",""
        if String=="crlf":
            self.Output_File+="\n"

        elif String=="dumpregs":
            self.Output_File+=str(self.Registers)+"\n"+str(self.Flags)

           # print("Registers ====>",self.Registers)
           # print("Flags ====>", self.Flags)
        elif String=="writeint":
            self.Output_File += str(self.Registers["eax"])
            #print("eax ====>",self.Registers["eax"])
        elif String == "writedec":

            if bool(self.Registers["eax"] &pow(2, (4 * 8)-1))==True:
                a=self.Registers["eax"]
                a = pow(2, (4 * 8)) -a
                self.Output_File += '-'+str(a)
                #print("eax ====>-", a)
            else:
                self.Output_File += '+' + str(self.Registers["eax"])
                #print("eax ====> +", self.Registers["eax"])
        elif String == "writechar":
            self.Output_File += chr(self.Registers["al"])
           # print(chr(self.Registers["al"]))
        elif String=="writestring":

            c=self.Get_value_from_memory(self.Registers["edx"],1)
            s=""
            i=0
            while (c!=0):
                s+=chr(c)
                i+=1
                c = self.Get_value_from_memory(self.Registers["edx"]+i, 1)
            self.Output_File += s
            #print(s)
        elif String=="readint":
            num=""
            while(self.Input_File_index<len(self.Input_File)):
                if self.Input_File[self.Input_File_index]=="\n":
                    break
                self.Input_File_index+=1

            if num.isdecimal()==True:
                self.Registers["eax"]=int(num)
            else:
                return False

        elif String == "readdec":

            num = ""
            while (self.Input_File_index < len(self.Input_File)):
                if self.Input_File[self.Input_File_index] == "\n":
                    break
                self.Input_File_index += 1

            if (num.isdecimal() == True)|((num[1:].isdecimal() == True)&((num[0] == '-')|num[0]=='+')):
                self.Registers["eax"] = int(num)
            else:
                return False

        elif String == "readchar":
            if (self.Input_File_index < len(self.Input_File)):
                self.Registers["al"]=ord(self.Input_File[self.Input_File_index])
                self.Input_File_index += 1
            else:
                return False

           # print(chr(self.Registers["al"]))
        elif String=="readstring":

            edx=self.Registers["edx"]
            ecx=self.Registers["ecx"]
            while (self.Input_File_index < len(self.Input_File))&(self.Registers["ecx"]>=0):
                if self.Input_File[self.Input_File_index] == "\n":
                    self.Save_value_in_memory(edx, ord(self.Input_File[self.Input_File_index]), 1)
                    break

                self.Save_value_in_memory(edx,ord(self.Input_File[self.Input_File_index]),1)
                edx+=1
                ecx-=1
                self.Input_File_index += 1

        return True



    def Mul_X(self,String,infix):
        return True

    def Div_X(self,String,infix):
        return True

    def Push_Pop(self,String,infix):
        return True

    def Neg_inc_dec(self,String,infix):
        tmp1 = self.Check_code_operand(infix[0])
        if (tmp1 == False):
            return False
        if (tmp1[0] == 'imm') | (tmp1[2] == 0):
            return False

        if String == 'inc':

            a = 0
            if  (tmp1[0] != 'add'):
                a = tmp1[1]
            else:
                a = self.Get_value_from_memory(tmp1[1], tmp1[2])


            # self.Flags["ac"] = (a & (pow(2,4 )-1))+(b & (pow(2,4 )-1))
            a = a + 1
            if a>=pow(2,tmp1[2]*8):
                a=a&(pow(2,tmp1[2]*8)-1)

            if bool(a &pow(2, (tmp1[2] * 8)-1))==True:
                self.Flags["sf"]=1
            else:
                self.Flags["sf"] = 0

            v = a
            one = 0
            for i in range(0, 8):
                if bool(v & 1) == True:
                    one += 1
                v = v.__rshift__(1)
            if bool(one & 1) == True:
                self.Flags["pf"] = 0
            else:
                self.Flags["pf"] = 1

            if a==0:
                self.Flags["zf"] = 1
            else:
                self.Flags["zf"] = 0

            if tmp1[0] == 'reg':
                self.Registers[infix[0][0]] = a
            else:
                if self.Save_value_in_memory(tmp1[1], a, tmp1[2]) == False:
                    return False
        elif String == 'neg':

            a = 0
            if (tmp1[0] != 'add'):
                a = tmp1[1]
            else:
                a = self.Get_value_from_memory(tmp1[1], tmp1[2])

            a = pow(2, (tmp1[2] * 8)) + a

            if a>=pow(2,tmp1[2]*8):
                a=a&(pow(2,tmp1[2]*8)-1)
                self.Flags["of"] = 1
            else:
                self.Flags["of"] = 0

            self.Flags["cf"]=1

            if bool(a &pow(2, (tmp1[2] * 8)-1))==True:
                self.Flags["sf"]=1
            else:
                self.Flags["sf"] = 0


            v = a
            one = 0
            for i in range(0, 8):
                if bool(v & 1) == True:
                    one += 1
                v = v.__rshift__(1)
            if bool(one & 1) == True:
                self.Flags["pf"] = 0
            else:
                self.Flags["pf"] = 1


            if a==0:
                self.Flags["zf"] = 1
            else:
                self.Flags["zf"] = 0

            if tmp1[0] == 'reg':
                self.Registers[infix[0][0]] = a
            else:
                if self.Save_value_in_memory(tmp1[1], a, tmp1[2]) == False:
                    return False
        elif String == 'dec':
            a = 0
            if (tmp1[0] != 'add'):
                a = tmp1[1]
            else:
                a = self.Get_value_from_memory(tmp1[1], tmp1[2])

            b = pow(2, (tmp1[2]*8)) -1


            a = a +b

            if a>=pow(2,tmp1[2]*8):
                a=a&(pow(2,tmp1[2]*8)-1)

            if bool(a &pow(2, (tmp1[2] * 8)-1))==True:
                self.Flags["sf"]=1
            else:
                self.Flags["sf"] = 0

            v = a
            one = 0
            for i in range(0, 8):
                if bool(v & 1) == True:
                    one += 1
                v = v.__rshift__(1)
            if bool(one & 1) == True:
                self.Flags["pf"] = 0
            else:
                self.Flags["pf"] = 1

            if a==0:
                self.Flags["zf"] = 1
            else:
                self.Flags["zf"] = 0

            if tmp1[0] == 'reg':
                self.Registers[infix[0][0]] = a
            else:
                if self.Save_value_in_memory(tmp1[1], a, tmp1[2]) == False:
                    return False
        return True

    def Mov_X(self,String,infix):
        tmp1=self.Check_code_operand(infix[0])
        tmp2=self.Check_code_operand(infix[1])
        if (tmp1==False)|(tmp2==False):
            return False
        if (tmp1[0]=='imm')|(tmp1[2]==0)|((tmp1[0]=='imm')&(tmp2[0]=='imm')):
            return False

        if String=='mov':

            if ((tmp1[0]=='add')&(tmp2[0]=='add'))|((tmp1[2]!=tmp2[2])&(tmp2[2]!=0)&(tmp2[0]!='imm')):
                return False
            b = 0
            if (tmp2[0] != 'add'):
                b = tmp2[1]
            else:
                b = self.Get_value_from_memory(tmp2[1], tmp2[2])


            if b < 0:
                b = pow(2, (tmp1[2]*8)) + b
            if b < 0:
                return False

            if tmp1[0] == 'reg':
                self.Registers[infix[0][0]]=b
            else:
                if self.Save_value_in_memory(tmp1[1],b, tmp1[2])==False:
                    return False
        elif String=='movzx':

            if ((tmp1[0]=='add')&(tmp2[0]=='add'))|((tmp1[2]<=tmp2[2])&(tmp2[2]!=0)&(tmp2[0]!='imm')):
                return False
            b = 0
            if  (tmp2[0] != 'add'):
                b = tmp2[1]
            else:
                b = self.Get_value_from_memory(tmp2[1], tmp2[2])

            if b < 0:
                b = pow(2, (tmp1[2]*8)) + b
            if b < 0:
                return False

            if tmp1[0] == 'reg':
                self.Registers[infix[0][0]]=b
            else:
                if self.Save_value_in_memory(tmp1[1],b, tmp1[2])==False:
                    return False
        elif String=='movsx':
            if ((tmp1[0]=='add')&(tmp2[0]=='add'))|((tmp1[2]<=tmp2[2])&(tmp2[2]!=0)&(tmp2[0]!='imm')):
                return False
            b = 0
            if  (tmp2[0] != 'add'):
                b = tmp2[1]
            else:
                b = self.Get_value_from_memory(tmp2[1], tmp2[2])

            if b < 0:
                b = pow(2, (tmp1[2]*8)) + b
            if b < 0:
                return False

            if (b&pow(2,(tmp2[2]*8)-1))==False:
                if tmp1[0] == 'reg':
                    self.Registers[infix[0][0]] = b
                else:
                    if self.Save_value_in_memory(tmp1[1], b, tmp1[2]) == False:
                        return False
            else:
                v=(pow(2,((tmp1[2]-tmp2[2])*8))-1)*pow(2,(tmp2[2]*8))
                b=v|b
                if tmp1[0] == 'reg':
                    self.Registers[infix[0][0]] = b
                else:
                    if self.Save_value_in_memory(tmp1[1], b, tmp1[2]) == False:
                        return False





        return True

    def Cmp(self,String,infix):
        tmp1 = self.Check_code_operand(infix[0])
        tmp2 = self.Check_code_operand(infix[1])
        if (tmp1 == False) | (tmp2 == False):
            return False
        if (tmp1[0] == 'imm') | (tmp1[2] == 0) | ((tmp1[0] == 'imm') & (tmp2[0] == 'imm')):
            return False
        if ((tmp1[0] == 'add') & (tmp2[0] == 'add')) | ((tmp1[2] != tmp2[2]) & (tmp2[2] != 0) & (tmp2[0] != 'imm')):
            return False
        a = 0
        if (tmp1[0] != 'var') & (tmp1[0] != 'add'):
            a = tmp1[1]
        else:
            a = self.Get_value_from_memory(tmp1[1], tmp1[2])
        b = 0
        if (tmp2[0] != 'var') & (tmp2[0] != 'add'):
            b = tmp2[1]
        else:
            b = self.Get_value_from_memory(tmp2[1], tmp2[2])

        if b < 0:
            b = pow(2, (tmp1[2] * 8)) + b
        if b < 0:
            return False

        b = pow(2, (tmp1[2] * 8)) - b

        v = bool((a & (pow(2, 4) - 1)) + (b & (pow(2, 4) - 1)))
        if v == True:
            self.Flags["ac"] = 0
        else:
            self.Flags["ac"] = 1

        v = bool((a & (pow(2, (tmp1[2] * 8) - 2) - 1)) + (b & (pow(2, (tmp1[2] * 8) - 2) - 1)))

        a = a + b

        if a >= pow(2, tmp1[2] * 8):
            a = a & (pow(2, tmp1[2] * 8) - 1)
            self.Flags["cf"] = 0
            if v == True:
                self.Flags["of"] = 1
            else:
                self.Flags["of"] = 0
        else:
            self.Flags["cf"] = 1
            if v == True:
                self.Flags["of"] = 0
            else:
                self.Flags["of"] = 1

        if bool(a & pow(2, (tmp1[2] * 8) - 1)) == True:
            self.Flags["sf"] = 1
        else:
            self.Flags["sf"] = 0

        v = a
        one = 0
        for i in range(0, 8):
            if bool(v & 1) == True:
                one += 1
            v = v.__rshift__(1)
        if bool(one & 1) == True:
            self.Flags["pf"] = 0
        else:
            self.Flags["pf"] = 1

        if a == 0:
            self.Flags["zf"] = 1
        else:
            self.Flags["zf"] = 0


        return True

    def Xchg(self,String,infix):
        tmp1 = self.Check_code_operand(infix[0])
        tmp2 = self.Check_code_operand(infix[1])
        if (tmp1 == False) | (tmp2 == False):
            return False
        if (tmp1[0] == 'imm') | (tmp1[2] == 0) | ((tmp1[0] == 'imm') & (tmp2[0] == 'imm')):
            return False
        if ((tmp1[0] == 'add') & (tmp2[0] == 'add'))|((tmp1[0] == 'imm') & (tmp2[0] == 'imm')) | ((tmp1[2] != tmp2[2]) & (tmp2[2] != 0)):
            return False

        a = 0
        if (tmp1[0] != 'var') & (tmp1[0] != 'add'):
            a = tmp1[1]
        else:
            a = self.Get_value_from_memory(tmp1[1], tmp1[2])
        b = 0
        if (tmp2[0] != 'var') & (tmp2[0] != 'add'):
            b = tmp2[1]
        else:
            b = self.Get_value_from_memory(tmp2[1], tmp2[2])

        if tmp1[0] == 'reg':
            self.Registers[infix[0][0]] = b
        else:
            if self.Save_value_in_memory(tmp1[1], b, tmp1[2]) == False:
                return False

        if tmp2[0] == 'reg':
            self.Registers[infix[1][0]] = a
        else:
            if self.Save_value_in_memory(tmp2[1], a, tmp2[2]) == False:
                return False
        return True

    def Add_sub(self,String,infix):

        tmp1 = self.Check_code_operand(infix[0])
        tmp2 = self.Check_code_operand(infix[1])
        if (tmp1 == False) | (tmp2 == False):
            return False
        if (tmp1[0] == 'imm') | (tmp1[2] == 0) | ((tmp1[0] == 'imm') & (tmp2[0] == 'imm')):
            return False
        if ((tmp1[0] == 'add') & (tmp2[0] == 'add')) | ((tmp1[2] != tmp2[2]) & (tmp2[2] != 0) & (tmp2[0] != 'imm')):
            return False

        if String=='add':

            a = 0
            if (tmp1[0] != 'var') & (tmp1[0] != 'add'):
                a = tmp1[1]
            else:
                a = self.Get_value_from_memory(tmp1[1], tmp1[2])
            b = 0
            if (tmp2[0] != 'var')&(tmp2[0] != 'add'):
                b = tmp2[1]
            else:
                b = self.Get_value_from_memory(tmp2[1], tmp2[2])


            if b < 0:
                b = pow(2, (tmp1[2]*8)) + b
            if b < 0:
                return False

            v=bool((a & (pow(2,4 )-1))+(b & (pow(2,4 )-1)))
            if v==True:
                self.Flags["ac"]=1
            else:
                self.Flags["ac"] = 0

            v = bool((a & (pow(2, (tmp1[2]*8)-2) - 1)) + (b & (pow(2, (tmp1[2]*8)-2) - 1)))



            a=a+b

            if a>=pow(2,tmp1[2]*8):
                a=a&(pow(2,tmp1[2]*8)-1)
                self.Flags["cf"] = 1
                if v==True:
                    self.Flags["of"]=0
                else:
                    self.Flags["of"] = 1
            else:
                self.Flags["cf"] = 0
                if v==True:
                    self.Flags["of"]=1
                else:
                    self.Flags["of"] = 0

            if bool(a &pow(2, (tmp1[2] * 8)-1))==True:
                self.Flags["sf"]=1
            else:
                self.Flags["sf"] = 0

            v=a
            one=0
            for i in range(0,8):
                if bool(v&1)==True:
                    one+=1
                v=v.__rshift__(1)
            if bool(one&1)==True:
                self.Flags["pf"]=0
            else:
                self.Flags["pf"] = 1

            if a==0:
                self.Flags["zf"] = 1
            else:
                self.Flags["zf"] = 0


            if tmp1[0] == 'reg':
                self.Registers[infix[0][0]]=a
            else:
                if self.Save_value_in_memory(tmp1[1],a, tmp1[2])==False:
                    return False
        elif String=='acd':

            a = 0
            if (tmp1[0] != 'var') & (tmp1[0] != 'add'):
                a = tmp1[1]
            else:
                a = self.Get_value_from_memory(tmp1[1], tmp1[2])
            b = 0
            if (tmp2[0] != 'var')&(tmp2[0] != 'add'):
                b = tmp2[1]
            else:
                b = self.Get_value_from_memory(tmp2[1], tmp2[2])


            if b < 0:
                b = pow(2, (tmp1[2]*8)) + b
            if b < 0:
                return False

            v = bool((a & (pow(2, 4) - 1)) + (b & (pow(2, 4) - 1))+self.Flags["cf"])
            if v==True:
                self.Flags["ac"]=1
            else:
                self.Flags["ac"] = 0

            v = bool((a & (pow(2, (tmp1[2]*8)-2) - 1)) + (b & (pow(2, (tmp1[2]*8)-2) - 1))+self.Flags["cf"])




            a=a+b+self.Flags["cf"]

            if a>=pow(2,tmp1[2]*8):
                a=a&(pow(2,tmp1[2]*8)-1)
                self.Flags["cf"] = 1
                if v == True:
                    self.Flags["of"] = 0
                else:
                    self.Flags["of"] = 1
            else:
                self.Flags["cf"] = 0
                if v == True:
                    self.Flags["of"] = 1
                else:
                    self.Flags["of"] = 0

            if bool(a &pow(2, (tmp1[2] * 8)-1))==True:
                self.Flags["sf"]=1
            else:
                self.Flags["sf"] = 0

            v = a
            one = 0
            for i in range(0, 8):
                if bool(v & 1) == True:
                    one += 1
                v = v.__rshift__(1)
            if bool(one & 1) == True:
                self.Flags["pf"] = 0
            else:
                self.Flags["pf"] = 1

            if a==0:
                self.Flags["zf"] = 1
            else:
                self.Flags["zf"] = 0

            if tmp1[0] == 'reg':
                self.Registers[infix[0][0]]=a
            else:
                if self.Save_value_in_memory(tmp1[1],a, tmp1[2])==False:
                    return False
        elif String=='sub':
            a = 0
            if (tmp1[0] != 'var') & (tmp1[0] != 'add'):
                a = tmp1[1]
            else:
                a = self.Get_value_from_memory(tmp1[1], tmp1[2])
            b = 0
            if (tmp2[0] != 'var')&(tmp2[0] != 'add'):
                b = tmp2[1]
            else:
                b = self.Get_value_from_memory(tmp2[1], tmp2[2])


            if b < 0:
                b = pow(2, (tmp1[2]*8)) + b
            if b < 0:
                return False

            b = pow(2, (tmp1[2] * 8)) - b

            v = bool((a & (pow(2, 4) - 1)) + (b & (pow(2, 4) - 1)))
            if v == True:
                self.Flags["ac"] = 0
            else:
                self.Flags["ac"] = 1


            v = bool((a & (pow(2, (tmp1[2]*8)-2) - 1)) + (b & (pow(2, (tmp1[2]*8)-2) - 1)))



            a=a+b

            if a>=pow(2,tmp1[2]*8):
                a=a&(pow(2,tmp1[2]*8)-1)
                self.Flags["cf"] = 0
                if v == True:
                    self.Flags["of"] = 1
                else:
                    self.Flags["of"] = 0
            else:
                self.Flags["cf"] = 1
                if v == True:
                    self.Flags["of"] = 0
                else:
                    self.Flags["of"] = 1

            if bool(a &pow(2, (tmp1[2] * 8)-1))==True:
                self.Flags["sf"]=1
            else:
                self.Flags["sf"] = 0

            v = a
            one = 0
            for i in range(0, 8):
                if bool(v & 1) == True:
                    one += 1
                v = v.__rshift__(1)
            if bool(one & 1) == True:
                self.Flags["pf"] = 0
            else:
                self.Flags["pf"] = 1


            if a==0:
                self.Flags["zf"] = 1
            else:
                self.Flags["zf"] = 0

            if tmp1[0] == 'reg':
                self.Registers[infix[0][0]]=a
            else:
                if self.Save_value_in_memory(tmp1[1],a, tmp1[2])==False:
                    return False
        elif String=='sbb':
            a = 0
            if (tmp1[0] != 'var') & (tmp1[0] != 'add'):
                a = tmp1[1]
            else:
                a = self.Get_value_from_memory(tmp1[1], tmp1[2])
            b = 0
            if (tmp2[0] != 'var')&(tmp2[0] != 'add'):
                b = tmp2[1]
            else:
                b = self.Get_value_from_memory(tmp2[1], tmp2[2])


            if b < 0:
                b = pow(2, (tmp1[2]*8)) + b
            if b < 0:
                return False

            b = pow(2, (tmp1[2] * 8)) - b

            v = bool((a & (pow(2, 4) - 1)) + (b & (pow(2, 4) - 1))+self.Flags["cf"])
            if v == True:
                self.Flags["ac"] = 0
            else:
                self.Flags["ac"] = 1

            v = bool((a & (pow(2, (tmp1[2] * 8) - 2) - 1)) + (b & (pow(2, (tmp1[2] * 8) - 2) - 1))+self.Flags["cf"])


            a=a+b+self.Flags["cf"]

            if a>=pow(2,tmp1[2]*8):
                a=a&(pow(2,tmp1[2]*8)-1)
                self.Flags["cf"] = 0
                if v == True:
                    self.Flags["of"] = 1
                else:
                    self.Flags["of"] = 0
            else:
                self.Flags["cf"] = 1
                if v == True:
                    self.Flags["of"] = 0
                else:
                    self.Flags["of"] = 1

            if bool(a &pow(2, (tmp1[2] * 8)-1))==True:
                self.Flags["sf"]=1
            else:
                self.Flags["sf"] = 0


            v = a
            one = 0
            for i in range(0, 8):
                if bool(v & 1) == True:
                    one += 1
                v = v.__rshift__(1)
            if bool(one & 1) == True:
                self.Flags["pf"] = 0
            else:
                self.Flags["pf"] = 1

            if a==0:
                self.Flags["zf"] = 1
            else:
                self.Flags["zf"] = 0

            if tmp1[0] == 'reg':
                self.Registers[infix[0][0]]=a
            else:
                if self.Save_value_in_memory(tmp1[1],a, tmp1[2])==False:
                    return False
        return True

    def Shift(self,String,infix):
        tmp1 = self.Check_code_operand(infix[0])
        tmp2 = self.Check_code_operand(infix[1])
        if (tmp1 == False) | (tmp2 == False):
            return False
        if ((tmp1[0] == 'reg')|(tmp1[0] == 'var')|((tmp1[0] == 'add')&(tmp1[2] != 0))) & ((((tmp2[0] == 'imm')&(tmp2[2] == 1)))|((tmp2[0] == 'reg')&(infix[1][0]=='cl'))):
           # "", "","", "", "rol", "ror", "rcl", "rcr"
            if (String=='shl')|(String=='sal'):
                a = 0
                if  (tmp1[0] != 'add'):
                    a = tmp1[1]
                else:
                    a = self.Get_value_from_memory(tmp1[1], tmp1[2])
                b = 0
                if (tmp2[0] != 'add'):
                    b = tmp2[1]
                else:
                    b = self.Get_value_from_memory(tmp2[1], tmp2[2])

                if b < 0:
                    b = pow(2, (tmp1[2] * 8)) + b
                if b < 0:
                    return False


                for i in range(0,b):
                    a = a * 2
                    if a >= pow(2, tmp1[2] * 8):
                        a = a & (pow(2, tmp1[2] * 8) - 1)
                        self.Flags["cf"] = 1
                    else:
                        self.Flags["cf"] = 0



                if bool(a & pow(2, (tmp1[2] * 8) - 1)) == True:
                    self.Flags["sf"] = 1
                else:
                    self.Flags["sf"] = 0

                v = a
                one = 0
                for i in range(0, 8):
                    if bool(v & 1) == True:
                        one += 1
                    v = v.__rshift__(1)
                if bool(one & 1) == True:
                    self.Flags["pf"] = 0
                else:
                    self.Flags["pf"] = 1

                if a == 0:
                    self.Flags["zf"] = 1
                else:
                    self.Flags["zf"] = 0

                if tmp1[0] == 'reg':
                    self.Registers[infix[0][0]] = a
                else:
                    if self.Save_value_in_memory(tmp1[1], a, tmp1[2]) == False:
                        return False
            elif  String=='shr':
                a = 0
                if (tmp1[0] != 'add'):
                    a = tmp1[1]
                else:
                    a = self.Get_value_from_memory(tmp1[1], tmp1[2])
                b = 0
                if  (tmp2[0] != 'add'):
                    b = tmp2[1]
                else:
                    b = self.Get_value_from_memory(tmp2[1], tmp2[2])

                if b < 0:
                    b = pow(2, (tmp1[2] * 8)) + b
                if b < 0:
                    return False


                for i in range(0,b):
                    if bool(a&1)==True:
                        self.Flags["cf"] = 1
                    else:
                        self.Flags["cf"] = 0
                    a = int(a / 2)


                if bool(a & pow(2, (tmp1[2] * 8) - 1)) == True:
                    self.Flags["sf"] = 1
                else:
                    self.Flags["sf"] = 0

                v = a
                one = 0
                for i in range(0, 8):
                    if bool(v & 1) == True:
                        one += 1
                    v = v.__rshift__(1)
                if bool(one & 1) == True:
                    self.Flags["pf"] = 0
                else:
                    self.Flags["pf"] = 1

                if a == 0:
                    self.Flags["zf"] = 1
                else:
                    self.Flags["zf"] = 0



                if tmp1[0] == 'reg':
                    self.Registers[infix[0][0]] = a
                else:
                    if self.Save_value_in_memory(tmp1[1], a, tmp1[2]) == False:
                        return False
            elif String == 'sar':
                a = 0
                if  (tmp1[0] != 'add'):
                    a = tmp1[1]
                else:
                    a = self.Get_value_from_memory(tmp1[1], tmp1[2])
                b = 0
                if  (tmp2[0] != 'add'):
                    b = tmp2[1]
                else:
                    b = self.Get_value_from_memory(tmp2[1], tmp2[2])

                if b < 0:
                    b = pow(2, (tmp1[2] * 8)) + b
                if b < 0:
                    return False

                if bool(a & pow(2, (tmp1[2] * 8) - 1)) == True:
                    self.Flags["sf"] = 1
                else:
                    self.Flags["sf"] = 0

                for i in range(0, b):
                    if bool(a & 1) == True:
                        self.Flags["cf"] = 1
                    else:
                        self.Flags["cf"] = 0
                    a = int(a / 2)
                    if self.Flags["sf"]==1:
                        a=a|pow(2, (tmp1[2] * 8) - 1)

                if bool(a & pow(2, (tmp1[2] * 8) - 1)) == True:
                    self.Flags["sf"] = 1
                else:
                    self.Flags["sf"] = 0

                v = a
                one = 0
                for i in range(0, 8):
                    if bool(v & 1) == True:
                        one += 1
                    v = v.__rshift__(1)
                if bool(one & 1) == True:
                    self.Flags["pf"] = 0
                else:
                    self.Flags["pf"] = 1

                if a == 0:
                    self.Flags["zf"] = 1
                else:
                    self.Flags["zf"] = 0

                if tmp1[0] == 'reg':
                    self.Registers[infix[0][0]] = a
                else:
                    if self.Save_value_in_memory(tmp1[1], a, tmp1[2]) == False:
                        return False
            elif String=='rol':
                a = 0
                if  (tmp1[0] != 'add'):
                    a = tmp1[1]
                else:
                    a = self.Get_value_from_memory(tmp1[1], tmp1[2])
                b = 0
                if (tmp2[0] != 'add'):
                    b = tmp2[1]
                else:
                    b = self.Get_value_from_memory(tmp2[1], tmp2[2])

                if b < 0:
                    b = pow(2, (tmp1[2] * 8)) + b
                if b < 0:
                    return False


                for i in range(0,b):
                    a = a * 2

                    if a >= pow(2, tmp1[2] * 8):
                        a = a & (pow(2, tmp1[2] * 8) - 1)
                        self.Flags["cf"] = 1
                        a = a | 1
                    else:
                        self.Flags["cf"] = 0



                if bool(a & pow(2, (tmp1[2] * 8) - 1)) == True:
                    self.Flags["sf"] = 1
                else:
                    self.Flags["sf"] = 0

                v = a
                one = 0
                for i in range(0, 8):
                    if bool(v & 1) == True:
                        one += 1
                    v = v.__rshift__(1)
                if bool(one & 1) == True:
                    self.Flags["pf"] = 0
                else:
                    self.Flags["pf"] = 1

                if a == 0:
                    self.Flags["zf"] = 1
                else:
                    self.Flags["zf"] = 0

                if tmp1[0] == 'reg':
                    self.Registers[infix[0][0]] = a
                else:
                    if self.Save_value_in_memory(tmp1[1], a, tmp1[2]) == False:
                        return False
            elif String == 'ror':
                a = 0
                if (tmp1[0] != 'add'):
                    a = tmp1[1]
                else:
                    a = self.Get_value_from_memory(tmp1[1], tmp1[2])
                b = 0
                if (tmp2[0] != 'add'):
                    b = tmp2[1]
                else:
                    b = self.Get_value_from_memory(tmp2[1], tmp2[2])

                if b < 0:
                    b = pow(2, (tmp1[2] * 8)) + b
                if b < 0:
                    return False

                for i in range(0, b):
                    if bool(a & 1) == True:
                        self.Flags["cf"] = 1
                    else:
                        self.Flags["cf"] = 0
                    a = int(a / 2)
                    if self.Flags["cf"]==1:
                        a=a|pow(2, (tmp1[2] * 8) - 1)

                if bool(a & pow(2, (tmp1[2] * 8) - 1)) == True:
                    self.Flags["sf"] = 1
                else:
                    self.Flags["sf"] = 0

                v = a
                one = 0
                for i in range(0, 8):
                    if bool(v & 1) == True:
                        one += 1
                    v = v.__rshift__(1)
                if bool(one & 1) == True:
                    self.Flags["pf"] = 0
                else:
                    self.Flags["pf"] = 1

                if a == 0:
                    self.Flags["zf"] = 1
                else:
                    self.Flags["zf"] = 0

                if tmp1[0] == 'reg':
                    self.Registers[infix[0][0]] = a
                else:
                    if self.Save_value_in_memory(tmp1[1], a, tmp1[2]) == False:
                        return False
            elif String == 'rcl':
                a = 0
                if (tmp1[0] != 'add'):
                    a = tmp1[1]
                else:
                    a = self.Get_value_from_memory(tmp1[1], tmp1[2])
                b = 0
                if (tmp2[0] != 'add'):
                    b = tmp2[1]
                else:
                    b = self.Get_value_from_memory(tmp2[1], tmp2[2])

                if b < 0:
                    b = pow(2, (tmp1[2] * 8)) + b
                if b < 0:
                    return False

                for i in range(0, b):
                    a = a * 2

                    if a >= pow(2, tmp1[2] * 8):
                        a = a & (pow(2, tmp1[2] * 8) - 1)
                        if self.Flags["cf"] == 1:
                            a=a|1
                        self.Flags["cf"] = 1

                    else:
                        if self.Flags["cf"] == 1:
                            a=a|1
                        self.Flags["cf"] = 0

                if bool(a & pow(2, (tmp1[2] * 8) - 1)) == True:
                    self.Flags["sf"] = 1
                else:
                    self.Flags["sf"] = 0

                v = a
                one = 0
                for i in range(0, 8):
                    if bool(v & 1) == True:
                        one += 1
                    v = v.__rshift__(1)
                if bool(one & 1) == True:
                    self.Flags["pf"] = 0
                else:
                    self.Flags["pf"] = 1

                if a == 0:
                    self.Flags["zf"] = 1
                else:
                    self.Flags["zf"] = 0

                if tmp1[0] == 'reg':
                    self.Registers[infix[0][0]] = a
                else:
                    if self.Save_value_in_memory(tmp1[1], a, tmp1[2]) == False:
                        return False
            elif String == 'rcr':
                a = 0
                if (tmp1[0] != 'add'):
                    a = tmp1[1]
                else:
                    a = self.Get_value_from_memory(tmp1[1], tmp1[2])
                b = 0
                if (tmp2[0] != 'add'):
                    b = tmp2[1]
                else:
                    b = self.Get_value_from_memory(tmp2[1], tmp2[2])

                if b < 0:
                    b = pow(2, (tmp1[2] * 8)) + b
                if b < 0:
                    return False

                for i in range(0, b):
                    f=self.Flags["cf"]
                    if bool(a & 1) == True:
                        self.Flags["cf"] = 1
                    else:
                        self.Flags["cf"] = 0
                    a = int(a / 2)
                    if f == 1:
                        a = a | pow(2, (tmp1[2] * 8) - 1)

                if bool(a & pow(2, (tmp1[2] * 8) - 1)) == True:
                    self.Flags["sf"] = 1
                else:
                    self.Flags["sf"] = 0

                v = a
                one = 0
                for i in range(0, 8):
                    if bool(v & 1) == True:
                        one += 1
                    v = v.__rshift__(1)
                if bool(one & 1) == True:
                    self.Flags["pf"] = 0
                else:
                    self.Flags["pf"] = 1

                if a == 0:
                    self.Flags["zf"] = 1
                else:
                    self.Flags["zf"] = 0

                if tmp1[0] == 'reg':
                    self.Registers[infix[0][0]] = a
                else:
                    if self.Save_value_in_memory(tmp1[1], a, tmp1[2]) == False:
                        return False



        else:
            return False

        return True

    def Test(self,String,infix):
        return True

    def Mem_opr(self,String,infix):
        return True

    def Get_value_from_memory(self,address,type):
        if (address<self.Memory_data_segment.__len__())&(address+(type)<=self.Memory_data_segment.__len__()):

            ret=""
            i=address
            while (i<(address+(type))):
                ret=self.Memory_data_segment[i]+ret
                i+=1
            return int(ret,16)
        else:
            return False

    def Save_value_in_memory(self,address,value,type):
        if (address<self.Memory_data_segment.__len__())&(address+(type)<=self.Memory_data_segment.__len__()):

            tmp = str(hex(value))[2:]
            if tmp.__len__()  > (type*2):
                return False

            for j in range(0, (type)):
                if tmp == "":
                    self.Memory_data_segment[address+j]="00"
                elif tmp.__len__() > 1:
                    self.Memory_data_segment[address+j] =tmp[len(tmp) - 2] + tmp[len(tmp) - 1]
                    tmp = tmp[:-2]
                else:
                    self.Memory_data_segment[address+j] ='0' + tmp[len(tmp) - 1]
                    tmp = tmp[:-1]

            return True
        else:
            return False

#############################


    def Check_code_operand(self,Operand):
        if len(Operand)==1:
            if self.Data_variables.__contains__(Operand[0])==True:
                tmp=self.Data_variables[Operand[0]]
                # name , address , Type
                return ["add",tmp[0],self.Type(tmp[1])]
            elif self.Registers.__contains__(Operand[0])==True:
                reg_32 = ["eax", "ebx", "ecx", "edx", "ebp", "esp", "esi", "edi"]
                reg_16 = ["ax", "bx", "cx", "dx"]
                tmp=0
                if reg_32.__contains__(Operand[0])==True:
                    tmp=4
                elif reg_16.__contains__(Operand[0])==True:
                    tmp=2
                else:
                    tmp=1
                # name , value , Type
                return ["reg",self.Registers[Operand[0]],tmp]
            elif self.Data_types.__contains__(Operand[0]) == True:
                return ["imm", self.Type(Operand[0]),self.Type(Operand[0])]
            else:
                try:
                    tmp = 0
                    if Operand[0] < pow(2, 8):
                        tmp = 1
                    elif Operand[0] < pow(2, 16):
                        tmp = 2
                    elif Operand[0] < pow(2, 32):
                        tmp = 4
                    else:
                        return False
                        # name , Type
                    return ["imm",Operand[0], tmp]
                    raise "Error"
                except Exception:
                    return False
        else:
            name=""
            type=0
            if Operand.__len__()>1:
                if Operand[1] == 'ptr':
                    name = "add"
                    if self.Data_types.__contains__(Operand[0]) == True:
                        type = self.Type(Operand[0])
                        Operand.append('+')
                    else:
                        return False
                    Operand=Operand[2:]
                    if Operand.__len__() > 0:
                        if (Operand[0] == 'ptr_X_') | (Operand[0] == 'ptr_'):
                            Operand.append('+')
                            name = "add"
                            type = 0
                            Operand = Operand[1:]
                elif (Operand[0] == 'ptr_X_') | (Operand[0] == 'ptr_'):
                    Operand.append('+')
                    name = "add"
                    type = 0
                    Operand = Operand[1:]
                else:
                    name = "imm"
            else:
                name = "imm"



            stak = []
            for i in range(0, len(Operand)):
                if (Operand[i] == '+') | (Operand[i] == '-') | (Operand[i] == '*') | (Operand[i] == '/'):
                    if stak.__len__() > 1:
                        tmp1=self.Check_code_operand([stak[stak.__len__()-1]])
                        tmp2 = self.Check_code_operand([stak[stak.__len__() - 2]])
                        if (tmp1==False)|(tmp2==False):

                            return False
                        tmp1_=tmp1[1]
                        tmp2_= tmp2[1]

                        stak = stak[:-1]
                        if (Operand[i] == '-'):
                            stak[stak.__len__()-1]=tmp1_-tmp2_
                        elif (Operand[i] == '+'):
                            stak[stak.__len__() - 1] = tmp1_ + tmp2_
                        elif (Operand[i] == '*'):
                            stak[stak.__len__() - 1] = tmp1_ * tmp2_
                        elif (Operand[i] == '/'):
                            if tmp2_!=0:
                                stak[stak.__len__() - 1] = tmp1_ / tmp2_
                            else:
                                return False
                    else:
                        if ((Operand[i] == '+') | (Operand[i] == '-')):
                            tmp1 = self.Check_code_operand([stak[stak.__len__() - 1]])
                            if (tmp1 == False):
                                return False
                            tmp1_ = tmp1[1]
                            if (Operand[i] == '-'):
                                stak[stak.__len__() - 1] = tmp1_ * -1
                            else:
                                stak[stak.__len__() - 1] = tmp1_
                        else:
                            return False
                elif (Operand[i] == 'lengthof') | (Operand[i] == 'sizeof') | (Operand[i] == 'type'):
                    if stak.__len__() > 0:
                        tmp1 = self.Check_code_operand([stak[stak.__len__() - 1]])
                        if tmp1==False:
                            return False
                        if ((tmp1[0]!="var") & ((Operand[i] == 'lengthof') | (Operand[i] == 'sizeof'))):
                            return False
                        elif (tmp1[0]!="var") & (Operand[i] == 'type'):
                            stak[stak.__len__() - 1] = 0
                        else:

                            tmp1_ = tmp1[2]
                            tmp2_=self.Data_variables[stak[stak.__len__() - 1]][2]
                            stak = stak[:-1]
                            if Operand[i] == 'lengthof':
                                stak.append(int(tmp2_ / tmp1_))
                            elif Operand[i] == 'sizeof':
                                stak.append(tmp2_)
                            else:
                                stak.append(tmp1_)
                    else:
                        return False
                elif (Operand[i] == 'offset'):
                    if stak.__len__() > 0:
                        tmp1 = self.Check_code_operand([stak[stak.__len__() - 1]])
                        if tmp1==False:
                            return False
                        stak[stak.__len__() - 1] = tmp1[1]
                    else:
                        return False
                else:
                    stak.append(Operand[i])

            if stak.__len__()==0:
                return False
            value = stak[0]
            if name=="imm":
                type_=self.Check_code_operand([value])
                if type_==False:
                    return False
                type=type_[2]

            return [name,value,type]

    def Start_Code(self):
        if self.Code_Lines[self.Code_Lines.__len__() - 1].__len__()==2:
            if (self.Code_Lines[self.Code_Lines.__len__() - 1][0] == "end") & (
            self.Functions_names.__contains__(self.Code_Lines[self.Code_Lines.__len__() - 1][1])):
                self.Registers.update({"eip":self.Functions_names[self.Code_Lines[self.Code_Lines.__len__() - 1][1]]})
                self.Registers.update({"eip": self.Registers["eip"] + 1})
                self.Stack_segment.append(-1)
                #self.Registers.update({"esp": self.Registers["esp"] + 1})
                while (self.Registers["eip"]<self.Code_segment.__len__()):
                    if self.Max_Memory < self.Memory_data_segment.__len__()+self.Stack_segment.__len__():
                        self.State = "ML"
                        return False
                    if self.Max_Instructions<self.Instructions:
                        self.State="TL"
                        return False
                    self.Instructions+=1
                    if self.Registers["eip"]==-1:
                        return True
                    #print("_______________",self.Code_segment[self.Registers["eip"]], "_   ", self.Registers["eip"])
                    if (self.Code_segment[self.Registers["eip"]]=="")&(self.Search_lable(self.Registers["eip"])==False):
                        return False


                   # print("_______________", self.Code_segment[self.Registers["eip"]][0], "_   ",self.Registers["eip"])
                    if (self.Code_segment[self.Registers["eip"]]==""):
                        self.Registers.update({"eip": self.Registers["eip"] + 1})
                        self.Instructions-=1
                        continue
                    elif self.Special_Names_no_Operands.__contains__(self.Code_segment[self.Registers["eip"]])==True:
                        if self.Code_segment[self.Registers["eip"]]=="exit":
                            return True
                        elif self.Code_segment[self.Registers["eip"]]=="pushfd":
                            Flags=""
                            for i in self.Flags:
                                Flags+=str(self.Flags[i])
                            self.Stack_segment.append(Flags)
                            self.Registers.update({"esp": self.Registers["esp"] + 1})
                        elif self.Code_segment[self.Registers["eip"]]=="popfd":
                            if self.Registers["esp"]>=0:
                                Flags = self.Stack_segment[self.Registers["esp"]]
                                self.Stack_segment = self.Stack_segment[:-1]
                                self.Registers.update({"esp": self.Registers["esp"] - 1})
                                try:
                                    Flags += 0
                                    return False
                                    raise Exception("String")
                                except Exception:
                                    j = 0
                                    for i in self.Flags:
                                        self.Flags.update({i: Flags[j]})
                                        j += 1
                            else:
                                return False
                        elif self.Code_segment[self.Registers["eip"]] == "pushad":
                            for i in self.Registers:
                                if i.__len__()==3:
                                    self.Stack_segment.append(self.Registers[i])
                                    self.Registers.update({"esp": self.Registers["esp"] + 1})
                        elif self.Code_segment[self.Registers["eip"]] == "popad":
                            b=20
                        elif self.Code_segment[self.Registers["eip"]] == "cbw":
                            b = 20
                        elif self.Code_segment[self.Registers["eip"]] == "cwd":
                            b = 20
                        elif self.Code_segment[self.Registers["eip"]] == "cdq":
                            b = 20
                        elif self.Code_segment[self.Registers["eip"]] == "cld":
                            self.Flags.update({"df": 0})
                        elif self.Code_segment[self.Registers["eip"]] == "std":
                            self.Flags.update({"df": 1})
                        elif self.Code_segment[self.Registers["eip"]] == "stc":
                            self.Flags.update({"cf": 1})
                        elif self.Code_segment[self.Registers["eip"]] == "clc":
                            self.Flags.update({"cf":0})
                        elif self.Code_segment[self.Registers["eip"]] == "ret":
                            if self.Use_Uses.__len__()==0:
                                #print("LLLLLLLLLLLLLLLLLLL")
                                self.Registers.update({"eip": self.Stack_segment[self.Registers["esp"]]})
                                self.Stack_segment = self.Stack_segment[:-1]
                                self.Registers.update({"esp": self.Registers["esp"] - 1})
                                continue
                            else:
                                b=20
                    elif self.Special_Names_one_Operands.__contains__(self.Code_segment[self.Registers["eip"]][0]) == True:

                        if (self.Code_segment[self.Registers["eip"]][0][0]=='j')|(self.Code_segment[self.Registers["eip"]][0][0]=='l'):
                            tmp=self.Jmp_X(self.Code_segment[self.Registers["eip"]][0])
                            if tmp==True:
                                self.Registers.update({"eip": self.Labels_names[self.Code_segment[self.Registers["eip"]][1]]})
                                continue
                        elif (self.Code_segment[self.Registers["eip"]][0]=='mul')|(self.Code_segment[self.Registers["eip"]][0]=='imul'):
                            if self.Mul_X(self.Code_segment[self.Registers["eip"]][0],self.Code_segment[self.Registers["eip"]][1])==False:
                                return False
                        elif (self.Code_segment[self.Registers["eip"]][0] == 'div') | (self.Code_segment[self.Registers["eip"]][0] == 'idiv'):
                            if self.Div_X(self.Code_segment[self.Registers["eip"]][0],self.Code_segment[self.Registers["eip"]][1])==False:
                                return False
                        elif (self.Code_segment[self.Registers["eip"]][0][0]=='p'):
                            if self.Push_Pop(self.Code_segment[self.Registers["eip"]][0],self.Code_segment[self.Registers["eip"]][1])==False:
                                return False
                        elif (self.Code_segment[self.Registers["eip"]][0]=='neg')|(self.Code_segment[self.Registers["eip"]][0]=='inc')|(self.Code_segment[self.Registers["eip"]][0]=='dec'):
                            if self.Neg_inc_dec(self.Code_segment[self.Registers["eip"]][0],self.Code_segment[self.Registers["eip"]][1])==False:
                                return False
                        elif (self.Code_segment[self.Registers["eip"]][0]=='call'):
                            if self.Functions_names.__contains__(self.Code_segment[self.Registers["eip"]][1])==True:
                                self.Stack_segment.append(self.Registers["eip"] + 1)
                                self.Registers.update({"esp": self.Registers["esp"] + 1})
                                self.Registers.update({"eip": self.Functions_names[self.Code_segment[self.Registers["eip"]][1]]})
                            else:
                                if self.Irvine32(self.Code_segment[self.Registers["eip"]][1])==False:
                                    return False


                    elif self.Special_Names_two_Operands.__contains__(self.Code_segment[self.Registers["eip"]][0]) == True:
                        L1=["add", "sub","sbb", "acd"]
                        L2=["test", "xor", "and", "or"]
                        L3=["scasb", "scasw", "scasd", "stosb", "stosw", "stosd","lodsb", "lodsw", "lodsd"]
                        L4=["shl", "shr","sal", "sar", "rol", "ror", "rcl", "rcr"]
                        if (self.Code_segment[self.Registers["eip"]][0][0]=='m'):
                            if self.Mov_X(self.Code_segment[self.Registers["eip"]][0],self.Code_segment[self.Registers["eip"]][1])==False:
                                return False
                        elif (self.Code_segment[self.Registers["eip"]][0][0]=='c'):
                            if self.Cmp(self.Code_segment[self.Registers["eip"]][0],self.Code_segment[self.Registers["eip"]][1])==False:
                                return False
                        elif (self.Code_segment[self.Registers["eip"]][0] == 'xchg'):
                            if self.Xchg(self.Code_segment[self.Registers["eip"]][0],self.Code_segment[self.Registers["eip"]][1])==False:
                                return False
                        elif (L1.__contains__(self.Code_segment[self.Registers["eip"]][0])==True):
                            if self.Add_sub(self.Code_segment[self.Registers["eip"]][0],self.Code_segment[self.Registers["eip"]][1])==False:
                                return False
                        elif (L2.__contains__(self.Code_segment[self.Registers["eip"]][0]) == True):
                            if self.Test(self.Code_segment[self.Registers["eip"]][0],self.Code_segment[self.Registers["eip"]][1])==False:
                                return False
                        elif (L3.__contains__(self.Code_segment[self.Registers["eip"]][0])==True):
                            if self.Mem_opr(self.Code_segment[self.Registers["eip"]][0],self.Code_segment[self.Registers["eip"]][1])==False:
                                return False
                        elif (L4.__contains__(self.Code_segment[self.Registers["eip"]][0])==True):
                            if self.Shift(self.Code_segment[self.Registers["eip"]][0],self.Code_segment[self.Registers["eip"]][1])==False:
                                return False

                        #print("222222222_", self.Code_segment[self.Registers["eip"]], "_   ", self.Registers["eip"])

                    self.Registers.update({"eip":self.Registers["eip"]+1})

                if (self.Registers["eip"]<0)|(self.Registers["eip"]>self.Code_segment.__len__()):
                    return False
            else:
                return False
        else:
            return False

        return True
######################################
    def postfix_code_line(self,Line):
        stak = []
        expression = []
        infix = []
        for i in range(0, len(Line)):

            reg_32 = ["eax", "ebx", "ecx", "edx", "ebp", "esp", "esi", "edi"]
            reg_16 = ["ax", "bx", "cx", "dx"]
            if (Line[i] == '(') | (Line[i] == '['):
               # print("____________",stak,"'''''''''",expression)
                if (stak.__len__() > 0):

                    if (Line[i] == '[') & ((stak[stak.__len__() - 1] == "lengthof") | (stak[stak.__len__() - 1] == "sizeof") | (stak[stak.__len__() - 1] == "type")|(stak[stak.__len__() - 1] == "offset") ):
                        return False
                    if (Line[i] == '(') & ((stak[stak.__len__() - 1] == "lengthof") | (stak[stak.__len__() - 1] == "sizeof")|(stak[stak.__len__() - 1] == "offset") ):
                        return False
                if (stak.__len__()==0)&(Line[i]=='(')&(expression.__len__()!=0):
                        return False
                if expression.__len__()>0:
                    if (Line[i] == '[') & ((expression[expression.__len__() - 1]) != "ptr") & ((reg_32.__contains__(expression[expression.__len__() - 1]) == False) & (self.Data_variables.__contains__(expression[expression.__len__() - 1]) == False)):
                        return False
                    elif (Line[i] == '[') & ((expression[expression.__len__() - 1]) != "ptr") & ((reg_32.__contains__(expression[expression.__len__() - 1]) == False)):
                        tmp=expression[expression.__len__() - 1]
                        expression[expression.__len__() - 1]="ptr_X_"
                        expression.append(tmp)
                    elif(Line[i] == '[') & ((expression[expression.__len__() - 1]) == "ptr"):
                        #continue
                        1==1
                    else:
                        return False
                else:
                    if Line[i]=='[':
                        expression.append("ptr_")

                stak.append(Line[i])
            elif (Line[i] == ')') | (Line[i] == ']'):
                if stak.__len__() == 0:
                    return False

                j = stak.__len__() - 1
                while (j >= 0):
                    if (stak[j] == '(') & (Line[i] == ')'):
                        break
                    elif (stak[j] == '(') & (Line[i] == ']'):
                        return False
                    elif (stak[j] == '[') & (Line[i] == ')'):
                        return False
                    elif (stak[j] == '[') & (Line[i] == ']'):
                        break
                    expression.append(stak[j])
                    stak = stak[:-1]
                    j = j - 1
                    if j < 0:
                        break

                stak = stak[:-1]
            elif Line[i] == ',':
                if expression.__len__() == 0:
                    return False
                if stak.__len__() != 0:
                    j = stak.__len__() - 1
                    while (j >= 0):
                        expression.append(stak[j])
                        stak = stak[:-1]
                        j = j - 1
                if expression.__len__() > 0:
                    infix.append(expression)
                expression = []
            elif Line[i][0].isdecimal() == True:
                if Line[i][len(Line[i]) - 1] == 'h':
                    tmp = Extra_functions.is_hexa(Line[i])
                    if tmp == False:
                        return False
                    expression.append(tmp)
                elif Line[i][len(Line[i]) - 1] == 'o':
                    tmp = Extra_functions.is_octa(Line[i])
                    if tmp == False:
                        return False
                    expression.append(tmp)
                elif Line[i][len(Line[i]) - 1] == 'b':
                    tmp = Extra_functions.is_binary(Line[i])
                    if tmp == False:
                        return False
                    expression.append(tmp)
                elif Line[i][len(Line[i]) - 1] == 'd':
                    tmp = int(Line[i][:-1], 10)
                    expression.append(tmp)
                elif Line[i].isdecimal() == True:
                    expression.append(int(Line[i]))
                else:
                    return False
            elif (Line[i] == "lengthof") | (Line[i] == "sizeof") | (Line[i] == "type")|(Line[i] == "offset"):
                stak.append(Line[i])
            else:
                if (Line[i] == '*') | (Line[i] == '-') | (Line[i] == '/') | (Line[i] == '+'):
                    if stak.__len__() > 0:
                        j = stak.__len__() - 1
                        while (j >= 0):
                            if ((stak[j] == '+') | (stak[j] == '-')) & ((Line[i] == '+') | (Line[i] == '-')):
                                expression.append(stak[j])
                                stak = stak[:-1]
                            elif ((stak[j] == '+') | (stak[j] == '-')) & ((Line[i] == '*') | (Line[i] == '/')):
                                break
                            elif ((stak[j] == '*') | (stak[j] == '/')) & ((Line[i] == '*') | (Line[i] == '/')):
                                expression.append(stak[j])
                                stak = stak[:-1]
                            elif ((stak[j] == '*') | (stak[j] == '/')) & ((Line[i] == '+') | (Line[i] == '-')):
                                expression.append(stak[j])
                                stak = stak[:-1]
                            elif ((stak[j] == 'dup') | (stak[j] == 'lengthof') | (stak[j] == 'type') | (
                                stak[j] == 'sizeof')):
                                expression.append(stak[j])
                                stak = stak[:-1]
                            else:
                                break
                            j = j - 1

                    stak.append(Line[i])
                else:
                    try:
                        if ((Line[i][0] == Line[i][len(Line[i]) - 1]) & (Line[i][0] == '"')) | (
                                    (Line[i][0] == Line[i][len(Line[i]) - 1]) & (Line[i][0] == "\'")):
                            tmp=Extra_functions.convert_string(Line[i])
                            expression.append(tmp)
                            continue
                        raise Exception("NotString")
                    except Exception:
                        expression.append(Line[i])
        j = stak.__len__() - 1
        while (j >= 0):
            if (stak[j] == '(') | (stak[j] == '['):
                return False
            expression.append(stak[j])
            stak = stak[:-1]
            j = j - 1

        if expression.__len__() > 0:
            infix.append(expression)
        return infix

    def Build_code_segment(self):
        i = 0
        if (self.Code_Lines[0].__len__() == 1) & (self.Code_Lines[0][0] == ".code"):
            self.Code_Lines.remove(self.Code_Lines[0])
        else:
            return False
        reg_32 = ["eax", "ebx", "ecx", "edx", "ebp", "esp", "esi", "edi"]
        reg_16 = ["ax", "bx", "cx", "dx"]
        while (i < self.Code_Lines.__len__() - 1):

            if (self.Code_Lines[i].__len__() == 1) & (self.Code_Lines[i][0] == ".code"):
                i=i+1
            else:
                if (self.Code_Lines[i].__len__()==1)&(self.Special_Names_no_Operands.__contains__(self.Code_Lines[i][0])==True):
                    self.Code_segment.append(self.Code_Lines[i][0])
                elif self.Code_Lines[i].__len__()>1:

                    if self.Code_Lines[i].__len__()==2:
                        if self.Code_Lines[i][1]=='proc':
                            if (self.Opened_function=="")&(self.Check_is_valid(self.Code_Lines[i][0])==True):
                                self.Opened_function=self.Code_Lines[i][0]
                                self.Functions_names[self.Code_Lines[i][0]]=self.Code_segment.__len__()
                                self.Code_segment.append("")
                            else:
                                return False
                        elif self.Code_Lines[i][1]=='endp':
                            if self.Opened_function==self.Code_Lines[i][0]:
                                self.Opened_function=""
                            else:
                                return False
                        elif self.Code_Lines[i][1]==':':
                            if (self.Check_is_valid(self.Code_Lines[i][0])==True):
                                self.Labels_names[self.Code_Lines[i][0]]=self.Code_segment.__len__()
                                self.Code_segment.append("")
                            else:
                                return False
                        elif self.Special_Names_one_Operands.__contains__(self.Code_Lines[i][0])==True:
                            if (self.Code_Lines[i][0]=='call')&((self.Functions_names.__contains__(self.Code_Lines[i][1])==True)|(self.Irvine32_functions.__contains__(self.Code_Lines[i][1])==True)):
                                self.Code_segment.append(self.Code_Lines[i])
                            elif ((self.Code_Lines[i][0][0]=='j')|(self.Code_Lines[i][0][0]=='l')|(self.Code_Lines[i][0][0]=='r'))&(self.Labels_names.__contains__(self.Code_Lines[i][1])==True):
                               self.Code_segment.append(self.Code_Lines[i])
                            elif ((self.Code_Lines[i][0]!='call')&(self.Code_Lines[i][0][0]!='j')&(self.Code_Lines[i][0][0]!='l')&(self.Code_Lines[i][0][0]!='r')):
                                infix = self.postfix_code_line(self.Code_Lines[i][1:])
                               # print("1111111111111111::",infix)
                                if (infix==False):
                                    return False
                                if infix.__len__()>1:
                                    return False
                                self.Code_segment.append([self.Code_Lines[i][0],infix])
                            else:
                                return False

                        elif self.Code_Lines[i][0]=='uses':
                            if self.Opened_function!="":
                                for j in range(1,len(self.Code_Lines[i])):
                                    if (reg_32.__contains__(self.Code_Lines[i][j])==False)&(reg_16.__contains__(self.Code_Lines[i][j])==False):
                                        return False
                                self.Code_segment.append(self.Code_Lines[i])
                            else:
                                return False
                        else:
                            return False
                    else:
                        if self.Code_Lines[i][1] == ':':
                            if (self.Check_is_valid(self.Code_Lines[i][0]) == True):
                                self.Labels_names[self.Code_Lines[i][0]] = self.Code_segment.__len__()
                                self.Code_segment.append("")
                                self.Code_Lines[i] = self.Code_Lines[i][2:]
                                i = i - 1
                            else:
                                return False
                        elif self.Code_Lines[i][1]=='proc':
                            if (self.Opened_function=="")&(self.Check_is_valid(self.Code_Lines[i][0])==True):
                                self.Opened_function=self.Code_Lines[i][0]
                                self.Functions_names[self.Code_Lines[i][0]]=self.Code_segment.__len__()
                                self.Code_segment.append("")
                                self.Code_Lines[i] = self.Code_Lines[i][2:]
                                i = i - 1
                            else:
                                return False
                        elif self.Special_Names_one_Operands.__contains__(self.Code_Lines[i][0])==True:
                            L = ["mul", "imul", "div", "idiv", "neg", "inc", "dec"]
                            if ((self.Code_Lines[i][0][0] == 'p') | (L.__contains__(self.Code_Lines[i][0])==True)):
                                infix = self.postfix_code_line(self.Code_Lines[i][1:])
                                # print("1111111111111111::",infix)
                                if (infix == False):
                                    return False
                                if infix.__len__() > 1:
                                    return False
                                self.Code_segment.append([self.Code_Lines[i][0], infix])
                            else:
                                return False
                        elif self.Special_Names_two_Operands.__contains__(self.Code_Lines[i][0])==True:
                            infix = self.postfix_code_line(self.Code_Lines[i][1:])
                           # print("3333333333333::", infix)
                            if (infix == False):
                                return False
                            if infix.__len__() > 2:
                                return False
                            self.Code_segment.append([self.Code_Lines[i][0], infix])
                        elif self.Code_Lines[i][0]=='uses':
                            if self.Opened_function!="":
                                for j in range(1,len(self.Code_Lines[i])):
                                    if (reg_32.__contains__(self.Code_Lines[i][j])==False)&(reg_16.__contains__(self.Code_Lines[i][j])==False):
                                        return False
                                self.Code_segment.append(self.Code_Lines[i])
                            else:
                                return False
                        else:
                            return False
                else:
                    return False
                i = i + 1


        return True

################
    def Check_data_line(self,Line,Comma):
        var_type_len=[] #(adress,data_type,length)
        tmp_memory=[]
        stak=[]
        if Comma==False:
            if self.Check_is_valid(Line[0])==False:
                if (self.Data_types.__contains__(Line[0])==True)&(Line.__len__()>1):
                    infix = Extra_functions.postfix(Line[1:])
                    if infix != False:
                        if Line[Line.__len__() - 1] == ',':
                            Comma = True
                       # print(infix)

                        tmp_memory = []
                        for i in range(0,len(infix)):
                            stak = []
                            for j in range(0,len(infix[i])):
                                if (infix[i][j] == '+') | (infix[i][j] == '-') | (infix[i][j] == '*') | (infix[i][j] == '/'):
                                    if stak.__len__() > 1:
                                        tmp = self.Check_is_valid_data(stak[stak.__len__() - 1])
                                        tmp1 = self.Check_is_valid_data(stak[stak.__len__() - 2])
                                        if (tmp == -1)| (tmp1 ==-1):
                                           return 0
                                        if tmp == -2:
                                            tmp = stak[stak.__len__() - 1]
                                        elif tmp == -3:

                                            tmp = Extra_functions.convert_string(stak[stak.__len__() - 1])

                                        else:
                                            tmp = tmp[0]

                                        if tmp1 == -2:
                                            tmp1 = stak[stak.__len__() - 1]
                                        elif tmp1 == -3:

                                            tmp1= Extra_functions.convert_string(stak[stak.__len__() - 1])

                                        else:
                                            tmp1 = tmp1[0]

                                        stak = stak[:-1]
                                        if (infix[i][j] == '-'):
                                            stak[stak.__len__() - 1] = tmp - tmp1
                                        elif (infix[i][j] == '+'):
                                            stak[stak.__len__() - 1] = tmp + tmp1
                                        elif (infix[i][j] == '*'):
                                            stak[stak.__len__() - 1] = tmp * tmp1
                                        elif (infix[i][j] == '/'):
                                            if tmp1 != 0:
                                                stak[stak.__len__() - 1] = int(tmp / tmp1)
                                            else:
                                                return 0
                                    else:
                                        if (infix[i][j] == '+') | (infix[i][j] == '-'):

                                            tmp = self.Check_is_valid_data(stak[stak.__len__() - 1])
                                            if tmp==-1:
                                                return 0
                                            elif tmp == -2:
                                                tmp = stak[stak.__len__() - 1]
                                            elif tmp==-3:

                                                tmp=Extra_functions.convert_string(stak[stak.__len__() - 1])

                                            else:
                                                tmp = tmp[0]
                                            if (infix[i][j] == '-'):
                                                stak[0] = tmp * -1
                                            else:
                                                stak[0]=tmp
                                        else:
                                            return 0
                                elif (infix[i][j] == 'dup'):
                                    a = 20
                                    ########
                                elif (infix[i][j] == 'lengthof') | (infix[i][j] == 'sizeof') | (infix[i][j] == 'type'):
                                    if stak.__len__() > 0:
                                      tmp = self.Check_is_valid_data(stak[stak.__len__() - 1])
                                      if (((tmp == 0)|(tmp == -1)|(tmp == -2)|(tmp == -3) ) &( (infix[i][j] == 'lengthof') | (infix[i][j] == 'sizeof'))):
                                          return 0
                                      elif ((tmp == 0)|(tmp == -1)|(tmp == -2)|(tmp == -3) )& (infix[i][j] == 'type'):
                                          stak[stak.__len__() - 1]=0
                                      else:
                                          stak = stak[:-1]
                                          tmp1 = self.Type(tmp[1])

                                          if infix[i][j] == 'lengthof':
                                              stak.append(int(tmp[2]/tmp1))
                                          elif infix[i][j] == 'sizeof':
                                              stak.append(tmp[2] )
                                          else:
                                              stak.append(tmp[0])
                                    else:
                                        return 0

                                else:
                                   if infix[i][j]=='?':
                                        stak.append(0)
                                   else:
                                       tmp = self.Check_is_valid_data(infix[i][j])
                                       if tmp == -1:
                                           return 0
                                       else:
                                           stak.append(infix[i][j])
                            tmp_memory.append(stak)

                        if self.Save_in_Memory(8*self.Type(Line[0]),tmp_memory)== False:
                            return 0
                        self.Data_type_for_comma=self.Type(Line[0])
                        #print(self.Memory_data_segment)
                    else:
                        return 0
                else:
                    return  0
            else:
                if Line.__len__()>1:
                    if self.Data_types.__contains__(Line[1])==True:
                        var_type_len.append(self.Memory_data_segment.__len__())
                        var_type_len.append(Line[1])
                        var_type_len.append(0)
                        infix=Extra_functions.postfix(Line[2:])
                        if infix !=False:
                            if Line[Line.__len__()-1]==',':
                                Comma=True

                           # print(infix)

                            tmp_memory = []
                            for i in range(0, len(infix)):
                                stak = []
                                for j in range(0, len(infix[i])):
                                    if (infix[i][j] == '+') | (infix[i][j] == '-') | (infix[i][j] == '*') | (infix[i][j] == '/'):
                                        if stak.__len__() > 1:

                                            tmp = self.Check_is_valid_data(stak[stak.__len__() - 1])
                                            tmp1 = self.Check_is_valid_data(stak[stak.__len__() - 2])
                                            if (tmp == -1) | (tmp1 == -1):
                                                return 0
                                            if tmp == -2:
                                                tmp = stak[stak.__len__() - 1]
                                            elif tmp == -3:

                                                tmp = Extra_functions.convert_string(stak[stak.__len__() - 1])
                                            else:
                                                tmp = tmp[0]

                                            if tmp1 == -2:
                                                tmp1 = stak[stak.__len__() - 2]
                                            elif tmp1 == -3:

                                                tmp1 = Extra_functions.convert_string(stak[stak.__len__() - 1])

                                            else:
                                                tmp1 = tmp1[0]

                                            stak = stak[:-1]
                                            if (infix[i][j] == '-'):
                                                stak[stak.__len__() - 1] = tmp - tmp1
                                            elif (infix[i][j] == '+'):
                                                stak[stak.__len__() - 1] = tmp + tmp1
                                            elif (infix[i][j] == '*'):
                                                stak[stak.__len__() - 1] = tmp * tmp1
                                            elif (infix[i][j] == '/'):
                                                if tmp1 != 0:
                                                    stak[stak.__len__() - 1] = int(tmp / tmp1)
                                                else:
                                                    return 0
                                        else:
                                            if (infix[i][j] == '+') | (infix[i][j] == '-'):

                                                tmp = self.Check_is_valid_data(stak[stak.__len__() - 1])
                                                if tmp == -1:
                                                    return 0
                                                elif tmp == -2:
                                                    tmp = stak[stak.__len__() - 1]
                                                elif tmp == -3:

                                                    tmp = Extra_functions.convert_string(stak[stak.__len__() - 1])

                                                else:
                                                    tmp = tmp[0]
                                                if (infix[i][j] == '-'):
                                                    stak[0] = tmp * -1
                                                else:
                                                    stak[0] = tmp
                                            else:
                                                return 0
                                    elif (infix[i][j] == 'dup'):
                                        a = 20
                                        ########
                                    elif (infix[i][j] == 'lengthof') | (infix[i][j] == 'sizeof') | (infix[i][j] == 'type'):
                                        if stak.__len__() > 0:
                                            tmp = self.Check_is_valid_data(stak[stak.__len__() - 1])
                                            if (((tmp == 0) | (tmp == -1) | (tmp == -2) | (tmp == -3)) & (
                                                (infix[i][j] == 'lengthof') | (infix[i][j] == 'sizeof'))):
                                                return 0
                                            elif ((tmp == 0) | (tmp == -1) | (tmp == -2) | (tmp == -3)) & (
                                                infix[i][j] == 'type'):
                                                stak[stak.__len__() - 1] = 0
                                            else:
                                                stak = stak[:-1]
                                                tmp1 = self.Type(tmp[1])

                                                if infix[i][j] == 'lengthof':
                                                    stak.append(int(tmp[2] / tmp1))
                                                elif infix[i][j] == 'sizeof':
                                                    stak.append(tmp[2])
                                                else:
                                                    stak.append(tmp[0])
                                        else:
                                            return 0

                                    else:
                                        if infix[i][j] == '?':
                                            stak.append(0)
                                        else:
                                            tmp = self.Check_is_valid_data(infix[i][j])
                                            if tmp == -1:
                                                return 0
                                            else:
                                                stak.append(infix[i][j])
                                tmp_memory.append(stak)


                            if self.Save_in_Memory(8 * self.Type(Line[1]), tmp_memory) == False:
                                return 0
                            self.Data_type_for_comma = self.Type(Line[1])
                            #print(self.Memory_data_segment)

                            var_type_len[2]=(self.Memory_data_segment.__len__()-var_type_len[0])

                            self.Data_variables[Line[0]]=var_type_len
                            #print(self.Data_variables)
                        else:
                            return 0
                    else:
                        return  0
                else:
                    return 0
        else:
            if self.Data_type_for_comma==0:
                return 0
            infix = Extra_functions.postfix(Line)
            if infix != False:
                if Line[Line.__len__() - 1] == ',':
                    Comma = True
                else:
                    Comma=False
               # print(infix)

                tmp_memory = []
                for i in range(0, len(infix)):
                    stak = []
                    for j in range(0, len(infix[i])):
                        if (infix[i][j] == '+') | (infix[i][j] == '-') | (infix[i][j] == '*') | (infix[i][j] == '/'):
                            if stak.__len__() > 1:
                                tmp = self.Check_is_valid_data(stak[stak.__len__() - 1])
                                tmp1 = self.Check_is_valid_data(stak[stak.__len__() - 2])
                                if (tmp == -1) | (tmp1 == -1):
                                    return 0
                                if tmp == -2:
                                    tmp = stak[stak.__len__() - 1]
                                elif tmp == -3:

                                    tmp = Extra_functions.convert_string(stak[stak.__len__() - 1])

                                else:
                                    tmp = tmp[0]

                                if tmp1 == -2:
                                    tmp1 = stak[stak.__len__() - 1]
                                elif tmp1 == -3:

                                    tmp1 = Extra_functions.convert_string(stak[stak.__len__() - 1])

                                else:
                                    tmp1 = tmp1[0]

                                stak = stak[:-1]
                                if (infix[i][j] == '-'):
                                    stak[stak.__len__() - 1] = tmp - tmp1
                                elif (infix[i][j] == '+'):
                                    stak[stak.__len__() - 1] = tmp + tmp1
                                elif (infix[i][j] == '*'):
                                    stak[stak.__len__() - 1] = tmp * tmp1
                                elif (infix[i][j] == '/'):
                                    if tmp1 != 0:
                                        stak[stak.__len__() - 1] = int(tmp / tmp1)
                                    else:
                                        return 0
                            else:
                                if (infix[i][j] == '+') | (infix[i][j] == '-'):

                                    tmp = self.Check_is_valid_data(stak[stak.__len__() - 1])
                                    if tmp == -1:
                                        return 0
                                    elif tmp == -2:
                                        tmp = stak[stak.__len__() - 1]
                                    elif tmp == -3:

                                        tmp = Extra_functions.convert_string(stak[stak.__len__() - 1])

                                    else:
                                        tmp = tmp[0]
                                    if (infix[i][j] == '-'):
                                        stak[0] = tmp * -1
                                    else:
                                        stak[0] = tmp
                                else:
                                    return 0
                        elif (infix[i][j] == 'dup'):
                            a = 20
                            ########
                        elif (infix[i][j] == 'lengthof') | (infix[i][j] == 'sizeof') | (infix[i][j] == 'type'):
                            if stak.__len__() > 0:
                                tmp = self.Check_is_valid_data(stak[stak.__len__() - 1])
                                if (((tmp == 0) | (tmp == -1) | (tmp == -2) | (tmp == -3)) & (
                                    (infix[i][j] == 'lengthof') | (infix[i][j] == 'sizeof'))):
                                    return 0
                                elif ((tmp == 0) | (tmp == -1) | (tmp == -2) | (tmp == -3)) & (infix[i][j] == 'type'):
                                    stak[stak.__len__() - 1] = 0
                                else:
                                    stak = stak[:-1]
                                    tmp1 = self.Type(tmp[1])

                                    if infix[i][j] == 'lengthof':
                                        stak.append(int(tmp[2] / tmp1))
                                    elif infix[i][j] == 'sizeof':
                                        stak.append(tmp[2])
                                    else:
                                        stak.append(tmp[0])
                            else:
                                return 0

                        else:
                            if infix[i][j] == '?':
                                stak.append(0)
                            else:
                                tmp = self.Check_is_valid_data(infix[i][j])
                                if tmp == -1:
                                    return 0
                                else:
                                    stak.append(infix[i][j])
                    tmp_memory.append(stak)
                L1=self.Memory_data_segment.__len__()

                if self.Save_in_Memory(8 * self.Data_type_for_comma, tmp_memory) == False:
                    return 0
                #print(self.Memory_data_segment)
                if self.Data_variables.__len__()>0:
                    V=sorted(self.Data_variables.keys())[-1]
                    self.Data_type_for_comma=self.Type(self.Data_variables[V][1])
                    if self.Data_variables[V][0]+self.Data_variables[V][2]==L1:
                        self.Data_variables[V][2] = (self.Memory_data_segment.__len__() - self.Data_variables[V][0])


            else:
                return 0

        if Comma==False:
            return 1