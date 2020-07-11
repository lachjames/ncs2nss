import re


def main():
    nws = NWScript.load()


def strip_comments(txt):
    lines = []

    for line in txt.split("\n"):
        uncommented = line.split("//")[0].strip()
        if uncommented == "":
            continue
        lines.append(uncommented)

    return lines


class NWScript:
    def __init__(self, txt):
        code = txt.split("// Constants", 1)[1]
        constants, functions = code.split("// 0: ", 1)

        constants = strip_comments(constants)
        functions = strip_comments("// 0: " + functions)

        self.constants = {}
        self.functions = {}

        for c in constants:
            c = NWScript.Constant.Parse(c)
            self.constants[c.const_name] = c
            # print(cs[-1])

        for f in functions:
            f = NWScript.Function.Parse(f)
            self.functions[f.func_name] = f
            # print(fs[-1])

    @classmethod
    def load(cls):
        with open("nwscript.nss") as f:
            return cls(f.read())

    class Constant:
        def __init__(self, const_type, const_name, const_val):
            self.const_type = const_type.strip().lower()
            self.const_name = const_name.strip()
            self.const_val = const_val.strip()

        @classmethod
        def Parse(cls, c):
            c = c.strip()
            const_type, c = c.split(" ", 1)
            const_name, c = c.split(" ", 1)
            const_val = c.split("=")[1][:-1].strip()

            return cls(const_type, const_name, const_val)

        def __str__(self):
            return "{} {}={}".format(self.const_type, self.const_name, self.const_val)

    class Function:
        def __init__(self, func_type, func_name, func_args):
            self.func_type = func_type.strip().lower()
            self.func_name = func_name.strip()
            self.func_args = func_args

        @classmethod
        def Parse(cls, f):
            f = f.strip()
            func_type, f = f.split(" ", 1)
            func_name, func_args = f.split("(", 1)
            func_args = func_args.split(")", 1)[0]
            # Strip vectors of the type [0, 0, 0]
            func_args = re.sub("=[\[].*?[\]]", "", func_args)

            args = []

            if func_args.strip() != "":
                for arg in func_args.split(","):
                    arg = arg.strip()
                    arg_type, arg = arg.split(" ", 1)
                    if "=" in arg:
                        # Has a default
                        arg_name, arg_default = arg.split("=")
                    else:
                        arg_name = arg
                        arg_default = None

                    args.append(NWScript.FunctionArgument(arg_type, arg_name, arg_default))

            return NWScript.Function(func_type, func_name, args)

        def __str__(self):
            return "{} {}({})".format(
                self.func_type,
                self.func_name,
                ", ".join([str(x) for x in self.func_args])
            )

    class FunctionArgument:
        def __init__(self, arg_type, arg_name, arg_default):
            self.arg_type = arg_type.strip().lower()
            self.arg_name = arg_name.strip()
            self.arg_default = arg_default.strip() if arg_default is not None else None

        def __str__(self):
            if self.arg_default is None:
                return "{} {}".format(self.arg_type, self.arg_name)
            else:
                return "{} {}={}".format(self.arg_type, self.arg_name, self.arg_default)


if __name__ == "__main__":
    main()
