import assembly as asm
from data_structures.util import OrderedSet


def create_basic_blocks(sub, return_tails):
    # Find leaders, which are:
    #   - the first instruction
    #   - target of conditional or unconditional jump
    #   - instruction after a conditional or unconditional jump
    leader_set = OrderedSet()
    for i in range(len(sub.commands)):
        cmd = sub.commands[i]

        if i == 0:
            leader_set.add(0)

        elif type(cmd) is asm.Jump:
            target = cmd.line
            if type(target) is str:
                target = sub.labels[target]

            leader_set.add(target)
            leader_set.add(i + 1)

        elif type(cmd) is asm.ConditionalJump:
            target = sub.labels[cmd.line]
            leader_set.add(target)
            leader_set.add(i + 1)

        elif type(cmd) is asm.StoreState:
            # This is an unconditional jump, just like asm.Jump,
            # which jumps to the target label
            target = sub.labels[cmd.label]
            leader_set.add(target)
            # TODO: Check if this is needed (it probably is)
            # leader_set.add(sub.start_address + i + 1)

        elif type(cmd) is asm.StoreStateReturn:
            # This jumps back to cmd.lineno (as set in the preprocessing stage)
            leader_set.add(int(cmd.lineno))

        # elif type(cmd) is asm.Return:
        #     # pass
        #     leader_set.add(i)
        #
        # elif type(cmd) is asm.InlineReturn:
        #     leader_set.add(i)

    # print(sorted(leader_set))

    blocks = []

    block_to_line = {}
    line_to_block = {}

    leader_list = list(sorted(leader_set))
    for i, leader in enumerate(leader_list):
        if i == len(leader_list) - 1:
            # This is the last block, so its length is just len(subroutine) - block.start_pos
            length = len(sub.commands) - leader
        else:
            length = leader_list[i + 1] - leader

        block = BasicBlock(leader, length)

        block_to_line[block] = leader
        line_to_block[leader] = block

        blocks.append(block)

    # print(block_to_line)
    # print(line_to_block)

    # Calculate connections between blocks
    cur_store_state = None
    for i, block in enumerate(blocks):
        # print(block.address, block.length)
        # print(sub.start_address, len(sub.asm_subroutine.commands) + sub.start_address, block.address + block.length - 1 - sub.start_address)
        last_address = block.address + block.length - 1
        last_statement = sub.commands[last_address]

        if type(last_statement) is asm.Jump:
            target = line_to_block[sub.labels[last_statement.line]]
            # Add a connection between the node and the next node
            block.succs.add(target)
            target.preds.add(block)
            # print("Connected {} -> {}".format(block, target))

        elif type(last_statement) is asm.ConditionalJump:
            target = line_to_block[sub.labels[last_statement.line]]
            # Add a connection between the node and the next node
            block.succs.add(target)
            target.preds.add(block)
            # print("Connected {} -> {}".format(block, target))

            # Jump is conditional so we might also go to the next line
            next_block = line_to_block[block.address + block.length]
            block.succs.add(next_block)
            next_block.preds.add(block)
            # print("Connected {} -> {}".format(block, next_block))

        # elif type(last_statement) is asm.StoreState:
        #     cur_store_state = block
        #
        # elif type(last_statement) is asm.StoreStateReturn:
        #     # Connect the last StoreState to this StoreStateReturn
        #     assert cur_store_state is not None
        #
        #     cur_store_state.succs.add(block)
        #     block.preds.add(cur_store_state)
        #     # print("SS Connected {} -> {}".format(cur_store_state, block))
        #
        #     cur_store_state = None
        #
        #     # Connect the StoreStateReturn to the line after the StoreState
        #     target = line_to_block[int(last_statement.lineno)]
        #     block.succs.add(target)
        #     target.preds.add(block)
        # print("SSR Connected {} -> {}".format(block, target))

        elif type(last_statement) is asm.Return:
            pass

        elif str(last_statement).startswith("return"):
            pass

        else:
            if "return_cmds" not in block.params:
                # Block doesn't end in a jump, so feed into the next line
                target = line_to_block[block.address + block.length]
                block.succs.add(target)
                target.preds.add(block)
                # print("Connected {} -> {}".format(block, target))

    # for block in blocks:
    #     last_address = block.address + block.length - 1
    #     last_statement = sub.commands[last_address]
    #
    #     if type(last_statement) in (asm.InlineReturn, asm.Return):
    #         block.succs = set()

    # For blocks which connect to the final block, we copy the contents of that block
    # into those nodes.
    # Find the last block
    last_block, last_block_addr = None, -1
    for block in blocks:
        if block.address > last_block_addr:
            last_block_addr = block.address
            last_block = block

    assert last_block is not None

    if type(last_block.last_command(sub)) is not asm.Return:
        last_block.params["last_block"] = True
    # last_cmds = sub.commands[last_block.address:]
    # for pred in last_block.preds:
    #     pred.params["return_cmds"] = last_cmds
    #     pred.succs.remove(last_block)
    #
    # last_block.preds = OrderedSet()

    for pred in last_block.preds:
        if len(pred.succs) == 1:
            pred.params["points_to_return"] = True

    # Prune unreachable blocks
    changed = True
    while changed:
        changed = False
        i = 1
        while i < len(blocks):
            if len(blocks[i].preds) == 0:
                changed = True
                for block in blocks:
                    if blocks[i] in block.preds:
                        block.preds.remove(blocks[i])
                del blocks[i]
            else:
                i += 1

    # Add a dummy final block
    # dummy_block = BasicBlock(-1, -1)
    # for block in blocks:
    #     if len(block.succs) == 0:
    #         block.succs.add(dummy_block)
    #         dummy_block.preds.add(block)

    for block in blocks:
        last_address = block.address + block.length - 1
        last_statement = sub.commands[last_address]

        if type(last_statement) is asm.Return:
            block.succs = OrderedSet()

            # Debugging check
            for other in blocks:
                assert block not in other.preds, "Found block with return as pred: {}".format(other)

    for block in blocks:
        if block.address in return_tails:
            block.params["return_cmds"] = return_tails[block.address]

    return blocks


