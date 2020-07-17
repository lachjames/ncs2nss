from data_flow_types import Variable, BinaryOperation, UnaryOperation, LogicalOperation, NSSGlobal, NSSArgumentAccess, NSSAssign, NSSCreateLocal, NSSAction, \
    NSSSSAction, \
    NSSReference, \
    NSSSubCall, NSSVector, NSSReturnValue, VectorDefinition, VectorView

import control_flow
import assembly as asm
from data_structures.stack import StackMatrix

import copy
import idioms
from nwscript import NWScript

from colorama import init, Fore

from data_flow_analysis import DFA_CONVERSIONS

init()

NWSCRIPT = NWScript.load()

import pickle


def copy_obj(obj):
    return pickle.loads(pickle.dumps(obj))


def main():
    pass


# m = StackMatrix(num_commands=10, stack_size=5)
# print(m)


def df_analysis(subroutine, subroutines, global_data, n_pass):
    blocks, matrix, return_tails = analyze_blocks(subroutine, subroutines, global_data, n_pass)
    # print(matrix)
    # with open("html/{}.html".format(subroutine.name), "w") as f:
    #     f.write(matrix.html())

    # print(matrix.var_names)
    # print(matrix.types)

    # print()
    # print("Blocks:")
    # for block in blocks:
    #     print(block)
    # print()

    # Replace all inactive blocks with None
    for i in range(len(blocks)):
        if "active" in dir(blocks[i]) and not blocks[i].active:
            blocks[i] = None
    assignment_dict = matrix.match_assignments(subroutine, subroutines, global_data)

    for var_name in assignment_dict:
        var_type, declared_pos = assignment_dict[var_name]

        blocks[declared_pos] = NSSCreateLocal(var_type, var_name, blocks[declared_pos])

    reduce_idioms(blocks)

    return blocks, matrix, return_tails


def num_args(sub):
    if len(sub.commands) == 1:
        return 0, True
    elif len(sub.commands) == 2:
        if type(sub.commands[-2]) is not asm.MoveSP:
            return 0, True
        return -sub.commands[-2].x // 4, False

    x = 0
    for i in (-1, -2, -3):
        if -i > len(sub.commands):
            break

        if type(sub.commands[i]) is asm.MoveSP:
            x = i
            break
        else:
            print("Skipping {}".format(sub.commands[i]))

    if x == 0:
        return 0, True

    if type(sub.commands[x - 1]) is asm.MoveSP:
        return -sub.commands[x].x // 4, True

    if type(sub.commands[x - 1]) is asm.JumpSubroutine:
        # TODO: Find a better solution for this
        print("Ambiguous whether this is from the JSR or from popping the arguments")
        return 0, False

    # Either the sub defines no local variables, or it has no arguments
    # Local variables are assigned when cpdownsp is used, so check for that
    for command in sub.commands:
        if type(command) is asm.CPDownSP:
            # Sub has local variables so it has no args
            return 0, True

    return -sub.commands[x].x // 4, True


