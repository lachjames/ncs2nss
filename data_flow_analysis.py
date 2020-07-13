import copy

import ncs2nss
from data_flow_types import ObjectType, NSSVector, VectorDefinition, VectorComponent, VectorAssign, VectorAssignment, GetVector, GetVectorElement, VectorValue, \
    VectorVariable, VectorView, NSSVectorConstant, VectorIndex
from data_flow_types import Variable, BinaryOperation, UnaryOperation, LogicalOperation, NSSAssign, NSSCreateLocal, NSSAction, NSSReference, NSSSubCall, \
    NSSSSAction, NSSReturnValue, NSSGlobal, NSSArgumentAccess

import assembly as asm
import pickle
from nwscript import NWScript

NWSCRIPT = NWScript.load()

DFA_CONVERSIONS = {}


def register_dfa(name):
    def decorator_fn(f):
        DFA_CONVERSIONS[name] = f
        return f

    return decorator_fn


def copy_obj(obj):
    return pickle.loads(pickle.dumps(obj))


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


@register_dfa(asm.RSAdd)
def convert_rsadd(i, command, sub, subs, global_data, matrix):
    # Reserve space on the stack
    var_type = ObjectType.MAP[command.op_type[-1].lower()]
    if var_type in ObjectType.DEFAULT_MAP:
        var_obj = Variable(var_type, ObjectType.DEFAULT_MAP[var_type], is_set=False)
    else:
        var_obj = Variable(var_type, None, is_set=False)

    matrix.push(var_obj, var_type, i)

    return None


@register_dfa(asm.Const)
def convert_const(i, command, sub, subs, global_data, matrix):
    const_type = ObjectType.MAP[command.const_type[-1].lower()]
    value = command.value
    const_obj = Variable(const_type, value)

    matrix.push(const_obj, const_type, i)

    return None


@register_dfa(asm.CPTopSP)
def convert_cptopsp(i, command, sub, subs, global_data, matrix):
    # Add the given number of bytes from the location specified in the stack to the top of the stack.
    # The value of SP is increased by the number of copied bytes.

    # We check if this is actually on the stack to begin with
    stack_pos = matrix.sp_offset_to_pos(i, command.a)

    if stack_pos < 0:
        # We are copying either an argument or a global
        arg_ref = -stack_pos - 1
        # print("Referencing {} with {} args".format(arg_ref, subs[sub.name].num_args))
        if arg_ref < subs[sub.name].num_args:
            reference = NSSArgumentAccess("arg" + str(-stack_pos - 1))
            # TODO: Find the actual type
            reference_type = ObjectType.INT
        else:
            global_name, global_type = global_data.from_offset(command.a + 4 * subs[sub.name].num_args)
            reference = NSSGlobal(global_name)
            reference_type = global_type

            # print("Name: {}; Type: {}".format(global_name, global_type))
    else:
        value = matrix.get_value(i, command.a)

        # TODO: Do this in StackMatrix, not here (as other DFA analysis functions need this too)
        if type(value) is NSSSSAction:
            # Technically, the NSSSAction is not really "pushed" onto the stack;
            # we just are overloading the use of the stack so we can push an "Action"
            # onto the stack rather than executing it like normal
            reference = matrix.get_value(i, command.a - 4)
            reference_type = matrix.types[i, stack_pos]

        elif type(value) is NSSSubCall:
            reference = value
            reference_type = matrix.types[i, stack_pos]

        elif type(value) in (NSSReference, NSSArgumentAccess, NSSGlobal):
            reference = value
            reference_type = matrix.types[i, stack_pos]

        elif type(value) is Variable and not value.is_set:
            # assert value.value is not None, "Don't know default value of type {}".format(value.var_type)
            reference = value
            reference_type = matrix.types[i, stack_pos]

        else:
            reference = NSSReference(matrix.var_names[i, stack_pos])
            reference_type = matrix.types[i, stack_pos]

        # matrix.set_local(i, stack_pos)

    matrix.push(reference, reference_type, i)


