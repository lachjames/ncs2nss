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


def df_analysis(subroutine, subroutines, global_data):
    blocks, matrix = analyze_blocks(subroutine, subroutines, global_data)
    # print(matrix)
    with open("html/{}.html".format(subroutine.name), "w") as f:
        f.write(matrix.html())

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


def analyze_blocks(sub, subs, global_data):
    if sub.name == "main":
        with open("html/running.html", "w") as f:
            pass

    cfa = control_flow.ControlFlowAnalysis(sub, True)
    cfg = cfa.cfg

    matrix = StackMatrix(len(sub.commands), len(sub.commands), sub)

    blocks = [None] * len(sub.commands)

    # Do a depth-first traversal of the cfg, analyzing each block as we go
    done = set()
    stack = [(cfg.header, None, None)]
    while len(stack) > 0:
        block, last_frame, sp = stack.pop()

        if block in done:
            continue

        if last_frame is not None:
            matrix.matrix.set_frame(block.address, last_frame)
            matrix.sps[block.address] = sp

        try:
            new_blocks = analyze_block(block, sub, subs, global_data, matrix)
        except Exception as e:
            print("Error in block {}".format(block))
            with open("html/dump.html", "w") as f:
                f.write(matrix.html())
            raise e

        blocks[block.address:block.address + block.length] = new_blocks

        last_frame = copy.deepcopy(matrix.matrix.get_frame(block.address + block.length - 1))
        for succ in block.succs:
            stack.append(
                (succ, last_frame, matrix.sps[block.address + block.length - 1])
            )

        done.add(block)

        if sub.name == "main":
            with open("html/running.html", "a") as f:
                f.write("<h3 style=\"color:White\">{}</h3>".format(block))
                f.write(matrix.html())

    return blocks, matrix


def analyze_block(block, sub, subs, global_data, matrix):
    blocks = []
    commands = sub.commands[block.address:block.address + block.length]
    for i_raw, command in enumerate(commands):
        i = block.address + i_raw

        if type(command) in DFA_CONVERSIONS:
            val = DFA_CONVERSIONS[type(command)](
                i, command, sub, subs, global_data, matrix
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