def has_return(sub, num_args):
    cmd_to_sp = trace_sp(sub)
    for cmd in sub.commands:
        if cmd not in cmd_to_sp:
            # Unreachable code
            continue

        if type(cmd) is asm.CPDownSP:
            # Check whether we are
            dest = cmd_to_sp[cmd] + (cmd.a // 4)
            print("sp={}, offset={}, pos={}".format(cmd_to_sp[cmd], cmd.a, dest))
            if dest < -num_args:
                print("{}: {}".format(cmd, cmd_to_sp[cmd]))
                return True

    return False


def trace_sp(sub):
    cfa = control_flow.ControlFlowAnalysis(sub, {}, True)
    cfg = cfa.cfg

    sp = 0

    # Do a depth-first traversal of the cfg, analyzing each block as we go
    done = set()
    stack = [(cfg.header, 0)]
    last_sp = 0
    last_addr = -1

    cmd_to_sp = {}

    while len(stack) > 0:
        stack.sort(key=lambda x: x[0].address)
        block, sp = stack.pop()

        if block in done:
            continue

        commands = sub.commands[block.address:block.address + block.length]
        block_cmd_to_sp = block_sp(commands, sp)
        cmd_to_sp.update(block_cmd_to_sp)

        new_sp = cmd_to_sp[commands[-1]]
        for succ in block.succs:
            stack.append((succ, new_sp))

        if block.address > last_addr:
            last_addr = block.address
            last_sp = new_sp

        done.add(block)

    # for command in sub.commands:
    #     if command in cmd_to_sp:
    #         print("{}: {}".format(command, cmd_to_sp[command]))
    #     else:
    #         # Unreachable code?
    #         print("{}: Unreachable".format(command))

    return cmd_to_sp


def block_sp(commands, sp):
    cmd_to_sp = {}
    for cmd in commands:
        # Commands which increase the sp by 1
        if type(cmd) in (asm.RSAdd, asm.Const, asm.CPTopSP, asm.CPTopBP, asm.Logical):
            sp += 1
        elif type(cmd) in (asm.BinaryOp, asm.ConditionalJump):
            # TODO: Check for binary ops on vectors
            sp -= 1
        # Commands which increase the sp by 12
        elif type(cmd) is VectorDefinition:
            sp += 3
        # Commands which decrease the sp by 1
        elif type(cmd) is asm.MoveSP:
            sp += cmd.x // 4
        elif type(cmd) is asm.Action:
            # ACTION pushes return values to the stack, but JSR doesnt
            func = NWSCRIPT.functions[cmd.label]
            sp -= len(func.func_args)
            if func.func_type != "void":
                sp += 1
        elif type(cmd) is asm.Destruct:
            sp -= cmd.a // 4
            sp += cmd.c // 4
        # elif type(cmd) is
        cmd_to_sp[cmd] = sp
    return cmd_to_sp


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

    DEFAULT_MAP = {
        INT: 0,
        FLOAT: 0.0,
        STRING: ""
    }

    @staticmethod
    def size(obj_type):
        if obj_type is ObjectType.VECTOR:
            return 3
        return 1


def analyze_blocks(sub, subs, global_data, n_pass):
    if sub.name == "main":
        with open("html/running.html", "w") as f:
            pass

    cfa = control_flow.ControlFlowAnalysis(sub, {}, True)
    cfg = cfa.cfg

    last_block = cfa.cfg.last_block()

    matrix = StackMatrix(len(sub.commands), len(sub.commands), sub)

    blocks = [None] * len(sub.commands)

    return_tails = {}

    # Do a depth-first traversal of the cfg, analyzing each block as we go
    done = set()
    stack = [(cfg.header, None, None)]
    while len(stack) > 0:
        block, last_frame, sp = stack.pop()
        if type(block) is tuple:
            block, prev_block = block
        else:
            prev_block = None

        if block is not last_block and block in done:
            continue

        if last_frame is not None:
            matrix.matrix.set_frame(block.address, last_frame)
            matrix.sps[block.address] = sp

        try:
            new_blocks = analyze_block(block, sub, subs, global_data, matrix, last_block, n_pass)
        except Exception as e:
            print("Error in block {}".format(block))
            with open("html/dump.html", "w") as f:
                f.write(matrix.html())
            raise e

        assert len(new_blocks) == block.length, "Invalid number of blocks found"

        if prev_block is not None:
            return_tails[prev_block.address] = new_blocks

        blocks[block.address:block.address + block.length] = new_blocks

        last_frame = copy.deepcopy(matrix.matrix.get_frame(block.address + block.length - 1))
        for succ in block.succs:
            if "points_to_return" in block.params:
                stack.append(
                    ((succ, block), last_frame, matrix.sps[block.address + block.length - 1])
                )
            else:
                stack.append(
                    (succ, last_frame, matrix.sps[block.address + block.length - 1])
                )

        done.add(block)

        # if sub.name == "main":
        #     with open("html/running.html", "a") as f:
        #         f.write("<h3 style=\"color:White\">{}</h3>".format(block))
        #         f.write(matrix.html())

    return blocks, matrix, return_tails


def analyze_block(block, sub, subs, global_data, matrix, last_block, n_pass):
    blocks = []
    commands = sub.commands[block.address:block.address + block.length]

    for i_raw, command in enumerate(commands):
        i = block.address + i_raw

        if type(command) in DFA_CONVERSIONS:
            val = DFA_CONVERSIONS[type(command)](
                i, command, sub, subs, global_data, matrix, n_pass
            )
        else:
            val = command

        blocks.append(val)

    return blocks


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
