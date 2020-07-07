import copy
import re
import assembly as asm

import parsing
import control_flow
import data_flow
import backend


class NCSProgram:
    def __init__(self, x):
        # Do some replacements
        x = x.replace("CONSTO 0", "CONSTO OBJECT_SELF")

        # Chop off the first few lines as they're not necessary
        self.lines = x.split("\n")[8:]
        # print("\n".join(self.lines))

        self.subs = {}
        cur_sub_name = None
        cur_sub_lines = None
        cur_sub_labels = None

        for line in self.lines:
            if line.strip() == "":
                continue
            elif line.startswith("  "):
                assert cur_sub_lines is not None
                cur_sub_lines.append(line.strip())
            elif line.startswith("loc_"):
                # This line is a label
                cur_sub_labels[line.strip().split(":")[0]] = len(cur_sub_lines)
            elif line.startswith("sta_"):
                # This line starts a STORESTATE section
                # raise Exception("STORESTATE not yet implemented")
                cur_sub_labels[line.strip().split(":")[0]] = len(cur_sub_lines)
            else:
                # Save the current sub
                if cur_sub_name is not None:
                    sub = NCSSubprocess(cur_sub_name, cur_sub_lines, cur_sub_labels)
                    self.subs[cur_sub_name] = sub

                # Create a new sub
                cur_sub_name = line.split(";")[0].strip().replace("_", "").replace(":", "")
                cur_sub_lines = []
                cur_sub_labels = {}

        # Push the final sub
        sub = NCSSubprocess(cur_sub_name, cur_sub_lines, cur_sub_labels)
        self.subs[cur_sub_name] = sub

        # print(self.subs)

    def to_nss(self):
        # Parse all the subroutines

        parsed_subs = {}
        for sub_name in self.subs:
            print("Parsing sub {}".format(sub_name))
            parsed_subs[sub_name] = self.subs[sub_name].parse()

        # Reduce subroutines using data flow analysis
        df_subs = {}
        for sub_name in parsed_subs:
            print("Computing data flow for sub {}".format(sub_name))
            # df_subs[sub_name] = data_flow.DataFlow(parsed_subs[sub_name]).blocks
            df_subs[sub_name] = copy.deepcopy(parsed_subs[sub_name])
            df_subs[sub_name].commands = data_flow.df_analysis(parsed_subs[sub_name], self.subs)

        # Reduce subroutines using control flow analysis
        cf_subs = {}
        for sub_name in df_subs:
            cf_subs[sub_name] = control_flow.ControlFlowAnalysis(df_subs[sub_name])

        # Reduce control flow analysis to NSS code
        nss_subs = {}
        for sub_name in cf_subs:
            sub_header = cf_subs[sub_name].header.header
            code = backend.write_code(sub_header, 1, None, None, None, None, cf_subs[sub_name])

            args = []
            for i, i_type in enumerate(self.subs[sub_name].arg_types):
                i_name = "arg" + str(i)
                if i_type is None:
                    args.append("unknown {}".format(i_name))
                else:
                    args.append("{} {}".format(data_flow.ObjectType.NAME_MAP[i_type], i_name))

            arg_str = ", ".join(args)
            signature = "{} {}({}) {{\n{}}}\n".format(
                "void",
                sub_name,
                arg_str,
                "".join(code),
            )

            nss_subs[sub_name] = signature

        codebase = ""

        # Print the global sub
        if "global" in nss_subs:
            global_sub = nss_subs["global"]
            codebase += "// Global Variables\n"
            codebase += "\n".join(x.strip() for x in global_sub.split("\n")[1:-6]) + "\n\n"

        for sub_name in nss_subs:
            if sub_name in ("global", "start"):
                continue

            codebase += "// {}".format(sub_name) + "\n"
            codebase += nss_subs[sub_name] + "\n"

        return codebase


