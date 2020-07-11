import os
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from rply import Token
from nss.operators import ArgType


def is_list(value):
    return isinstance(value, list)


TEMPLATE_FOLDER = "C:/Users/lachl/OneDrive/Desktop/KOTOR/nss/templates/"
NAMESPACE = "KotOR"

TYPE_MAP = {
    "vector": "float[]",
    "object": "AuroraObject",
    "location": "AuroraLocation",
    "talent": "AuroraTalent",
    "itemproperty": "AuroraItemProperty",
    "effect": "AuroraEffect",
    "action": "AuroraAction",
    "event": "AuroraEvent",
    "INT": "int",
    "OBJECT_ID": "AuroraObjectID"
}

OBJECT_MAP = {
    "OBJECT_SELF": "AuroraObject.GetObjectSelf()",
    "OBJECT_INVALID": "AuroraObject.GetObjectInvalid()",
    "OBJECT_TYPE_INVALID": "AuroraObject.GetObjectTypeInvalid()"
}

DEFAULT_VALUES = {
    "int": "0",
    "string": "\"\"",
    "float": "0.0f"
}


class Tree:
    def __init__(self, value):
        self.children = []
        self.value = value

    def add_child(self, child):
        self.children.append(child)

    def __str__(self):
        return type(self.value).__name__

    def recursive_print(self, level=0, space="  "):
        print(space * level + str(self.value))
        for child in reversed(self.children):
            child.recursive_print(level + 1, space)

    def show(self):
        from graphviz import Digraph
        dot = Digraph()

        node_dict = {}

        # Create all vertices
        nodes = [self]
        i = 0
        while len(nodes) > 0:
            cur = nodes.pop()
            if type(cur.value) is Token:
                desc = "{}: {}".format(cur.value.gettokentype(), cur.value.getstr())
            elif issubclass(type(cur.value), Code):
                desc = type(cur.value).__name__
            else:
                desc = type(cur.value).__name__
            dot.node(str(i), desc)
            node_dict[cur] = str(i)
            i += 1
            for child in reversed(cur.children):
                nodes.append(child)

        # Create all edges
        nodes = [self]
        while len(nodes) > 0:
            cur = nodes.pop()
            for child in cur.children:
                dot.edge(node_dict[cur], node_dict[child])
                nodes.append(child)

        dot.view()


def convert(value, sep=";\n", add_prefix=""):
    # print(value, type(value))
    if value is None:
        return ""

    elif type(value) is list:
        arr = []
        for x in value:
            arr.append(convert(x, sep).strip())
        return sep.join(arr)

    elif type(value) is Token:
        if value.gettokentype() == "TYPE" and value.getstr().strip() in TYPE_MAP:
            return TYPE_MAP[value.getstr().strip()]
        return value.getstr().strip()

    else:
        if add_prefix != "":
            print(add_prefix)
        return add_prefix + value.get_prefix() + value.convert()


def if_else(else_):
    if else_ is None:
        return ""
    elif type(else_) is Body:
        return "else"
    else:
        return "else if"


def semicolon(line):
    return "" if type(line) in (If, While, For, Switch) else ";"


env = Environment(
    loader=FileSystemLoader(TEMPLATE_FOLDER)
)
env.undefined = StrictUndefined

env.filters.update({
    'is_list': is_list,
    'convert': convert,
    "semicolon": semicolon
})


class Program:
    def __init__(self, body):
        self.body = body

    def convert(self, class_name):
        code = ""

        for segment in self.body:
            code += segment.convert() + "\n"

        template = env.get_template("Program.jinja2")
        result = template.render(namespace=NAMESPACE, class_name=class_name, code=code)

        while ";;" in result:
            result = result.replace(";;", ";")

        while "\n\n\n" in result:
            result = result.replace("\n\n\n", "\n\n")

        # For some reason, they refer to the empty string as 32289?
        # It might be a bug or a misuse of the engine... idk?
        # Some discussions here https://deadlystream.com/search/?q=32289&quick=1
        result = result.replace("NWScript.GetStringByStrRef (32289)", "\"TEST\"")

        result = result.split("\n")
        result_cleaned = [
            "using System;",
            "using UnityEngine;",
            ""
        ]
        for l in result:
            if l.strip() == ";":
                continue
            # elif "NWScript.AssignCommand" in l or "ActionDoCommand" in l:
            #     result_cleaned.append("//" + l)
            #     continue

            result_cleaned.append(l)

        return "\n".join(result_cleaned)

    def find_instances_of(self, cls):
        instances = []
        queue = self.body[:]

        while len(queue) > 0:
            cur = queue.pop()

            if issubclass(type(cur), cls):
                instances.append(cur)

            if type(cur) is list:
                queue += cur
            elif issubclass(type(cur), Code):
                for var_name in vars(cur):
                    queue.append(vars(cur)[var_name])

        return instances

    def construct_tree(self):
        tree = Tree("root")
        queue = [(tree, child) for child in self.body]

        while len(queue) > 0:
            parent_tree, node = queue.pop()

            if type(node) is list:
                for c in node:
                    queue.append((parent_tree, c))

            elif issubclass(type(node), Code):
                child_tree = Tree(node)
                parent_tree.add_child(child_tree)
                for var_name in vars(node):
                    queue.append((child_tree, vars(node)[var_name]))

            else:
                child_node = Tree(node)
                parent_tree.add_child(child_node)

        return tree


