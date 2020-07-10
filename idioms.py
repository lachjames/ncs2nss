import copy

from data_flow_types import Variable, BinaryOperation, UnaryOperation, LogicalOperation, NSSAssign, NSSCreateLocal, NSSAction, NSSReference, NSSSubCall, \
    NSSSSAction, NSSReturnValue

import assembly as asm

IDIOMS = {}


class IDIOM_TYPE:
    GLOBAL, SUB = range(2)


class VAR_TYPE:
    INT, STRING, FLOAT, OBJECT = range(4)


def register_idiom(name):
    def decorator_fn(cls):
        IDIOMS[name] = cls
        return cls

    return decorator_fn


class Idiom:
    def __init__(self):
        pass

    def recognize(self, instructions, stack):
        raise NotImplementedError()

    def convert(self, instructions, stack):
        raise NotImplementedError()


# class Global:
#     def __init__(self, var_type, var_value):
#         self.var_type = var_type
#         self.var_value = var_value
#
#     def to_nss(self):
#         pass
#
#     def __repr__(self):
#         return "CREATE VAR_TYPE({}) = {}".format(self.var_type, self.var_value)


@register_idiom("create_and_assign")
class CreateAndAssignVariableIdiom(Idiom):
    def recognize(self, i, blocks):
        if len(blocks) < 2:
            return False

        if type(blocks[i]) is not NSSCreateLocal:
            return False

        # print("Found create local")
        for j in range(i + 1, len(blocks)):
            if blocks[j] is None:
                continue

            if type(blocks[j]) is not NSSAssign:
                # print("Next block was not NSSAssign, but {}".format(type(blocks[j])))
                return False

            return True

    def convert(self, i, blocks):
        create_block = blocks[i]
        assign_block = None
        j = None

        for j in range(i + 1, len(blocks)):
            if blocks[j] is not None:
                assign_block = blocks[j]
                break

        assert type(assign_block) is NSSAssign
        assert j is not None

        new_create_block = copy.deepcopy(create_block)
        new_create_block.value = assign_block.expression
        return {
            i: new_create_block,
            j: None
        }

# @register_idiom("assign_and_return")
# class SSAssignReturn(Idiom):
#     def recognize(self, i, blocks):
#         if len(blocks) < 2:
#             return False
#
#         last_block = blocks[-1]
#         if type(last_block) is not asm.Return:
#             return False
#
#         second_last_block = None
#         for block in reversed(blocks[:-1]):
#             if block is not None:
#                 second_last_block = block
#                 break
#
#         if second_last_block is None:
#             return False
#
#         if type(second_last_block) is not NSSAssign:
#             return False
#
#         return True
#
#     def convert(self, i, blocks):
#         if len(blocks) < 2:
#             return False
#
#         last_block = blocks[-1]
#         if type(last_block) is not asm.Return:
#             return False
#
#         second_last_block = None
#         j = -1
#         for j, block in enumerate(reversed(blocks[:-1])):
#             if block is not None:
#                 second_last_block = block
#                 break
#
#         second_last_index = j
#
#         return {
#             -1: NSSReturnValue(second_last_block),
#             second_last_index: None
#         }

# @register_idiom("ssaction_declaration")
# class SSActionDeclaration(Idiom):
#     def recognize(self, i, blocks):
#         if len(blocks) < 2:
#             return False
#
#         if type(blocks[i]) is not NSSCreateLocal:
#             return False
#
#         # print("Found create local")
#         for j in range(i + 1, len(blocks)):
#             if blocks[j] is None:
#                 continue
#
#             if type(blocks[j]) is not NSSSSAction:
#                 # print("Next block was not NSSSSAction, but {}".format(type(blocks[j])))
#                 return False
#
#             return True
#
#     def convert(self, i, blocks):
#         create_block = blocks[i]
#         assign_block = None
#         j = None
#
#         for j in range(i + 1, len(blocks)):
#             if blocks[j] is not None:
#                 assign_block = blocks[j]
#                 break
#
#         assert type(assign_block) is NSSSSAction
#         assert j is not None
#
#         return {
#             i: None
#         }

# @register_idiom("create_stack_variable")
# class CreateStackVariableIdiom:
#     def recognize(self, i, instructions):
#         if len(instructions[i:]) < 3:
#             return False
#
#         space, val, asgn = instructions[i:i + 3]
#         if type(space) is not asm.RSAdd:
#             return False
#         if type(val) is not asm.Const:
#             return False
#         if type(asgn) is not asm.CPDownSP:
#             return False
#
#         return True
#
#     def convert(self, i, instructions, stack):
#         # assert self.recognize(i, instructions, stack), "This is not a valid global assignment"
#
#         space, val, asgn = instructions[i:i + 3]
#         op_type = space.op_type[-1].lower()
#
#         if op_type == "i":
#             var_type = VAR_TYPE.INT
#         elif op_type == "s":
#             var_type = VAR_TYPE.STRING
#         elif op_type == "f":
#             var_type = VAR_TYPE.FLOAT
#         elif op_type == "o":
#             var_type = VAR_TYPE.OBJECT
#         else:
#             raise Exception("Invalid global assignment type {} found".format(op_type))
#
#         value = val.value
#
#         return 3, Global(var_type, value)
#
#
# class CreateVariable:
#     TYPE = IDIOM_TYPE.SUB
#
#     def recognize(self, instructions, stack):
#         if len(instructions) < 2:
#             return False