class NCSSubprocess:
    def __init__(self, name, lines, labels):
        self.name = name
        self.lines = lines
        self.labels = labels

        self.arg_types = []

        self.global_vars = None
        if self.name == "global":
            self.init_global()

        if self.name in ("global", "main", "StartingConditional"):
            self.num_args = 0

        # Check if the second-last
        elif len(self.lines) < 2:
            self.num_args = 0
        elif "MOVSP" not in self.lines[-2]:
            self.num_args = 0
        else:
            n = self.lines[-2].split(" ")[1].strip()
            self.num_args = abs(int(n) // 4)

        # Preprocess storestate commands
        for i in range(len(lines)):
            line = lines[i]
            if "storestate" in line.lower():
                storestate_name = "NOOP"  # line.split(" ")[1]

                # Create a label for the jump after the store state
                # labels[storestate_name + "_retn"] = i + 1

                # Create a jump for the storestate
                lines[i] = "NOOP"  # "JMP {}".format(storestate_name)
                lines[i + 1] = "NOOP"
                # next_spot = storestate_name + "_retn"  # lines[i + 1].split(" ")[1]

                storestates = 1
                for j in range(i + 1, len(lines)):
                    action_line = lines[j - 1]
                    future_line = lines[j]
                    if "storestate" in future_line.lower():
                        storestates += 1
                    elif "retn" in future_line.lower():
                        storestates -= 1
                    if storestates == 0:
                        lines[j - 1] = "SSACTION " + lines[j - 1].split(" ", 1)[1]
                        lines[j] = "NOOP"  # "JMP {}".format(next_spot)
                        break

    def init_global(self):
        found_globals = []

        i = 1
        while i < len(self.lines):
            if "const" not in self.lines[i].lower():
                i += 1
                continue

            global_name = "GLOBAL_" + str(len(found_globals))
            global_type = data_flow.ObjectType.NAME_MAP[data_flow.ObjectType.MAP[self.lines[i].split(" ")[0].strip().lower()[-1]]]

            found_globals.append((global_type, global_name))
            i += 1

        self.global_vars = {}
        offset = -4
        for x in reversed(found_globals):
            # print("Global {} is at position {}".format(x, offset))

            self.global_vars[offset] = x
            offset -= 4

    def get_global(self, offset):
        assert self.name == "global", "This is not the global function; it's {}".format(self.name)
        return self.global_vars[offset]

    def parse(self):
        # for i, line in enumerate(self.lines):
        #     print("{}: {}".format(i, line), end="")
        #     for label in self.labels:
        #         if self.labels[label] == i:
        #             print(" <- {}".format(label), end="")
        #     print()
        lexer = parsing.Lexer()
        parser = parsing.Parser(lexer)
        p = parser.get_parser()

        with_semicolons = "\n".join([line + ";" for line in self.lines])
        parsed = p.parse(lexer.lex(with_semicolons))

        parsed.name = self.name
        parsed.labels = self.labels

        return parsed


# Returns the lines, as well a dict from labels to where they point to
def preprocess(x):
    lines = x.split("\n")

    cleaned_lines = []

    labels = {}

    last_store_state = None

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Strip comments
        line = line.split(";")[0]

        if "STORESTATE" in line:
            last_store_state = len(cleaned_lines)

        if ":" in line.split(" ")[0]:
            # This is a label, so point to the next line
            # TODO: Handle multiple labels in a row? Not sure if ncsdis.exe does this
            label = line.split(" ")[0][:-1]
            labels[label] = len(cleaned_lines)
            i += 1

            if label.startswith("sta"):
                assert last_store_state is not None
                # Starts with sta
                for j in range(i + 1, len(lines)):
                    if "RETN" in lines[j]:
                        lines[j] = lines[j].replace("RETN", "STORESTATERETURN {}".format(last_store_state + 1))
                        break

            continue

        if line.strip() == "":
            i += 1
            continue

        cleaned_lines.append(line + ";")
        i += 1

    cleaned = "\n".join(cleaned_lines)

    return cleaned, labels