@register_dfa(asm.CPDownSP)
def convert_cpdownsp(i, command, sub, subs, global_data, matrix):
    # Copy the given number of bytes from the top of the stack down to the location specified.
    # The value of SP remains unchanged.
    # print("CPDownSP from {} to {}".format(new_stack_state.sp))
    stack_pos = matrix.sp_offset_to_pos(i, command.a)
    if stack_pos < 0:
        # TODO: Make this work with changing arg values inside a function...
        #       does NWScript even allow that? Idk
        # For now, we assume that it's the return value
        if "active" in dir(matrix.get_value(i, -4)):
            matrix.get_value(i, -4).active = False
            value = copy.deepcopy(matrix.get_value(i, -4))
            value.active = True

            matrix.return_value = value
        else:
            matrix.return_value = matrix.get_value(i, -4)

        return None
    matrix.set_local(i, command.a)

    value = matrix.get_value(i, -4)
    value_type = matrix.get_type(i, -4)
    if "active" in dir(value):
        value.active = False
        value = copy_obj(value)
        value.active = True

    matrix.propagate(value, value_type, i, command.a)

    return_val = NSSAssign(matrix.var_names[i, matrix.sp_offset_to_pos(i, command.a)], matrix.get_value(i, command.a))
    return return_val


@register_dfa(asm.CPTopBP)
def convert_cptopbp(i, command, sub, subs, global_data, matrix):
    # Add the given number of bytes from the location specified in the stack to the top of the stack.
    # The value of SP is increased by the number of copied bytes.

    # We are getting a global variable's value
    # global_type, global_name = subs["global"].get_global(command.a)
    global_name, global_type = global_data.from_offset(command.a)

    reference = NSSGlobal(global_name)
    reference_type = global_type

    matrix.push(reference, reference_type, i)


@register_dfa(asm.CPDownBP)
def convert_cpdownbp(i, command, sub, subs, global_data, matrix):
    # Copy the given number of bytes from the base pointer down to the location specified.
    # This instruction is used to assign new values to global variables.
    # The value of SP remains unchanged.

    dest = command.a
    num_items = command.b // 4

    if num_items == 3:
        # This is a vector
        raise Exception("Vector BP operations not yet implmemented")
    elif num_items == 1:
        copy_from = matrix.get_value(i, -4)
    else:
        raise Exception("Trying to copy {} bytes with CPDownBP".format(command.b))

    global_name, global_type = global_data.from_offset(dest)

    reference = NSSGlobal(global_name)

    return_val = NSSAssign(reference, copy_from)
    return return_val


@register_dfa(asm.UnaryOp)
def convert_unaryop(i, command, sub, subs, global_data, matrix):
    value_type = matrix.get_type(i, -4)
    value = matrix.pop(i)
    if "active" in dir(value):
        value.active = False
        value = copy_obj(value)
        value.active = True

    matrix.push(UnaryOperation(value, asm_to_nss(command.op_type)), value_type, i)


@register_dfa(asm.Logical)
def convert_logical(i, command, sub, subs, global_data, matrix):
    value_type = matrix.get_type(i, -4)

    arg2 = matrix.pop(i)
    arg1 = matrix.pop(i)

    if "active" in dir(arg2):
        arg2.active = False
        arg2 = copy_obj(arg2)
        arg2.active = True
    if "active" in dir(arg1):
        arg1.active = False
        arg1 = copy_obj(arg1)
        arg1.active = True

    matrix.push(LogicalOperation(arg1, asm_to_nss(command.op_type), arg2), value_type, i)


@register_dfa(asm.BinaryOp)
def convert_binary(i, command, sub, subs, global_data, matrix):
    arg1_type = matrix.get_type(i, -4)

    if arg1_type is ObjectType.VECTOR:
        arg2_type = matrix.get_type(i, -16)
    else:
        arg2_type = matrix.get_type(i, -8)

    # print(matrix.sps[i])
    arg2 = matrix.pop(i)
    arg1 = matrix.pop(i)
    # print(matrix.sps[i])

    if "active" in dir(arg2):
        arg2.active = False
        arg2 = copy_obj(arg2)
        arg2.active = True
    if "active" in dir(arg1):
        arg1.active = False
        arg1 = copy_obj(arg1)
        arg1.active = True

    value = BinaryOperation(arg1, asm_to_nss(command.op_type), arg2)

    if arg1_type is ObjectType.VECTOR or arg2_type is ObjectType.VECTOR:
        matrix.push(value, ObjectType.VECTOR, i)
        matrix.push(value, ObjectType.VECTOR, i)
        matrix.push(value, ObjectType.VECTOR, i)
    else:
        matrix.push(value, arg1_type, i)


