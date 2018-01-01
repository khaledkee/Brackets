"""
    This file contains some function used in our code
"""
def is_hexa(string):
    """
                                        This function check that number is hexadecimal or not

                                        Return :
                                        False if it not valid hexadecimal
                                        Decimal value for the number
    """

    try:
        a = int(string[:-1], 16)
        return a
    except Exception:
        return False

def is_binary(string):
    """
                                            This function check that number is binary or not

                                            Return :
                                            False if it not valid binary
                                            Decimal value for the number
    """

    try:
        a = int(string[:-1], 2)
        return a
    except Exception:
        return False

def is_octa(string):
    """
                                                This function check that number is octal or not

                                                Return :
                                                False if it not valid octal
                                                Decimal value for the number
    """

    try:
        a = int(string[:-1], 8)
        return a
    except Exception:
        return False

def convert_string(string):
    """
                                                This function try to convert string to decimal value

                                                Return :
                                                False if it not valid to convert
                                                Decimal value for the string
    """

    try:
        string = string[1:]
        string = string[:-1]
        num = ""
        for i in range(0, len(string)):
            num += str(ord(string[i]))
        return int(num)
    except Exception:
        return False



