import assembly as asm
import data_flow as df
import control_flow as cf
import control_analysis as ca
from data_flow_types import BinaryOperation

NSS_TYPES = {
    0: "int"
}

INDENT = "    "


def get_loop_data(bb, cfa, code):
    if "loop" in bb.params:
        return bb.params["loop"]
    return None

    # for ds in cfa.steps:
    #     # Peel back the layers to find the header node
    #     for interval in ds.blocks:
    #         if type(interval) is not ca.Interval or not interval.loop:
    #             continue
    #
    #         x = interval
    #         while type(x) is ca.Interval:
    #             x = x.header
    #
    #         print("Header: ", x)
    #         print("BB: ", bb)
    #         if bb is x.nodes[0]:
    #             print("Found it!")
    #             return interval.loop
    # return False


def is_loop_header(bb, cfa, code):
    return get_loop_data(bb, cfa, code) is not None


def get_if_data(bb, cfa, code):
    if "if" in bb.params:
        return bb.params["if"]
    return None


def is_2_way(bb, cfa, code):
    return get_if_data(bb, cfa, code) is not None


def is_n_way(bb, cfa, code):
    return "case_nodes" in bb.params


def write_bb(bb, i, cfa, code):
    bb.traversed = True
    # if "last_block" in bb.params:
    #     return
    for line in cfa.sub.commands[bb.address:bb.address + bb.length]:

        if line is None:
            continue
        if type(line) in (asm.Jump, asm.ConditionalJump):
            # This should be taken care of by control flow
            continue
        if type(line) is asm.Return:
            code.append(INDENT * i + "return;\n")
            continue

        if str(line) == "":
            continue

        if type(line) is list:
            for x in line:
                code.append(INDENT * i + str(x) + ";" + "\n")
            continue

        code.append(INDENT * i + str(line) + ";" + "\n")

        if "continue" in bb.params and bb.params["break"]:
            code.append(INDENT * i + "continue;\n")
        elif "break" in bb.params and bb.params["break"]:
            code.append(INDENT * i + "break;\n")

    if "return_cmds" in bb.params and len(bb.succs) == 1:
        print("Block {} has return commands")
        for cmd in bb.params["return_cmds"]:
            if cmd is None:
                continue
            code.append(INDENT * i + str(cmd) + ";\n")


def write_loop(bb, i, loop_data, latch_node, if_follow, n_follow, cur_if, cur_loop, cfa, code):
    print("Writing loop {}".format(bb))
    print("Setting {} as traversed from loop".format(bb))
    bb.traversed = True

    loop_type = loop_data.loop_type()

    # Loop header
    if loop_type is ca.LoopType.PRETESTED:
        write_bb(bb, i, cfa, code)
        condition = cfa.sub.commands[bb.address + bb.length - 1].conditional
        code.append(INDENT * i + "while ({}) {{\n".format(str(condition)))
    elif loop_type is ca.LoopType.POSTTESTED:
        code.append(INDENT * i + "do {\n")
        # bb.traversed = False
        if "if" in bb.params:
            write_2_way(bb, i + 1, latch_node, if_follow, n_follow, cur_if, loop_data, cfa, code)
        else:
            write_bb(bb, i + 1, cfa, code)
    elif loop_type is ca.LoopType.ENDLESS:
        raise Exception("Endless loops not yet implemented")

    # Loop body
    # Check if we return from this basic block
    if type(cfa.sub.commands[bb.address + bb.length - 1]) is asm.Return:
        return

    if bb is latch_node:
        return

    print("Writing loop body")

    # If the header is not its own back node...
    if bb is not loop_data.back:
        # Write code for all successors of bb inside the loop
        for s in bb.succs:
            if s in loop_data.nodes or loop_type is not ca.LoopType.PRETESTED:
                print(loop_data.nodes)
                print(s)
                ## print("{} is inside the loop".format(s))
                # print("Traversing {}".format(s))
                # TODO: Check if this is a bug in the thesis?
                if not s.traversed:
                    write_code(s, i + 1, loop_data.back, if_follow, n_follow, cur_if, loop_data, cfa, code)
                # else:
                #     raise Exception("GOTO would be required but that's impossible")

    ## print("Finished writing loop body")
    # Loop trailer
    if loop_type is ca.LoopType.PRETESTED:
        code.append(INDENT * i + "}\n")
    elif loop_type is ca.LoopType.POSTTESTED:
        back_bb = list(loop_data.back.preds)[0]
        back_conditional = cfa.sub.commands[back_bb.address + back_bb.length - 1].conditional
        code.append(INDENT * i + "}} while ({});\n".format(back_conditional))
    elif loop_type is ca.LoopType.ENDLESS:
        pass
    else:
        raise Exception("Invalid loop type {} found".format(loop_type))

    follow_node = loop_data.follow
    if not follow_node.traversed:
        write_code(follow_node, i, latch_node, if_follow, n_follow, cur_if, cur_loop, cfa, code)

    ## print("Finished writing loop {}".format(bb))


