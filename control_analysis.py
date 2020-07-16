from blocks import common_idom, idom
from data_flow_types import BinaryOperation
from data_structures.util import OrderedSet

import assembly as asm
import time
import pydot

from data_structures.util import OrderedSet


class ControlFlowGraph:
    def __init__(self, intervals, header, sub, initial_cfg):
        self.intervals = intervals
        self.header = header

        self.sub = sub

        self.done_dfs = False
        self.initial_cfg = initial_cfg
        if self.initial_cfg is None:
            self.bbs = self.intervals
        else:
            self.bbs = self.initial_cfg.bbs

        self.my_intervals = None

        # self.structure_ncond()
        self.structure_switch()

    def last_block(self):
        last_block = None
        last_block_addr = -1
        for bb in self.bbs:
            if bb.address > last_block_addr:
                last_block_addr = bb.address
                last_block = bb

        return last_block

    def structure_if(self):
        unresolved = OrderedSet()
        for node in reversed(self.rev_dfs_order()):
            # Check that this is an if node
            if len(node.succs) != 2:
                continue

            if "no_if" in node.params:
                ## print("Skipping node {} because it has no_if set".format(node))
                continue

            # if "back_node" in node.params:
            #     continue

            ## print("Found an if node: {}".format(node))

            # If we reach this point, this is an if node
            node_dominates = OrderedSet()
            for other in self.bbs:
                if other.idom is node and len(other.preds) >= 2:
                    # print("{} dominates {}".format(node, other))
                    node_dominates.add(other)

            if len(node_dominates) == 0:
                ## print("Node {} is unresolved".format(node))
                unresolved.add(node)
                continue

            follow_node = max(node_dominates, key=lambda x: x.rev_postorder)
            for un in unresolved:
                ## print("Resolving {} by setting follow to {}".format(un, follow_node))
                # self.ifs.append(IfStatement(follow_node, [un], un))
                if_statement = IfStatement(follow_node, [un], un)
                un.params["if"] = if_statement
                un.follow_node = follow_node

            unresolved = OrderedSet()

            if_statement = IfStatement(follow_node, [node], node)
            # self.ifs.append(if_statement)
            ## print("Created if statement with header {} and follow {}".format(node, follow_node))

            node.params["if"] = if_statement

        # assert len(unresolved) == 0, "Found {} unresolved nodes: {}".format(len(unresolved), [(str(x), type(x)) for x in unresolved])
        if len(unresolved) > 0:
            print("Warning: unresolved if statements found {}".format([str(x) for x in unresolved]))

    def structure_switch(self):
        switches = {}
        unresolved = set()
        for node_m in self.rev_dfs_order():
            if "no_switch" in node_m.params:
                continue

            # if node is not an n-way node, continue
            if len(node_m.succs) <= 1:
                continue

            if "conditional" not in dir(self.sub.commands[node_m.address + node_m.length - 1]):
                continue

            conditional = self.sub.commands[node_m.address + node_m.length - 1].conditional
            if type(conditional) is not BinaryOperation:
                continue

            if conditional.op != "==":
                continue

            # If there exists some successor to m, s, such that m is not the idom of s, n = common_idom(succ(m))
            # otherwise, n = m
            for succ in node_m.succs:
                if node_m is not succ.idom:
                    node_n = common_idom(node_m.succs)
                    break
            else:
                node_n = node_m

            print(node_m, node_n)
            node_j = None
            in_j = -1
            for node in self.bbs:
                if node.idom is node_n and len(node.preds) >= 2 and in_j < len(node.preds):
                    node_j = node
                    in_j = len(node.preds)

            if in_j <= 2:
                continue

            switch_head = node_n
            switch_follow = node_j

            case_nodes = []

            # Loop through and find all the cases
            cur_node = switch_head
            default_node = None
            while cur_node is not None:
                if len(cur_node.succs) == 1:
                    # This is a default edge
                    default_node = cur_node
                    break
                else:
                    t, f = cur_node.outward_edges(self.sub)
                    if t is switch_follow:
                        break
                    case_nodes.append(cur_node)
                    cur_node = f

            is_switch = True
            for cn in case_nodes:
                if "conditional" not in dir(self.sub.commands[node_m.address + node_m.length - 1]):
                    is_switch = False
                    break
                conditional = self.sub.commands[node_m.address + node_m.length - 1].conditional
                if type(conditional) is not BinaryOperation:
                    is_switch = False
                    break
                if conditional.op != "==":
                    is_switch = False
                    break

            if not is_switch:
                continue

            print("Switch {} has cases {} and default {}".format(switch_head, case_nodes, default_node))
            switch_head.params["case_nodes"] = [(cn, cn.outward_edges(self.sub)[0]) for cn in case_nodes]
            if default_node is None:
                switch_head.params["default_case"] = None
            else:
                switch_head.params["default_case"] = list(default_node.succs)[0]

            switch_head.params["switch_follow"] = switch_follow
            switch_head.params["no_if"] = True
            for cn in case_nodes:
                cn.params["no_if"] = True
                cn.params["no_switch"] = True

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
                if "if" not in node.params:
                    continue

                t, e = node.compute_conditional(self)

                if t is not None and "if" in t.params and len(t.preds) == 1:
                    a, b = t.compute_conditional(self)
                    if a is e:
                        # not n or t
                        ## print("Condition is !{} && {}".format(node, t))
                        node.clear_conditional()
                        change = True
                    elif b is e:
                        # n or t
                        ## print("Condition is {} || {}".format(node, t))
                        node.clear_conditional()
                        change = True
                elif e is not None and "if" in e.params and len(e.preds) == 1:
                    a, b = e.compute_conditional(self)
                    if a is t:
                        # n or e
                        ## print("Condition is {} && {}".format(node, e))
                        node.clear_conditional()
                        change = True
                    elif b is t:
                        # not n or e
                        ## print("Condition is !{} || {}".format(node, e))
                        node.clear_conditional()
                        change = True

                # change = False

    def rev_dfs_order(self):
        if not self.done_dfs:
            self.dfs()

        return sorted(self.bbs, key=lambda b: b.rev_postorder)

    def dfs(self):
        if self.initial_cfg is not None:
            return

        for block in self.bbs:
            block.visited = False
            block.rev_postorder = -1
        self.dfs_recursive(self.header, counter=[None] * len(self.bbs))
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
        if self.initial_cfg is None:
            # This is the initial cfg
            between = self.rev_dfs_order()[a.rev_postorder:b.rev_postorder + 1]
        else:
            return self.initial_cfg.dfs_between(a, b)
        print("From {} to {} is {}".format(a, b, between))
        return between

    def find_intervals(self):
        if self.my_intervals is not None:
            return self.my_intervals

        self.dfs()
        nodes = set(self.intervals)

        print("Nodes: {}".format(nodes))

        intervals = []
        headers = {self.header}

        while len(headers) > 0:
            print("Headers: {}".format(headers))
            interval_nodes = OrderedSet()
            interval_header = headers.pop()
            interval_nodes.add(interval_header)
            nodes.remove(interval_header)

            # Build interval
            while True:
                additions = OrderedSet()
                for node in nodes:
                    if node in interval_nodes:
                        # print("Skipping {} as it's already in the interval".format(node))
                        continue
                    # Check if all predecessors of this node are in the interval
                    if node.preds.issubset(interval_nodes):
                        # If so, add this node too
                        additions.add(node)
                        # print("{}'s predecessors ({}) are in the interval, so adding it too".format(node, node.preds.set))
                    # else:
                    #     print("Skipping {} as it's predecessors ({}) aren't in the interval".format(node, node.preds.set))

                if len(additions) == 0:
                    break

                for addition in additions:
                    interval_nodes.add(addition)
                    nodes.remove(addition)

            # print("Found interval {}".format(interval))
            interval = Interval(interval_nodes, interval_header, self)
            interval.collapse()
            intervals.append(interval)

            # The header for a new interval will be any node which has a pred
            # inside the interval we just created, but is not in the interval
            # itself.
            for node in nodes:
                if node in headers:
                    continue

                if node in interval.base_nodes:
                    continue

                if len(node.preds.intersection(interval.base_nodes)) > 0:
                    headers.add(node)

        # print("Found intervals {}".format(intervals))

        for bb in self.bbs:
            counter = 0
            for interval in intervals:
                if bb in interval.nodes:
                    counter += 1

            assert counter == 1, "{} found in {} intervals".format(bb, counter)
            # if counter != 1:
            #     print("Warning: {} found in {} intervals".format(bb, counter))

        self.structure_if()
        # self.structure_comp_conds()

        self.my_intervals = intervals

        return intervals

    def bb_color(self, bb):
        # Using this color palette
        # https://www.schemecolor.com/rainbow-pastels-color-scheme.php
        node_last = bb.last_command(self.sub)
        if type(node_last) is asm.ConditionalJump:
            if node_last.op_type.lower() == "jz":
                col = "#c7ceea"
            elif node_last.op_type.lower() == "jnz":
                col = "#b5ead7"
            else:
                raise Exception("Invalid op type {} for conditional jump found while plotting graph".format(node_last.op_type))
        elif len(bb.succs) == 0:
            col = "#ff9aa2"
        elif type(node_last) in (asm.SSJumpSubroutine, asm.SSAction):
            col = "#e2f0cb"
        else:
            col = "white"

        return col

    def draw(self, loc):
        ## print("Drawing graph {}".format(loc))

        pydot_graph = pydot.Dot(rank="rl")

        intervals = self.find_intervals()
        pydot_nodes = {}
        # For each interval...
        for i, interval in enumerate(intervals):
            # Create a subgraph
            cluster = pydot.Cluster(str(i))
            pydot_graph.add_subgraph(cluster)

            # For each node in the interval...
            for node in interval.nodes:
                col = self.bb_color(node)
                pydot_node = pydot.Node(str(node), fillcolor=col, style="filled")
                cluster.add_node(pydot_node)
                pydot_nodes[node] = pydot_node

        # For each edge in the graph...

        for bb in self.bbs:
            pydot_node = pydot_nodes[bb]
            t, f = bb.outward_edges(self.sub)

            if t is not None:
                pydot_t = pydot_nodes[t]
                pydot_t_edge = pydot.Edge(pydot_node, pydot_t, label="t" if f is not None else "")
                pydot_graph.add_edge(pydot_t_edge)

            if f is not None:
                pydot_f = pydot_nodes[f]
                pydot_f_edge = pydot.Edge(pydot_node, pydot_f, label="f")
                pydot_graph.add_edge(pydot_f_edge)

        pydot_graph.write_png(loc, prog="dot")


