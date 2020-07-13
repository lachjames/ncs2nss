class ObjectType:
    INT, FLOAT, STRING, OBJECT, LOCATION, EFFECT, EVENT, TALENT, ITEMPROPERTY, VECTOR = range(10)

    MAP = {
        "i": INT,
        "f": FLOAT,
        "s": STRING,
        "o": OBJECT,
        "l": LOCATION,
        "0": EFFECT,
        "1": EVENT,
        "2": LOCATION,
        "3": TALENT,
        "4": ITEMPROPERTY,
        "v": VECTOR
    }

    INV_MAP = {
        v: k for k, v in MAP.items()
    }

    NAME_MAP = {
        INT: "int",
        FLOAT: "float",
        STRING: "string",
        OBJECT: "object",
        LOCATION: "location",
        EFFECT: "effect",
        EVENT: "event",
        TALENT: "talent",
        ITEMPROPERTY: "itemproperty",
        VECTOR: "vector"
    }

    INV_NAME_MAP = {
        v: k for k, v in NAME_MAP.items()
    }

    DEFAULT_MAP = {
        INT: 0,
        FLOAT: 0.0,
        STRING: "",
        VECTOR: "[0.0, 0.0, 0.0]"
    }

    @staticmethod
    def size(obj_type):
        if obj_type is ObjectType.VECTOR:
            return 3
        return 1


class Constant:
    def __init__(self, const_type, value):
        self.const_type = const_type
        self.value = value

        self.active = True

    def __str__(self):
        return "CONST({}) {}".format(self.const_type, self.value)


class Variable:
    def __init__(self, var_type, value, is_set=True):
        self.var_type = var_type
        self.value = value
        self.is_set = is_set

        self.active = True

    def __str__(self):
        # return "{}({})".format(ObjectType.INV_MAP[self.var_type], self.value)
        return str(self.value)


class SubroutineCall:
    def __init__(self, sub, args):
        self.sub = sub
        self.args = args

        self.active = True

    def __str__(self):
        return "{}({})".format(self.sub, self.args)


class BinaryOperation:
    def __init__(self, a, op, b):
        self.a = a
        self.op = op
        self.b = b

        self.value = self
        self.active = True

    def __str__(self):
        # if not self.active:
        #     return ""
        return "({} {} {})".format(self.a, self.op, self.b)


class UnaryOperation:
    def __init__(self, a, op):
        self.a = a
        self.op = op

        self.value = self
        self.active = True

    def __str__(self):
        # if not self.active:
        #     return ""
        if self.op in ("-", "!"):
            return "({}{})".format(self.op, self.a)
        else:
            return "({}{})".format(self.a, self.op)


class LogicalOperation:
    def __init__(self, a, op, b):
        self.a = a
        self.op = op
        self.b = b

        self.value = self
        self.active = True

    def __str__(self):
        # if not self.active:
        #     return ""
        return "({} {} {})".format(self.a, self.op, self.b)


class NSSTerminal:
    # An NSS terminal is a line of NCS which corresponds to the final execution of
    # a line of NSS. These include:
    #   - CPDownSP/CPDownBP (saving variable values)
    #   - Action (calling an action subroutine)
    #   - JSR (calling a subroutine)
    def __init__(self, expression):
        self.expression = expression

        self.active = True


class NSSAssign(NSSTerminal):
    def __init__(self, var_name, expression):
        self.var_name = var_name
        self.expression = expression

    def __str__(self):
        return "{} = {}".format(self.var_name, self.expression)
        # return "{} <- {}".format(self.var_name, self.expression)


class NSSCreateLocal(NSSTerminal):
    def __init__(self, var_type, expression, value):
        self.var_type = var_type
        self.expression = expression
        self.value = value

    def __str__(self):
        if self.value is None:
            return "{} {}".format(self.var_type, self.expression)
        else:
            return "{} {} = {}".format(self.var_type, self.expression, self.value)
        # return "Define {} (type {})".format(self.expression, self.var_type)


class NSSReturnValue(NSSTerminal):
    def __str__(self):
        return "return {}".format(self.expression)


class NSSAction(NSSTerminal):
    def __init__(self, action_name, action_args):
        self.action_name = action_name
        self.action_args = action_args

        self.active = True

    def get_value(self):
        return "{}({})".format(self.action_name, ", ".join([str(x) for x in self.action_args]))

    def __str__(self):
        # if not self.active:
        #     return ""
        return self.get_value()


class NSSReturnValue(NSSTerminal):
    def __str__(self):
        return "return {}".format(self.expression)


class NSSSSAction(NSSAction):
    pass


class NSSReference(NSSTerminal):
    def __init__(self, expression):
        super().__init__(expression)

        self.value = self.expression

    def __str__(self):
        return "{}".format(self.expression)


class NSSVector(NSSTerminal):
    def __init__(self, expression):
        super().__init__(expression)

        self.value = self.expression
        # self.active = False

    def ref(self, idx):
        return NSSStructAccess(self.value, idx)


class NSSVectorConstant(NSSTerminal):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return "[{}, {}, {}]".format(self.x, self.y, self.z)


class NSSStructAccess(NSSTerminal):
    def __init__(self, variable, idx):
        self.variable = variable
        self.idx = idx

    def __str__(self):
        return "{}.{}".format(self.variable, self.idx)


class NSSGlobal(NSSTerminal):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return str(self.name)


class NSSSubCall(NSSTerminal):
    def __init__(self, sub_name, sub_args):
        self.sub_name = sub_name
        self.sub_args = sub_args

        self.active = True

    def __str__(self):
        # if not self.active:
        #     return ""
        return "{}({})".format(self.sub_name, ", ".join([str(x) for x in self.sub_args]))


class NSSArgumentAccess(NSSTerminal):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


class VectorDefinition:
    def __init__(self, rsadds):
        self.rsadds = rsadds


class GetVectorElement:
    def __init__(self, get_vector, destruct):
        self.get_vector = get_vector
        self.destruct = destruct


class VectorAssignment:
    def __init__(self, cpdownsp):
        self.cpdownsp = cpdownsp
        # self.movesp = movesp


class GetVector:
    def __init__(self, cptopsp):
        self.cptopsp = cptopsp


class VectorIndex:
    def __init__(self, var_name, index):
        self.var_name = var_name
        self.index = index

    def __str__(self):
        return "{}.{}".format(self.var_name, self.index)


class VectorValue:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return "[{}, {}, {}]".format(self.x, self.y, self.z)


class VectorVariable(Variable):
    pass


class VectorView:
    def __init__(self, vector, idx):
        self.vector = vector
        self.idx = idx

    def __str__(self):
        return "{}.{}".format(self.vector, self.idx)


class VectorComponent(NSSTerminal):
    def __str__(self):
        return str(self.expression)


class VectorCreate:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return "vector {}".format(self.x, self.y, self.z)


class VectorAssign:
    def __init__(self, var_name, x, y, z):
        self.var_name = var_name
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return "{} = [{}, {}, {}]".format(self.var_name, self.x, self.y, self.z)
