import sys
import subprocess
import shutil

import copy
import re
import assembly as asm

import parsing
import control_flow
import data_flow
import backend
import fingerprint
from fingerprint import FingerprintLibrary, GlobalSet

from rply.errors import ParsingError
import pickle


def main():
    infile = sys.argv[1]

    if infile.endswith(".pcode"):
        with open(infile, "r") as f:
            txt = f.read()
    else:
        # Compile first if ends with nss
        if infile.endswith("nss"):
            # subprocess.run("nwnnsscomp.exe -c --optimize -o tmp.ncs {}".format(infile), shell=True)
            subprocess.run("nwnnsscomp.exe -c -o tmp.ncs {}".format(infile), shell=True)
        else:
            shutil.copy(infile, "tmp.ncs")

        process = subprocess.Popen("xt\\ncsdis.exe --assembly --kotor tmp.ncs".format(infile), shell=True, stdout=subprocess.PIPE)
        txt = process.communicate()[0].decode()

        with open("raw.pcode", "w") as f:
            f.write("\n".join([x.strip() for x in txt.split("\n")]))

    # line_map = parsing.line_map(txt)
    # txt, labels = parsing.preprocess(txt)

    ncs_program = NCSProgram(txt)
    nss_code = ncs_program.to_nss()

    with open("decompiled.nss", "w") as f:
        f.write(nss_code)


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

        retn_type = "void"
        args = []

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
                cur_sub_labels[line.strip().split(":")[0]] = len(cur_sub_lines)
            else:
                # Save the current sub
                if cur_sub_name is not None:
                    sub = NCSSubprocess(cur_sub_name, cur_sub_lines, cur_sub_labels, retn_type, args)
                    self.subs[cur_sub_name] = sub

                cur_sub_name = line.split(";")[0].strip().replace("_", "").replace(":", "")
                # Create a new sub
                if ";" in line:
                    # The line contains some sub metadata
                    sub_data = line.split(";", 1)[1].strip()
                    retn_type, sub_data = sub_data.split(" ", 1)
                    args = sub_data.strip().split("(", 1)[1][:-1].split(",")
                    if len(args) == 1 and args[0] == "":
                        args = []
                    retn_type = retn_type.strip()

                    print(args)
                    print(retn_type)
                elif cur_sub_name == "StartingConditional":
                    retn_type = "int"
                    args = []
                else:
                    retn_type = "void"
                    args = []

                cur_sub_lines = []
                cur_sub_labels = {}

        # Push the final sub
        sub = NCSSubprocess(cur_sub_name, cur_sub_lines, cur_sub_labels, retn_type, args)
        self.subs[cur_sub_name] = sub

        # print(self.subs)

    def to_nss(self):
        # Parse all the subroutines

        parsed_subs = {}
        for sub_name in self.subs:
            parsed_subs[sub_name] = self.subs[sub_name].parse()

        print("Parsed subs")

        # If there are global variables, parse them first
        if "global" in parsed_subs:
            _, global_matrix = data_flow.df_analysis(parsed_subs["global"], self.subs, None)
            with open("html/global_parser.html", "w") as f:
                f.write(global_matrix.html())
            global_values = global_matrix.matrix.last_frame()
            global_types = global_matrix.types.last_frame()

            print(global_values)

            while global_values[-1] is None:
                global_values.pop()
                global_types.pop()

            global_data = NCSGlobals(global_values, global_types)
        else:
            global_data = NCSGlobals([], [])

        # Reduce subroutines using data flow analysis
        df_subs = {}
        for sub_name in parsed_subs:
            print("Computing data flow for sub {}".format(sub_name))
            print("Parsing sub {}".format(sub_name))
            for i, line in enumerate(self.subs[sub_name].lines):
                print("{}: {}".format(i, line))
            # df_subs[sub_name] = data_flow.DataFlow(parsed_subs[sub_name]).blocks
            df_subs[sub_name] = copy.deepcopy(parsed_subs[sub_name])
            df_subs[sub_name].commands, _ = data_flow.df_analysis(parsed_subs[sub_name], self.subs, global_data)

        # Reduce subroutines using control flow analysis
        cf_subs = {}
        for sub_name in df_subs:
            cf_subs[sub_name] = control_flow.ControlFlowAnalysis(df_subs[sub_name])

        # Reduce control flow analysis to NSS code
        nss_subs = {}
        signatures = {}
        for sub_name in cf_subs:
            retn_type = self.subs[sub_name].retn_type
            sub_header = cf_subs[sub_name].header
            code = backend.write_code(sub_header, 1, None, None, None, None, None, cf_subs[sub_name], None)

            args = []
            for i, i_type in enumerate(self.subs[sub_name].args):
                i_name = "arg" + str(i)
                if i_type is None:
                    args.append("unknown {}".format(i_name))
                else:
                    args.append("{} {}".format(i_type, i_name))

            arg_str = ", ".join(args)
            function_signature = "{} {}({});".format(
                retn_type,
                sub_name,
                arg_str
            )
            function_code = "{} {}({}) {{\n{}}}\n".format(
                retn_type,
                sub_name,
                arg_str,
                "".join(code),
            )

            nss_subs[sub_name] = function_code
            signatures[sub_name] = function_signature

        codebase = ""

        # Print the global sub
        if "global" in df_subs:
            global_sub = df_subs["global"]
            codebase += "// Global Variables\n"
            for line in global_sub.commands:
                if type(line) is data_flow.NSSCreateLocal:
                    codebase += str(line).strip() + "\n"

        codebase += "\n// Signatures\n"
        # Function signatures
        for sub_name in nss_subs:
            if sub_name in ("global", "start"):
                continue

            codebase += signatures[sub_name] + "\n"

        codebase += "\n// Actual code\n"
        # Actual code
        for sub_name in nss_subs:
            if sub_name in ("global", "start"):
                continue

            # if sub_name == "StartingConditional":
            #     nss_subs[sub_name] = nss_subs[sub_name].replace("void StartingConditional", "int StartingConditional")

            codebase += "// {}".format(sub_name) + "\n"
            codebase += nss_subs[sub_name] + "\n"

        print(codebase)

        return codebase