class Interval:
    def __init__(self, nodes, header, cfg):
        if type(header) is Interval:
            header = header.header

        self.header = header

        self.base_nodes = nodes

        self.nodes = OrderedSet()
        for node in nodes:
            if type(node) is Interval:
                for sub_node in node.nodes:
                    self.nodes.add(sub_node)
            else:
                self.nodes.add(node)

        self.cfg = cfg

        self.preds = OrderedSet()
        self.succs = OrderedSet()

        self.bb_preds = OrderedSet()
        self.bb_succs = OrderedSet()

        for node in self.nodes:
            for pred in node.preds:
                self.bb_preds.add(pred)

            for succ in node.succs:
                self.bb_succs.add(succ)

        self.loop = None
        self.ifs = []

    def collapse(self):
        # self.structure_ncond()
        self.loop = None
        if self.is_loop():
            self.structure_loop()
            # assert self.loop is not None, "self.loop not set to a loop"
            ## print("Found loop")
            # print("Found loop of type", self.loop.loop_type())
        # else:
        # print("Did not find a loop")

        # self.structure_ncond()

    def nodes_to_interval(self, other):
        found = OrderedSet()

        for node in self.nodes:
            for succ in node.succs:
                if succ is other.header:
                    found.add(node)

        return found

    def back_nodes(self):
        nodes = OrderedSet()

        for pred in self.header.preds:
            if pred in self.nodes:
                nodes.add(pred)

        return list(nodes)

    def is_loop(self):
        return len(self.back_nodes()) > 0

    def loop_nodes(self, back_node):
        eligible_raw = list(self.cfg.dfs_between(self.header, back_node))
        eligible = OrderedSet()
        for x in eligible_raw:
            eligible.add(x)

        print("Eligible: {}".format(eligible))

        in_loop = OrderedSet()
        in_loop.add(self.header)

        for node in eligible:
            node_doms = node.dominators
            node_idom = node.idom

            if node_idom in in_loop and node in self.nodes:
                in_loop.add(node)

        in_loop.add(back_node)
        print("LOOP NODES", in_loop)

        return in_loop

    def structure_loop(self):
        # If this is called, this must contain a loop
        back_nodes = self.back_nodes()
        # print("Loop with header {} has back nodes {}".format(self.header, [str(x) for x in back_nodes]))
        # assert len(back_nodes) == 1, "len(back_nodes) should be 1 but is {}".format(len(back_nodes))

        # print("back nodes: {}".format(back_nodes))

        back_nodes = list(sorted(back_nodes, key=lambda b: b.rev_postorder))
        back_node = back_nodes[-1]

        # All other back nodes are basic blocks ending with a "continue"
        other_back_nodes = back_nodes[:-1]
        for obn in other_back_nodes:
            obn.params["continue"] = True

        # print("Found last back node {}".format(back_node))

        loop_nodes = list(self.loop_nodes(back_node))

        # Find the loop's condition node, which is the last node in the reversed-postorder
        # traversal which points both in and out the loop, but before any other node that does so
        condition_node = self.header
        loop = Loop(back_node, None, loop_nodes, condition_node)

        # print("Loop {} contains {}".format(loop, loop_nodes))
        loop_type = loop.loop_type()

        if loop_type is LoopType.PRETESTED:
            # self.header.params["no_if"] = True
            header_succs = list(condition_node.succs)
            if header_succs[0] in loop_nodes:
                loop_follow = header_succs[1]
            elif header_succs[1] in loop_nodes:
                loop_follow = header_succs[0]
            else:
                raise Exception("Invalid while loop detected")
        elif loop_type is LoopType.POSTTESTED:
            back_succs = list(back_node.succs)
            if len(back_succs) == 1 and len(back_node.preds) == 1:
                real_back_node = list(back_node.preds)[0]
                # real_back_node.params["no_if"] = True
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
                raise Exception("Invalid do loop detected")
        else:
            loop_follow = None

        loop.follow = loop_follow

        condition_node = self.header

        for node in sorted(loop_nodes, key=lambda x: x.rev_postorder):
            if len(node.succs) == 2:
                # If the loop follow is in the node's successors,
                # this points out of the loop
                if loop_follow in node.succs:
                    condition_node = node
                    continue

                # Otherwise, if all the loop nodes are in the loop, break
                if node.succs.set.issubset(loop_nodes):
                    break

                condition_node = node

        print("Condition node is {}".format(condition_node))
        loop.condition_node = condition_node

        # Find all nodes which link to the loop follow
        for node in loop_nodes:
            if node in (condition_node, back_node):
                continue
            if loop_follow in node.succs and len(node.succs) == 1:
                node.params["break"] = True
            elif condition_node in node.succs and len(node.succs) == 1:
                node.params["continue"] = True

        self.loop = loop

        condition_node.params["loop"] = loop

    def __repr__(self):
        return "Interval: " + str(self.nodes.set)


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

        ## print("Loop from {} to {} contains {}".format(self.header, self.back, self.nodes))

    def loop_type(self):
        back_succs = list(self.back.succs)
        head_succs = list(self.header.succs)

        ## print("Back succs: {}; Head succs: {}".format(back_succs, head_succs))

        # if len(back_succs) == 1 and len(self.back.preds) == 1:
        #     ## print("Passing the buck back to the previous node as this is a one-way jump")
        #     # We check the node before this one as that's the conditional node
        #     back_succs = list(self.back.preds)[0].succs

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
                ## print("Head_succ: {}, Back_succ: {}".format(head_succs, back_succs))
                return LoopType.ENDLESS


class LoopType:
    PRETESTED, POSTTESTED, ENDLESS = range(3)


class IfStatement(AST):
    def __init__(self, follow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.follow = follow


class SwitchStatement(AST):
    def __init__(self, end_node, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.end_node = end_node
