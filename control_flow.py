import networkx as nx

import assembly as asm
import time
import pydot

from util import OrderedSet


class ControlFlowAnalysis:
    def __init__(self, subroutine, only_graph=False):
        self.sub = subroutine
        self.only_graph = only_graph

        # Build initial CFG from basic blocks
        basic_blocks = create_basic_blocks(self.sub)

        init_cfg = ControlFlowGraph(basic_blocks, basic_blocks[0], self.sub)

        if self.only_graph:
            init_cfg.simple_draw("graphs/{}_only_graph.png".format(subroutine.name))
            self.cfg = init_cfg
            return

        init_cfg.simple_draw("graphs/{}_basic.png".format(subroutine.name))
        # for i, block in enumerate(basic_blocks):
        #     print("{}: {}".format(i, block))

        dominators = compute_dominators(basic_blocks)
        for block in basic_blocks:
            block.dominators = dominators[block]

        for block in basic_blocks:
            if block is basic_blocks[0]:
                block.idom = None
            else:
                block.idom = idom(block)
        # exit()

        self.blocks = basic_blocks

        self.header = self.blocks[0]

        self.cfg = ControlFlowGraph(self.blocks, self.header, self.sub)

        # Draw the initial state
        # self.cfg.draw("graphs/{}_simple.png".format(subroutine.name))
        # self.cfg.draw("init.png")

        self.steps = [self.cfg]

        print("Calculating DS step", 0)
        for i, step in enumerate(self.derived_sequence()):
            print("Calculated DS step", i)
            self.steps.append(step)
            step.draw("graphs/{}_step_{}.png".format(subroutine.name, i))

    def draw(self, loc):
        self.cfg.draw(loc)

    def derived_sequence(self):
        G = self.cfg

        changed = True
        while changed:
            G, changed = self.ds_step(G)
            yield G

    def ds_step(self, G):
        intervals = G.intervals()
        new_header = intervals[0]

        new_G = ControlFlowGraph(intervals, new_header, self.sub)

        node_to_interval = {}
        for interval in intervals:
            for node in interval.nodes:
                node_to_interval[node] = interval

        if len(intervals) == 1:
            print("Only found one interval, so returning")
            return new_G, False

        changed = False

        for interval in intervals:
            for pred in interval.header.preds:
                if pred not in interval.nodes:
                    pred_interval = node_to_interval[pred]
                    interval.preds.add(pred_interval)
                    pred_interval.succs.add(interval)

                    changed = True

            for interval_node in interval.nodes:
                for succ in interval_node.succs:
                    if succ not in interval.nodes:
                        succ_interval = node_to_interval[succ]
                        # This is a pointer outside the interval
                        interval.succs.add(succ_interval)
                        succ_interval.preds.add(interval)

                        changed = True

        return new_G, changed


def create_basic_blocks(sub):
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

        elif type(cmd) is asm.Return:
            # pass
            leader_set.add(i)

        elif type(cmd) is asm.InlineReturn:
            leader_set.add(i)

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

        elif str(last_statement).startswith("return "):
            pass

        else:
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
    dominators = block.dominators

    # print("For block {}, considering dominators {}".format(block, dominators))

    for dom in dominators:
        if dom is block:
            continue

        # print("Considering {}".format(dom))
        is_idom = True

        for other in dominators:
            if other is block:
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

    raise Exception("Could not find idom for {} out of {}".format(block, dominators))


