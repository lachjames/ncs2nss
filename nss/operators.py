OPERATORS = {}
LEVELS = {}
LEVEL = 0


# Numeric args can be int or float
class ArgType:
    Integer, Float, Numeric, Boolean, String, Shared = range(6)


class OpType:
    Binary, Unary, UnaryPrefix, UnaryPostfix, SelfModifying = range(5)


class OperatorMetaclass(type):
    def __init__(cls, name, bases, clsdict):
        if name == "Operator":
            return
        OPERATORS[name] = cls
        if LEVEL not in LEVELS:
            LEVELS[LEVEL] = []
        LEVELS[LEVEL].append(name)


class Operator(metaclass=OperatorMetaclass):
    regex = None

    optype = OpType.Binary
    argtype = ArgType.Numeric
    rettype = ArgType.Numeric

    lex_priority = 0


def register_operator(c):
    OPERATORS[c.__name__.lower()] = c
    return c


class Increment(Operator):
    regex = r"\+\+"
    optype = OpType.SelfModifying

    lex_priority = -1


class Decrement(Operator):
    regex = r"\-\-"
    optype = OpType.SelfModifying

    lex_priority = -1


LEVEL += 1


class LogicalNot(Operator):
    regex = r"\!"
    optype = OpType.UnaryPrefix
    argtype = ArgType.Boolean
    rettype = ArgType.Boolean


LEVEL += 1


class Multiplication(Operator):
    regex = r"\*"


class Division(Operator):
    regex = r"/"


class Modulus(Operator):
    regex = r"%"


LEVEL += 1


class Plus(Operator):
    regex = r"\+"


class Minus(Operator):
    regex = r"\-"


LEVEL += 1


class ShiftLeft(Operator):
    regex = r"<<"
    argtype = ArgType.Integer

    lex_priority = -1


class ShiftRight(Operator):
    regex = r">>"
    argtype = ArgType.Integer

    lex_priority = -1


LEVEL += 1


class GTE(Operator):
    regex = r">="

    lex_priority = -1


class LTE(Operator):
    regex = r"<="

    lex_priority = -1


class GT(Operator):
    regex = r">"


class LT(Operator):
    regex = r"<"


LEVEL += 1


class Equals(Operator):
    regex = r"=="


class NotEquals(Operator):
    regex = r"\!="

    lex_priority = -1


LEVEL += 1


class BitwiseOr(Operator):
    regex = r"\|"
    argtype = ArgType.Integer
    rettype = ArgType.Integer


class BitwiseAnd(Operator):
    regex = r"&"
    argtype = ArgType.Integer
    rettype = ArgType.Integer


class BitwiseInverse(Operator):
    regex = r"~"
    argtype = ArgType.Integer


LEVEL += 1


class LogicalAnd(Operator):
    regex = r"&&"
    argtype = ArgType.Boolean
    rettype = ArgType.Boolean

    lex_priority = -1


LEVEL += 1


class LogicalOr(Operator):
    regex = r"\|\|"
    argtype = ArgType.Boolean
    rettype = ArgType.Boolean

    lex_priority = -1
# Debug
# for level in LEVELS:
#     print("{}: {}".format(level, LEVELS[level]))