class Code:
    # Note that convert assumes that the template will have the same name
    # as the class it's a template for
    def convert(self):
        cls_name = type(self).__name__
        template_loc = "{}.jinja2".format(cls_name)

        if not os.path.exists(TEMPLATE_FOLDER + template_loc):
            return "not_implemented"

        # print(template_loc)

        template = env.get_template(template_loc)
        return template.render(x=self)

    def get_prefix(self):
        if "prefix" in vars(self):
            return self.prefix
        return ""

    def set_prefix(self, prefix):
        self.prefix = prefix


class FunctionDefinition(Code):
    def __init__(self, return_type, name, args, body):
        self.return_type = return_type
        self.name = name
        self.args = args
        self.body = body


class DefinedArgument(Code):
    def __init__(self, var_type, var_name, default_expression):
        self.var_type = var_type
        self.var_name = var_name
        self.default_expression = default_expression


class FunctionCall(Code):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def convert(self):
        if convert(self.name) == "DelayCommand":
            t = convert(self.args[0])
            call = convert(self.args[1])
            if call.startswith("N("):
                call = call[2:-1]
            self.name = "_ignore"
            return "Engine.DelayCommand({}, () => {{{};}})".format(t, call)
        elif convert(self.name) == "AssignCommand":
            obj = convert(self.args[0])
            call = convert(self.args[1])
            if call.startswith("N("):
                call = call[2:-1]
            self.name = "_ignore"
            return "Engine.AssignCommand({}, () => {{{};}})".format(obj, call)
        elif convert(self.name) == "ActionDoCommand":
            call = convert(self.args[0])
            if call.startswith("N("):
                call = call[2:-1]
            self.name = "_ignore"
            return "Engine.ActionDoCommand(() => {{{};}})".format(call)
        else:
            return super().convert()


class CreateVariable(Code):
    def __init__(self, var_type, var_name, var_expression, force_public=False):
        self.var_type = var_type
        self.var_name = var_name
        self.var_expression = var_expression
        self.force_public = force_public

    def default_value(self):
        var_type = convert(self.var_type)
        if var_type in DEFAULT_VALUES:
            return DEFAULT_VALUES[var_type]
        return "null"

    def convert(self):
        var_type = convert(self.var_type)
        var_name = convert(self.var_name)
        if self.var_expression is None:
            var_value = self.default_value()
        else:
            var_value = convert(self.var_expression)
        return "{}{} {} = {}".format(
            "public " if self.force_public else "",
            var_type,
            var_name,
            var_value
        )


class DefinedConstant(Code):
    DEFAULTS = {
        "int": "0",
        "string": "",
        "float": "0.0f",
        "object": "null"
    }

    def __init__(self, var_type, var_name, var_expression):
        self.var_type = RawText(var_type.getstr().strip())
        self.var_name = var_name
        self.var_expression = var_expression

        if self.var_expression is None:
            self.var_expression = RawText(self.DEFAULTS[convert(self.var_type)])


class StructAssignment(Code):
    def __init__(self, var_name, operator, expression):
        self.var_name = var_name
        self.operator = operator
        self.expression = expression


class Assignment(Code):
    def __init__(self, var_name, operator, expression):
        self.var_name = var_name
        self.operator = operator
        self.expression = expression


class Include(Code):
    def __init__(self, name):
        self.name = name


class UsedVariable(Code):
    def __init__(self, var_name):
        self.var_name = var_name

    # def convert(self):
    #     name = convert(self.var_name)
    #     if name in OBJECT_MAP:
    #         return OBJECT_MAP[name]
    #     return self.get_prefix() + name


ARGTYPE_MAP = {
    ArgType.Integer: "I({})",
    ArgType.Float: "F({})",
    ArgType.Numeric: "N({})",
    ArgType.Boolean: "B({})",
    ArgType.String: "S({})",
    ArgType.Shared: "{}",
}


class BinaryOperation(Code):
    def __init__(self, opdef, exp1, operator, exp2):
        self.opdef = opdef
        self.exp1 = exp1
        self.operator = operator
        self.exp2 = exp2

    def convert(self):
        argmap = ARGTYPE_MAP[self.opdef.argtype]
        retmap = ARGTYPE_MAP[self.opdef.rettype]

        arg1 = argmap.format(convert(self.exp1))
        arg2 = argmap.format(convert(self.exp2))

        return retmap.format("{} {} {}".format(arg1, self.operator.getstr(), arg2))


class UnaryPrefixOperation(Code):
    def __init__(self, opdef, operator, exp):
        self.opdef = opdef
        self.operator = operator
        self.exp = exp

    def convert(self):
        argmap = ARGTYPE_MAP[self.opdef.argtype]
        retmap = ARGTYPE_MAP[self.opdef.rettype]

        arg = argmap.format(convert(self.exp))

        return retmap.format("{}{}".format(self.operator.getstr(), arg))


