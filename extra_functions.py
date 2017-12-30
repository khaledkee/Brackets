def is_hexa(string):
    try:
        a = int(string[:-1], 16)
        return a
    except Exception:
        return False


def is_binary(string):
    try:
        a = int(string[:-1], 2)
        return a
    except Exception:
        return False


def is_octa(string):
    try:
        a = int(string[:-1], 8)
        return a
    except Exception:
        return False


def convert_string(string):

    string = string[1:]
    string = string[:-1]
    num = ""
    for i in range(0, len(string)):
        num += str(ord(string[i]))
    return int(num)


##############################