def write_1_way(bb, i, latch_node, if_follow, n_follow, cur_if, cur_loop, cfa, code):
    bb.traversed = True

    ## print("Writing {}".format(bb))
    write_bb(bb, i, cfa, code)
    if len(bb.succs) == 0:
        # This is a return node
        return
    elif len(bb.succs) > 1:
        print("Warning: writing node {} with {} successors as 1-way node".format(bb, bb.succs))
        print("  (this is fine if it's a case node)")
        # raise Exception("Writing 1-way node {} with multiple successors!".format(bb))

    if "no_follow" in bb.params:
        return

    succ = list(bb.succs)[0]
    # assert not succ.traversed, "We would require a goto label if this were traversed"
    if not succ.traversed:
        write_code(succ, i, latch_node, if_follow, n_follow, cur_if, cur_loop, cfa, code)
    else:
        ## print("Expected {} to not be traversed yet".format(succ))
        pass


def write_2_way(bb, i, latch_node, if_follow, n_follow, cur_if, cur_loop, cfa, code):
    bb.traversed = True

    if_data = get_if_data(bb, cfa, code)

    # Check if we are an else if component of an if statement
    if cur_if is not None and cur_if.follow is if_data.follow:
        # This is an else if
        is_else_if = True
    else:
        is_else_if = False

    ## print("is_else_if: {}".format(is_else_if))

    # Write the start of the node
    write_bb(bb, i, cfa, code)

    condition = cfa.sub.commands[bb.address + bb.length - 1].conditional
    # TODO: This is awfully hacky
    if str(condition) == "unknown_var":
        for succ in bb.succs:
            write_code(succ, i, latch_node, if_follow, n_follow, cur_if, cur_loop, cfa, code)
        return

    code.append(INDENT * i + ("} else " if is_else_if else "") + "if ({}) {{\n".format(str(condition)))
    # code.append(INDENT * i + "{\n")

    ## print("Follow node for if statement at {} is {}".format(bb, if_data.follow))

    # The part inside the if statement will be the part which IS NOT
    # immediately after the condition, because in NCS all conditions are
    # jnz (which means that we jump when the condition is met)

    if_part, else_part = bb.compute_conditional(cfa)

    # if len(non_follow) == 1:
    write_code(if_part, i + 1, latch_node, if_data.follow, n_follow, if_data, cur_loop, cfa, code)
    if else_part is not None:
        # Check for any "else if" conditions
        print(is_2_way(else_part, cfa, code))
        print(get_if_data(else_part, cfa, code))
        print(if_data.follow)
        if is_2_way(else_part, cfa, code) and get_if_data(else_part, cfa, code).follow is if_data.follow:
            print("Detected else if!!")
            # code.append(INDENT * i + "}")
            write_code(else_part, i, latch_node, if_data.follow, n_follow, if_data, cur_loop, cfa, code)
            # code.append(INDENT * i + "}\n")
        else:
            # code.append(INDENT * i + "}\n")
            print("Else clause detected")
            code.append("\n" + INDENT * i + "} else {\n")
            write_code(else_part, i + 1, latch_node, if_data.follow, n_follow, if_data, cur_loop, cfa, code)
            code.append(INDENT * i + "}\n")
    else:
        code.append(INDENT * i + "}\n")

    # else:
    #     raise Exception("Invalid number of succs {} found".format(non_follow))

    write_code(if_data.follow, i, latch_node, if_follow, n_follow, cur_if, cur_loop, cfa, code)


