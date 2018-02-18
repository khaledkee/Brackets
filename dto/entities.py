from enum import Enum


class VType(Enum):
    byte = 1
    word = 2
    dword = 3


class Register:
    name = 0


class Memory:
    name = ""
    address = 0
    type = VType.byte
    length = 0


class Immediate:
    value = 0
    length = 0
    _float = False


class Operand:
    variables = []


class Label:
    _global = False
    address = 0
    name = ""


class Variable:
    name = ""
    type = VType.byte
    content = []


class Operation:
    name = ""


class Instruction:
    name = ""
    operands = []