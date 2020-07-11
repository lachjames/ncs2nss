import assembly as asm


def make_loops(loop_set):
    for loop in loop_set.get_loops():
        nss_loop = DoWhile(
            loop.blocks[-1].last_compare_instruction(),
            loop.blocks,
            loop.post_dominator(),
            loop.blocks[-1]
        )
        cb = nss_loop.continue_block
        if len(cb.statements) == 1:
            if type(cb.statements[0]) is not asm.ConditionalJump or loop.header not in cb.succs:
                nss_loop.continue_block = None

        loop.header.statements[-1] = nss_loop

        structure_break_continue(nss_loop)


def structure_break_continue(nss_loop):
    cont_block = nss_loop.continue_block
    break_block = nss_loop.break_block


class DoWhile:
    def __init__(self, expr, blocks, break_block, continue_block):
        self.expr = expr
        self.blocks = blocks
        self.break_block = break_block
        self.continue_block = continue_block
