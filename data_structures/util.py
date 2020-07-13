class HTMLColors:
    GREEN = "#AFC97E"
    BLUE = "#5398BE"
    RED = "#F24236"
    DARKBLUE = "#BCE7FD"
    BLACK = "#2E282A"


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
