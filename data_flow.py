from data_flow_types import Variable, BinaryOperation, UnaryOperation, LogicalOperation, NSSGlobal, NSSArgumentAccess, NSSAssign, NSSCreateLocal, NSSAction, \
    NSSSSAction, \
    NSSReference, \
    NSSSubCall, NSSVector

import control_flow
import assembly as asm
from util import PropagateTable

import copy
import idioms
from nwscript import NWScript

from colorama import init, Fore

init()

NWSCRIPT = NWScript.load()

import pickle


def copy_obj(obj):
    return pickle.loads(pickle.dumps(obj))


def main():
    pass


class HTMLColors:
    GREEN = "#AFC97E"
    BLUE = "#5398BE"
    RED = "#F24236"
    DARKBLUE = "#BCE7FD"
    BLACK = "#2E282A"


# m = StackMatrix(num_commands=10, stack_size=5)
# print(m)


def df_analysis(subroutine, subroutines, global_data):
    blocks, matrix = analyze_blocks(subroutine, subroutines, global_data)
    # print(matrix)
    with open("html/{}.html".format(subroutine.name), "w") as f:
        f.write(matrix.html())

    defined = set()

    for i in range(0, matrix.num_commands - 1):
        # We want to check for variables only when space is put on the stack
        if matrix.sps[i + 1] <= matrix.sps[i]:
            continue

        # print("Checking block {}".format(i))

        pos = matrix.sps[i]

        var_pos = matrix.sps[i]
        for j in range(i + 1, matrix.num_commands):
            if matrix.sps[j] < pos:
                # Variable was pushed off the stack
                break

            if matrix.var_names[j, pos - 1]:
                if matrix.var_names[j, pos - 1] in defined:
                    break

                # Variable was assigned so it's a local
                # Create a new block for the local variable's creation
                if matrix.types[i, pos - 1] is not None:
                    var_type = ObjectType.NAME_MAP[matrix.types[i, pos - 1]]
                elif matrix.types[j, pos - 1] is not None:
                    var_type = ObjectType.NAME_MAP[matrix.types[j, pos - 1]]
                elif (pos - 1) < 0:
                    arg_types = subroutines[subroutine.name].arg_types
                    if (-(pos - 1)) <= len(arg_types):
                        var_type = ObjectType.NAME_MAP[arg_types[-pos - 1]]
                    else:
                        # Get a global variable
                        _, var_type = global_data.from_offset((-pos - 1 - len(arg_types)) * 4)
                else:
                    var_type = "unknown"
                    # raise Exception("Failed to calculate type of block {} = {} with sp = {}".format(i, blocks[i], pos - 1))

                blocks[i] = NSSCreateLocal(var_type, matrix.var_names[j, pos - 1], blocks[i])

                defined.add(matrix.var_names[j, pos - 1])
                # print("created: {}".format(blocks[i]))
                break

    # Replace all inactive blocks with None
    for i in range(len(blocks)):
        if "active" in dir(blocks[i]) and not blocks[i].active:
            blocks[i] = None

    reduce_idioms(blocks)

    # for block in blocks:
    #     print(block)

    # We need to find any blocks which create a variable

    return blocks, matrix


def asm_to_nss(x):
    x = x.lower()
    if x.startswith("add"):
        return "+"

    if x.startswith("sub"):
        return "-"

    if x.startswith("eq"):
        return "=="

    if x.startswith("leq"):
        return "<="

    if x.startswith("lt"):
        return "<"

    if x.startswith("geq"):
        return ">="

    if x.startswith("gt"):
        return ">"

    if x.startswith("mul"):
        return "*"

    if x.startswith("div"):
        return "/"

    if x.startswith("neg"):
        return "-"

    if x.startswith("neq"):
        return "!="

    if x.startswith("logor"):
        return "||"

    if x.startswith("logand"):
        return "&&"

    if x.startswith("not"):
        return "!"

    return x


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

    @staticmethod
    def size(obj_type):
        if obj_type is ObjectType.VECTOR:
            return 3
        return 1