@register_dfa(asm.MoveSP)
def convert_movesp(i, command, sub, subs, global_data, matrix):
    matrix.modify_sp(i, command.x)


@register_dfa(asm.Destruct)
def convert_destruct(i, command, sub, subs, global_data, matrix):
    matrix.destruct(i, command.a, command.b, command.c)


@register_dfa(asm.StackOp)
def convert_stackop(i, command, sub, subs, global_data, matrix):
    # These just increment/decrement variables relative
    # to either the stack of base pointer.
    # sp_val = new_stack_state.sp_offset_to_pos(command.value)
    # bp_val = new_stack_state.bp + command.value

    if command.op_type == "DECSPI":
        # Decrease a variable relative to the stack pointer
        var_type = matrix.get_type(i, command.value)
        var = matrix.get_value(i, command.value)

        op = UnaryOperation(var, "--")

        matrix.propagate(op, var_type, i, command.value)

        return_val = op

        # return_val = NSSAssign(matrix.var_names[i, matrix.sp_offset_to_pos(i, command.value)], value)

    elif command.op_type == "INCSPI":
        var_type = matrix.get_type(i, command.value)
        var = matrix.get_value(i, command.value)

        op = UnaryOperation(var, "++")

        matrix.propagate(op, var_type, i, command.value)

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

    else:
        raise Exception("Invalid stack operation {} found".format(command.op_type))

    return return_val


@register_dfa(asm.ConditionalJump)
def convert_condjump(i, command, sub, subs, global_data, matrix):
    value = matrix.pop(i)
    if "active" in dir(value):
        value.active = False
        value = copy_obj(value)
        value.active = True

    command.conditional = value

    return_val = command
    return return_val


def pop_args(i, matrix, modifier):
    args = []
    for pops in range(modifier):
        arg_type = matrix.get_type(i, -4)
        arg = matrix.pop(i)

        if "active" in dir(arg):
            arg.active = False
            arg = copy_obj(arg)
            arg.active = True

        args.append(arg)
    return args


def jsr(command, i, matrix, subs, sub_name):
    assert sub_name in subs, "Could not find subroutine {}".format(sub_name)
    called_sub = subs[sub_name]
    modifier = called_sub.num_args
    # print("Calling sub {} with {} args and retn value {}".format(sub_name, modifier, called_sub.retn_type))

    args = pop_args(i, matrix, modifier)

    return_val = NSSSubCall(sub_name, args)

    return return_val


@register_dfa(asm.JumpSubroutine)
def convert_jsr(i, command, sub, subs, global_data, matrix):
    sub_name = command.line.replace("_", "")

    return_val = jsr(command, i, matrix, subs, sub_name)
    if subs[sub_name].retn_type == "void":
        # print("Not pushing void return to the stack")
        pass
    elif subs[sub_name].retn_type == "vector":
        matrix.propagate(return_val, ObjectType.INV_NAME_MAP[subs[sub_name].retn_type], i, -4)
        matrix.propagate(return_val, ObjectType.INV_NAME_MAP[subs[sub_name].retn_type], i, -8)
        matrix.propagate(return_val, ObjectType.INV_NAME_MAP[subs[sub_name].retn_type], i, -12)

        # raise Exception("Vector subprocesses are not currently implemented")
    else:
        matrix.propagate(return_val, ObjectType.INV_NAME_MAP[subs[sub_name].retn_type], i, -4)
        # matrix.modify_sp(i, 1)

    return return_val


@register_dfa(asm.SSJumpSubroutine)
def convert_ssjsr(i, command, sub, subs, global_data, matrix):
    sub_name = command.line.replace("_", "")

    return_val = jsr(command, i, matrix, subs, sub_name)

    matrix.push(return_val, None, i)

    return return_val


def action(i, command, matrix):
    func = NWSCRIPT.functions[command.label]
    modifier = len(func.func_args)

    args = pop_args(i, matrix, modifier)

    # args = list(reversed(args))
    return_val = NSSAction(func.func_name, args)
    return func, return_val


