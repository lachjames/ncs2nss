import copy

import assembly as asm
from data_flow_types import VectorDefinition, VectorAssignment, GetVector, GetVectorElement

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


def chain_length(start, blocks, x_type):
    i = start
    while i < len(blocks) and type(blocks[i]) is x_type:
        i += 1
    return i - start


@register_idiom("create_vector")
class CreateVectorIdiom(Idiom):
    def recognize(self, i, blocks):
        if len(blocks[i:]) < 3:
            return False

        for j in range(i, i + 3):
            if type(blocks[j]) is not asm.RSAdd:
                return False

            if blocks[j].op_type[-1].lower() != "f":
                return False

        return True

    def convert(self, i, blocks):
        struct_def = VectorDefinition(blocks[i:i + 3])

        return {
            i: struct_def,
            i + 1: None,
            i + 2: None
        }


@register_idiom("assign_vector")
class AssignVector(Idiom):
    def recognize(self, i, blocks):
        # We look for a chain of Consts, then a CPDownSP, then a MovSP
        if len(blocks[i:]) < 4:
            return False

        if type(blocks[i]) is not asm.CPDownSP:
            return False

        if blocks[i].b <= 4:
            return False

        if type(blocks[i + 1]) is not asm.MoveSP:
            return False

        return True

    def convert(self, i, blocks):
        cpdownsp = blocks[i]

        assign_vec = VectorAssignment(cpdownsp)

        return {
            i: assign_vec
        }


@register_idiom("get_vector")
class GetVectorIdiom(Idiom):
    def recognize(self, i, blocks):
        if type(blocks[i]) is not asm.CPTopSP:
            return False

        return blocks[i].b > 4

    def convert(self, i, blocks):
        return {
            i: GetVector(blocks[i])
        }


@register_idiom("get_struct_element")
class GetVectorElementIdiom(Idiom):
    def recognize(self, i, blocks):
        if len(blocks[i:]) < 2:
            return False

        return type(blocks[i]) is GetVector and type(blocks[i + 1]) is asm.Destruct

    def convert(self, i, blocks):
        return {
            i: GetVectorElement(blocks[i], blocks[i + 1]),
            i + 1: None
        }