class Interval:
    def __init__(self, nodes, header, cfg):
        self.nodes = nodes
        self.header = header

        self.cfg = cfg

        self.preds = OrderedSet()
        self.succs = OrderedSet()

        self.loop = None
        self.ifs = []

    def header_bb(self):
        x = self.header

        while type(x) is Interval:
            x = x.header

        return x

    def collapse(self):
        # self.structure_ncond()
        self.loop = None
        if self.is_loop():
            self.structure_loop()
            # assert self.loop is not None, "self.loop not set to a loop"
            print("Found loop")
            # print("Found loop of type", self.loop.loop_type())
        else:
            print("Did not find a loop")

        # self.structure_ncond()

    def interval_bbs(self):
        bbs = []

        for node in self.nodes:
            if type(node) is Interval:
                bbs += node.interval_bbs()
            else:
                bbs.append(node)

        return bbs

    def nodes_to_interval(self, other):
        my_bbs = set(self.interval_bbs())

        found = OrderedSet()

        for node in my_bbs:
            for succ in node.succs:
                if succ is other.header_bb():
                    found.add(node)
                print("Found connection between {} and {}".format(node, succ))
        return found

    def back_nodes(self):
        nodes = OrderedSet()
        # print("Nodes: {}".format([str(x) for x in self.nodes]))
        # print("Header {} has preds {}".format(self.header, [str(p) for p in self.header.preds]))

        for pred in self.header.preds:
            if pred in self.nodes:
                # print("Found back node from {} to {}".format(pred, self.header))
                if type(pred) is BasicBlock:
                    nodes.add(pred)
                else:
                    for connector in pred.nodes_to_interval(self):
                        nodes.add(connector)
            # else:
            #     print("Pred node {} is not in {}".format(pred, self.nodes))

        print("Found {} back nodes from {} to {}".format(len(nodes), nodes, self.header_bb()))

        return list(nodes)

    def is_loop(self):
        return len(self.back_nodes()) > 0

    def loop_nodes(self, back_node):
        eligible = list(self.cfg.dfs_between(self.header, back_node))

        in_loop = {self.header}

        for node in eligible:
            if type(node) is BasicBlock:
                node_doms = node.dominators
                node_idom = node.idom
            else:
                node_doms = node.header_bb().dominators
                node_idom = node.header_bb().idom

            if node_idom in in_loop and node in self.nodes:
                in_loop.add(node)

        in_loop.add(back_node)

        return in_loop

    def structure_loop(self):
        # If this is called, this must contain a loop
        back_nodes = self.back_nodes()
        # print("Loop with header {} has back nodes {}".format(self.header, [str(x) for x in back_nodes]))
        # assert len(back_nodes) == 1, "len(back_nodes) should be 1 but is {}".format(len(back_nodes))

        print("back nodes: {}".format(back_nodes))

        back_nodes = list(sorted(back_nodes, key=lambda b: b.rev_postorder))
        back_node = back_nodes[-1]

        # All other back nodes are basic blocks ending with a "continue"
        other_back_nodes = back_nodes[:-1]
        for obn in other_back_nodes:
            obn.params["continue"] = True

        print("Found last back node {}".format(back_node))

        raw_loop_nodes = list(self.loop_nodes(back_node))
        print("Found raw loop nodes {}".format(raw_loop_nodes))
        loop_nodes = []

        while len(raw_loop_nodes) > 0:
            node = raw_loop_nodes.pop()
            if type(node) is Interval:
                raw_loop_nodes += list(node.interval_bbs())
            elif node is back_node or back_node not in node.dominators:
                loop_nodes.append(node)
            else:
                print("Node {} not in loop as it's dominated by the back node".format(node))
        loop = Loop(back_node, None, loop_nodes, self.header)

        print("Loop {} contains {}".format(loop, loop_nodes))
        loop_type = loop.loop_type()

        if loop_type is LoopType.PRETESTED:
            self.header.params["no_if"] = True
            header_succs = list(self.header.succs)
            if header_succs[0] in loop_nodes:
                loop_follow = header_succs[1]
            elif header_succs[1] in loop_nodes:
                loop_follow = header_succs[0]
            else:
                raise Exception("Invalid do loop detected")
        elif loop_type is LoopType.POSTTESTED:

            back_succs = list(back_node.succs)
            if len(back_succs) == 1 and len(back_node.preds) == 1:
                real_back_node = list(back_node.preds)[0]
                real_back_node.params["no_if"] = True
                real_back_node.params["no_follow"] = True
                back_succs = list(real_back_node.succs)
            else:
                back_node.params["no_follow"] = True
                back_node.params["no_if"] = True

            if back_succs[0] in loop_nodes:
                loop_follow = back_succs[1]
            elif back_succs[1] in loop_nodes:
                loop_follow = back_succs[0]
            else:
                raise Exception("Invalid while loop detected")
        else:
            loop_follow = None

        loop.follow = loop_follow
        # Find all nodes which link to the loop follow
        for node in loop_nodes:
            if node in (self.header, back_node):
                continue
            # TODO: Implement breaking
            # if loop_follow in node.succs:
            #     node.params["break"] = True

        self.loop = loop
        self.header_bb().params["loop"] = loop

    def to_nss(self, sub):
        code = ""

        if self.is_loop():
            # Write the loop code first
            code += self.loop.to_nss(sub) + "\n"

            # Write the tail code from after the loop
            for node in self.nodes:
                if node in self.loop.nodes or node is self.header or node is self.loop.back:
                    continue
                code += node.to_nss(sub)
                code += "\n"
        else:
            for node in self.nodes:
                code += node.to_nss(sub)
                code += "\n"

        return code


