from data_structures.util import HTMLColors


class PropagateStructure:
    def __init__(self, size, default_value=None):
        self.size = size
        self.default_value = default_value

        pass

    def __getitem__(self, pos):
        raise NotImplementedError()

    def __setitem__(self, pos, value):
        raise NotImplementedError()

    def __len__(self):
        raise NotImplementedError()

    def __str__(self):
        raise NotImplementedError()


class PropagateVector(PropagateStructure):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.matrix = PropagateMatrix((self.size, 1), self.default_value)

    def __getitem__(self, pos):
        return self.matrix[pos, 0]

    def __setitem__(self, pos, value):
        self.matrix[pos, 0] = value

    def __len__(self):
        return self.size

    def __str__(self):
        return str(self.matrix)


# class PropagateMatrixSimple(PropagateStructure):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         num_cmds, stack_size = self.size
#         # When indexing from matrix, first index is the command no; second index is the stack index
#         self.matrix = [[self.default_value for _ in range(stack_size)] for _ in range(num_cmds)]
#
#     def __getitem__(self, pos):
#         cmd_no, stack_pos = pos
#         return self.matrix[cmd_no][stack_pos]
#
#     def __setitem__(self, pos, value):
#         cmd_no, stack_pos = pos
#         for c in range(cmd_no, self.size[0]):
#             if c > cmd_no and self.matrix[c][stack_pos] is not self.default_value:
#                 break
#             self.matrix[c][stack_pos] = value
#         print(self.matrix)
#
#     def __len__(self):
#         return self.size[0] * self.size[1]
#
#     def __str__(self):
#         s = []
#
#         for stack_pos in range(self.size[1]):
#             for cmd_no in range(self.size[0]):
#                 s.append(str(self[cmd_no, stack_pos]) + "\t")
#             s.append("\n")
#
#         return "".join(s)


class PropagateMatrix(PropagateStructure):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.values = [dict() for _ in range(self.size[1])]

    def get_frame(self, i):
        # Returns the i-th stack frame
        frame = [None] * self.size[1]

        for j in range(self.size[1]):
            frame[j] = self[i, j]

        assert len(frame) == self.size[1]

        return frame

    def set_frame(self, i, frame):
        assert len(frame) == self.size[1]
        for j in range(self.size[1]):
            self[i, j] = frame[j]

    def last_frame(self):
        return self.get_frame(self.size[0] - 1)

    def __getitem__(self, pos):
        stack_pos = pos[1]
        cmd = pos[0]

        # Get the latest item assigned to self.values[cmd]
        if len(self.values[stack_pos]) == 0:
            return self.default_value

        max_key = -1
        for key in self.values[stack_pos]:
            if key > cmd:
                continue
            max_key = max(key, max_key)

        if max_key == -1:
            return self.default_value

        return self.values[stack_pos][max_key]

    def __setitem__(self, pos, item):
        stack_pos = pos[1]
        cmd = pos[0]
        self.values[stack_pos][cmd] = item

    def __str__(self):
        s = []

        for stack_pos in range(self.size[1]):
            for cmd_no in range(self.size[0]):
                s.append(str(self[cmd_no, stack_pos]) + "\t")
            s.append("\n")

        return "".join(s)

# PropagateMatrix = PropagateMatrixSimple