def compute_dominators(basic_blocks):
    dominators = {}

    dominators[basic_blocks[0]] = {basic_blocks[0]}

    for block in basic_blocks:
        if block is basic_blocks[0]:
            dominators[block] = {block}
        else:
            dominators[block] = set(basic_blocks)

    changed = True
    while changed:
        changed = False
        for block in basic_blocks:
            if block is basic_blocks[0]:
                continue
            block_doms = {block}

            preds = list(block.preds)
            if len(preds) == 0:
                continue

            pred_doms = dominators[preds[0]]
            for p in preds[1:]:
                pred_doms = pred_doms.intersection(dominators[p])

            block_doms = block_doms.union(pred_doms)

            if block_doms != dominators[block]:
                dominators[block] = block_doms
                changed = True

    # for block in basic_blocks:
    #     print("Block {} has dominators {}".format(block, dominators[block]))

    return dominators


def idom(block):
    # The idom dominates the block, but no other dominators of the block.

    # Find the immediate dominator, which must have all other
    # dominators dominating it
    return latest_dominator(block.dominators, [block])

    # print("For block {}, considering dominators {}".format(block, dominators))


def common_idom(blocks):
    # Find the node which dominates all nodes in blocks, as well as all other nodes in that set of nodes
    blocks = list(blocks)
    common_dominators = blocks[0].dominators

    for block in blocks[1:]:
        common_dominators = common_dominators.intersection(block.dominators)

    return latest_dominator(common_dominators, blocks)


def latest_dominator(dominators, excludes):
    for dom in dominators:
        if dom in excludes:
            continue

        # print("Considering {}".format(dom))
        is_idom = True

        for other in dominators:
            if other in excludes:
                continue

            if dom is other:
                continue

            if other not in dom.dominators:
                # print("Node {} with doms {} not dominated by {}".format(dom, dom.dominators, other))
                is_idom = False
                break

        if is_idom:
            # print("Found idom {}".format(dom))
            return dom

    raise Exception("Could not find idom for {} out of {}".format(excludes, dominators))


class BasicBlock:
    def __init__(self, address, length):
        self.address = address
        self.length = length

        self.preds = OrderedSet()
        self.succs = OrderedSet()

        self.dominators = OrderedSet()

        self.visited = False
        self.traversed = False
        self.params = {}

    def to_nss(self, sub):
        code_lines = []
        for line in sub.commands[self.address:self.address + self.length]:
            if line is None:
                continue
            if type(line) in (asm.Jump, asm.ConditionalJump):
                # This should be taken care of by control flow
                continue
            if type(line) is asm.Return:
                code_lines.append("return")
                continue
            code_lines.append(str(line))
        return ";\n".join(code_lines) + (";" if len(code_lines) > 0 else "")

    def outward_edges(self, sub):
        # Returns t, f where t is the block navigated to on a true condition
        # and f is navigated to on a false condition
        if len(self.succs) == 0:
            return None, None

        if len(self.succs) == 1:
            return list(self.succs)[0], None

        assert len(self.succs) == 2, "Too many successors found for {} with succs {}".format(self, self.succs)
        a, b = list(self.succs)

        bb_last = self.last_command(sub)

        on_condition_true = sub.labels[bb_last.line]
        if a.address == on_condition_true:
            t = a
            f = b
        elif b.address == on_condition_true:
            t = b
            f = a
        else:
            raise Exception("Could not find successor with address {}".format(on_condition_true))

        if bb_last.op_type.lower() == "jz":
            t, f = f, t
        elif bb_last.op_type.lower() == "jnz":
            pass
        else:
            raise Exception("Invalid bb op type {} found".format(bb_last.op_type))

        return t, f

    def compute_conditional(self, cfa):
        if_data = self.params["if"]
        # Returns if_part, else_part
        non_follow = [x for x in self.succs if x is not if_data.follow]
        ## print("Non follow nodes: {}".format(non_follow))
        # assert len(non_follow) == 2, "Found {} non_follow, should be 2".format(non_follow)
        if len(non_follow) == 2:
            if non_follow[0].address == self.address + self.length:
                else_part = non_follow[1]
                if_part = non_follow[0]
            else:
                assert non_follow[1].address == self.address + self.length
                else_part = non_follow[0]
                if_part = non_follow[1]
        elif len(non_follow) == 1:
            if_part = non_follow[0]
            else_part = None
        else:
            raise Exception("Invalid non-follow values {} for {}".format(non_follow, self))

        bb_last = cfa.sub.commands[self.address + self.length - 1]
        if bb_last.op_type.lower() == "jz":
            pass
        elif bb_last.op_type.lower() == "jnz":
            if_part, else_part = else_part, if_part
        else:
            raise Exception("Invalid bb op type {} found".format(bb_last.op_type))

        return if_part, else_part

    def last_command(self, sub):
        return sub.commands[self.address + self.length - 1]

    def clear_conditional(self):
        del self.params["if"]

    def __repr__(self):
        return "{}-{}".format(self.address, self.address + self.length - 1)