def __repr__(self):
    if self.is_loop():
        return "Loop " + str([str(x) for x in self.nodes])
    else:
        return "Non loop " + str([str(x) for x in self.nodes])


class LoopType:
    PRETESTED, POSTTESTED, ENDLESS = range(3)


class ControlFlowGraph:
    def __init__(self, blocks, header, sub):
        self.blocks = blocks
        self.header = header

        self.sub = sub

        self.done_dfs = False

        # self.structure_ncond()

    def structure_if(self):
        unresolved = OrderedSet()
        for node in reversed(self.rev_dfs_order()):
            # Check that this is an if node
            if len(node.succs) != 2:
                continue

            # TODO: This is suspicious, like below
            if type(node) is Interval:
                node = node.header_bb()

            if "no_if" in node.params:
                continue

            # if "back_node" in node.params:
            #     continue

            print("Found an if node: {}".format(node))

            # If we reach this point, this is an if node
            node_dominates = OrderedSet()
            for other in self.blocks:
                # print("idom of {} is {}:".format(other, other.header.idom))
                # TODO: The following two if statements are suspicious...
                if type(other) is Interval:
                    other = other.header_bb()
                if other.idom is node and len(other.preds) >= 2:
                    # print("{} dominates {}".format(node, other))
                    node_dominates.add(other)

            if len(node_dominates) == 0:
                print("Node {} is unresolved".format(node))
                unresolved.add(node)
                continue

            follow_node = max(node_dominates, key=lambda x: x.rev_postorder)
            for un in unresolved:
                print("Resolving {} by setting follow to {}".format(un, follow_node))
                # self.ifs.append(IfStatement(follow_node, [un], un))
                if_statement = IfStatement(follow_node, [un], un)
                un.params["if"] = if_statement
                un.follow_node = follow_node

            unresolved = OrderedSet()

            if_statement = IfStatement(follow_node, [node], node)
            # self.ifs.append(if_statement)
            print("Found if statement")

            node.params["if"] = if_statement

        # assert len(unresolved) == 0, "Found unresolved nodes {}".format(unresolved)

    def structure_switch(self):
        for node in reversed(self.rev_dfs_order()):
            # if node is not an n-way node, continue
            case_head = node
            # Find the end node, which is a node y such that y.idom == x, and
            # for all z such that z.idom == x, inedges(y) > inedges(z)

            node_is_idom = [b for b in self.blocks if b.idom is node]
            end_node = max(node_is_idom, key=lambda x: len(x.preds))

            case_nodes = set(case_head)
            for s in case_head.succs:
                self.case_nodes(case_nodes, case_head, end_node, s)

            print("Found switch statement")
            node.params["switch"] = SwitchStatement(end_node, case_nodes, case_head)
            exit()

    def case_nodes(self, case_nodes, head, end, s):
        s.case_traversed = True
        if s != end and "case" not in s.params and s.idom in case_nodes:
            case_nodes.add(s)
            for r in s.succs:
                if not r.case_traversed:
                    self.case_nodes(case_nodes, head, end, r)

    def structure_comp_conds(self):
        change = True
        while change:
            change = False
            for node in reversed(self.rev_dfs_order()):
                if type(node) is Interval:
                    node = node.header_bb()

                if "if" not in node.params:
                    continue

                t, e = node.compute_conditional(self)

                if t is not None and "if" in t.params and len(t.preds) == 1:
                    a, b = t.compute_conditional(self)
                    if a is e:
                        # not n or t
                        print("Condition is !{} || {}".format(node, t))
                        node.clear_conditional()
                        change = True
                    elif b is e:
                        # n or t
                        print("Condition is {} || {}".format(node, t))
                        node.clear_conditional()
                        change = True
                elif e is not None and "if" in e.params and len(e.preds) == 1:
                    a, b = e.compute_conditional(self)
                    if a is t:
                        # n or e
                        print("Condition is {} || {}".format(node, e))
                        node.clear_conditional()
                        change = True
                    elif b is t:
                        # not n or e
                        print("Condition is !{} || {}".format(node, e))
                        node.clear_conditional()
                        change = True

                # change = False

    def rev_dfs_order(self):
        if not self.done_dfs:
            self.dfs()

        return sorted(self.blocks, key=lambda b: b.rev_postorder)

    def dfs(self):
        for block in self.blocks:
            block.visited = False
            block.rev_postorder = -1
        self.dfs_recursive(self.header, counter=[None] * len(self.blocks))
        self.done_dfs = True

    def dfs_recursive(self, x, counter):
        x.visited = True
        for s in x.succs:
            if s.visited:
                continue
            self.dfs_recursive(s, counter)

        x.rev_postorder = len(counter) - 1
        counter.pop()

    def dfs_between(self, a, b):
        between = self.rev_dfs_order()[a.rev_postorder:b.rev_postorder + 1]
        print("From {} to {} is {}".format(a, b, between))
        return between

    def nx_graph(self):
        g = nx.Graph()

        for block in self.blocks:
            g.add_node(block)

        for block in self.blocks:
            for succ in block.succs:
                g.add_edge(block, succ)

        return g

    def intervals(self):
        self.dfs()
        nodes = set(self.blocks)

        intervals = []
        headers = {self.header}

        while len(headers) > 0:
            # print("Headers: {}".format(headers))
            n = headers.pop()
            interval = Interval({n}, n, self)
            nodes.remove(n)

            # Build interval
            while True:
                additions = OrderedSet()
                for node in nodes:
                    if node in interval.nodes:
                        # print("Skipping {} as it's already in the interval".format(node))
                        continue
                    # Check if all predecessors of this node are in the interval
                    if node.preds.issubset(interval.nodes):
                        # If so, add this node too
                        additions.add(node)
                        # print("{}'s predecessors are in the interval, so adding it too".format(node))
                    # else:
                    # print("Skipping {} as it's predecessors aren't in the interval".format(node))

                if len(additions) == 0:
                    break

                for addition in additions:
                    interval.nodes.add(addition)
                    nodes.remove(addition)

            # print("Found interval {}".format(interval))
            interval.collapse()
            intervals.append(interval)

            # Find headers for new intervals
            for node in nodes:
                if node in headers:
                    continue

                if node in interval.nodes:
                    continue

                if len(node.preds.intersection(interval.nodes)) > 0:
                    headers.add(node)

        # for node in self.blocks:
        #     counter = 0
        #     for interval in intervals:
        #         if node in interval.nodes:
        #             counter += 1
        #
        #     assert counter == 1

        # print("{} found in {} intervals".format(node, counter))

        self.structure_if()
        # self.structure_switch()
        self.structure_comp_conds()

        return intervals

    def simple_draw(self, loc):
        nx_graph = self.nx_graph()

        pydot_graph = pydot.Dot()

        graph_to_pydot = {}
        for graph_node in nx_graph:
            pydot_node = pydot.Node(str(graph_node))
            graph_to_pydot[graph_node] = pydot_node
            pydot_graph.add_node(pydot_node)

        for graph_node in nx_graph:
            for other_node in graph_node.succs:
                pydot_edge = pydot.Edge(graph_to_pydot[graph_node], graph_to_pydot[other_node])
                pydot_graph.add_edge(pydot_edge)

        pydot_graph.write_png(loc)

    def draw(self, loc):
        print("Drawing graph {}".format(loc))
        print("Blocks: ", self.blocks)
        for block in self.blocks:
            for succ in block.succs:
                print("{} -> {}".format(block, succ))

        pydot_graph = pydot.Dot()

        intervals = self.intervals()

        clusters = {}
        cluster_nodes = {}
        for i, interval in enumerate(intervals):
            clusters[i] = pydot.Cluster(str(i))
            if type(interval) is Interval:
                cluster_nodes[interval] = interval.interval_bbs()
            else:
                cluster_nodes[interval] = [interval]

            pydot_graph.add_subgraph(clusters[i])

        pydot_nodes = {}

        # Add nodes
        for block in self.blocks:
            if type(block) is Interval:
                nodes = block.interval_bbs()
            else:
                nodes = [block]

            for node in nodes:
                # print("Adding node {}".format(node))
                for cluster_id in clusters:
                    cluster = clusters[cluster_id]

                    if node in intervals[cluster_id].interval_bbs():
                        # print("Adding node {}".format(node))
                        # Found the node in a subgraph
                        pydot_node = pydot.Node(str(node))
                        cluster.add_node(pydot_node)
                        pydot_nodes[node] = pydot_node

                        # Every node is in only one subgraph
                        break

        # Add edges
        for node in self.blocks:
            if type(node) is Interval:
                nodes = node.interval_bbs()
            else:
                nodes = [node]

            for block in nodes:
                for other in block.succs:
                    print("Block: {}".format(block))
                    print("Other: {}".format(other))
                    pydot_node = pydot_nodes[block]
                    pydot_other = pydot_nodes[other]

                    pydot_edge = pydot.Edge(pydot_node, pydot_other)
                    pydot_graph.add_edge(pydot_edge)

            # print("Found {} intervals".format(len(intervals)))

            print("Writing graph {}".format(loc))
            pydot_graph.write_png(loc, prog="dot")