def write_n_way(bb, i, latch_node, if_follow, n_follow, cur_if, cur_loop, cfa, code):
    write_bb(bb, i, cfa, code)

    condition = cfa.sub.commands[bb.address + bb.length - 1].conditional
    # assert type(condition) is BinaryOperation, "{} should be a binary operation".format(condition)
    if type(condition) is not BinaryOperation:
        var = "unknown_var"
        print("Warning: {} should be of type BinaryOperation".format(condition))
    else:
        var = condition.a
    code.append(INDENT * i + "switch ({}) {{\n".format(var))

    case_nodes = bb.params["case_nodes"]
    for k, (case_node, on_true) in enumerate(case_nodes):
        condition = cfa.sub.commands[case_node.address + case_node.length - 1].conditional
        if type(condition) is not BinaryOperation:
            value = "unknown"
            print("Warning: {} should be of type BinaryOperation".format(condition))
        else:
            value = condition.b
        code.append(INDENT * i + "case {}:\n".format(value))
        if k < len(case_nodes) - 1 and on_true is case_nodes[k + 1][1]:
            # Case falls through
            pass
        else:
            write_code(on_true, i + 1, latch_node, if_follow, bb.params["switch_follow"], cur_if, cur_loop, cfa, code)
            # code.append(INDENT * (i + 1) + "break;\n")
    # Write the default case if it exists
    if bb.params["default_case"] is not None:
        code.append(INDENT * i + "default:\n")
        write_code(bb.params["default_case"], i + 1, latch_node, if_follow, bb.params["switch_follow"], cur_if, cur_loop, cfa, code)

    code.append(INDENT * i + "}\n")
    write_code(bb.params["switch_follow"], i, latch_node, if_follow, n_follow, cur_if, cur_loop, cfa, code)


def write_code(bb, i, latch_node, if_follow, n_follow, cur_if, cur_loop, cfa, code):
    if code is None:
        code = []

    if bb in (if_follow, n_follow):
        print("bb is a follow")
        return

    if bb.traversed:
        return

    bb.traversed = True
    # print("Setting {} as traversed from write_code".format(bb))

    if is_loop_header(bb, cfa, code) and get_loop_data(bb, cfa, code) is not cur_loop:
        print("Writing loop {}".format(bb))
        loop_data = get_loop_data(bb, cfa, code)
        write_loop(bb, i, loop_data, latch_node, if_follow, n_follow, cur_if, cur_loop, cfa, code)
    elif is_n_way(bb, cfa, code):
        # raise Exception("Switch statements not currently supported")
        write_n_way(bb, i, latch_node, if_follow, n_follow, cur_if, cur_loop, cfa, code)
    elif is_2_way(bb, cfa, code):
        print("Writing if {}".format(bb))
        write_2_way(bb, i, latch_node, if_follow, n_follow, cur_if, cur_loop, cfa, code)
    else:
        print("Writing 1-way {}".format(bb))
        write_1_way(bb, i, latch_node, if_follow, n_follow, cur_if, cur_loop, cfa, code)

    return code


# Takes a control flow analysis as input
def to_nss(cfa):
    name = cfa.sub.name
    retn_type = "void"
    args = "..."

    code = "{} {} ({})".format(retn_type, name, args)

    # The code should be contained in the header of the last item
    # in the derived sequence
    code += "{\n"

    code_lines = ["    " + line for line in cfa.steps[-1].header.to_nss(cfa.sub).split("\n")]

    code += "\n".join(code_lines) + "\n"

    code += "}"

    return code

# def backend(commands):
#     code = "void main () {\n"
#
#     indent = 1
#     for command in commands:
#         if command is None:
#             continue
#
#         code += "    " * indent
#
#         if type(command) is asm.Return:
#             code += "return;\n"
#         elif type(command) is df.NSSCreateLocal:
#             code += "{} {};\n".format(NSS_TYPES[command.var_type], command.expression)
#         elif type(command) is df.NSSAssign:
#             code += "{} = {};\n".format(command.var_name, command.expression)
#         else:
#             print("Could not convert {}".format(command))
#
#     code += "}"
#
#     return code
