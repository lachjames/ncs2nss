class Constant:
    def __init__(self, const_type, value):
        self.const_type = const_type
        self.value = value

        self.active = True

    def __str__(self):
        return "CONST({}) {}".format(self.const_type, self.value)


class Variable:
    def __init__(self, var_type, value):
        self.var_type = var_type
        self.value = value

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
        if self.op == "-":
            return "-{}".format(self.a)
        else:
            return "{}{}".format(self.a, self.op)


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


class NSSSSAction(NSSAction):
    pass


class NSSReference(NSSTerminal):
    def __init__(self, expression):
        super().__init__(expression)

        self.value = self.expression

    def __str__(self):
        return "{}".format(self.expression)


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