class Program:
    def __init__(self, subroutines):
        self.subroutines = subroutines


# class Subroutine:
#     def __init__(self, start_address, asm_subroutine, labels):
#         self.start_address = start_address
#         self.asm_subroutine = asm_subroutine
#         self.labels = labels
#
#         self.branches = {}
#         self.jumps = {}
#
#     def next_label(self, position):
#         # It's possible there is no label after a certain point in the code
#         adjusted_pos = position + 1
#         for label_pos in range(adjusted_pos, self.start_address + len(self.asm_subroutine.commands)):
#             print("LS: ", label_pos)
#             if label_pos in self.labels.values():
#                 # A label points to this position
#                 return label_pos
#
#         return 10 ** 20
#
#     def next_branch(self, position):
#         # There should always be one more branch in the code (even if it's just RETN)
#         adjusted_pos = position - self.start_address + 1
#         for branch_pos in range(adjusted_pos, len(self.asm_subroutine.commands)):
#             print("BS:", self.asm_subroutine.commands[branch_pos])
#             if type(self.asm_subroutine.commands[branch_pos]) in (asm.Jump, asm.ConditionalJump, asm.Return):
#                 return branch_pos + self.start_address, self.asm_subroutine.commands[branch_pos]
#
#         raise Exception("No branch found after position {}, which should be impossible".format(position))

