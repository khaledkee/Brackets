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
    Code_segment=[]
    Functions_names={}
    Labels_names={}
    Opened_function=""
    Data_type_for_comma=0
    def __init__(self,Code):
        Code=Code.replace('\t','   ')
        self.Code =Code.lower()

    def Start(self):
        if self.Split_to_Lines()!=False:
            if self.Remove_constants() == False:
                print("syntax error")
                return
            else:
                X = 0
                if self.Build_Memory()==False:
                    print("syntax error")
                    return
                else:
                    if self.Build_code_segment() == False:
                        print("syntax error")
                        return
        else:
            print("syntax error")
            return


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

    def Build_code_segment(self):
        i = 0
        if (self.Code_Lines[0].__len__() == 1) & (self.Code_Lines[0][0] == ".code"):
            self.Code_Lines.remove(self.Code_Lines[0])
        else:
            return False
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
                            else:
                                b=20
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
                                b=20
                        elif self.Special_Names_two_Operands.__contains__(self.Code_Lines[i][0])==True:
                            b=20
                        elif self.Code_Lines[i][0]=='uses':
                            b=0
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
                                    if (infix[i][j] == '+') | (infix[i][j] == '-') | (infix[i][j] == '*') | (
                                        infix[i][j] == '/'):
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
                                    elif (infix[i][j] == 'lengthof') | (infix[i][j] == 'sizeof') | (
                                        infix[i][j] == 'type'):
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