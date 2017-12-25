
def is_hexa(String):
    try:
        A=int(String[:-1],16)
        return A
        raise Exception("Error")
    except Exception:
            return False

def is_binary(String):
    try:
        A=int(String[:-1],2)
        return A
        raise Exception("Error")
    except Exception:
            return False

def is_octa(String):
    try:
        A=int(String[:-1],8)
        return A
        raise Exception("Error")
    except Exception:
            return False

def convert_string(String):
    String=String[1:]
    String=String[:-1]
    num=""
    for i in range(0,len(String)):
        num+=str(ord(String[i]))
    return int(num)


##############################
def postfix(Line):
    stak=[]
    expression=[]
    infix=[]
    for i in range(0,len(Line)):
       # print(stak)
        if (Line[i]=='(')|(Line[i]=='['):
            if (stak.__len__()>0):
                if (Line[i]=='[')&((stak[stak.__len__()-1]=="lengthof")|(stak[stak.__len__()-1]=="dup")|(stak[stak.__len__()-1]=="sizeof")|(stak[stak.__len__()-1]=="type")):
                    return False
            if (stak.__len__()>0):
                if (Line[i]=='(')&((stak[stak.__len__()-1]=="lengthof")|(stak[stak.__len__()-1]=="sizeof")):
                    return False
            if (stak.__len__() == 0) & (Line[i] == '('):
                return False
            stak.append(Line[i])
        elif (Line[i]==')')|(Line[i]==']'):
            if stak.__len__()==0:
                return False

            j=stak.__len__()-1
            while(j>=0):
                if (stak[j]=='(')&(Line[i]==')'):
                    break
                elif (stak[j]=='(')&(Line[i]==']'):
                    return False
                elif (stak[j]=='[')&(Line[i]==')'):
                    return False
                elif (stak[j]=='[')&(Line[i]==']'):
                    break
                expression.append(stak[j])
                stak=stak[:-1]
                j=j-1
                if j<0:
                    break



            stak = stak[:-1]
        elif Line[i]==',':
            if expression.__len__() == 0:
                return False
            if stak.__len__()!=0:
                j = stak.__len__() - 1
                while (j >= 0):
                    expression.append(stak[j])
                    stak = stak[:-1]
                    j = j - 1
            if expression.__len__()>0:
                infix.append(expression)
            expression=[]
        elif Line[i][0].isdecimal()==True:
            if Line[i][len(Line[i])-1]=='h':
                tmp=is_hexa(Line[i])
                if tmp==False:
                    return False
                expression.append(tmp)
            elif Line[i][len(Line[i])-1]=='o':
                tmp=is_octa(Line[i])
                if tmp==False:
                    return False
                expression.append(tmp)
            elif Line[i][len(Line[i])-1]=='b':
                tmp=is_binary(Line[i])
                if tmp==False:
                    return False
                expression.append(tmp)
            elif Line[i][len(Line[i])-1]=='d':
                tmp=int(Line[i][:-1],10)
                expression.append(tmp)
            elif Line[i].isdecimal()==True:
                expression.append(int(Line[i]))
            else:
                return False
        elif (Line[i]=="lengthof")|(Line[i]=="sizeof")|(Line[i]=="type")|(Line[i]=="dup"):
            j = stak.__len__() - 1
            while (j >= 0):
                if (stak[j] == '(') | (stak[j] == '['):
                    break
                expression.append(stak[j])
                stak = stak[:-1]
                j = j - 1
            stak.append(Line[i])
        else:
            if(Line[i]=='*')|(Line[i]=='-')|(Line[i]=='/')|(Line[i]=='+'):
                if stak.__len__()>0:
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
                        elif ((stak[j] == 'dup') | (stak[j] == 'lengthof')|(stak[j] == 'type') | (stak[j] == 'sizeof')):
                            expression.append(stak[j])
                            stak = stak[:-1]
                        else:
                            break
                        j=j-1

                stak.append(Line[i])
            else:
                expression.append(Line[i])

    j=stak.__len__()-1
    while(j>=0):
        if (stak[j]=='(')|(stak[j]=='['):
            return False
        expression.append(stak[j])
        stak=stak[:-1]
        j=j-1

    if expression.__len__() > 0:
        infix.append(expression)
    return infix