class AST:
    def __init__(self, nodes, header):
        self.nodes = nodes
        self.header = header

        self.preds = OrderedSet()
        self.succs = OrderedSet()

        self.create()

    def create(self):
        # raise NotImplementedError()
        pass


class Loop(AST):
    def __init__(self, back, follow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.back = back
        self.follow = follow

        print("Loop from {} to {} contains {}".format(self.header, self.back, self.nodes))

    def loop_type(self):
        back_succs = list(self.back.succs)
        if type(self.header) is Interval:
            head_succs = list(self.header.header_bb().succs)
        else:
            head_succs = list(self.header.succs)

        print("Back succs: {}; Head succs: {}".format(back_succs, head_succs))

        if len(back_succs) == 1 and len(self.back.preds) == 1:
            print("Passing the buck back to the previous node as this is a one-way jump")
            # We check the node before this one as that's the conditional node
            back_succs = list(self.back.preds)[0].succs

        if len(back_succs) == 2:
            # We think about jumping back, so this is posttested
            if len(head_succs) == 2:
                if head_succs[0] in self.nodes and head_succs[1] in self.nodes:
                    # Both places the header node can go are within the loop
                    return LoopType.POSTTESTED
                else:
                    return LoopType.PRETESTED
            else:
                return LoopType.POSTTESTED
        else:
            # We jump back unconditionally, so this might be pre-tested
            if len(head_succs) == 2:
                return LoopType.PRETESTED
            else:
                print("Head_succ: {}, Back_succ: {}".format(head_succs, back_succs))
                return LoopType.ENDLESS

    def to_nss(self, sub):
        loop_type = self.loop_type()
        code = ""
        # Write code for nodes in the loop
        if loop_type is LoopType.PRETESTED:
            code += "while ("
            # Calculate condition
            h = self.header.nodes[0]
            jump = sub.commands[h.address + h.length - 1]
            assert type(jump) is asm.ConditionalJump, "Expected {} to be type asm.ConditionalJump but is {}".format(jump, type(jump))
            conditional = jump.conditional
            code += str(conditional)
            code += ")\n{\n"

            for node in self.nodes:
                code += "    " + "// Basic block {}\n".format(node)
                code += "    " + node.to_nss(sub) + "\n"

            code += "}"
        # Write code for the nodes after the loop
        # for node in self.loop_follow:
        #     pass
        # elif self.loop_type is LoopType.POSTTESTED:
        #     code += "do\n{\n"
        #
        #     for node in self.nodes:
        #         code += "    " + node.to_nss(sub) + "\n"
        #
        #     code += "} while ({});".format()
        else:
            code += "while (TRUE)\n{\n"

        return code


class IfStatement(AST):
    def __init__(self, follow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.follow = follow


class SwitchStatement(AST):
    def __init__(self, end_node, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.end_node = end_node


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

    def compute_conditional(self, cfa):
        if_data = self.params["if"]
        # Returns if_part, else_part
        non_follow = [x for x in self.succs if x is not if_data.follow]
        print("Non follow nodes: {}".format(non_follow))
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

    def clear_conditional(self):
        del self.params["if"]

    def __repr__(self):
        return "{}-{}".format(self.address, self.address + self.length - 1)
