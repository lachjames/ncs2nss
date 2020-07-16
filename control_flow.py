from blocks import create_basic_blocks, compute_dominators, idom
from control_analysis import ControlFlowGraph


class ControlFlowAnalysis:
    def __init__(self, subroutine, return_tails, only_graph=False):
        self.sub = subroutine
        self.only_graph = only_graph

        # Build initial CFG from basic blocks
        basic_blocks = create_basic_blocks(self.sub, return_tails)
        dominators = compute_dominators(basic_blocks)
        for block in basic_blocks:
            block.dominators = dominators[block]

        for block in basic_blocks:
            print(block)
            if block is basic_blocks[0]:
                print("Setting {}.idom to None as it's the header".format(block))
                block.idom = None
            else:
                print("Setting {}.idom to {}".format(block, idom(block)))
                block.idom = idom(block)
        # exit()

        init_cfg = ControlFlowGraph(basic_blocks, basic_blocks[0], self.sub, None)

        # init_cfg.simple_draw("graphs/{}_basic.png".format(subroutine.name))
        # for i, block in enumerate(basic_blocks):
        #     print("{}: {}".format(i, block))

        if self.only_graph:
            # init_cfg.simple_draw("graphs/{}_only_graph.png".format(subroutine.name))
            self.cfg = init_cfg
            return

        self.blocks = basic_blocks

        self.header = self.blocks[0]

        self.cfg = ControlFlowGraph(self.blocks, self.header, self.sub, None)

        # Draw the initial state
        self.cfg.draw("graphs/{}_simple.png".format(subroutine.name))

        self.steps = [self.cfg]

        ## print("Calculating DS step", 0)
        for i, step in enumerate(self.derived_sequence()):
            ## print("Calculated DS step", i)
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
        intervals = G.find_intervals()
        new_header = intervals[0]

        new_G = ControlFlowGraph(intervals, new_header, self.sub, self.cfg)

        node_to_interval = {}
        for interval in intervals:
            for node in interval.nodes:
                node_to_interval[node] = interval

        if len(intervals) == 1:
            ## print("Only found one interval, so returning")
            return new_G, False

        changed = False

        for interval in intervals:
            for other in intervals:
                if interval is other:
                    continue
                if len(interval.bb_preds.set.intersection(other.nodes.set)) > 0:
                    # A node in the interval "other" is a pred to a node in this interval
                    print("Connecting {} and {}".format(interval, other))
                    interval.preds.add(other)
                    other.succs.add(interval)

                    changed = True

        return new_G, changed
