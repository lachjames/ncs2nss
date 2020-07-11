def main():
    test = PropagateVector(10)
    for i in range(10):
        print(test[i], end=" ")

    print()

    test[5] = "abc"
    test[2] = "123"
    test[7] = "duck"

    for i in range(10):
        print(test[i], end=" ")


# def main():
#     test = PropagateTable(5, 5)
#
#     # Add some values
#     test[0, 0] = "abc"
#     for i in range(5):
#         assert test[i, 0] == "abc"
#
#     test[3, 0] = "xyz"
#     for i in range(5):
#         if i < 3:
#             assert test[i, 0] == "abc"
#         else:
#             assert test[i, 0] == "xyz"
#
#     test[2, 3] = "test"
#     test[1, 4] = "qwe"
#
#     print(test)
#     for i in range(test.num_commands):
#         print(test.get_frame(i))


class PropagateVector:
    def __init__(self, size, default_value=None):
        self.size = size
        self.default_value = default_value

        self.values = {}

    def __getitem__(self, pos):
        if len(self.values) == 0:
            return self.default_value

        max_key = -1
        for key in self.values:
            if key < max_key:
                continue
            if key > pos:
                continue
            max_key = key

        if max_key == -1:
            return self.default_value

        return self.values[max_key]

    def __setitem__(self, pos, value):
        self.values[pos] = value

    def __len__(self):
        return self.size

    def __str__(self):
        return str(self.values)


class PropagateTable:
    def __init__(self, num_commands, stack_size, default_value=None):
        self.num_commands = num_commands
        self.stack_size = stack_size
        self.default_value = default_value

        self.values = [dict() for _ in range(num_commands)]

    def get_frame(self, i):
        # Returns the i-th stack frame

        frame = [self.default_value] * self.stack_size

        for j in range(self.stack_size):
            frame[j] = self[i, j]

        return frame

    def last_frame(self):
        return self.get_frame(self.num_commands - 1)

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

        for i in range(self.stack_size):
            for j in range(self.num_commands):
                s.append(str(self[j, i]) + "\t")
            s.append("\n")

        return "".join(s)


class OrderedSet:
    def __init__(self):
        self.set = set()
        self.order = []

    def add(self, item):
        if item not in self.set:
            self.set.add(item)
            self.order.append(item)

    def remove(self, item):
        if item in self.set:
            self.set.remove(item)
            self.order.remove(item)

    def __iter__(self):
        return iter(self.order)

    def __contains__(self, x):
        return x in self.set

    def __len__(self):
        return len(self.set)

    def issubset(self, x):
        return self.set.issubset(x)

    def intersection(self, x):
        return self.set.intersection(x)


if __name__ == "__main__":
    main()