class StackMatrix:
    def __init__(self, num_commands, stack_size, sub):
        self.num_commands = num_commands
        self.stack_size = stack_size
        self.sub = sub

        self.matrix = PropagateTable(num_commands, stack_size)  # [[None for _ in range(stack_size)] for _ in range(num_commands)]
        self.var_names = PropagateTable(num_commands, stack_size)  # [[None for _ in range(stack_size)] for _ in range(num_commands)]
        self.types = PropagateTable(num_commands, stack_size)  # [[None for _ in range(stack_size)] for _ in range(num_commands)]

        self.sps = [0 for _ in range(num_commands)]
        self.bps = [0 for _ in range(num_commands)]

        self.num_vars = 0

        self.defines_local = [None for _ in range(num_commands)]

    def __getitem__(self, pos):
        return self.matrix[pos[0], pos[1]]

    def __setitem__(self, pos, value):
        self.matrix[pos[0], pos[1]] = value

    def propagate(self, obj, obj_type, start_command, stack_pos):
        # for cmd in range(start_command, self.num_commands):
        self[start_command, stack_pos] = obj
        self.types[start_command, stack_pos] = obj_type

    def top_of_stack(self, i):
        return self.sps[i]

    def sp_offset_to_pos(self, i, offset):
        return self.top_of_stack(i) + (offset // 4)

    def value_from_offset(self, i, offset):
        # pos = self.sp_offset_to_pos(i, offset)
        # if pos < 0:
        #     print("OFFSET {} -> {}".format(offset, pos))
        #     pos = -pos - 1
        #     return NSSArgumentAccess("arg" + str(pos))
        # else:
        return self.matrix[i, self.sp_offset_to_pos(i, offset)]

    def type_from_offset(self, i, offset):
        return self.types[i, self.sp_offset_to_pos(i, offset)]

    def modify_sp(self, i, offset):
        value = self.sps[i] + offset
        if value < 0:
            # This should not be possible, so something's gone wrong
            # print("INVALID STACK OPERATION DETECTED")
            # print(self)
            # raise Exception("Invalid stack operation detected; tried to set sps[{}] to {} (offset {})".format(i, value, offset))
            pass
        for j in range(i, self.num_commands):
            self.sps[j] = value

    def set_local(self, i, pos):
        has_set = False
        for j in range(i, self.num_commands):
            if self.var_names[j, pos] is None:
                if self.sub.name == "global":
                    self.var_names[j, pos] = "GLOBAL_{}".format(self.num_vars)
                else:
                    self.var_names[j, pos] = "VAR_{}".format(self.num_vars)
                has_set = True
        if has_set:
            self.num_vars += 1

    def __str__(self):
        string = []

        # Header row
        string.append(Fore.LIGHTBLUE_EX)
        string.append("\t")
        for i in range(self.num_commands):
            string.append(str(i) + "\t")
        string.append("\n")

        string.append(Fore.WHITE)
        for stack_pos in range(self.stack_size):
            string.append(Fore.LIGHTBLUE_EX)
            string.append(str(stack_pos) + "\t")
            string.append(Fore.WHITE)
            # Header column
            for cmd in range(self.num_commands):
                had_value = False
                if stack_pos >= self.top_of_stack(cmd):
                    col = Fore.LIGHTRED_EX
                else:
                    col = Fore.LIGHTGREEN_EX
                item = self.matrix[cmd, stack_pos]
                if item is None:
                    string.append(col + "--" + Fore.WHITE)
                else:
                    had_value = True
                    val = str(item)
                    if len(val) > 7:
                        val = val[:5] + ".."
                    string.append(col + val + Fore.WHITE)
                string.append("\t")

                if not had_value:
                    break
            string.append("\n")

        string.append(Fore.LIGHTYELLOW_EX)
        string.append("SP\t")
        for sp in self.sps:
            string.append(str(sp))
            string.append("\t")
        string.append("\n")

        string.append(Fore.LIGHTCYAN_EX)
        string.append("BP\t")
        for bp in self.bps:
            string.append(str(bp))
            string.append("\t")
        string.append("\n")

        string.append(Fore.WHITE)

        return "".join(string)

    def html(self):
        preamble = """
        <style>
        table, th, td {
            border: 1px dotted grey;
        }
        body {
            background-color:black;
        }
        </style>
        """
        string = [preamble, "<table style=\"color:white\">"]

        # Header row
        string.append("<tr><td></td>")
        for i in range(self.num_commands):
            string.append("<th>" + str(i) + "</th>")
        string.append("</tr>")

        for stack_pos in range(self.stack_size):
            string.append("<tr><td><b>" + str(stack_pos) + "</b></td>")
            changed = False
            for cmd in range(self.num_commands):
                if stack_pos >= self.top_of_stack(cmd):
                    col = HTMLColors.RED
                else:
                    col = HTMLColors.GREEN
                string.append("<td style=\"color:{}\">".format(col))
                item = self.matrix[cmd, stack_pos]
                if item is None:
                    string.append("--")
                else:
                    changed = True
                    val = str(item)
                    if len(val) > 13:
                        val = val[:10] + "..."
                    string.append(val)
                string.append("</td>")

            string.append("</tr>")
            if not changed:
                break

        string.append("<tr style=\"color:{}\">".format(HTMLColors.DARKBLUE) + "<td>SP</td>")
        for sp in self.sps:
            string.append("<td>" + str(sp) + "</td>")
        string.append("</tr>")

        string.append("<tr style=\"color:{}\">".format(HTMLColors.DARKBLUE) + "<td>BP</td>")
        for bp in self.bps:
            string.append("<td>" + str(bp) + "</td>")
        string.append("</tr>")

        string.append("</table>")
        return "".join(string)


def analyze_blocks(sub, subs, global_data):
    cfa = control_flow.ControlFlowAnalysis(sub, True)
    cfg = cfa.cfg

    init_matrix = StackMatrix(len(sub.commands), len(sub.commands), sub)
    command_to_matrix = {}

    blocks = [None] * len(sub.commands)

    # Do a depth-first traversal of the cfg, analyzing each block as we go
    done = set()
    stack = [(cfg.header, init_matrix)]
    while len(stack) > 0:
        block, matrix = stack.pop()
        # print(block)
        if block in done:
            continue

        new_blocks, block_matrix = analyze_block(block, sub, subs, global_data, matrix)

        # print(" *** Matrix after {} *** ".format(block))
        # print(block_matrix)

        for command in new_blocks:
            command_to_matrix[command] = block_matrix
        blocks[block.address:block.address + block.length] = new_blocks

        for succ in block.succs:
            stack.append((succ, copy_obj(block_matrix)))

        done.add(block)

    return blocks, command_to_matrix[sub.commands[-1]]


def analyze_block(block, sub, subs, global_data, matrix):
    stack_size = 0
    # for cmd in sub.commands:
    #     if type(cmd) in (asm.RSAdd, asm.Const, asm.CPTopSP, asm.CPTopBP):  # , asm.MoveSP):
    #         stack_size += 1

    # N = len(sub.commands)
    # matrix = StackMatrix(N, stack_size, sub)
    # matrix = StackMatrix(N, N, sub)

    # print("*** START ***")
    # print(matrix)

    blocks = []
    commands = sub.commands[block.address:block.address + block.length]
    for i_raw, command in enumerate(commands):
        i = block.address + i_raw
        return_val = None
        # print("Command {}: {}".format(i, command))
        if type(command) is asm.RSAdd:
            # Reserve space on the stack
            var_type = ObjectType.MAP[command.op_type[-1].lower()]
            var_obj = Variable(var_type, None)
            matrix.propagate(var_obj, var_type, i, matrix.top_of_stack(i))
            matrix.modify_sp(i, ObjectType.size(var_type))

        elif type(command) is asm.Const:
            const_type = ObjectType.MAP[command.const_type[-1].lower()]
            value = command.value
            const_obj = Variable(const_type, value)

            matrix.propagate(const_obj, const_type, i, matrix.top_of_stack(i))
            matrix.modify_sp(i, ObjectType.size(const_type))

        # Stack pointer changes
        elif type(command) is asm.CPTopSP:
            # Add the given number of bytes from the location specified in the stack to the top of the stack.
            # The value of SP is increased by the number of copied bytes.
            stack_pos = matrix.sp_offset_to_pos(i, command.a)
            if stack_pos < 0:
                # We are copying either an argument or a global
                arg_ref = -stack_pos - 1
                print("Referencing {} with {} args".format(arg_ref, subs[sub.name].num_args))
                if arg_ref < subs[sub.name].num_args:
                    reference = NSSArgumentAccess("arg" + str(-stack_pos - 1))
                    # TODO: Find the actual type
                    reference_type = ObjectType.INT
                else:
                    global_name, global_type = global_data.from_offset(command.a + 4 * subs[sub.name].num_args)
                    reference = NSSGlobal(global_name)
                    reference_type = global_type

                    print("Name: {}; Type: {}".format(global_name, global_type))
            else:
                value = matrix.value_from_offset(i, command.a)
                if type(value) is NSSSSAction:
                    # Technically, the NSSSAction is not really "pushed" onto the stack;
                    # we just are overloading the use of the stack so we can push an "Action"
                    # onto the stack rather than executing it like normal
                    reference = matrix.value_from_offset(i, command.a - 4)
                    reference_type = matrix.types[i, stack_pos]
                elif type(value) is NSSReference:
                    reference = value
                    reference_type = matrix.types[i, stack_pos]
                else:
                    reference = NSSReference(matrix.var_names[i, stack_pos])
                    reference_type = matrix.types[i, stack_pos]

                matrix.set_local(i, stack_pos)

            matrix.propagate(reference, reference_type, i, matrix.top_of_stack(i))
            matrix.modify_sp(i, ObjectType.size(reference_type))

        elif type(command) is asm.CPDownSP:
            # Copy the given number of bytes from the top of the stack down to the location specified.
            # The value of SP remains unchanged.
            # print("CPDownSP from {} to {}".format(new_stack_state.sp))
            value = matrix.value_from_offset(i, -4)
            value_type = matrix.type_from_offset(i, -4)
            if "active" in dir(value):
                value.active = False
                value = copy_obj(value)
                value.active = True

            stack_pos = matrix.sp_offset_to_pos(i, command.a)
            # print("Copying {} to {}".format(value, stack_pos))

            matrix.propagate(value, value_type, i, stack_pos)
            matrix.set_local(i, stack_pos)

            return_val = NSSAssign(matrix.var_names[i, matrix.sp_offset_to_pos(i, command.a)], matrix.value_from_offset(i, command.a))

        # Base pointer changes
        elif type(command) is asm.CPTopBP:
            # Add the given number of bytes from the location specified in the stack to the top of the stack.
            # The value of SP is increased by the number of copied bytes.

            # We are getting a global variable's value
            # global_type, global_name = subs["global"].get_global(command.a)
            global_name, global_type = global_data.from_offset(command.a)

            reference = NSSGlobal(global_name)
            reference_type = global_type

            matrix.propagate(reference, reference_type, i, matrix.top_of_stack(i))
            matrix.modify_sp(i, ObjectType.size(reference_type))

        elif type(command) is asm.CPDownBP:
            # Copy the given number of bytes from the base pointer down to the location specified.
            # This instruction is used to assign new values to global variables.
            # The value of SP remains unchanged.

            dest = command.a
            num_items = command.b // 4

            if num_items == 3:
                # This is a vector
                raise Exception("Vector BP operations not yet implmemented")
            elif num_items == 1:
                copy_from = matrix.value_from_offset(i, -4)
            else:
                raise Exception("Trying to copy {} bytes with CPDownBP".format(command.b))

            global_name, global_type = global_data.from_offset(dest)

            reference = NSSGlobal(global_name)

            return_val = NSSAssign(reference, copy_from)
            # pass
            # raise NotImplementedError("BP operations not yet implemented")
            # Copy the given number of bytes from the base pointer down to the location specified. This instruction is used to assign new values to global variables.
            # The value of SP remains unchanged.
            # value = new_stack_state[new_stack_state.sp].value
            #
            # new_stack_state[(new_stack_state.bp + command.a)].value = value
            # new_stack_state.set_local((new_stack_state.bp + command.a))
            #
            # return_val = NSSAssign(new_stack_state[(new_stack_state.bp + command.a)])

        # Unary stack operations
        elif type(command) is asm.UnaryOp:
            pos = matrix.sp_offset_to_pos(i, -4)
            value = matrix.value_from_offset(i, -4)
            value_type = matrix.type_from_offset(i, -4)
            if "active" in dir(value):
                value.active = False
                value = copy_obj(value)
                value.active = True

            matrix.propagate(UnaryOperation(value, asm_to_nss(command.op_type)), value_type, i, pos)

        # Logical stack operations
        elif type(command) is asm.Logical:
            pos = matrix.sp_offset_to_pos(i, -8)
            arg2 = matrix.value_from_offset(i, -4)
            arg1 = matrix.value_from_offset(i, -8)

            if "active" in dir(arg2):
                arg2.active = False
                arg2 = copy_obj(arg2)
                arg2.active = True
            if "active" in dir(arg1):
                arg1.active = False
                arg1 = copy_obj(arg1)
                arg1.active = True

            value_type = matrix.type_from_offset(i, -4)

            matrix.propagate(LogicalOperation(arg1, asm_to_nss(command.op_type), arg2), value_type, i, pos)
            matrix.modify_sp(i, -1)

        # Binary stack operations
        elif type(command) is asm.BinaryOp:
            pos = matrix.sp_offset_to_pos(i, -8)
            arg2 = matrix.value_from_offset(i, -4)
            arg1 = matrix.value_from_offset(i, -8)

            popped_size = ObjectType.size(matrix.type_from_offset(i, -4)) + ObjectType.size(matrix.type_from_offset(i, -8))

            if "active" in dir(arg2):
                arg2.active = False
                arg2 = copy_obj(arg2)
                arg2.active = True

            if "active" in dir(arg1):
                arg1.active = False
                arg1 = copy_obj(arg1)
                arg1.active = True

            if {matrix.type_from_offset(i, -4), matrix.type_from_offset(i, -8)} == {ObjectType.VECTOR, ObjectType.FLOAT}:
                value_type = ObjectType.VECTOR
                # value_type = ObjectType.FLOAT
            else:
                value_type = matrix.type_from_offset(i, -4)

            matrix.propagate(BinaryOperation(arg1, asm_to_nss(command.op_type), arg2), value_type, i, pos)
            pushed_size = ObjectType.size(value_type)
            matrix.modify_sp(i, -1 * popped_size + pushed_size)

        elif type(command) is asm.MoveSP:
            matrix.modify_sp(i, command.x // 4)

        elif type(command) is asm.Destruct:
            destruct_size = command.a
            save_start = command.b
            save_length = command.c

            saved_items = []

            while save_length > 0:
                offset = (save_start - save_length) - 4
                # print("Saving item from offset {}".format(offset))
                saved_items.append(
                    (matrix.value_from_offset(i, offset), matrix.type_from_offset(i, offset))
                )
                save_length -= 4

            # print("Saved {} item(s): {}".format(len(saved_items), saved_items))
            #
            # print("Taking {} items off stack".format(destruct_size // 4))

            matrix.modify_sp(i, -destruct_size // 4)

            # print("Putting {} items on stack".format(len(saved_items)))

            while len(saved_items) > 0:
                item, item_type = saved_items.pop()
                pos = matrix.top_of_stack(i)
                matrix.propagate(item, item_type, i, pos)
                matrix.modify_sp(i, 1)

            # print("Destruct on line {}".format(i))
            # with open("output.html", "w") as f:
            #     f.write(matrix.html())
            # exit()

        elif type(command) is asm.StackOp:
            # These just increment/decrement variables relative
            # to either the stack of base pointer.
            # sp_val = new_stack_state.sp_offset_to_pos(command.value)
            # bp_val = new_stack_state.bp + command.value

            if command.op_type == "DECSPI":
                # Decrease a variable relative to the stack pointer
                pos = matrix.sp_offset_to_pos(i, command.value)
                var_type = matrix.type_from_offset(i, command.value)
                # value = matrix.value_from_offset(i, command.value)
                var = matrix.var_names[i, pos]

                op = UnaryOperation(var, "--")

                matrix.propagate(op, var_type, i, pos)

                return_val = op

                # return_val = NSSAssign(matrix.var_names[i, matrix.sp_offset_to_pos(i, command.value)], value)

            elif command.op_type == "INCSPI":
                pos = matrix.sp_offset_to_pos(i, command.value)
                var_type = matrix.type_from_offset(i, command.value)
                # value = matrix.value_from_offset(i, command.value)
                var = matrix.var_names[i, pos]

                op = UnaryOperation(var, "++")

                matrix.propagate(op, var_type, i, pos)
                return_val = op

            elif command.op_type == "DECBPI":
                # Decrease a variable relative to the stack pointer
                global_name, global_type = global_data.from_offset(command.value)
                global_ref = NSSGlobal(global_name)

                return_val = UnaryOperation(global_ref, "--")

            elif command.op_type == "INCBPI":
                global_name, global_type = global_data.from_offset(command.value)
                global_ref = NSSGlobal(global_name)

                return_val = UnaryOperation(global_ref, "++")


        elif type(command) is asm.JumpSubroutine:
            sub_name = command.line.replace("_", "")
            assert sub_name in subs, "Could not find subroutine {}".format(sub_name)

            called_sub = subs[sub_name]
            modifier = called_sub.num_args

            print("Sub {} has {} args".format(sub_name, called_sub.num_args))
            # exit()

            args = []
            arg_types = []
            for pops in range(modifier):
                args.append(matrix.value_from_offset(i, -4))
                arg_types.append(matrix.type_from_offset(i, -4))
                matrix.modify_sp(i, -1)

            called_sub.arg_types = arg_types

            return_val = NSSSubCall(sub_name, args)

        elif type(command) is asm.SSJumpSubroutine:
            sub_name = command.line.replace("_", "")
            assert sub_name in subs, "Could not find subroutine {}".format(sub_name)

            called_sub = subs[sub_name]
            modifier = called_sub.num_args

            print("Sub {} has {} args".format(sub_name, called_sub.num_args))
            # exit()

            args = []
            arg_types = []
            for pops in range(modifier):
                args.append(matrix.value_from_offset(i, -4))
                arg_types.append(matrix.type_from_offset(i, -4))
                matrix.modify_sp(i, -1)

            called_sub.arg_types = arg_types

            return_val = NSSSubCall(sub_name, args)
            matrix.propagate(return_val, None, i, matrix.top_of_stack(i))
            matrix.modify_sp(i, 1)


        elif type(command) is asm.ConditionalJump:
            value = matrix.value_from_offset(i, -4)
            if "active" in dir(value):
                value.active = False
                value = copy_obj(value)
                value.active = True

            command.conditional = value
            # print("Conditional jump has condition {} is not zero".format(command.conditional))
            matrix.modify_sp(i, -1)
            return_val = command

        elif type(command) is asm.Action:
            func = NWSCRIPT.functions[command.label]
            modifier = len(func.func_args)

            args = []

            for pops in range(modifier):
                arg = matrix.value_from_offset(i, -4)
                arg_type = matrix.type_from_offset(i, -4)
                if "active" in dir(arg):
                    arg.active = False
                    arg = copy_obj(arg)
                    arg.active = True

                if arg_type is ObjectType.VECTOR:
                    if type(arg) is NSSReference:
                        # We're already passing a variable through, so just leave it be
                        pass
                    else:
                        # We're passing an inline-defined vector
                        arg = arg.variable
                    matrix.modify_sp(i, -3)
                else:
                    matrix.modify_sp(i, -1)

                args.append(arg)

            return_val = NSSAction(func.func_name, args)
            # Pop arguments from the stack
            if func.func_type != "void":
                # Push the return value to the stack
                if func.func_type == "vector":
                    vector = NSSVector(return_val)
                    return_val = None

                    matrix.propagate(vector.ref("x"), ObjectType.INV_NAME_MAP[func.func_type], i, matrix.top_of_stack(i))
                    matrix.modify_sp(i, 1)
                    matrix.propagate(vector.ref("y"), ObjectType.INV_NAME_MAP[func.func_type], i, matrix.top_of_stack(i))
                    matrix.modify_sp(i, 1)
                    matrix.propagate(vector.ref("z"), ObjectType.INV_NAME_MAP[func.func_type], i, matrix.top_of_stack(i))
                    matrix.modify_sp(i, 1)

                    # print("Vector function on line {}".format(i))
                    # with open("output.html", "w") as f:
                    #     f.write(matrix.html())
                    # exit()
                else:
                    matrix.propagate(return_val, ObjectType.INV_NAME_MAP[func.func_type], i, matrix.top_of_stack(i))
                    matrix.modify_sp(i, 1)

        elif type(command) is asm.SSAction:
            func = NWSCRIPT.functions[command.label]
            modifier = len(func.func_args)

            args = []

            for pops in range(modifier):
                arg = matrix.value_from_offset(i, -4)
                arg_type = matrix.type_from_offset(i, -4)
                if "active" in dir(arg):
                    arg.active = False
                    arg = copy_obj(arg)
                    arg.active = True

                if arg_type is ObjectType.VECTOR:
                    if type(arg) is NSSReference:
                        # We're already passing a variable through, so just leave it be
                        pass
                    else:
                        # We're passing an inline-defined vector
                        arg = arg.variable
                    matrix.modify_sp(i, -3)
                else:
                    matrix.modify_sp(i, -1)

                args.append(arg)

            # Pop arguments from the stack
            return_val = NSSSSAction(func.func_name, args)

            # Push the SSAction to the stack
            matrix.propagate(return_val, None, i, matrix.top_of_stack(i))
            matrix.modify_sp(i, 1)

        elif type(command) is asm.NoOp:
            return_val = None

        # Some other operation that doesn't affect the stack
        else:
            return_val = command

        blocks.append(return_val)

    return blocks, matrix


def reduce_idioms(blocks):
    changed = True

    while changed:
        changed = False
        for idiom_cls in idioms.IDIOMS:
            idiom = idioms.IDIOMS[idiom_cls]()
            i = 0
            while i < len(blocks):
                if idiom.recognize(i, blocks):
                    changed = True

                    conversion = idiom.convert(i, blocks)
                    for convert_idx in conversion:
                        blocks[convert_idx] = conversion[convert_idx]
                i += 1

    return blocks


if __name__ == "__main__":
    main()
