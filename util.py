def main():
    test = PropagateTable(5, 5)

    # Add some values
    test[0, 0] = "abc"
    for i in range(5):
        assert test[i, 0] == "abc"

    test[3, 0] = "xyz"
    for i in range(5):
        if i < 3:
            assert test[i, 0] == "abc"
        else:
            assert test[i, 0] == "xyz"

    test[2, 3] = "test"
    test[1, 4] = "qwe"

    print(test)
    for i in range(test.num_commands):
        print(test.get_frame(i))


class PropagateTable:
    def __init__(self, num_commands, stack_size):
        self.num_commands = num_commands
        self.stack_size = stack_size

        self.values = [dict() for _ in range(num_commands)]

    def get_frame(self, i):
        # Returns the i-th stack frame

        frame = [None] * self.stack_size

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
            return None

        max_key = -1
        for key in self.values[stack_pos]:
            if key > cmd:
                continue
            max_key = max(key, max_key)

        if max_key == -1:
            return None

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