class NCSGlobals:
    def __init__(self, global_values, global_types):
        self.global_values = global_values
        self.global_types = global_types

        self.global_vars = {}
        offset = 0
        i = 0
        for x, x_type in reversed(list(zip(self.global_values, self.global_types))):
            print("Global {} is at position {}".format(x, offset))

            self.global_vars[offset] = ("GLOBAL_{}".format(i), x_type)
            offset -= 4
            i += 1

        # matches = fp_library.find_matches(self)
        # print(list(matches))
        # best = sorted(list(matches), key=lambda x: x[1])[0]
        # print(best)
        # exit()

    def from_offset(self, bp_offset):
        if bp_offset not in self.global_vars:
            return ("unknown_global", "unknown_type")
        return self.global_vars[bp_offset]


class NCSSubprocess:
    def __init__(self, name, lines, labels, retn_type, args):
        self.name = name
        self.lines = lines
        self.labels = labels

        self.retn_type = retn_type
        self.args = args

        self.arg_types = []

        if self.name in ("global", "main", "StartingConditional"):  # , "StartingConditional"):
            self.num_args = 0
        else:
            self.num_args = len(self.args)
        # # Check if the second-last
        # elif len(self.lines) < 2:
        #     self.num_args = 0
        # elif "MOVSP" not in self.lines[-2]:
        #     self.num_args = 0
        # else:
        #     n = self.lines[-2].split(" ")[1].strip()
        #     self.num_args = abs(int(n) // 4)

        return_line = len(lines) - 1
        return_label = None
        for label in labels:
            if labels[label] == return_line:
                return_label = label
                break

        # Preprocess storestate commands
        for i in range(len(lines)):
            line = lines[i]

            if "jmp" in line.lower():
                target = line.split(" ")[1]
                if target == return_label:
                    lines[i] = "INLINERETN"

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
                        if "ACTION" in lines[j - 1]:
                            lines[j - 1] = "SSACTION " + lines[j - 1].split(" ", 1)[1]
                        elif "JSR" in lines[j - 1]:
                            lines[j - 1] = "SSJSR " + lines[j - 1].split(" ", 1)[1]
                        else:
                            raise Exception("Invalid line {} found".format(lines[j - 1]))
                        lines[j] = "NOOP"  # "JMP {}".format(next_spot)
                        break

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
        print(with_semicolons)
        try:
            parsed = p.parse(lexer.lex(with_semicolons))
        except ParsingError as e:
            print("Failed on line {} with following exception:".format(e.source_pos.lineno - 1))
            print("Line: '{}'".format(with_semicolons.split(";\n")[e.source_pos.lineno - 1]))
            raise e
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


if __name__ == "__main__":
    print("Loading library")
    with open("library.pickle", "rb") as f:
        fp_library = pickle.load(f)
        print(fp_library.known_vars)

    print("Decompiling")
    main()
