import os
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from rply import Token


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
    def __init__(self, size, rsadd_command, jump_to_subroutine, rtn, subroutines):
        self.size = size
        self.rsadd_command = rsadd_command
        self.jump_to_subroutine = jump_to_subroutine
        self.rtn = rtn
        self.subroutines = subroutines

        i = 3
        for subroutine in self.subroutines:
            for cmd in subroutine.commands:
                cmd.line_num = i
                i += 1

    def convert(self):
        code = ""

        main_fn = self.subroutines[0]
        if len(self.subroutines) > 1:
            subs = self.subroutines[1:]
        else:
            subs = []

        return code

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


class Subroutine:
    def __init__(self, commands):
        self.commands = commands
        self.name = None
        self.labels = None

        if type(self.commands[-1]) is not Return:
            self.commands.append(Return())

        # print(self.commands)

        # for cmd in commands:
        #     print(cmd)

    def set_labels(self, labels):
        self.labels = labels


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


class ConditionalJump(Code):
    def __init__(self, op_type, line):
        self.op_type = op_type
        self.line = line


class Jump(Code):
    def __init__(self, line):
        self.line = line


class JumpSubroutine(Code):
    def __init__(self, line):
        self.line = line


class SSJumpSubroutine(Code):
    def __init__(self, line):
        self.line = line


class Return(Code):
    def __init__(self):
        pass


class InlineReturn(Code):
    def __init__(self):
        pass

    def __str__(self):
        return "return"


class CPDownSP(Code):
    def __init__(self, a, b):
        self.a = a
        self.b = b


class CPTopSP(Code):
    def __init__(self, a, b):
        self.a = a
        self.b = b


class CPDownBP(Code):
    def __init__(self, a, b):
        self.a = a
        self.b = b


class CPTopBP(Code):
    def __init__(self, a, b):
        self.a = a
        self.b = b


class MoveSP(Code):
    def __init__(self, x):
        self.x = x


class RSAdd(Code):
    def __init__(self, op_type):
        self.op_type = op_type


class Const(Code):
    def __init__(self, const_type, value):
        self.const_type = const_type
        self.value = value


class Action(Code):
    def __init__(self, label, args):
        self.label = label
        self.args = args


class SSAction(Code):
    def __init__(self, label, args):
        self.label = label
        self.args = args


class Logical(Code):
    def __init__(self, op_type):
        self.op_type = op_type


class BinaryOp(Code):
    def __init__(self, op_type, value):
        self.op_type = op_type
        self.value = value


class UnaryOp(Code):
    def __init__(self, op_type):
        self.op_type = op_type


class StackOp(Code):
    def __init__(self, op_type, value):
        self.op_type = op_type
        self.value = value


class Destruct(Code):
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c


class BaseCmd(Code):
    def __init__(self, op_type):
        self.op_type = op_type


class StoreState(Code):
    def __init__(self, label, size, n):
        self.label = label
        self.size = size
        self.n = n


class StoreStateReturn(Code):
    def __init__(self, lineno):
        self.lineno = lineno


class Size(Code):
    def __init__(self, size):
        self.size = size


class NoOp(Code):
    def __init__(self):
        pass
