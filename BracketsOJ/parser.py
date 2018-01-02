from BracketsOJ import extra_functions
import string

class Parser:
    Special_Symbols = "~!@#$%^&*()+=/-,{}<:>?[]\|"
    Digits = "0123456789"
    Special_Names = [
        "include", "equ", "proc", "endp", "end", "uses","ax", "bx", "cx", "dx",
            "al", "ah", "bl", "bh", "ch", "cl", "dh", "dl",
        "type", "sizeof", "lengthof", "ptr", "dup", "offset"]
    Data_types = [
        "byte", "sbyte", "word", "sword", "dword", "sdword"
    ]
    Irvine32_functions = [
        "crlf", "readchar", "readdec", "readstring", "readint", "writechar", "writedec", "writestring", "writeint",
        "dumpregs"
    ]
    Special_Names_no_Operands = [
         "cbw",
        "cwd", "cdq", "cld", "std", "stc", "clc", "ret", "exit"
    ]
    Special_Names_one_Operands = [
        "call", "jmp", "neg", "inc", "dec", "loop",
        "je", "jz", "jne", "jnz", "ja", "jnbe",
        "jg", "jnle", "jae", "jnb", "jge", "jnl", "jb", "jnae",
        "jl", "jnge", "jbe", "jna", "jle", "jng", "mul", "imul",
        "div", "idiv","jc", "jnc"

    ]
    Special_Names_two_Operands = [
        "sbb", "acd", "shl", "shr",
        "sal", "sar", "rol", "ror", "rcl", "rcr", "mov", "movsx",
        "movzx", "add", "sub", "xchg", "test", "xor", "and", "or", "cmp"
    ]

    def __init__(self, Code, Max_Instructions, Max_Memory, Input_File):
        self.Input_File = Input_File
        Code = Code.replace('\t', '   ')
        Code = Code.replace('\r', '')
        self.Code_Lines = []
        self.Code = Code+'\n'
        self.Max_Instructions = Max_Instructions
        self.Max_Memory = Max_Memory
        self.State = ""
        self.Input_File_index = 0
        self.Output_File = ""
        self.Registers = {
            "eax": 0, "ecx": 0, "edx": 0, "ebx": 0,
            "esp": 0, "ebp": 0, "esi": 0, "edi": 0,
            "eip": 0
        }
        self.Flags = {"cf": 0, "of": 0, "sf": 0, "ac": 0, "pf": 0, "zf": 0, "df": 0}
        self.Data_variables = {}
        self.Memory_data_segment = []
        self.Code_segment = []
        self.Stack_segment = []
        self.Functions_names = {}
        self.Labels_names = {}
        self.Opened_function = ""
        self.Use_Uses = []
        self.Data_type_for_comma = 0
        self.Instructions = 0
        self.Error_Line=0
        self.Error = ""
    def Start(self):

        """
            This function start some operations on code
            split code to lines ,
            remove constants ,
            build data segment ,
            build code segment
            then start to get results from the code

            Return :
            False if there where syntax error
            String "TL" if there where time limit
            String "ML" if there where memory limit
            String "RTE" if there where runtime error
            List contains 'number of instructions , number of bytes that code used in memory , string contains output from the code'
        """
        try:
            if self.Split_to_Lines():
                if not self.Remove_constants():
                    self.Error_Line = -1
                    self.Error=""" Error in data or constant"""
                    return False
                else:
                    if not self.Build_Memory():
                        self.Error_Line =-1
                        """ Error in data or constant"""
                        if self.State != "":
                            return self.State
                        return False
                    else:
                        if not self.Build_code_segment():
                            self.Error_Line = len(self.Code_segment)
                            self.Error=""" Error build code"""
                            if self.State != "":
                                return self.State
                            return False
                        else:
                            if not self.Start_Code():
                                self.Error_Line = self.Registers["eip"]
                                self.Error = """ Error in code"""
                                if self.State != "":
                                    return self.State
                                return False
                            else:
                                if self.State != "":
                                    return self.State
                                return [self.Instructions, len(self.Memory_data_segment) + len(self.Stack_segment),
                                        self.Output_File]
            else:
                return False
        except Exception:
            self.State="RTE"
            return False

    def Split_to_Lines(self):

        """
            This function start some operations on code
            split code to lines by removing extra spaces and comments ,
            convert capital letters to small letters except the strings
            then stop when find " end <lable> " or when the code end

            Return :
            False if there where syntax error
            List contains 'Strings that for each code word'
        """

        line = []
        word = ""
        comment = False
        String = False
        for i in range(0, len(self.Code)):
            if self.Code[i] == '\n':
                if word != '':
                    if (String is True) and (word[0] != word[len(word) - 1]):
                        return False
                    line.append(word)
                if len(line) != 0:
                    self.Code_Lines.append(line)
                    if len(line) >= 2:
                        if line[0] == "end":
                            break
                word = ""
                line = []
                comment = False
                String = False
            elif not comment:
                if self.Code[i] == ' ':
                    if not String:
                        if word != "" and word != '':
                            line.append(str(word))
                            word = ""
                    else:
                        word += self.Code[i]
                else:
                    if self.Code[i] == '"':
                        if not String:
                            if word != "":
                                if word != '':
                                    line.append(word)
                            word = '"'
                            String = True
                        elif word[0] == self.Code[i]:
                            String = False
                            word += self.Code[i]
                            if word != '':
                                line.append(word)
                                word = ""
                        else:
                            word += self.Code[i]
                    elif self.Code[i] == '\'':
                        if not String:
                            if word != "":
                                if word != '':
                                    line.append(word)
                            word = '\''
                            String = True
                        elif word[0] == self.Code[i]:
                            String = False
                            word += self.Code[i]
                            if word != '':
                                line.append(word)
                                word = ""
                        else:
                            word += self.Code[i]
                    else:
                        if String:
                            word += self.Code[i]
                        else:
                            if self.Code[i] == ';':
                                comment = True

                            elif self.Code[i] in self.Special_Symbols:
                                if word != '':
                                    line.append(word)
                                    line.append(self.Code[i])
                                    word = ""
                                else:
                                    line.append(self.Code[i])

                            else:
                                word += self.Code[i].lower()

        return self.Code_Lines

    def Remove_constants(self):

        """
                    This function start some operations on code
                    removing constants from the code

                    Return :
                    False if there where syntax error
                    True if there where no syntax error
        """

        i = 0
        while i < len(self.Code_Lines):
            if len(self.Code_Lines[i]) > 2:
                if self.Code_Lines[i][1] == "equ":
                    if not self.Check_is_valid(self.Code_Lines[i][0]):
                        return False
                    else:
                        for j in range(0, len(self.Code_Lines)):
                            if j != i:
                                if self.Code_Lines[i][0] in self.Code_Lines[j]:
                                    Index = self.Code_Lines[j].index(self.Code_Lines[i][0])
                                    for k in range(0, len(self.Code_Lines[i]) - 2):
                                        self.Code_Lines[j].insert(Index + k, self.Code_Lines[i][k + 2])
                                    self.Code_Lines[j].remove(self.Code_Lines[i][0])

                    self.Code_Lines.remove(self.Code_Lines[i])
                    continue
            i = i + 1
        return True

    def Build_Memory(self):

        """
                    This function start some operations on code
                    build data segment by check the first from " include irvine32.inc " ,
                    loop between " .data " and " .code " ,
                    by checking that line is valid or not
                    then build the memory if was valid

                    Return :
                    False if there where syntax error
                    True if there where  no syntax error
        """

        Comma = False
        if (len(self.Code_Lines[0]) == 2) and (self.Code_Lines[0][0] == "include") and (
                    self.Code_Lines[0][1] == "irvine32.inc"):
            self.Code_Lines.remove(self.Code_Lines[0])
            i = 0
            while i < len(self.Code_Lines) - 1:
                if (len(self.Code_Lines[i]) == 1) and (self.Code_Lines[i][0] == ".data"):
                    self.Code_Lines.remove(self.Code_Lines[i])
                    while i < self.Code_Lines.__len__() - 1:
                        if (self.Code_Lines[i].__len__() == 1) and (self.Code_Lines[i][0] == ".code"):
                            i = i + 1
                            break
                        elif (self.Code_Lines[i].__len__() == 1) and (self.Code_Lines[i][0] == ".data"):
                            self.Code_Lines.remove(self.Code_Lines[i])
                        else:
                            tmp = self.Check_data_line(self.Code_Lines[i], Comma)
                            if tmp == 0:
                                return False
                            elif tmp == 1:
                                Comma = False
                            else:
                                Comma = True
                            self.Code_Lines.remove(self.Code_Lines[i])
                else:
                    i = i + 1
            if Comma:
                return False
        else:
            return False

        return True

    def Check_data_line(self, Line, Comma):

        """
                            This function start some operations on code
                            checking that line is valid data line or not
                            by convert each value to infix notation
                            calculate it
                            find variables names , adress , types and size
                            then save it in memory



                            Return :
                            0 if there where no comma at the end of the line
                            1 if there where  comma at the end of the line
        """

        var_type_len = []  # (adress,data_type,size)
        if not Comma:

            if not self.Check_is_valid(Line[0]):
                if (Line[0] in self.Data_types) and (len(Line) > 1):
                    infix = self.postfix(Line[1:])
                    if infix:
                        if Line[Line.__len__() - 1] == ',':
                            Comma = True
                        tmp_memory = []
                        for i in range(0, len(infix)):
                            tmp=self.Calc_infix(infix[i])
                            if tmp!=False:
                                tmp_memory.append(tmp)
                            else:
                                return 0

                        if not self.Save_in_Memory(8 * self.Type(Line[0]), tmp_memory):
                            return 0
                        self.Data_type_for_comma = self.Type(Line[0])
                    else:
                        return 0
                else:
                    return 0
            else:
                if Line.__len__() > 1:
                    if self.Data_types.__contains__(Line[1]):
                        var_type_len.append(self.Memory_data_segment.__len__())
                        var_type_len.append(Line[1])
                        var_type_len.append(0)
                        a=self.Type(Line[1])
                        self.Data_variables[Line[0]] = var_type_len
                        infix = self.postfix(Line[2:])

                        if infix:
                            if Line[Line.__len__() - 1] == ',':
                                Comma = True
                            tmp_memory = []
                            for i in range(0, len(infix)):
                                tmp = self.Calc_infix(infix[i])

                                if  (tmp!=False):
                                    self.Data_variables[Line[0]][2]+=a
                                    tmp_memory.append(tmp)
                                else:
                                    return 0
                            if not self.Save_in_Memory(8 * self.Type(Line[1]), tmp_memory):
                                return 0
                            self.Data_type_for_comma = self.Type(Line[1])
                            var_type_len[2] = (self.Memory_data_segment.__len__() - var_type_len[0])
                            self.Data_variables[Line[0]] = var_type_len
                        else:
                            return 0
                    else:
                        return 0
                else:
                    return 0
        else:
            if self.Data_type_for_comma == 0:
                return 0
            infix = self.postfix(Line)
            if infix:
                if Line[Line.__len__() - 1] == ',':
                    Comma = True
                else:
                    Comma = False
                tmp_memory = []
                for i in range(0, len(infix)):
                    tmp = self.Calc_infix(infix[i])
                    if (tmp != False):
                        tmp_memory.append(tmp)
                    else:
                        return 0
                L1 = len(self.Memory_data_segment)
                if not self.Save_in_Memory(8 * self.Data_type_for_comma, tmp_memory):
                    return 0
                if len(self.Data_variables) > 0:
                    V = sorted(self.Data_variables.keys())[-1]
                    self.Data_type_for_comma = self.Type(self.Data_variables[V][1])
                    if self.Data_variables[V][0] + self.Data_variables[V][2] == L1:
                        self.Data_variables[V][2] = (len(self.Memory_data_segment) - self.Data_variables[V][0])
            else:
                return 0

        if not Comma:
            return 1

    def Check_is_valid(self, String):

        """
                                    This function start some operations on code
                                    checking that the word is valid data variable , lable or not
                                    by check in the lists that contains old one and some special names

                                    Return :
                                    False if it not valid
                                    True if it valid
        """

        if self.Special_Names.__contains__(String):
            return False
        elif self.Special_Names_no_Operands.__contains__(String):
            return False
        elif self.Special_Names_one_Operands.__contains__(String):
            return False
        elif self.Special_Names_two_Operands.__contains__(String):
            return False
        elif self.Data_types.__contains__(String):
            return False
        elif self.Registers.__contains__(String):
            return False
        elif self.Irvine32_functions.__contains__(String):
            return False
        elif String.__contains__('"'):
            return False
        elif String.__contains__('\''):
            return False
        elif String.__contains__('.'):
            return False
        elif String[0].isdecimal():
            return False
        if len(self.Data_variables) > 0:
            if self.Data_variables.__contains__(String):
                return False
        if len(self.Functions_names) > 0:
            if self.Functions_names.__contains__(String):
                return False
        if len(self.Labels_names) > 0:
            if self.Labels_names.__contains__(String):
                return False
        return True

    def postfix(self,Line):

        """
                                    This function start some operations on code
                                    convert each value to infix notation
                                    remove " dup " recursively

                                    Return :
                                    False if there where syntax error
                                    List contains 'infix notation for the line'
        """

        stak = []
        expression = []
        infix = []
        i=0
        while( i <(len(Line))):
            if (Line[i] == '(') or (Line[i] == '['):
                if len(stak) > 0:
                    if (Line[i] == '[') and ((stak[len(stak) - 1] == "lengthof") or (stak[len(stak) - 1] == "dup") or (stak[len(stak) - 1] == "sizeof") or (stak[len(stak) - 1] == "type")):
                        return False
                if len(stak) > 0:
                    if (Line[i] == '(') and ((stak[len(stak) - 1] == "lengthof") or (stak[len(stak) - 1] == "sizeof")):
                        return False
                if (len(stak) == 0) and (Line[i] == '('):
                    return False
                stak.append(Line[i])
            elif (Line[i] == ')') or (Line[i] == ']'):
                if len(stak) == 0:
                    return False

                j = len(stak) - 1
                while j >= 0:
                    if (stak[j] == '(') and (Line[i] == ')'):
                        break
                    elif (stak[j] == '(') and (Line[i] == ']'):
                        return False
                    elif (stak[j] == '[') and (Line[i] == ')'):
                        return False
                    elif (stak[j] == '[') and (Line[i] == ']'):
                        break
                    expression.append(stak[j])
                    stak = stak[:-1]
                    j = j - 1
                    if j < 0:
                        break

                stak = stak[:-1]
                if (len(stak) > 0) and (stak[stak.__len__() - 1] == 'dup'):
                    expression.append(stak[stak.__len__() - 1])
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
                if (expression.__len__() > 0)and(expression!=["dup"]):
                    infix.append(expression)
                expression = []
            elif Line[i][0].isdecimal():
                if Line[i][len(Line[i]) - 1] == 'h':
                    tmp = extra_functions.is_hexa(Line[i])
                    if not tmp:
                        return False
                    expression.append(tmp)

                elif Line[i][len(Line[i]) - 1] == 'o':
                    tmp = extra_functions.is_octa(Line[i])
                    if not tmp:
                        return False
                    expression.append(tmp)
                elif Line[i][len(Line[i]) - 1] == 'b':
                    tmp = extra_functions.is_binary(Line[i])
                    if not tmp:
                        return False
                    expression.append(tmp)
                elif Line[i][len(Line[i]) - 1] == 'd':
                    tmp = int(Line[i][:-1], 10)
                    expression.append(tmp)
                elif Line[i].isdecimal():
                    expression.append(int(Line[i]))
                else:
                    return False
            elif (Line[i] == "lengthof") or (Line[i] == "sizeof") or (Line[i] == "type") or (Line[i] == "dup"):
                if (Line[i] == "dup"):
                    if stak.__len__()>0:
                        j = stak.__len__() - 1
                        while (j >= 0):
                            expression.append(stak[j])
                            stak = stak[:-1]
                            j = j - 1
                    S = []
                    L = []
                    i = 1 + i
                    while (i < len(Line)):
                        if (Line[i] == '(') or (Line[i] == '['):
                            S.append(Line[i])
                        elif (Line[i] == ')') or (Line[i] == ']'):
                            if len(S) == 0:
                                return False
                            j = len(S) - 1
                            while j >= 0:
                                if (S[j] == '(') and (Line[i] == ')'):
                                    break
                                elif (S[j] == '(') and (Line[i] == ']'):
                                    return False
                                elif (S[j] == '[') and (Line[i] == ')'):
                                    return False
                                elif (S[j] == '[') and (Line[i] == ']'):
                                    break
                                S = S[:-1]
                                j = j - 1
                                if j < 0:
                                    break
                            S = S[:-1]

                        L.append(Line[i])
                        if len(S) == 0:
                            break
                        i += 1
                    if L.__len__() > 1:
                        if (L[L.__len__() - 1] == ')') and (L[0] == '('):
                            L = L[:-1]
                            L = L[1:]
                        else:
                            return False
                    else:
                        return False
                    tmp = self.postfix(L)
                    i = i + 1
                    if tmp != False:
                        tmp1 = self.Calc_infix(expression)
                        if tmp1 != False:
                            for j in range(0, tmp1[0]):
                                infix = infix + tmp
                        else:
                            return False
                    else:
                        return False
                    expression=["dup"]
                    continue
                stak.append(Line[i])
            else:
                if (Line[i] == '*') | (Line[i] == '-') | (Line[i] == '/') | (Line[i] == '+'):
                    if len(stak) > 0:
                        j = len(stak) - 1
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
                            elif (stak[j] == 'dup') | (stak[j] == 'lengthof') | (stak[j] == 'type') | (stak[j] == 'sizeof'):
                                expression.append(stak[j])
                                stak = stak[:-1]
                            else:
                                break
                            j = j - 1
                    stak.append(Line[i])
                else:
                    expression.append(Line[i])
            i += 1

        j = len(stak) - 1
        while j >= 0:
            if (stak[j] == '(') or (stak[j] == '['):
                return False
            expression.append(stak[j])
            stak = stak[:-1]
            j = j - 1

        if (expression.__len__() > 0)and(expression!=["dup"]):
            infix.append(expression)
        return infix

    def Calc_infix(self,infix):

        """
                                    This function start some operations on code
                                    calculate infix notation

                                    Return :
                                    False if there where syntax error
                                    List contains 'value of infix notation'
        """

        stak=[]
        for i in range(0, len(infix)):
            if (infix[i] == '+') or (infix[i] == '-') or (infix[i] == '*') or (infix[i] == '/'):
                if len(stak) > 1:
                    tmp = self.Check_is_valid_data(stak[len(stak) - 1])
                    tmp1 = self.Check_is_valid_data(stak[len(stak) - 2])
                    if (tmp == -1) or (tmp1 == -1):
                        return False
                    if tmp == -2:
                        tmp = stak[len(stak) - 1]
                    elif tmp == -3:
                        tmp = extra_functions.convert_string(stak[len(stak) - 1])

                    else:
                        tmp = tmp[0]

                    if tmp1 == -2:
                        tmp1 = stak[len(stak) - 2]
                    elif tmp1 == -3:

                        tmp1 = extra_functions.convert_string(stak[len(stak) - 2])

                    else:
                        tmp1 = tmp1[0]

                    stak = stak[:-1]
                    if infix[i] == '-':
                        stak[len(stak) - 1] = tmp - tmp1
                    elif infix[i] == '+':
                        stak[len(stak) - 1] = tmp + tmp1
                    elif infix[i] == '*':
                        stak[len(stak) - 1] = tmp * tmp1
                    elif infix[i]== '/':
                        if tmp1 != 0:
                            stak[len(stak) - 1] = int(tmp / tmp1)
                        else:
                            return False
                else:
                    if (infix[i] == '+') or (infix[i] == '-'):

                        tmp = self.Check_is_valid_data(stak[len(stak) - 1])
                        if tmp == -1:
                            return False
                        elif tmp == -2:
                            tmp = stak[len(stak) - 1]
                        elif tmp == -3:

                            tmp = extra_functions.convert_string(stak[len(stak) - 1])

                        else:
                            tmp = tmp[0]
                        if infix[i] == '-':
                            stak[0] = tmp * -1
                        else:
                            stak[0] = tmp
                    else:
                        return False
            elif (infix[i] == 'lengthof') or (infix[i]== 'sizeof') or (infix[i] == 'type'):
                if len(stak) > 0:
                    tmp = self.Check_is_valid_data(stak[len(stak) - 1])
                    if (((tmp == 0) or (tmp == -1) or (tmp == -2) or (tmp == -3)) and ((infix[i]== 'lengthof') or (infix[i] == 'sizeof'))):
                        return False
                    elif ((tmp == 0) or (tmp == -1) or (tmp == -2) or (tmp == -3)) and (infix[i] == 'type'):
                        stak[len(stak) - 1] = 0
                    else:
                        stak = stak[:-1]
                        tmp1 = self.Type(tmp[1])

                        if infix[i] == 'lengthof':
                            stak.append(int(tmp[2] / tmp1))
                        elif infix[i] == 'sizeof':
                            stak.append(tmp[2])
                        else:
                            stak.append(tmp[0])
                else:
                    return False
            else:
                if infix[i] == '?':
                    stak.append(0)
                else:
                    tmp = self.Check_is_valid_data(infix[i])
                    if self.Data_types.__contains__(infix[i]):
                        stak.append(self.Type(infix[i]))
                        continue
                    if tmp == -1:
                        return False
                    else:
                        stak.append(infix[i])

        if stak.__len__() == 1:
            return stak
        return False

    def Check_is_valid_data(self, String):

        """
                                            This function start some operations on code
                                            check the value is valid or not

                                            Return :
                                            -1 if there not valid
                                            -2 if it was number
                                            -3 if it was string
                                            List contains 'address , data type , size' for data variable
        """
        if len(self.Data_variables) > 0:
            if self.Data_variables.__contains__(String):
                return self.Data_variables[String]
        try:
            String += 0
            return -2
        except Exception:
            if ((String[0] == String[len(String) - 1]) and (String[0] == '"')) or (
                    (String[0] == String[len(String) - 1]) and (String[0] == "\'")):
                return -3
        return -1

    def Type(self, String):

        """
                                    This function start some operations on code

                                    Return :
                                    1 if there where byte
                                    2 if there where  word
                                    4 if there where  dword
        """

        if (String == "byte") or (String == "sbyte"):
            return 1
        elif (String == "word") or (String == "sword"):
            return 2
        else:
            return 4

    def Save_in_Memory(self, Type, tmp_memory):

        """
                                    This function start some operations on code
                                    save values in memory



                                    Return :
                                    False by set state to "ML" if there where memory limit
                                    False without set state if there where syntax error
                                    True if there where no syntax error
        """

        for i in range(0, len(tmp_memory)):
            if self.Max_Memory < self.Memory_data_segment.__len__():
                self.State = "ML"
                return False
            try:
                tmp_memory[i][0] += 0
                if tmp_memory[i][0] < 0:
                    tmp_memory[i][0] = pow(2, Type) + tmp_memory[i][0]
                if tmp_memory[i][0] < 0:
                    return False
                tmp = str(hex(tmp_memory[i][0]))[2:]
                if tmp.__len__() * 4 > Type:
                    return False

                for j in range(0, int(Type / 8)):
                    if tmp == "":
                        self.Memory_data_segment.append("00")
                    elif tmp.__len__() > 1:
                        self.Memory_data_segment.append(tmp[len(tmp) - 2] + tmp[len(tmp) - 1])
                        tmp = tmp[:-2]
                    else:
                        self.Memory_data_segment.append('0' + tmp[len(tmp) - 1])
                        tmp = tmp[:-1]
                continue
            except Exception:
                string = tmp_memory[i][0]
                string = string[:-1]
                string = string[1:]
                for j in range(0, len(string)):
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
        return True

    def Build_code_segment_Lables(self):

        """
            This function start some operations on code
            store lables names before check the code lines

            Return :
            False if there where syntax error
            True if there where no syntax error
        """

        i = 0
        while (i < len(self.Code_Lines) - 1):
            if len(self.Code_Lines[i]) > 1:
                if len(self.Code_Lines[i]) == 2:
                    if self.Code_Lines[i][1] == 'proc':
                        if (self.Check_is_valid(self.Code_Lines[i][0])):
                            self.Functions_names[self.Code_Lines[i][0]] = 0
                        else:
                            return False
                    if self.Code_Lines[i][1] == ':':
                        if (self.Check_is_valid(self.Code_Lines[i][0]) == True):
                            self.Labels_names[self.Code_Lines[i][0]] = 0
                        else:
                            return False
                else:
                    if self.Code_Lines[i][1] == 'proc':
                        if (self.Check_is_valid(self.Code_Lines[i][0])):
                            self.Functions_names[self.Code_Lines[i][0]] = 0
                        else:
                            return False
                    if self.Code_Lines[i][1] == ':':
                        if (self.Check_is_valid(self.Code_Lines[i][0]) == True):
                            self.Labels_names[self.Code_Lines[i][0]] = 0
                        else:
                            return False
            i = i + 1
        return True

    def Build_code_segment(self):

        """
            This function start some operations on code
            remove lables ,
            loop between " .code " and " .code " or the end of code ,
            by checking that line is valid or not ,
            convert it to infix notation
            then build the code segment if was valid

            Return :
            False if there where syntax error
            True if there where no syntax error
        """

        if self.Build_code_segment_Lables() is False:
            return False


        i = 0
        if (self.Code_Lines[0].__len__() == 1) and (self.Code_Lines[0][0] == ".code"):
            self.Code_Lines.remove(self.Code_Lines[0])
        else:
            return False
        reg_32 = ["eax", "ebx", "ecx", "edx", "ebp", "esp", "esi", "edi"]
        reg_16 = ["ax", "bx", "cx", "dx"]
        while i < len(self.Code_Lines) - 1:

            if (len(self.Code_Lines[i]) == 1) and (self.Code_Lines[i][0] == ".code"):
                i = i + 1
            else:
                if (len(self.Code_Lines[i]) == 1) and (self.Code_Lines[i][0] in self.Special_Names_no_Operands):
                    self.Code_segment.append(self.Code_Lines[i][0])
                elif len(self.Code_Lines[i]) > 1:

                    if len(self.Code_Lines[i]) == 2:
                        if self.Code_Lines[i][1] == 'proc':
                            if (self.Opened_function == ""):
                                self.Opened_function = self.Code_Lines[i][0]
                                self.Functions_names[self.Code_Lines[i][0]] = self.Code_segment.__len__()
                                self.Code_segment.append("")
                            else:
                                return False
                        elif self.Code_Lines[i][1] == 'endp':
                            if self.Opened_function == self.Code_Lines[i][0]:
                                self.Opened_function = ""
                            else:
                                return False
                        elif self.Code_Lines[i][1] == ':':
                            self.Labels_names[self.Code_Lines[i][0]] = len(self.Code_segment)
                            self.Code_segment.append("")
                        elif self.Code_Lines[i][0] in self.Special_Names_one_Operands:
                            if (self.Code_Lines[i][0] == 'call') and ((self.Code_Lines[i][1] in self.Functions_names) or (self.Code_Lines[i][1] in self.Irvine32_functions)):
                                self.Code_segment.append(self.Code_Lines[i])
                            elif ((self.Code_Lines[i][0][0] == 'j') or (self.Code_Lines[i][0][0] == 'l')) and (self.Code_Lines[i][1] in self.Labels_names):
                                self.Code_segment.append(self.Code_Lines[i])
                            elif ((self.Code_Lines[i][0] != 'call') and (self.Code_Lines[i][0][0] != 'j') and (self.Code_Lines[i][0][0] != 'l')):
                                infix = self.postfix_code_line(self.Code_Lines[i][1:])
                                if not infix:
                                    return False
                                if len(infix) > 1:
                                    return False
                                self.Code_segment.append([self.Code_Lines[i][0], infix])
                            else:
                                return False
                        elif self.Code_Lines[i][0] == 'uses':
                            if self.Opened_function != "":
                                for j in range(1, len(self.Code_Lines[i])):
                                    if (reg_32.__contains__(self.Code_Lines[i][j]) == False) and (reg_16.__contains__(self.Code_Lines[i][j]) == False):
                                        return False
                                self.Code_segment.append(self.Code_Lines[i])
                            else:
                                return False
                        else:
                            return False
                    else:
                        if self.Code_Lines[i][1] == ':':
                            self.Labels_names[self.Code_Lines[i][0]] = self.Code_segment.__len__()
                            self.Code_segment.append("")
                            self.Code_Lines[i] = self.Code_Lines[i][2:]
                            i = i - 1
                        elif self.Code_Lines[i][1] == 'proc':
                            if (self.Opened_function == ""):
                                self.Opened_function = self.Code_Lines[i][0]
                                self.Functions_names[self.Code_Lines[i][0]] = self.Code_segment.__len__()
                                self.Code_segment.append("")
                                self.Code_Lines[i] = self.Code_Lines[i][2:]
                                i = i - 1
                            else:
                                return False
                        elif self.Special_Names_one_Operands.__contains__(self.Code_Lines[i][0]):
                            L = ["mul", "imul", "div", "idiv", "neg", "inc", "dec"]
                            if self.Code_Lines[i][0][0] == 'p' or self.Code_Lines[i][0] in L:
                                infix = self.postfix_code_line(self.Code_Lines[i][1:])
                                if not infix:
                                    return False
                                if infix.__len__() > 1:
                                    return False
                                self.Code_segment.append([self.Code_Lines[i][0], infix])
                            else:
                                return False
                        elif self.Special_Names_two_Operands.__contains__(self.Code_Lines[i][0]):
                            infix = self.postfix_code_line(self.Code_Lines[i][1:])
                            if not infix:
                                return False
                            if len(infix) > 2:
                                return False
                            self.Code_segment.append([self.Code_Lines[i][0], infix])
                        elif self.Code_Lines[i][0] == 'uses':
                            if self.Opened_function != "":
                                for j in range(1, len(self.Code_Lines[i])):
                                    if (reg_32.__contains__(self.Code_Lines[i][j]) == False) and (reg_16.__contains__(self.Code_Lines[i][j]) == False):
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

    def postfix_code_line(self, Line):

        """
                                    This function start some operations on code
                                    convert each value to infix notation

                                    Return :
                                    False if there where syntax error
                                    List contains 'infix notation for the line'
        """

        stak = []
        expression = []
        infix = []
        for i in range(0, len(Line)):

            reg_32 = ["eax", "ebx", "ecx", "edx", "ebp", "esp", "esi", "edi"]
            reg_16 = ["ax", "bx", "cx", "dx"]
            if (Line[i] == '(') or (Line[i] == '['):
                if len(stak) > 0:
                    if (Line[i] == '[') and ((stak[len(stak) - 1] == "lengthof") or (stak[len(stak) - 1] == "sizeof") or (stak[len(stak) - 1] == "type") or (stak[len(stak) - 1] == "offset")):
                        return False
                    if (Line[i] == '(') and ((stak[len(stak) - 1] == "lengthof") or (stak[len(stak) - 1] == "sizeof") or (stak[len(stak) - 1] == "offset")):
                        return False
                if (len(stak) == 0) and (Line[i] == '(') and (expression.__len__() != 0):
                    return False
                if expression.__len__() > 0:
                    if (Line[i] == '[') and ((expression[expression.__len__() - 1]) != "ptr") and ((reg_32.__contains__(expression[expression.__len__() - 1]) == False) and (self.Data_variables.__contains__(expression[expression.__len__() - 1]) == False)):
                        return False
                    elif (Line[i] == '[') and ((expression[expression.__len__() - 1]) != "ptr") and ((reg_32.__contains__(expression[expression.__len__() - 1]) == False)):
                        tmp = expression[expression.__len__() - 1]
                        expression[expression.__len__() - 1] = "ptr_X_"
                        expression.append(tmp)
                    elif (Line[i] == '[') and ((expression[expression.__len__() - 1]) == "ptr"):
                        # continue
                        1 == 1
                    else:
                        return False
                else:
                    if Line[i] == '[':
                        expression.append("ptr_")
                stak.append(Line[i])
            elif (Line[i] == ')') or (Line[i] == ']'):
                if len(stak) == 0:
                    return False

                j = len(stak) - 1
                while j >= 0:
                    if (stak[j] == '(') and (Line[i] == ')'):
                        break
                    elif (stak[j] == '(') and (Line[i] == ']'):
                        return False
                    elif (stak[j] == '[') and (Line[i] == ')'):
                        return False
                    elif (stak[j] == '[') and (Line[i] == ']'):
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
                if len(stak) != 0:
                    j = len(stak) - 1
                    while j >= 0:
                        expression.append(stak[j])
                        stak = stak[:-1]
                        j = j - 1
                if expression.__len__() > 0:
                    infix.append(expression)
                expression = []
            elif Line[i][0].isdecimal():
                if Line[i][len(Line[i]) - 1] == 'h':
                    tmp = extra_functions.is_hexa(Line[i])
                    if not tmp:
                        return False
                    expression.append(tmp)
                elif Line[i][len(Line[i]) - 1] == 'o':
                    tmp = extra_functions.is_octa(Line[i])
                    if not tmp:
                        return False
                    expression.append(tmp)
                elif Line[i][len(Line[i]) - 1] == 'b':
                    tmp = extra_functions.is_binary(Line[i])
                    if not tmp:
                        return False
                    expression.append(tmp)
                elif Line[i][len(Line[i]) - 1] == 'd':
                    tmp = int(Line[i][:-1], 10)
                    expression.append(tmp)
                elif Line[i].isdecimal():
                    expression.append(int(Line[i]))
                else:
                    return False
            elif (Line[i] == "lengthof") or (Line[i] == "sizeof") or (Line[i] == "type") or (Line[i] == "offset"):
                stak.append(Line[i])
            else:
                if (Line[i] == '*') or (Line[i] == '-') or (Line[i] == '/') or (Line[i] == '+'):
                    if len(stak) > 0:
                        j = len(stak) - 1
                        while j >= 0:
                            if ((stak[j] == '+') or (stak[j] == '-')) and ((Line[i] == '+') or (Line[i] == '-')):
                                expression.append(stak[j])
                                stak = stak[:-1]
                            elif ((stak[j] == '+') or (stak[j] == '-')) and ((Line[i] == '*') or (Line[i] == '/')):
                                break
                            elif ((stak[j] == '*') or (stak[j] == '/')) and ((Line[i] == '*') or (Line[i] == '/')):
                                expression.append(stak[j])
                                stak = stak[:-1]
                            elif ((stak[j] == '*') or (stak[j] == '/')) and ((Line[i] == '+') or (Line[i] == '-')):
                                expression.append(stak[j])
                                stak = stak[:-1]
                            elif ((stak[j] == 'dup') or (stak[j] == 'lengthof') or (stak[j] == 'type') or (stak[j] == 'sizeof')):
                                expression.append(stak[j])
                                stak = stak[:-1]
                            else:
                                break
                            j = j - 1

                    stak.append(Line[i])
                else:
                    try:
                        if ((Line[i][0] == Line[i][len(Line[i]) - 1]) and (Line[i][0] == '"')) or ((Line[i][0] == Line[i][len(Line[i]) - 1]) and (Line[i][0] == "\'")):
                            tmp = extra_functions.convert_string(Line[i])
                            expression.append(tmp)
                            continue
                        raise Exception("NotString")
                    except Exception:
                        expression.append(Line[i])

        j = len(stak) - 1
        while j >= 0:
            if (stak[j] == '(') or (stak[j] == '['):
                return False
            expression.append(stak[j])
            stak = stak[:-1]
            j = j - 1

        if expression.__len__() > 0:
            infix.append(expression)

        return infix

    def Start_Code(self):
        """
            This function start some operations on code
            execute the code
            by search for start function ,
            build the stack
            then send the code line to his function

            Return :
            False by set state to "ML" if there where memory limit
            False by set state to "TL" if there where time limit
            False by set state to "RTE" if there where memory out of range
            False without set state if there where syntax error
            True if there where no syntax error
        """
        if len(self.Code_Lines[len(self.Code_Lines) - 1]) == 2:
            if (self.Code_Lines[self.Code_Lines.__len__() - 1][0] == "end") and ((self.Code_Lines[len(self.Code_Lines) - 1][1]) in self.Functions_names):
                self.Registers.update({"eip": self.Functions_names[self.Code_Lines[len(self.Code_Lines) - 1][1]]})
                self.Registers.update({"eip": self.Registers["eip"] + 1})
                self.Stack_segment.append(-1)
                while self.Registers["eip"] < len(self.Code_segment):
                    if self.Max_Memory < len(self.Memory_data_segment) + len(self.Stack_segment):
                        self.State = "ML"
                        return False
                    if self.Max_Instructions < self.Instructions:
                        self.State = "TL"
                        return False
                    self.Instructions += 1
                    if self.Registers["eip"] == -1:
                        return True
                    if (self.Code_segment[self.Registers["eip"]] == "") and (self.Search_lable(self.Registers["eip"]) == False):
                        return False
                    if self.Code_segment[self.Registers["eip"]] == "":
                        self.Registers.update({"eip": self.Registers["eip"] + 1})
                        self.Instructions -= 1
                        continue
                    elif self.Special_Names_no_Operands.__contains__(self.Code_segment[self.Registers["eip"]]):
                        if self.Code_segment[self.Registers["eip"]] == "exit":
                            return True
                        elif self.Code_segment[self.Registers["eip"]] == "cbw":
                            a=self.Get_value_from_reg_X("al")
                            if bool(a & pow(2, (8) - 1)):
                                self.Save_value_in_reg_X("ah",pow(2, (8) - 1))
                            else:
                                self.Save_value_in_reg_X("ah", 0)
                        elif self.Code_segment[self.Registers["eip"]] == "cwd":
                            a = self.Get_value_from_reg_X("ax")
                            if bool(a & pow(2, (2*8) - 1)):
                                self.Save_value_in_reg_X("dx", pow(2, (2*8) - 1))
                            else:
                                self.Save_value_in_reg_X("dx", 0)
                        elif self.Code_segment[self.Registers["eip"]] == "cdq":
                            a = self.Registers["eax"]
                            if bool(a & pow(2, (4*8) - 1)):
                                self.Registers["edx"]=pow(2, (4*8) - 1)
                            else:
                                self.Registers["edx"]=0
                        elif self.Code_segment[self.Registers["eip"]] == "cld":
                            self.Flags.update({"df": 0})
                        elif self.Code_segment[self.Registers["eip"]] == "std":
                            self.Flags.update({"df": 1})
                        elif self.Code_segment[self.Registers["eip"]] == "stc":
                            self.Flags.update({"cf": 1})
                        elif self.Code_segment[self.Registers["eip"]] == "clc":
                            self.Flags.update({"cf": 0})
                        elif self.Code_segment[self.Registers["eip"]] == "ret":
                            if self.Use_Uses.__len__() != 0:

                                reg_32 = {"edi": 0, "esi": 0, "ebp": 0, "esp": 0, "ebx": 0, "edx": 0, "ecx": 0,"eax": 0}

                                i = self.Use_Uses.__len__() - 1
                                while (i >= 0):
                                    if (len(self.Stack_segment) == 0) or (self.Registers["esp"] < 0):
                                        self.State = "RTE"
                                        return False
                                    reg_32.update({self.Use_Uses[i]: self.Stack_segment[self.Registers["esp"]]})
                                    self.Stack_segment = self.Stack_segment[:-1]
                                    self.Registers.update({"esp": self.Registers["esp"] - 1})
                                    i -= 1

                                for i in self.Use_Uses:
                                    if (i.__len__() == 3) and (i != 'eip'):
                                        self.Registers.update({i: reg_32[i]})

                                self.Use_Uses=[]
                            self.Registers.update({"eip": self.Stack_segment[self.Registers["esp"]]})
                            self.Stack_segment = self.Stack_segment[:-1]
                            self.Registers.update({"esp": self.Registers["esp"] - 1})
                            continue
                    elif self.Special_Names_one_Operands.__contains__(self.Code_segment[self.Registers["eip"]][0]):
                        if (self.Code_segment[self.Registers["eip"]][0][0] == 'j') or (self.Code_segment[self.Registers["eip"]][0][0] == 'l'):
                            tmp = self.Jmp_X(self.Code_segment[self.Registers["eip"]][0])
                            if tmp:
                                self.Registers.update({"eip": self.Labels_names[self.Code_segment[self.Registers["eip"]][1]]})
                                continue
                        elif (self.Code_segment[self.Registers["eip"]][0] == 'mul') or (self.Code_segment[self.Registers["eip"]][0] == 'imul'):
                            if not self.Mul_X(self.Code_segment[self.Registers["eip"]][0],self.Code_segment[self.Registers["eip"]][1]):
                                return False
                        elif (self.Code_segment[self.Registers["eip"]][0] == 'div') or (self.Code_segment[self.Registers["eip"]][0] == 'idiv'):
                            if not self.Div_X(self.Code_segment[self.Registers["eip"]][0],self.Code_segment[self.Registers["eip"]][1]):
                                return False
                        elif (self.Code_segment[self.Registers["eip"]][0] == 'neg') or (self.Code_segment[self.Registers["eip"]][0] == 'inc') or (self.Code_segment[self.Registers["eip"]][0] == 'dec'):
                            if not self.Neg_inc_dec(self.Code_segment[self.Registers["eip"]][0], self.Code_segment[self.Registers["eip"]][1]):
                                return False
                        elif self.Code_segment[self.Registers["eip"]][0] == 'call':
                            if self.Functions_names.__contains__(self.Code_segment[self.Registers["eip"]][1]):
                                self.Stack_segment.append(self.Registers["eip"] + 1)
                                self.Registers.update({"esp": self.Registers["esp"] + 1})
                                self.Registers.update({"eip": self.Functions_names[self.Code_segment[self.Registers["eip"]][1]]})
                            else:
                                if not self.Irvine32(self.Code_segment[self.Registers["eip"]][1]):
                                    return False
                    elif self.Special_Names_two_Operands.__contains__(self.Code_segment[self.Registers["eip"]][0]):
                        L1 = ["add", "sub", "sbb", "acd"]
                        L2 = ["test", "xor", "and", "or"]
                        L4 = ["shl", "shr", "sal", "sar", "rol", "ror", "rcl", "rcr"]
                        if self.Code_segment[self.Registers["eip"]][0][0] == 'm':
                            if not self.Mov_X(self.Code_segment[self.Registers["eip"]][0],self.Code_segment[self.Registers["eip"]][1]):
                                return False
                        elif self.Code_segment[self.Registers["eip"]][0][0] == 'c':
                            if not self.Cmp(self.Code_segment[self.Registers["eip"]][0],self.Code_segment[self.Registers["eip"]][1]):
                                return False
                        elif self.Code_segment[self.Registers["eip"]][0] == 'xchg':
                            if not self.Xchg(self.Code_segment[self.Registers["eip"]][0],self.Code_segment[self.Registers["eip"]][1]):
                                return False
                        elif L1.__contains__(self.Code_segment[self.Registers["eip"]][0]):
                            if not self.Add_sub(self.Code_segment[self.Registers["eip"]][0],self.Code_segment[self.Registers["eip"]][1]):
                                return False
                        elif L2.__contains__(self.Code_segment[self.Registers["eip"]][0]):
                            if not self.Test(self.Code_segment[self.Registers["eip"]][0],self.Code_segment[self.Registers["eip"]][1]):
                                return False
                        elif L4.__contains__(self.Code_segment[self.Registers["eip"]][0]):
                            if not self.Shift(self.Code_segment[self.Registers["eip"]][0],self.Code_segment[self.Registers["eip"]][1]):
                                return False
                    elif self.Code_segment[self.Registers["eip"]][0]=='uses':
                        if self.Use_Uses.__len__()!=0:
                            return False
                        else:
                            self.Use_Uses=self.Code_segment[self.Registers["eip"]][1:]

                            reg_32 = {"eax": 0, "ecx": 0, "edx": 0, "ebx": 0, "esp": 0, "ebp": 0, "esi": 0, "edi": 0}
                            for i in self.Use_Uses:
                                if (i.__len__() == 3) and (i != 'eip'):
                                    reg_32.update({i: self.Registers[i]})
                            for i in self.Use_Uses:
                                if (i.__len__() == 3) and (i != 'eip'):
                                    self.Stack_segment.append(reg_32[i])
                                    self.Registers.update({"esp": self.Registers["esp"] + 1})


                    self.Registers.update({"eip": self.Registers["eip"] + 1})

                if (self.Registers["eip"] < 0) or (self.Registers["eip"] >= self.Code_segment.__len__()):
                    self.State = "RTE"
                    return False
            else:
                return False
        else:
            return False

        return True

    def Get_value_from_reg_X(self,string):

        """
                                    This function start some operations on code

                                    Return :
                                    Decimal value for register
        """
        tmp='e'+string[0]+'x'

        if string[1]=='l':
            return (self.Registers[tmp]&(pow(2,8)-1))
        elif string[1]=='h':
            a=(pow(2,8)-1)
            a=a.__lshift__(8)
            a=(self.Registers[tmp]&a)
            a=a.__rshift__(8)
            return a
        else:
            a=(self.Registers[tmp] & (pow(2, 16) - 1))
            return a

    def Save_value_in_reg_X(self, string,val):

        """
                                    This function start some operations on code
                                    save value in register
        """
        tmp = 'e' + string[0] + 'x'
        tmp1=self.Registers[tmp]
        if string[1] == 'l':
            tmp1=tmp1&((pow(2, 24)-1)*pow(2, 8))
            self.Registers.update({tmp:tmp1|val})
        elif string[1] == 'h':
            tmp1 = tmp1 & (((pow(2, 16) - 1) * pow(2, 16))|(pow(2,8)-1))
            self.Registers.update({tmp: tmp1 | (val* pow(2, 8))})
        else:
            tmp1 = tmp1 & ((pow(2, 16) - 1) * pow(2, 16))
            self.Registers.update({tmp: tmp1 | val})

    def Search_lable(self, address):

        """
                                    This function start some operations on code
                                    search for the address in the lables

                                    Return :
                                    False if it not exist
                                    True if it exist
        """
        ret = False
        for i in self.Labels_names:
            if self.Labels_names[i] == address:
                return True
        return ret

    def Jmp_X(self, String):

        """
                                    This function start some operations on code
                                    check flags to jump or not

                                    Return :
                                    False to stay
                                    True to jump
        """
        if String == "jmp":
            return True
        elif (String == "je") or (String == "jz"):
            if self.Flags["zf"] == 1:
                return True
            return False
        elif (String == "jne") or (String == "jnz"):
            if self.Flags["zf"] == 0:
                return True
            return False
        elif (String == "ja") or (String == "jnbe") :
            if self.Flags["zf"] == 0 and self.Flags["cf"] == 0:
                return True
            return False
        elif (String == "jb") or (String == "jnae"):
            if self.Flags["zf"] ==0 and  self.Flags["cf"]==1:
                return True
            return False
        elif (String == "jae") or (String == "jnb") :
            if self.Flags["zf"] == 0 and self.Flags["cf"] == 0:
                return True
            if self.Flags["zf"] == 1 and self.Flags["cf"] == 0:
                return True
            return False
        elif (String == "jbe") or (String == "jna") :
            if self.Flags["zf"] == 0 and self.Flags["cf"] == 1:
                return True
            if self.Flags["zf"] == 1 and self.Flags["cf"] == 0:
                return True
            return False
        elif (String == "jg") or (String == "jnle"):
            if self.Flags["sf"] ==self.Flags["of"]:
                return True
            return False
        elif (String == "jl") or (String == "jnge"):
            if self.Flags["sf"] !=self.Flags["of"]:
                return True
            return False
        elif (String == "jge") or (String == "jnl"):
            if self.Flags["sf"] ==self.Flags["of"]:
                return True
            if self.Flags["zf"]==1:
                return True
            return False
        elif (String == "jle") or (String == "jng"):
            if self.Flags["sf"] !=self.Flags["of"]:
                return True
            if self.Flags["zf"]==1:
                return True
            return False
        elif String == "loop":

            self.Neg_inc_dec('dec', [['ecx']])
            if self.Flags["zf"] == 1:
                return False
            return True
        elif String == "jc":
            if self.Flags["cf"] == 1:
                return True
            return False
        elif String == "jnc":
            if self.Flags["cf"] == 0:
                return True
            return False

    def Check_code_operand(self, Operand):

        """
            This function start some operations on code
            check the Operand state and return it

            Return :
            False if there where syntax error
            List contains 'name ,value ,type'
        """
        reg_16_8 = ["ax", "bx", "cx", "dx","ax", "bx", "cx", "dx","al", "ah", "bl", "bh", "ch", "cl", "dh", "dl"]
        if len(Operand) == 1:
            if Operand[0] in self.Data_variables:
                tmp = self.Data_variables[Operand[0]]
                # name , address , Type
                return ["add", tmp[0], self.Type(tmp[1])]
            elif Operand[0] in self.Registers or Operand[0] in reg_16_8:
                reg_32 = ["eax", "ebx", "ecx", "edx", "ebp", "esp", "esi", "edi"]
                reg_16 = ["ax", "bx", "cx", "dx"]
                tmp = 0
                if Operand[0] in reg_32:
                    tmp = 4
                    # name , value , Type
                    return ["reg", self.Registers[Operand[0]], tmp]
                elif Operand[0] in reg_16:
                    tmp = 2
                    # name , value , Type
                    return ["reg", self.Get_value_from_reg_X(Operand[0]), tmp]
                else:
                    tmp = 1
                    # name , value , Type
                    return ["reg", self.Get_value_from_reg_X(Operand[0]), tmp]
            elif Operand[0] in self.Data_types:
                return ["imm", self.Type(Operand[0]), self.Type(Operand[0])]
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
                        # name,value , Type
                    return ["imm", Operand[0], tmp]
                except Exception:
                    return False
        else:

            name = ""
            type = 0
            if Operand.__len__() > 1:
                if Operand[1] == 'ptr':
                    name = "add"
                    if Operand[0] in self.Data_types:
                        type = self.Type(Operand[0])
                        Operand.append('+')
                    else:
                        return False
                    Operand = Operand[2:]
                    if len(Operand) > 0:
                        if (Operand[0] == 'ptr_X_') or (Operand[0] == 'ptr_'):
                            Operand.append('+')
                            Operand = Operand[1:]
                elif (Operand[0] == 'ptr_X_') or (Operand[0] == 'ptr_'):
                    Operand.append('+')
                    name = "add"
                    type = 0
                    if (Operand[0] == 'ptr_X_'):
                        type=self.Type(self.Data_variables[Operand[1]][1])
                    Operand = Operand[1:]
                else:
                    name = "imm"
            else:
                name = "imm"

            stak = []
            for i in range(0, len(Operand)):
                if (Operand[i] == '+') or (Operand[i] == '-') or (Operand[i] == '*') or (Operand[i] == '/'):
                    if len(stak) > 1:
                        tmp1 = self.Check_code_operand([stak[len(stak) - 1]])
                        tmp2 = self.Check_code_operand([stak[len(stak) - 2]])
                        if (tmp1 is False) or (tmp2 is False):
                            return False
                        tmp1_ = tmp1[1]
                        tmp2_ = tmp2[1]

                        stak = stak[:-1]
                        if Operand[i] == '-':
                            stak[len(stak) - 1] = tmp1_ - tmp2_
                        elif Operand[i] == '+':
                            stak[len(stak) - 1] = tmp1_ + tmp2_
                        elif Operand[i] == '*':
                            stak[len(stak) - 1] = tmp1_ * tmp2_
                        elif Operand[i] == '/':
                            if tmp2_ != 0:
                                stak[len(stak) - 1] = tmp1_ / tmp2_
                            else:
                                return False
                    else:
                        if (Operand[i] == '+') or (Operand[i] == '-'):
                            tmp1 = self.Check_code_operand([stak[len(stak) - 1]])
                            if tmp1 is False:
                                return False
                            tmp1_ = tmp1[1]
                            if Operand[i] == '-':
                                stak[len(stak) - 1] = tmp1_ * -1
                            else:
                                stak[len(stak) - 1] = tmp1_
                        else:
                            return False
                elif (Operand[i] == 'lengthof') or (Operand[i] == 'sizeof') or (Operand[i] == 'type'):
                    if len(stak) > 0:
                        tmp1 = self.Check_code_operand([stak[len(stak) - 1]])
                        if tmp1 is False:
                            return False
                        if (tmp1[0] != "add") and ((Operand[i] == 'lengthof') or (Operand[i] == 'sizeof')):
                            return False
                        elif (tmp1[0] != "add") and (Operand[i] == 'type'):
                            stak[len(stak) - 1] = 0
                        else:

                            tmp1_ = tmp1[2]
                            tmp2_ = self.Data_variables[stak[len(stak) - 1]][2]
                            stak = stak[:-1]
                            if Operand[i] == 'lengthof':
                                stak.append(int(tmp2_ / tmp1_))
                            elif Operand[i] == 'sizeof':
                                stak.append(tmp2_)
                            else:
                                stak.append(tmp1_)
                    else:
                        return False
                elif Operand[i] == 'offset':
                    if len(stak) > 0:
                        tmp1 = self.Check_code_operand([stak[len(stak) - 1]])
                        if not tmp1:
                            return False
                        stak[len(stak) - 1] = tmp1[1]
                    else:
                        return False
                else:
                    stak.append(Operand[i])

            if len(stak) == 0:
                return False
            value = stak[0]
            if name == "imm":
                type_ = self.Check_code_operand([value])
                if not type_:
                    return False
                type = type_[2]

            return [name, value, type]

    def Get_value_from_memory(self, address, type):

        """
            This function start some operations on code
            get value from memory

            Return :
            False by set state to "RTE" if there where memory out of range
            The value
        """


        if (address < len(self.Memory_data_segment)) and (address + type <= len(self.Memory_data_segment)):

            ret = ""
            i = address
            while i < (address + type):
                ret = self.Memory_data_segment[i] + ret
                i += 1
            return int(ret, 16)
        else:
            self.State="RTE"
            return False

    def Save_value_in_memory(self, address, value, type):
        """
            This function start some operations on code
            save value in memory

            Return :
            False by set state to "RTE" if there where memory out of range
            True if is no problem
        """
        if (address <= self.Memory_data_segment.__len__()) and (address + type-1 <= self.Memory_data_segment.__len__()):

            tmp = str(hex(value))[2:]
            if tmp.__len__() > (type * 2):
                return False

            for j in range(0, type):
                if tmp == "":
                    self.Memory_data_segment[address + j] = "00"
                elif tmp.__len__() > 1:
                    self.Memory_data_segment[address + j] = tmp[len(tmp) - 2] + tmp[len(tmp) - 1]
                    tmp = tmp[:-2]
                else:
                    self.Memory_data_segment[address + j] = '0' + tmp[len(tmp) - 1]
                    tmp = tmp[:-1]

            return True
        else:
            self.State = "RTE"
            return False

    def Mov_X(self, String, infix):
        """
                                    This function start some operations on code
                                    make mov movzx movsx instructions

                                    Return :
                                    False if there where syntax error
                                    True if there where no syntax error
        """

        tmp1 = self.Check_code_operand(infix[0])
        tmp2 = self.Check_code_operand(infix[1])
        if tmp1 is False or tmp2 is False:
            return False
        if (tmp1[0] == 'imm') or (tmp1[2] == 0) or ((tmp1[0] == 'imm') and (tmp2[0] == 'imm')):
            if (tmp1[2] == 0) and (tmp2[2] != 0):
                tmp1[2]=tmp2[2]
            else:
                return False

        if String == 'mov':
            if ((tmp1[0] == 'add') and (tmp2[0] == 'add')) or ((tmp1[2] != tmp2[2]) and (tmp2[2] != 0) and (tmp2[0] != 'imm')):
                return False

            b = 0
            if tmp2[0] != 'add':
                b = tmp2[1]
            else:
                b = self.Get_value_from_memory(tmp2[1], tmp1[2])

            if b < 0:
                b = pow(2, (tmp1[2] * 8)) + b
            if b < 0:
                return False

            if tmp1[0] == 'reg':
                if len(infix[0][0])==3:
                    self.Registers[infix[0][0]] = b
                else:
                    self.Save_value_in_reg_X(infix[0][0],b)
            else:
                if not self.Save_value_in_memory(tmp1[1], b, tmp1[2]):
                    return False
        elif String == 'movzx':

            if ((tmp1[0] == 'add') and (tmp2[0] == 'add')) or ((tmp1[2] <= tmp2[2]) and (tmp2[2] != 0) and (tmp2[0] != 'imm'))or ((tmp1[2] <= tmp2[2]) and (tmp2[2] == 0) and (tmp2[0] != 'imm')):
                return False

            b = 0
            if tmp2[0] != 'add':
                b = tmp2[1]
            else:
                b = self.Get_value_from_memory(tmp2[1], tmp2[2])

            if b < 0:
                b = pow(2, (tmp1[2] * 8)) + b
            if b < 0:
                return False

            if tmp1[0] == 'reg':
                if len(infix[0][0])==3:
                    self.Registers[infix[0][0]] = b
                else:
                    self.Save_value_in_reg_X(infix[0][0],b)
            else:
                if not self.Save_value_in_memory(tmp1[1], b, tmp1[2]):
                    return False
        elif String == 'movsx':
            if ((tmp1[0] == 'add') and (tmp2[0] == 'add')) or ((tmp1[2] <= tmp2[2]) and (tmp2[2] != 0) and (tmp2[0] != 'imm'))or ((tmp1[2] <= tmp2[2]) and (tmp2[2] == 0) and (tmp2[0] != 'imm')):
                return False
            b = 0
            if tmp2[0] != 'add':
                b = tmp2[1]
            else:
                b = self.Get_value_from_memory(tmp2[1], tmp2[2])

            if b < 0:
                b = pow(2, (tmp1[2] * 8)) + b
            if b < 0:
                return False

            if not (b & pow(2, (tmp2[2] * 8) - 1)):
                if tmp1[0] == 'reg':
                    if len(infix[0][0]) == 3:
                        self.Registers[infix[0][0]] = b
                    else:
                        self.Save_value_in_reg_X(infix[0][0], b)
                else:
                    if not self.Save_value_in_memory(tmp1[1], b, tmp1[2]):
                        return False
            else:
                v = (pow(2, ((tmp1[2] - tmp2[2]) * 8)) - 1) * pow(2, (tmp2[2] * 8))
                b = v | b
                if tmp1[0] == 'reg':
                    if len(infix[0][0]) == 3:
                        self.Registers[infix[0][0]] = b
                    else:
                        self.Save_value_in_reg_X(infix[0][0], b)
                else:
                    if not self.Save_value_in_memory(tmp1[1], b, tmp1[2]):
                        return False

        return True

    def Add_sub(self, String, infix):

        """
                                    This function start some operations on code
                                    make add sub acd sbb instructions

                                    Return :
                                    False if there where syntax error
                                    True if there where no syntax error
        """
        tmp1 = self.Check_code_operand(infix[0])
        tmp2 = self.Check_code_operand(infix[1])
        if (tmp1 is False) or (tmp2 is False):
            return False
        if (tmp1[0] == 'imm') or (tmp1[2] == 0) or ((tmp1[0] == 'imm') and (tmp2[0] == 'imm')):
            if (tmp1[2] == 0) and (tmp2[2] != 0):
                tmp1[2]=tmp2[2]
            else:
                return False
        if ((tmp1[0] == 'add') and (tmp2[0] == 'add')) or ((tmp1[2] != tmp2[2]) and (tmp2[2] != 0) and (tmp2[0] != 'imm')):
            return False

        if String == 'add':

            a = 0
            if (tmp1[0] != 'add'):
                a = tmp1[1]
            else:
                a = self.Get_value_from_memory(tmp1[1], tmp1[2])
            b = 0
            if (tmp2[0] != 'add'):
                b = tmp2[1]
            else:
                b = self.Get_value_from_memory(tmp2[1], tmp1[2])

            if b < 0:
                b = pow(2, (tmp1[2] * 8)) + b
            if b < 0:
                return False

            v = bool((a & (pow(2, 4) - 1)) + (b & (pow(2, 4) - 1)))
            if v:
                self.Flags["ac"] = 1
            else:
                self.Flags["ac"] = 0

            v = bool((a & (pow(2, (tmp1[2] * 8) - 2) - 1)) + (b & (pow(2, (tmp1[2] * 8) - 2) - 1)))

            a = a + b

            if a >= pow(2, tmp1[2] * 8):
                a = a & (pow(2, tmp1[2] * 8) - 1)
                self.Flags["cf"] = 1
                if v:
                    self.Flags["of"] = 0
                else:
                    self.Flags["of"] = 1
            else:
                self.Flags["cf"] = 0
                if v:
                    self.Flags["of"] = 1
                else:
                    self.Flags["of"] = 0

            if bool(a & pow(2, (tmp1[2] * 8) - 1)):
                self.Flags["sf"] = 1
            else:
                self.Flags["sf"] = 0

            v = a
            one = 0
            for i in range(0, 8):
                if bool(v & 1):
                    one += 1
                v = v.__rshift__(1)
            if bool(one & 1):
                self.Flags["pf"] = 0
            else:
                self.Flags["pf"] = 1

            if a == 0:
                self.Flags["zf"] = 1
            else:
                self.Flags["zf"] = 0

            if tmp1[0] == 'reg':
                if len(infix[0][0])==3:
                    self.Registers[infix[0][0]] = a
                else:
                    self.Save_value_in_reg_X(infix[0][0],a)
            else:
                if not self.Save_value_in_memory(tmp1[1], a, tmp1[2]):
                    return False
        elif String == 'acd':

            a = 0
            if (tmp1[0] != 'add'):
                a = tmp1[1]
            else:
                a = self.Get_value_from_memory(tmp1[1], tmp1[2])
            b = 0
            if (tmp2[0] != 'add'):
                b = tmp2[1]
            else:
                b = self.Get_value_from_memory(tmp2[1], tmp1[2])

            if b < 0:
                b = pow(2, (tmp1[2] * 8)) + b
            if b < 0:
                return False

            v = bool((a & (pow(2, 4) - 1)) + (b & (pow(2, 4) - 1)) + self.Flags["cf"])
            if v:
                self.Flags["ac"] = 1
            else:
                self.Flags["ac"] = 0

            v = bool((a & (pow(2, (tmp1[2] * 8) - 2) - 1)) + (b & (pow(2, (tmp1[2] * 8) - 2) - 1)) + self.Flags["cf"])

            a = a + b + self.Flags["cf"]

            if a >= pow(2, tmp1[2] * 8):
                a = a & (pow(2, tmp1[2] * 8) - 1)
                self.Flags["cf"] = 1
                if v:
                    self.Flags["of"] = 0
                else:
                    self.Flags["of"] = 1
            else:
                self.Flags["cf"] = 0
                if v:
                    self.Flags["of"] = 1
                else:
                    self.Flags["of"] = 0

            if bool(a & pow(2, (tmp1[2] * 8) - 1)):
                self.Flags["sf"] = 1
            else:
                self.Flags["sf"] = 0

            v = a
            one = 0
            for i in range(0, 8):
                if bool(v & 1):
                    one += 1
                v = v.__rshift__(1)
            if bool(one & 1):
                self.Flags["pf"] = 0
            else:
                self.Flags["pf"] = 1

            if a == 0:
                self.Flags["zf"] = 1
            else:
                self.Flags["zf"] = 0

            if tmp1[0] == 'reg':
                if len(infix[0][0])==3:
                    self.Registers[infix[0][0]] = a
                else:
                    self.Save_value_in_reg_X(infix[0][0],a)
            else:
                if not self.Save_value_in_memory(tmp1[1], a, tmp1[2]):
                    return False
        elif String == 'sub':
            a = 0
            if (tmp1[0] != 'add'):
                a = tmp1[1]
            else:
                a = self.Get_value_from_memory(tmp1[1], tmp1[2])
            b = 0
            if (tmp2[0] != 'add'):
                b = tmp2[1]
            else:
                b = self.Get_value_from_memory(tmp2[1], tmp1[2])

            if b < 0:
                b = pow(2, (tmp1[2] * 8)) + b
            if b < 0:
                return False

            b = pow(2, (tmp1[2] * 8)) - b

            v = (bool(((a & (pow(2, 4) - 1)) + (b & (pow(2, 4) - 1)))&pow(2,4)))
            if v:
                self.Flags["ac"] = 0
            else:
                self.Flags["ac"] = 1

            v = not bool(((a & (pow(2, (tmp1[2] * 8) - 1) - 1)) + (b & (pow(2, (tmp1[2] * 8) - 1) - 1)))&pow(2, (tmp1[2] * 8) - 1))

            a = a + b

            if a >= pow(2, tmp1[2] * 8):
                a = a & (pow(2, tmp1[2] * 8) - 1)
                self.Flags["cf"] = 0
                if v:
                    self.Flags["of"] = 1
                else:
                    self.Flags["of"] = 0
            else:
                self.Flags["cf"] = 1
                if v:
                    self.Flags["of"] = 0
                else:
                    self.Flags["of"] = 1

            if bool(a & pow(2, (tmp1[2] * 8) - 1)):
                self.Flags["sf"] = 1
            else:
                self.Flags["sf"] = 0

            v = a
            one = 0
            for i in range(0, 8):
                if bool(v & 1):
                    one += 1
                v = v.__rshift__(1)
            if bool(one & 1):
                self.Flags["pf"] = 0
            else:
                self.Flags["pf"] = 1

            if a == 0:
                self.Flags["zf"] = 1
            else:
                self.Flags["zf"] = 0

            if tmp1[0] == 'reg':
                if len(infix[0][0])==3:
                    self.Registers[infix[0][0]] = a
                else:
                    self.Save_value_in_reg_X(infix[0][0],a)
            else:
                if not self.Save_value_in_memory(tmp1[1], a, tmp1[2]):
                    return False
        elif String == 'sbb':
            a = 0
            if (tmp1[0] != 'add'):
                a = tmp1[1]
            else:
                a = self.Get_value_from_memory(tmp1[1], tmp1[2])
            b = 0
            if (tmp2[0] != 'add'):
                b = tmp2[1]
            else:
                b = self.Get_value_from_memory(tmp2[1], tmp1[2])

            if b < 0:
                b = pow(2, (tmp1[2] * 8)) + b
            if b < 0:
                return False

            b = pow(2, (tmp1[2] * 8)) - b

            v =  bool(((a & (pow(2, 4) - 1)) + (b & (pow(2, 4) - 1)) + self.Flags["cf"])&pow(2,4))
            if v:
                self.Flags["ac"] = 0
            else:
                self.Flags["ac"] = 1

            v =not  bool(((a & (pow(2, (tmp1[2] * 8) - 1) - 1)) + (b & (pow(2, (tmp1[2] * 8) - 1) - 1)) + self.Flags["cf"])&pow(2, (tmp1[2] * 8) - 1))

            a = a + b + self.Flags["cf"]

            if a >= pow(2, tmp1[2] * 8):
                a = a & (pow(2, tmp1[2] * 8) - 1)
                self.Flags["cf"] = 0
                if v:
                    self.Flags["of"] = 1
                else:
                    self.Flags["of"] = 0
            else:
                self.Flags["cf"] = 1
                if v:
                    self.Flags["of"] = 0
                else:
                    self.Flags["of"] = 1

            if bool(a & pow(2, (tmp1[2] * 8) - 1)):
                self.Flags["sf"] = 1
            else:
                self.Flags["sf"] = 0

            v = a
            one = 0
            for i in range(0, 8):
                if bool(v & 1):
                    one += 1
                v = v.__rshift__(1)
            if bool(one & 1):
                self.Flags["pf"] = 0
            else:
                self.Flags["pf"] = 1

            if a == 0:
                self.Flags["zf"] = 1
            else:
                self.Flags["zf"] = 0

            if tmp1[0] == 'reg':
                if len(infix[0][0])==3:
                    self.Registers[infix[0][0]] = a
                else:
                    self.Save_value_in_reg_X(infix[0][0],a)
            else:
                if not self.Save_value_in_memory(tmp1[1], a, tmp1[2]):
                    return False
        return True

    def Cmp(self, String, infix):

        """
                                    This function start some operations on code
                                    make cmp instructions

                                    Return :
                                    False if there where syntax error
                                    True if there where no syntax error
        """

        tmp1 = self.Check_code_operand(infix[0])
        tmp2 = self.Check_code_operand(infix[1])
        if (tmp1 == False) or (tmp2 == False):
            return False
        if (tmp1[0] == 'imm') or (tmp1[2] == 0) or ((tmp1[0] == 'imm') and (tmp2[0] == 'imm')):
            if (tmp1[2] == 0) and (tmp2[2] != 0):
                tmp1[2]=tmp2[2]
            else:
                return False
        if ((tmp1[0] == 'add') and (tmp2[0] == 'add')) or (
                (tmp1[2] != tmp2[2]) and (tmp2[2] != 0) and (tmp2[0] != 'imm')):
            return False
        a = 0
        if (tmp1[0] != 'add'):
            a = tmp1[1]
        else:
            a = self.Get_value_from_memory(tmp1[1], tmp1[2])
        b = 0
        if (tmp2[0] != 'add'):
            b = tmp2[1]
        else:
            b = self.Get_value_from_memory(tmp2[1], tmp1[2])

        if b < 0:
            b = pow(2, (tmp1[2] * 8)) + b
        if b < 0:
            return False

        if b!=0 :
            b = pow(2, (tmp1[2] * 8)) - b

        v = (bool(((a & (pow(2, 4) - 1)) + (b & (pow(2, 4) - 1))) & pow(2, 4)))

        if v:
            self.Flags["ac"] = 0
        else:
            self.Flags["ac"] = 1

        v = not bool(
            ((a & (pow(2, (tmp1[2] * 8) - 1) - 1)) + (b & (pow(2, (tmp1[2] * 8) - 1) - 1))) & pow(2, (tmp1[2] * 8) - 1))

        a = a + b
        if a >= pow(2, tmp1[2] * 8):
            a = a & (pow(2, tmp1[2] * 8) - 1)
            self.Flags["cf"] = 0
            if v:
                self.Flags["of"] = 1
            else:
                self.Flags["of"] = 0
        else:
            self.Flags["cf"] = 1
            if v:
                self.Flags["of"] = 0
            else:
                self.Flags["of"] = 1

        if bool(a & pow(2, (tmp1[2] * 8) - 1)):
            self.Flags["sf"] = 1
        else:
            self.Flags["sf"] = 0

        v = a
        one = 0
        for i in range(0, 8):
            if bool(v & 1):
                one += 1
            v = v.__rshift__(1)
        if bool(one & 1):
            self.Flags["pf"] = 0
        else:
            self.Flags["pf"] = 1

        if a == 0:
            self.Flags["zf"] = 1
        else:
            self.Flags["zf"] = 0

        return True

    def Xchg(self, String, infix):

        """
                                    This function start some operations on code
                                    make xchg instructions

                                    Return :
                                    False if there where syntax error
                                    True if there where no syntax error
        """

        tmp1 = self.Check_code_operand(infix[0])
        tmp2 = self.Check_code_operand(infix[1])
        if (tmp1 == False) or (tmp2 == False):
            return False
        if (tmp1[0] == 'imm') or (tmp1[2] == 0) or ((tmp1[0] == 'imm') and (tmp2[0] == 'imm')):
            if (tmp1[2]==0)and(tmp2[2]!=0)and (tmp2[0] != 'imm'):
                tmp1[2]=tmp2[2]
            else:
                return False
        if ((tmp1[0] == 'add') and (tmp2[0] == 'add')) or ((tmp1[0] == 'imm') and (tmp2[0] == 'imm')) or ((tmp1[2] != tmp2[2]) and (tmp2[2] != 0)):
            return False

        a = 0
        if (tmp1[0] != 'add'):
            a = tmp1[1]
        else:
            a = self.Get_value_from_memory(tmp1[1], tmp1[2])
        b = 0
        if (tmp2[0] != 'add'):
            b = tmp2[1]
        else:
            b = self.Get_value_from_memory(tmp2[1], tmp1[2])

        if tmp1[0] == 'reg':
            if len(infix[0][0]) == 3:
                self.Registers[infix[0][0]] = b
            else:
                self.Save_value_in_reg_X(infix[0][0], b)
        else:
            if not self.Save_value_in_memory(tmp1[1], b, tmp1[2]):
                return False

        if tmp2[0] == 'reg':
            if len(infix[1][0]) == 3:
                self.Registers[infix[1][0]] = a
            else:
                self.Save_value_in_reg_X(infix[1][0], a)
        else:
            if not self.Save_value_in_memory(tmp2[1], a, tmp1[2]):
                return False
        return True

    def Shift(self, String, infix):

        """
                                    This function start some operations on code
                                    make shift instructions

                                    Return :
                                    False if there where syntax error
                                    True if there where no syntax error
        """

        tmp1 = self.Check_code_operand(infix[0])
        tmp2 = self.Check_code_operand(infix[1])
        if (tmp1 is False) or (tmp2 is False):
            return False
        if ((tmp1[0] == 'reg') or  ((tmp1[0] == 'add') and (tmp1[2] != 0))) and (((tmp2[0] == 'imm' and tmp2[2] == 1)) or ((tmp2[0] == 'reg') and (infix[1][0] == 'cl'))):
            if (String == 'shl') or (String == 'sal'):
                a = 0
                if tmp1[0] != 'add':
                    a = tmp1[1]
                else:
                    a = self.Get_value_from_memory(tmp1[1], tmp1[2])

                b = tmp2[1]


                if b < 0:
                    b = pow(2, (tmp1[2] * 8)) + b
                if b < 0:
                    return False

                for i in range(0, b):
                    a = a * 2
                    if a >= pow(2, tmp1[2] * 8):
                        a = a & (pow(2, tmp1[2] * 8) - 1)
                        self.Flags["cf"] = 1
                    else:
                        self.Flags["cf"] = 0

                if bool(a & pow(2, (tmp1[2] * 8) - 1)):
                    self.Flags["sf"] = 1
                else:
                    self.Flags["sf"] = 0

                v = a
                one = 0
                for i in range(0, 8):
                    if bool(v & 1):
                        one += 1
                    v = v.__rshift__(1)
                if bool(one & 1):
                    self.Flags["pf"] = 0
                else:
                    self.Flags["pf"] = 1

                if a == 0:
                    self.Flags["zf"] = 1
                else:
                    self.Flags["zf"] = 0

                if tmp1[0] == 'reg':
                    if len(infix[0][0]) == 3:
                        self.Registers[infix[0][0]] = a
                    else:
                        self.Save_value_in_reg_X(infix[0][0], a)
                else:
                    if not self.Save_value_in_memory(tmp1[1], a, tmp1[2]):
                        return False
            elif String == 'shr':
                a = 0
                if tmp1[0] != 'add':
                    a = tmp1[1]
                else:
                    a = self.Get_value_from_memory(tmp1[1], tmp1[2])

                b = tmp2[1]

                if b < 0:
                    b = pow(2, (tmp1[2] * 8)) + b
                if b < 0:
                    return False

                for i in range(0, b):
                    if bool(a & 1):
                        self.Flags["cf"] = 1
                    else:
                        self.Flags["cf"] = 0
                    a = int(a / 2)

                if bool(a & pow(2, (tmp1[2] * 8) - 1)):
                    self.Flags["sf"] = 1
                else:
                    self.Flags["sf"] = 0

                v = a
                one = 0
                for i in range(0, 8):
                    if bool(v & 1):
                        one += 1
                    v = v.__rshift__(1)
                if bool(one & 1):
                    self.Flags["pf"] = 0
                else:
                    self.Flags["pf"] = 1

                if a == 0:
                    self.Flags["zf"] = 1
                else:
                    self.Flags["zf"] = 0

                if tmp1[0] == 'reg':
                    if len(infix[0][0]) == 3:
                        self.Registers[infix[0][0]] = a
                    else:
                        self.Save_value_in_reg_X(infix[0][0], a)
                else:
                    if not self.Save_value_in_memory(tmp1[1], a, tmp1[2]):
                        return False
            elif String == 'sar':
                a = 0
                if tmp1[0] != 'add':
                    a = tmp1[1]
                else:
                    a = self.Get_value_from_memory(tmp1[1], tmp1[2])
                b = tmp2[1]

                if b < 0:
                    b = pow(2, (tmp1[2] * 8)) + b
                if b < 0:
                    return False

                if bool(a & pow(2, (tmp1[2] * 8) - 1)):
                    self.Flags["sf"] = 1
                else:
                    self.Flags["sf"] = 0

                for i in range(0, b):
                    if bool(a & 1):
                        self.Flags["cf"] = 1
                    else:
                        self.Flags["cf"] = 0
                    a = int(a / 2)
                    if self.Flags["sf"] == 1:
                        a = a | pow(2, (tmp1[2] * 8) - 1)

                if bool(a & pow(2, (tmp1[2] * 8) - 1)):
                    self.Flags["sf"] = 1
                else:
                    self.Flags["sf"] = 0

                v = a
                one = 0
                for i in range(0, 8):
                    if bool(v & 1):
                        one += 1
                    v = v.__rshift__(1)
                if bool(one & 1):
                    self.Flags["pf"] = 0
                else:
                    self.Flags["pf"] = 1

                if a == 0:
                    self.Flags["zf"] = 1
                else:
                    self.Flags["zf"] = 0

                if tmp1[0] == 'reg':
                    if len(infix[0][0]) == 3:
                        self.Registers[infix[0][0]] = a
                    else:
                        self.Save_value_in_reg_X(infix[0][0], a)
                else:
                    if not self.Save_value_in_memory(tmp1[1], a, tmp1[2]):
                        return False
            elif String == 'rol':
                a = 0
                if tmp1[0] != 'add':
                    a = tmp1[1]
                else:
                    a = self.Get_value_from_memory(tmp1[1], tmp1[2])
                b = tmp2[1]

                if b < 0:
                    b = pow(2, (tmp1[2] * 8)) + b
                if b < 0:
                    return False

                for i in range(0, b):
                    a = a * 2

                    if a >= pow(2, tmp1[2] * 8):
                        a = a & (pow(2, tmp1[2] * 8) - 1)
                        self.Flags["cf"] = 1
                        a = a | 1
                    else:
                        self.Flags["cf"] = 0

                if bool(a & pow(2, (tmp1[2] * 8) - 1)):
                    self.Flags["sf"] = 1
                else:
                    self.Flags["sf"] = 0

                v = a
                one = 0
                for i in range(0, 8):
                    if bool(v & 1):
                        one += 1
                    v = v.__rshift__(1)
                if bool(one & 1):
                    self.Flags["pf"] = 0
                else:
                    self.Flags["pf"] = 1

                if a == 0:
                    self.Flags["zf"] = 1
                else:
                    self.Flags["zf"] = 0

                if tmp1[0] == 'reg':
                    if len(infix[0][0]) == 3:
                        self.Registers[infix[0][0]] = a
                    else:
                        self.Save_value_in_reg_X(infix[0][0], a)
                else:
                    if not self.Save_value_in_memory(tmp1[1], a, tmp1[2]):
                        return False
            elif String == 'ror':
                a = 0
                if tmp1[0] != 'add':
                    a = tmp1[1]
                else:
                    a = self.Get_value_from_memory(tmp1[1], tmp1[2])

                b = tmp2[1]

                if b < 0:
                    b = pow(2, (tmp1[2] * 8)) + b
                if b < 0:
                    return False

                for i in range(0, b):
                    if bool(a & 1):
                        self.Flags["cf"] = 1
                    else:
                        self.Flags["cf"] = 0
                    a = int(a / 2)
                    if self.Flags["cf"] == 1:
                        a = a | pow(2, (tmp1[2] * 8) - 1)

                if bool(a & pow(2, (tmp1[2] * 8) - 1)):
                    self.Flags["sf"] = 1
                else:
                    self.Flags["sf"] = 0

                v = a
                one = 0
                for i in range(0, 8):
                    if bool(v & 1):
                        one += 1
                    v = v.__rshift__(1)
                if bool(one & 1):
                    self.Flags["pf"] = 0
                else:
                    self.Flags["pf"] = 1

                if a == 0:
                    self.Flags["zf"] = 1
                else:
                    self.Flags["zf"] = 0

                if tmp1[0] == 'reg':
                    if len(infix[0][0]) == 3:
                        self.Registers[infix[0][0]] = a
                    else:
                        self.Save_value_in_reg_X(infix[0][0], a)
                else:
                    if not self.Save_value_in_memory(tmp1[1], a, tmp1[2]):
                        return False
            elif String == 'rcl':
                a = 0
                if tmp1[0] != 'add':
                    a = tmp1[1]
                else:
                    a = self.Get_value_from_memory(tmp1[1], tmp1[2])
                b = tmp2[1]


                if b < 0:
                    b = pow(2, (tmp1[2] * 8)) + b
                if b < 0:
                    return False

                for i in range(0, b):
                    a = a * 2

                    if a >= pow(2, tmp1[2] * 8):
                        a = a & (pow(2, tmp1[2] * 8) - 1)
                        if self.Flags["cf"] == 1:
                            a = a | 1
                        self.Flags["cf"] = 1

                    else:
                        if self.Flags["cf"] == 1:
                            a = a | 1
                        self.Flags["cf"] = 0

                if bool(a & pow(2, (tmp1[2] * 8) - 1)):
                    self.Flags["sf"] = 1
                else:
                    self.Flags["sf"] = 0

                v = a
                one = 0
                for i in range(0, 8):
                    if bool(v & 1):
                        one += 1
                    v = v.__rshift__(1)
                if bool(one & 1):
                    self.Flags["pf"] = 0
                else:
                    self.Flags["pf"] = 1

                if a == 0:
                    self.Flags["zf"] = 1
                else:
                    self.Flags["zf"] = 0

                if tmp1[0] == 'reg':
                    if len(infix[0][0]) == 3:
                        self.Registers[infix[0][0]] = a
                    else:
                        self.Save_value_in_reg_X(infix[0][0], a)
                else:
                    if not self.Save_value_in_memory(tmp1[1], a, tmp1[2]):
                        return False
            elif String == 'rcr':
                a = 0
                if tmp1[0] != 'add':
                    a = tmp1[1]
                else:
                    a = self.Get_value_from_memory(tmp1[1], tmp1[2])
                b = tmp2[1]

                if b < 0:
                    b = pow(2, (tmp1[2] * 8)) + b
                if b < 0:
                    return False

                for i in range(0, b):
                    f = self.Flags["cf"]
                    if bool(a & 1):
                        self.Flags["cf"] = 1
                    else:
                        self.Flags["cf"] = 0
                    a = int(a / 2)
                    if f == 1:
                        a = a | pow(2, (tmp1[2] * 8) - 1)

                if bool(a & pow(2, (tmp1[2] * 8) - 1)):
                    self.Flags["sf"] = 1
                else:
                    self.Flags["sf"] = 0

                v = a
                one = 0
                for i in range(0, 8):
                    if bool(v & 1):
                        one += 1
                    v = v.__rshift__(1)
                if bool(one & 1):
                    self.Flags["pf"] = 0
                else:
                    self.Flags["pf"] = 1

                if a == 0:
                    self.Flags["zf"] = 1
                else:
                    self.Flags["zf"] = 0

                if tmp1[0] == 'reg':
                    if len(infix[0][0]) == 3:
                        self.Registers[infix[0][0]] = a
                    else:
                        self.Save_value_in_reg_X(infix[0][0], a)
                else:
                    if not self.Save_value_in_memory(tmp1[1], a, tmp1[2]):
                        return False
        else:
            return False

        return True

    def Neg_inc_dec(self, String, infix):

        """
                                    This function start some operations on code
                                    make neg inc dec instructions

                                    Return :
                                    False if there where syntax error
                                    True if there where no syntax error
        """

        tmp1 = self.Check_code_operand(infix[0])
        if not tmp1:
            return False
        if (tmp1[0] == 'imm') or (tmp1[2] == 0):
            return False

        if String == 'inc':

            a = 0
            if tmp1[0] != 'add':
                a = tmp1[1]
            else:
                a = self.Get_value_from_memory(tmp1[1], tmp1[2])

            a = a + 1
            if a >= pow(2, tmp1[2] * 8):
                a = a & (pow(2, tmp1[2] * 8) - 1)

            if bool(a & pow(2, (tmp1[2] * 8) - 1)):
                self.Flags["sf"] = 1
            else:
                self.Flags["sf"] = 0

            v = a
            one = 0
            for i in range(0, 8):
                if bool(v & 1):
                    one += 1
                v = v.__rshift__(1)
            if bool(one & 1):
                self.Flags["pf"] = 0
            else:
                self.Flags["pf"] = 1

            if a == 0:
                self.Flags["zf"] = 1
            else:
                self.Flags["zf"] = 0

            if tmp1[0] == 'reg':
                if len(infix[0][0]) == 3:
                    self.Registers[infix[0][0]] = a
                else:
                    self.Save_value_in_reg_X(infix[0][0], a)
            else:
                if not self.Save_value_in_memory(tmp1[1], a, tmp1[2]):
                    return False
        elif String == 'neg':

            a = 0
            if tmp1[0] != 'add':
                a = tmp1[1]
            else:
                a = self.Get_value_from_memory(tmp1[1], tmp1[2])

            a = pow(2, (tmp1[2] * 8)) + a

            if a >= pow(2, tmp1[2] * 8):
                a = a & (pow(2, tmp1[2] * 8) - 1)
                self.Flags["of"] = 1
            else:
                self.Flags["of"] = 0

            self.Flags["cf"] = 1

            if bool(a & pow(2, (tmp1[2] * 8) - 1)):
                self.Flags["sf"] = 1
            else:
                self.Flags["sf"] = 0

            v = a
            one = 0
            for i in range(0, 8):
                if bool(v & 1):
                    one += 1
                v = v.__rshift__(1)
            if bool(one & 1):
                self.Flags["pf"] = 0
            else:
                self.Flags["pf"] = 1

            if a == 0:
                self.Flags["zf"] = 1
            else:
                self.Flags["zf"] = 0

            if tmp1[0] == 'reg':
                if len(infix[0][0]) == 3:
                    self.Registers[infix[0][0]] = a
                else:
                    self.Save_value_in_reg_X(infix[0][0], a)
            else:
                if not self.Save_value_in_memory(tmp1[1], a, tmp1[2]):
                    return False
        elif String == 'dec':
            a = 0
            if tmp1[0] != 'add':
                a = tmp1[1]
            else:
                a = self.Get_value_from_memory(tmp1[1], tmp1[2])

            b = pow(2, (tmp1[2] * 8)) - 1

            a = a + b

            if a >= pow(2, tmp1[2] * 8):
                a = a & (pow(2, tmp1[2] * 8) - 1)

            if bool(a & pow(2, (tmp1[2] * 8) - 1)):
                self.Flags["sf"] = 1
            else:
                self.Flags["sf"] = 0

            v = a
            one = 0
            for i in range(0, 8):
                if bool(v & 1):
                    one += 1
                v = v.__rshift__(1)
            if bool(one & 1):
                self.Flags["pf"] = 0
            else:
                self.Flags["pf"] = 1

            if a == 0:
                self.Flags["zf"] = 1
            else:
                self.Flags["zf"] = 0

            if tmp1[0] == 'reg':
                if len(infix[0][0]) == 3:
                    self.Registers[infix[0][0]] = a
                else:
                    self.Save_value_in_reg_X(infix[0][0], a)
            else:
                if not self.Save_value_in_memory(tmp1[1], a, tmp1[2]):
                    return False
        return True

    def Irvine32(self, String):

        """
                                    This function contains some Irvine32 functions

                                    Return :
                                    False if there where syntax error
                                    True if there where no syntax error
        """

        if String == "crlf":
            self.Output_File += "\n"
        elif String == "dumpregs":
             self.Output_File += str(self.Registers) + "\n" + str(self.Flags)+"\n"
        elif String == "writeint" :
            if bool(self.Registers["eax"] & pow(2, (4 * 8) - 1)) is True:
                a = self.Registers["eax"]
                a = pow(2, (4 * 8)) - a
                self.Output_File += '-' + str(a)
            else:
                self.Output_File += '+' + str(self.Registers["eax"])
        elif String == "writedec":
            self.Output_File += str(self.Registers["eax"])
        elif String == "writechar":
            self.Output_File += chr(self.Get_value_from_reg_X("al"))
        elif String == "writestring":
            c = self.Get_value_from_memory(self.Registers["edx"], 1)
            s = ""
            i = 0
            while c != 0:
                s += chr(c)
                i += 1
                c = self.Get_value_from_memory(self.Registers["edx"] + i, 1)

            self.Output_File += s
        elif String == "readdec":
            num = ""
            while (self.Input_File_index < len(self.Input_File)):
                if self.Input_File[self.Input_File_index] == "\n":
                    self.Input_File_index += 1
                    break
                num += self.Input_File[self.Input_File_index]
                self.Input_File_index += 1
            if num.isdecimal() == True:
                self.Registers["eax"] = int(num)
            else:
                return False
        elif String == "readint":

            num = ""

            while (self.Input_File_index < len(self.Input_File)):
                if self.Input_File[self.Input_File_index] == "\n":
                    self.Input_File_index += 1
                    break
                num += self.Input_File[self.Input_File_index]
                self.Input_File_index += 1

            a = num[1:]
            if ((num.isdecimal() == True) or ((a.isdecimal() == True) and ((num[0] == '-') or num[0] == '+'))):
                self.Registers["eax"] = int(num)
            else:

                return False


        elif String == "readchar":
            if (self.Input_File_index < len(self.Input_File)):
                self.Save_value_in_reg_X("al", ord(self.Input_File[self.Input_File_index]))
                self.Input_File_index += 1
            else:
                return False
        elif String == "readstring":
            edx = self.Registers["edx"]
            ecx = self.Registers["ecx"]
            while (self.Input_File_index < len(self.Input_File)) & (self.Registers["ecx"] >= 0):

                if not self.Save_value_in_memory(edx, ord(self.Input_File[self.Input_File_index]), 1):
                    return False
                self.Input_File_index += 1
                if self.Input_File[self.Input_File_index] == "\n":
                    self.Input_File_index += 1
                    break
                edx += 1
                ecx -= 1
        return True

    def Mul_X(self, String, infix):
        """
                                     This function start some operations on code
                                     make mul imul instructions

                                     Return :
                                     False if there where syntax error
                                     True if there where no syntax error
         """
        tmp1 = self.Check_code_operand(infix[0])
        if (tmp1 == False):
            return False
        if (tmp1[0] == 'imm') | (tmp1[2] == 0):
            return False

        if String == 'mul':
            a = 0
            if (tmp1[0] != 'add'):
                a = tmp1[1]
            else:
                a = self.Get_value_from_memory(tmp1[1], tmp1[2])

            if tmp1[2] == 1:
                a = a * self.Get_value_from_reg_X("al")

                if a >= pow(2, 2 * 8):
                    a = a & (pow(2, 2 * 8) - 1)
                self.Save_value_in_reg_X("ax",a)

                a = a & (pow(2, 8) - 1)
                if bool(self.Get_value_from_reg_X("ah")):
                    self.Flags["cf"] = 1
                    self.Flags["of"] = 1
                else:
                    self.Flags["cf"] = 0
                    self.Flags["of"] = 0

                if bool(a & pow(2, ( 8) - 1)):
                    self.Flags["sf"] = 1
                else:
                    self.Flags["sf"] = 0

                v = a
                one = 0
                for i in range(0, 8):
                    if bool(v & 1):
                        one += 1
                    v = v.__rshift__(1)
                if bool(one & 1):
                    self.Flags["pf"] = 0
                else:
                    self.Flags["pf"] = 1

                self.Flags["zf"] = 0
            elif tmp1[2] == 2:
                a = a * self.Get_value_from_reg_X("ax")
                b=a
                if a >= pow(2, 2 * 8):
                    a = a & (pow(2, 2 * 8) - 1)
                self.Save_value_in_reg_X("ax", a)

                b = b.__rshift__(16)
                if b >= pow(2, 2 * 8):
                    b = b & (pow(2, 2 * 8) - 1)
                self.Save_value_in_reg_X("dx", b)

                if bool(self.Get_value_from_reg_X("dx")):
                    self.Flags["cf"] = 1
                    self.Flags["of"] = 1
                else:
                    self.Flags["cf"] = 0
                    self.Flags["of"] = 0

                if bool(a & pow(2, (2*8) - 1)):
                    self.Flags["sf"] = 1
                else:
                    self.Flags["sf"] = 0

                v = a
                one = 0
                for i in range(0, 8):
                    if bool(v & 1):
                        one += 1
                    v = v.__rshift__(1)
                if bool(one & 1):
                    self.Flags["pf"] = 0
                else:
                    self.Flags["pf"] = 1


                self.Flags["zf"] = 0
            elif tmp1[2] == 4:
                a = a * self.Registers["eax"]
                b = a
                if a >= pow(2, 4 * 8):
                    a = a & (pow(2, 4 * 8) - 1)
                self.Registers["eax"] = a

                b = b.__rshift__(32)
                if b >= pow(2, 4 * 8):
                    b = b & (pow(2, 4 * 8) - 1)
                self.Registers["edx"] = b
                if b != 0:
                    self.Flags["cf"] = 1
                    self.Flags["of"] = 1
                else:
                    self.Flags["cf"] = 0
                    self.Flags["of"] = 0

                if bool(a & pow(2, (4*8) - 1)):
                    self.Flags["sf"] = 1
                else:
                    self.Flags["sf"] = 0

                v = a
                one = 0
                for i in range(0, 8):
                    if bool(v & 1):
                        one += 1
                    v = v.__rshift__(1)
                if bool(one & 1):
                    self.Flags["pf"] = 0
                else:
                    self.Flags["pf"] = 1

                self.Flags["zf"] = 0
        elif String == 'imul':
            a = 0
            if (tmp1[0] != 'add'):
                a = tmp1[1]
            else:
                a = self.Get_value_from_memory(tmp1[1], tmp1[2])

            if tmp1[2] == 1:
                a = a * self.Get_value_from_reg_X("al")

                if a >= pow(2, 2 * 8):
                    a = a & (pow(2, 2 * 8) - 1)
                self.Save_value_in_reg_X("ax", a)

                a=a&(pow(2,  8)-1)
                if bool(a & pow(2, (8) - 1)):
                    self.Flags["sf"] = 1
                else:
                    self.Flags["sf"] = 0


                if (bool(self.Get_value_from_reg_X("ah"))!= bool(self.Flags["sf"])):
                    self.Flags["cf"] = 1
                    self.Flags["of"] = 1
                else:
                    self.Flags["cf"] = 0
                    self.Flags["of"] = 0



                v = a
                one = 0
                for i in range(0, 8):
                    if bool(v & 1):
                        one += 1
                    v = v.__rshift__(1)
                if bool(one & 1):
                    self.Flags["pf"] = 0
                else:
                    self.Flags["pf"] = 1


                self.Flags["zf"] = 0
            elif tmp1[2] == 2:

                a = a * self.Get_value_from_reg_X("ax")
                b = a
                if a >= pow(2, 2 * 8):
                    a = a & (pow(2, 2 * 8) - 1)
                self.Save_value_in_reg_X("ax", a)

                b = b.__rshift__(16)
                if b >= pow(2, 2 * 8):
                    b = b & (pow(2, 2 * 8) - 1)
                self.Save_value_in_reg_X("dx", b)

                if bool(a & pow(2, (2*8) - 1)):
                    self.Flags["sf"] = 1
                else:
                    self.Flags["sf"] = 0


                if (bool(self.Get_value_from_reg_X("dx")) != bool(self.Flags["sf"])):
                    self.Flags["cf"] = 1
                    self.Flags["of"] = 1
                else:
                    self.Flags["cf"] = 0
                    self.Flags["of"] = 0



                v = a
                one = 0
                for i in range(0, 8):
                    if bool(v & 1):
                        one += 1
                    v = v.__rshift__(1)
                if bool(one & 1):
                    self.Flags["pf"] = 0
                else:
                    self.Flags["pf"] = 1


                self.Flags["zf"] = 0
            elif tmp1[2] == 4:
                a = a * self.Registers["eax"]
                b = a
                if a >= pow(2, 4 * 8):
                    a = a & (pow(2, 4 * 8) - 1)
                self.Registers["eax"] = a

                b = b.__rshift__(32)
                if b >= pow(2, 4 * 8):
                    b = b & (pow(2, 4 * 8) - 1)
                self.Registers["edx"] = b

                if bool(a & pow(2, (4*8) - 1)):
                    self.Flags["sf"] = 1
                else:
                    self.Flags["sf"] = 0

                if (bool(b) != bool(self.Flags["sf"])):
                    self.Flags["cf"] = 1
                    self.Flags["of"] = 1
                else:
                    self.Flags["cf"] = 0
                    self.Flags["of"] = 0



                v = a
                one = 0
                for i in range(0, 8):
                    if bool(v & 1):
                        one += 1
                    v = v.__rshift__(1)
                if bool(one & 1):
                    self.Flags["pf"] = 0
                else:
                    self.Flags["pf"] = 1


                self.Flags["zf"] = 0

        return True

    def Div_X(self, String, infix):
        """
                                     This function start some operations on code
                                     make div idiv instructions

                                     Return :
                                     False if there where syntax error
                                     True if there where no syntax error
         """
        tmp1 = self.Check_code_operand(infix[0])
        if (tmp1 == False):
            return False
        if (tmp1[0] == 'imm') | (tmp1[2] == 0):
            return False

        a = 0
        if (tmp1[0] != 'add'):
            a = tmp1[1]
        else:
            a = self.Get_value_from_memory(tmp1[1], tmp1[2])

        if a==0:
            self.State="RTE"
            return False

        if tmp1[2] == 1:
            a, b = divmod((self.Get_value_from_reg_X("ax")), a)
            if a >= pow(2, 8):
                return False
            self.Save_value_in_reg_X("al", a)

            if b >= pow(2, 8):
                return False
            self.Save_value_in_reg_X("ah", b)


            if bool(a & pow(2, (8) - 1)):
                self.Flags["sf"] = 1
            else:
                self.Flags["sf"] = 0
            """"
            v = a
            one = 0
            for i in range(0, 8):
                if bool(v & 1):
                    one += 1
                v = v.__rshift__(1)
            if bool(one & 1):
                self.Flags["pf"] = 0
            else:
            
                        if a == 0:
                self.Flags["zf"] = 1
            else:
                """
            self.Flags["pf"] = 1


            self.Flags["zf"] = 1
        elif tmp1[2] == 2:
            a, b = divmod((self.Get_value_from_reg_X("dx").__lshift__(16) | self.Get_value_from_reg_X("ax")), a)
            if a >= pow(2, 2 * 8):
                return False
            self.Save_value_in_reg_X("ax", a)

            if b >= pow(2, 2 * 8):
                return False
            self.Save_value_in_reg_X("dx", b)


            if bool(a & pow(2, (2 * 8) - 1)):
                self.Flags["sf"] = 1
            else:
                self.Flags["sf"] = 0
                """
            v = a
            one = 0
            for i in range(0, 8):
                if bool(v & 1):
                    one += 1
                v = v.__rshift__(1)
            if bool(one & 1):
                self.Flags["pf"] = 0
            else:
                

            if a == 0:
                self.Flags["zf"] = 1
            else:
            """
            self.Flags["pf"] = 1
            self.Flags["zf"] = 1
        elif tmp1[2] == 4:
            a, b = divmod((self.Registers["edx"].__lshift__(32) | self.Registers["eax"]), a)
            if a >= pow(2, 4 * 8):
                return False
            self.Registers["eax"] = a

            if b >= pow(2, 4 * 8):
                return False
            self.Registers["edx"] = b

            if bool(a & pow(2, (4 * 8) - 1)):
                self.Flags["sf"] = 1
            else:
                self.Flags["sf"] = 0
                """
            v = a
            one = 0
            for i in range(0, 8):
                if bool(v & 1):
                    one += 1
                v = v.__rshift__(1)
            if bool(one & 1):
                self.Flags["pf"] = 0
            else:
                self.Flags["pf"] = 1

            if a == 0:
                self.Flags["zf"] = 1
            else:
                self.Flags["zf"] = 0
                """
            self.Flags["pf"] = 1
            self.Flags["zf"] = 1
        return True

    def Test(self, String, infix):

        """
                                    This function start some operations on code
                                    make and test or xor instructions

                                    Return :
                                    False if there where syntax error
                                    True if there where no syntax error
        """
        tmp1 = self.Check_code_operand(infix[0])
        tmp2 = self.Check_code_operand(infix[1])
        if (tmp1 is False) or (tmp2 is False):
            return False
        if (tmp1[0] == 'imm') or (tmp1[2] == 0) or ((tmp1[0] == 'imm') and (tmp2[0] == 'imm')):
            if (tmp1[2] == 0) and (tmp2[2] != 0):
                tmp1[2]=tmp2[2]
            else:
                return False
        if ((tmp1[0] == 'add') and (tmp2[0] == 'add')) or ((tmp1[2] != tmp2[2]) and (tmp2[2] != 0) and (tmp2[0] != 'imm')):
            return False

        if String == 'and':

            a = 0
            if (tmp1[0] != 'add'):
                a = tmp1[1]
            else:
                a = self.Get_value_from_memory(tmp1[1], tmp1[2])
            b = 0
            if (tmp2[0] != 'add'):
                b = tmp2[1]
            else:
                b = self.Get_value_from_memory(tmp2[1], tmp1[2])

            if b < 0:
                b = pow(2, (tmp1[2] * 8)) + b
            if b < 0:
                return False

            self.Flags["ac"] = 0
            self.Flags["of"] = 0
            self.Flags["cf"] = 0

            a = a & b


            if bool(a & pow(2, (tmp1[2] * 8) - 1)):
                self.Flags["sf"] = 1
            else:
                self.Flags["sf"] = 0

            v = a
            one = 0
            for i in range(0, 8):
                if bool(v & 1):
                    one += 1
                v = v.__rshift__(1)
            if bool(one & 1):
                self.Flags["pf"] = 0
            else:
                self.Flags["pf"] = 1

            if a == 0:
                self.Flags["zf"] = 1
            else:
                self.Flags["zf"] = 0

            if tmp1[0] == 'reg':
                if len(infix[0][0])==3:
                    self.Registers[infix[0][0]] = a
                else:
                    self.Save_value_in_reg_X(infix[0][0],a)
            else:
                if not self.Save_value_in_memory(tmp1[1], a, tmp1[2]):
                    return False
        elif String == 'test':

            a = 0
            if (tmp1[0] != 'add'):
                a = tmp1[1]
            else:
                a = self.Get_value_from_memory(tmp1[1], tmp1[2])
            b = 0
            if (tmp2[0] != 'add'):
                b = tmp2[1]
            else:
                b = self.Get_value_from_memory(tmp2[1], tmp1[2])

            if b < 0:
                b = pow(2, (tmp1[2] * 8)) + b
            if b < 0:
                return False

            self.Flags["ac"] = 0
            self.Flags["of"] = 0
            self.Flags["cf"] = 0

            a = a & b


            if bool(a & pow(2, (tmp1[2] * 8) - 1)):
                self.Flags["sf"] = 1
            else:
                self.Flags["sf"] = 0

            v = a
            one = 0
            for i in range(0, 8):
                if bool(v & 1):
                    one += 1
                v = v.__rshift__(1)
            if bool(one & 1):
                self.Flags["pf"] = 0
            else:
                self.Flags["pf"] = 1

            if a == 0:
                self.Flags["zf"] = 1
            else:
                self.Flags["zf"] = 0
        elif String == 'or':

            a = 0
            if (tmp1[0] != 'add'):
                a = tmp1[1]
            else:
                a = self.Get_value_from_memory(tmp1[1], tmp1[2])
            b = 0
            if (tmp2[0] != 'add'):
                b = tmp2[1]
            else:
                b = self.Get_value_from_memory(tmp2[1], tmp1[2])

            if b < 0:
                b = pow(2, (tmp1[2] * 8)) + b
            if b < 0:
                return False

            self.Flags["ac"] = 0
            self.Flags["of"] = 0
            self.Flags["cf"] = 0

            a = a | b


            if bool(a & pow(2, (tmp1[2] * 8) - 1)):
                self.Flags["sf"] = 1
            else:
                self.Flags["sf"] = 0

            v = a
            one = 0
            for i in range(0, 8):
                if bool(v & 1):
                    one += 1
                v = v.__rshift__(1)
            if bool(one & 1):
                self.Flags["pf"] = 0
            else:
                self.Flags["pf"] = 1

            if a == 0:
                self.Flags["zf"] = 1
            else:
                self.Flags["zf"] = 0

            if tmp1[0] == 'reg':
                if len(infix[0][0])==3:
                    self.Registers[infix[0][0]] = a
                else:
                    self.Save_value_in_reg_X(infix[0][0],a)
            else:
                if not self.Save_value_in_memory(tmp1[1], a, tmp1[2]):
                    return False
        elif String == 'xor':

            a = 0
            if (tmp1[0] != 'add'):
                a = tmp1[1]
            else:
                a = self.Get_value_from_memory(tmp1[1], tmp1[2])
            b = 0
            if (tmp2[0] != 'add'):
                b = tmp2[1]
            else:
                b = self.Get_value_from_memory(tmp2[1], tmp1[2])

            if b < 0:
                b = pow(2, (tmp1[2] * 8)) + b
            if b < 0:
                return False

            self.Flags["ac"] = 0
            self.Flags["of"] = 0
            self.Flags["cf"] = 0

            a = a ^ b


            if bool(a & pow(2, (tmp1[2] * 8) - 1)):
                self.Flags["sf"] = 1
            else:
                self.Flags["sf"] = 0

            v = a
            one = 0
            for i in range(0, 8):
                if bool(v & 1):
                    one += 1
                v = v.__rshift__(1)
            if bool(one & 1):
                self.Flags["pf"] = 0
            else:
                self.Flags["pf"] = 1

            if a == 0:
                self.Flags["zf"] = 1
            else:
                self.Flags["zf"] = 0

            if tmp1[0] == 'reg':
                if len(infix[0][0])==3:
                    self.Registers[infix[0][0]] = a
                else:
                    self.Save_value_in_reg_X(infix[0][0],a)
            else:
                if not self.Save_value_in_memory(tmp1[1], a, tmp1[2]):
                    return False
        return True



