@register_dfa(asm.Action)
def convert_action(i, command, sub, subs, global_data, matrix):
    func, return_val = action(i, command, matrix)
    # Pop arguments from the stack
    if func.func_type != "void":
        # Push the return value to the stack
        if func.func_type == "vector":
            matrix.push(return_val, ObjectType.VECTOR, i)
            matrix.push(return_val, ObjectType.VECTOR, i)
            matrix.push(return_val, ObjectType.VECTOR, i)
        else:
            matrix.push(return_val, ObjectType.INV_NAME_MAP[func.func_type], i)

    # for stack_pos in range(len(matrix.fresh)):
    #     for cmd in range(len(matrix.fresh[0])):
    #         print(matrix.fresh[cmd][stack_pos], "\t", end="")
    #     print()
    return return_val


@register_dfa(asm.SSAction)
def convert_ssaction(i, command, sub, subs, global_data, matrix):
    func, return_val = action(i, command, matrix)

    # Push the SSAction to the stack
    matrix.push(return_val, None, i)

    return return_val


@register_dfa(asm.NoOp)
def convert_noop(i, command, sub, subs, global_data, matrix):
    return None


@register_dfa(asm.Return)
def convert_return(i, command, sub, subs, global_data, matrix):
    if subs[sub.name].retn_type != "void":
        return_val = NSSReturnValue(matrix.return_value)
    else:
        return_val = command

    return return_val


@register_dfa(VectorDefinition)
def define_vector(i, command, sub, subs, global_data, matrix):
    var_type = ObjectType.VECTOR
    var_obj = Variable(var_type, None, is_set=False)

    matrix.push(var_obj, var_type, i)
    matrix.push(var_obj, var_type, i)
    matrix.push(var_obj, var_type, i)

    return None


@register_dfa(VectorAssignment)
def assign_vector(i, command, sub, subs, global_data, matrix):
    # Find if we are assigning to the return value
    stack_pos = matrix.sp_offset_to_pos(i, command.cpdownsp.a)
    if stack_pos < 0:
        # TODO: Allow the reassigning of vector arguments? Not sure if that's even
        #       allowed in NWScript?
        # Returning a vector
        matrix.get_value(i, -4).active = False
        value = copy.deepcopy(matrix.get_value(i, -4))
        value.active = True
        matrix.return_value = NSSReference(value)
        return None

    matrix.set_local(i, command.cpdownsp.a)
    target_name = matrix.var_names[i, matrix.sp_offset_to_pos(i, command.cpdownsp.a)]

    # Find the vector at the top of the stack; this is either composed of three
    # constants, or a reference to another vector
    if matrix.get_type(i, -4) is ObjectType.VECTOR:
        # Vector at the top of the stack
        # Pop the vector off the stack
        # Get the name of the vector
        matrix.get_value(i, -4).active = False
        matrix.get_value(i, -8).active = False
        matrix.get_value(i, -12).active = False

        vector_name = NSSReference(matrix.get_value(i, -4))
        value = NSSReference(vector_name)

    elif matrix.get_type(i, -4) is ObjectType.FLOAT:
        # Float constants at the top of the stack
        z = matrix.get_value(i, -4)
        y = matrix.get_value(i, -8)
        x = matrix.get_value(i, -12)
        value = NSSVectorConstant(x, y, z)
    else:
        raise Exception("Invalid object type for vector assigning {} found".format(matrix.get_type(i, -4)))

    to_return = NSSAssign(target_name, value)

    return to_return


@register_dfa(GetVector)
def get_vector(i, command, sub, subs, global_data, matrix):
    # Copy a reference to a vector from the given position to the top of the stack
    vector_name = matrix.var_names[i, matrix.sp_offset_to_pos(i, command.cptopsp.a)]
    for _ in range(3):
        matrix.push(NSSReference(vector_name), ObjectType.VECTOR, i)
    # return convert_cptopsp(i, command.cptopsp, sub, subs, global_data, matrix)


@register_dfa(GetVectorElement)
def get_vector_element(i, command, sub, subs, global_data, matrix):
    vector_name = matrix.var_names[i, matrix.sp_offset_to_pos(i, command.get_vector.cptopsp.a)]
    idx = {0: "x", 4: "y", 8: "z"}[command.destruct.b]

    obj = VectorIndex(vector_name, idx)
    obj_type = ObjectType.FLOAT

    matrix.push(obj, obj_type, i)