class UnaryPostfixOperation(Code):
    def __init__(self, opdef, exp, operator):
        self.opdef = opdef
        self.exp = exp
        self.operator = operator

    def convert(self):
        argmap = ARGTYPE_MAP[self.opdef.argtype]
        retmap = ARGTYPE_MAP[self.opdef.rettype]

        arg = argmap.format(convert(self.exp))

        return retmap.format("{}{}".format(arg, self.operator.getstr()))


class SelfModifyingPostfixOperation(Code):
    def __init__(self, opdef, exp, operator):
        self.opdef = opdef
        self.exp = exp
        self.operator = operator

    def convert(self):
        arg = convert(self.exp)

        return "{} {}".format(arg, self.operator.getstr())


class SelfModifyingPrefixOperation(Code):
    def __init__(self, opdef, operator, exp):
        self.opdef = opdef
        self.operator = operator
        self.exp = exp

    def convert(self):
        arg = convert(self.exp)

        return "{}{}".format(self.operator.getstr(), arg)


class Minus(Code):
    def __init__(self, exp):
        self.exp = exp

    def convert(self):
        return "-N({})".format(convert(self.exp))


class CallingArgument(Code):
    def __init__(self, exp):
        self.exp = exp


class Integer(Code):
    def __init__(self, value, is_negative):
        self.value = value
        self.is_negative = is_negative

    def convert(self):
        return "{}{}".format("-" if self.is_negative else "", self.value.getstr())


class String(Code):
    def __init__(self, value):
        self.value = value

    def convert(self):
        return self.value.getstr()


class Hexadecimal(Code):
    def __init__(self, value):
        self.value = value

    def convert(self):
        return self.value.getstr()


class Vector(Code):
    def __init__(self, value):
        self.value = value

    def convert(self):
        x, y, z = self.value.getstr()[1:-1].split(",")
        return "new float[] {" + "{}f, {}f, {}f".format(x, y, z) + "}"


class Float(Code):
    def __init__(self, value, is_negative):
        self.value = value
        self.is_negative = is_negative

    def convert(self):
        return "{}{}{}".format(
            "-" if self.is_negative else "",
            self.value.getstr(),
            "f" if self.value.getstr()[-1] != "f" else ""
        )


class If(Code):
    def __init__(self, expression, body, else_):
        self.expression = expression
        self.body = body
        self.else_ = else_


class While(Code):
    def __init__(self, expression, body):
        self.expression = expression
        self.body = body


class Do(Code):
    def __init__(self, expression, body):
        self.expression = expression
        self.body = body


class Comment(Code):
    def __init__(self, text):
        self.text = text


class For(Code):
    def __init__(self, for_def, body):
        self.for_def = for_def
        self.body = body


class ForDef(Code):
    def __init__(self, init, cond, after):
        self.init = init
        self.cond = cond
        self.after = after

        if type(self.init) is UsedVariable:
            # In C# we just leave this blank
            self.init = RawText("")


class Body(Code):
    def __init__(self, body):
        self.body = body


class Return(Code):
    def __init__(self, expression):
        self.expression = expression


class Switch(Code):
    def __init__(self, expression, body):
        self.expression = expression
        self.body = body

        is_first = True
        for case in self.body:
            case.lhs = self.expression
            case.is_first = is_first
            is_first = False


class RawText(Code):
    def __init__(self, txt):
        self.txt = txt

    def convert(self):
        return self.txt


class SwitchCase(Code):
    def __init__(self, expression, body, has_break):
        self.expression = expression
        self.body = body
        self.has_break = has_break


class FunctionDeclaration(Code):
    def __init__(self, return_type, name, args):
        self.return_type = return_type
        self.name = name
        self.args = args


class CreateMultipleVariables(Code):
    def __init__(self, var_type, var_assignments):
        self.var_type = var_type
        self.var_assignments = var_assignments

    def default_value(self):
        var_type = convert(self.var_type)
        if var_type in DEFAULT_VALUES:
            return DEFAULT_VALUES[var_type]
        return "null"

    def convert(self):
        d = self.default_value()
        s = convert(self.var_type) + " "
        for var_name in self.var_assignments:
            s += "{} = {}".format(convert(var_name), d)
            if var_name != self.var_assignments[-1]:
                s += ", "
        return s


class NullOp(Code):
    def __init__(self):
        pass

    def convert(self):
        return ""


class Struct(Code):
    def __init__(self, name, params):
        self.name = name
        self.params = params


class StructAccess(Code):
    def __init__(self, struct_name, var_name):
        self.struct_name = struct_name
        self.var_name = var_name


class Define(Code):
    def __init__(self, name, value):
        self.name = name
        self.value = value


class DeclareStruct(Code):
    def __init__(self, struct_type, struct_name):
        self.struct_type = struct_type
        self.struct_name = struct_name
