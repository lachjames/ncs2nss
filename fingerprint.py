import sys
import os
from nss.parsing import Lexer as NSSLexer
from nss.parsing import Parser as NSSParser
from nss import script

from multiprocessing.pool import ThreadPool
import rply
import tqdm
import pickle

from data_flow import ObjectType


def main():
    loc = sys.argv[1]

    library = FingerprintLibrary(loc)
    with open("library.pickle", "wb") as f:
        pickle.dump(library, f)


class FingerprintLibrary:
    def __init__(self, loc):
        self.loc = loc
        self.known_vars = {}

        lexer = NSSLexer()
        parser_gen = NSSParser(lexer)
        parser = parser_gen.get_parser()

        files = [loc + "/" + x for x in os.listdir(loc) if x.endswith("nss")]
        pbar = tqdm.tqdm(len(files))

        self.prints = []
        for file in files:
            self.prints.append(read_nss(file, lexer, parser))
            pbar.update()

        pbar.close()

    def find_matches(self, ncs_globals):
        # We create a new list of globals from the data in ncs_globals
        values = []
        for value, val_type in zip(ncs_globals.global_values, ncs_globals.global_types):
            if val_type not in (ObjectType.INT, ObjectType.STRING):
                continue

            if value is None:
                continue

            values.append(str(value).lower())

        globals = GlobalSet(values)

        # Then we find the best matching set of includes for this list
        solutions = []
        self.matching_fingerprints(globals, [], solutions, 0)

        solutions.sort(key=lambda x: x[1], reverse=True)

        print("Optimal solution: {}".format([str(x) for x in solutions[0][0]]))
        print("Matched {} globals".format(solutions[0][1]))
        return solutions[0][0]

    def matching_fingerprints(self, globals, cur, solutions, matched):
        solutions.append((cur, matched))
        print(" " * len(cur) + "Solution: {} with {} remaining".format(",".join([str(x) for x in cur]), len(globals)))

        match_list = []
        for fingerprint in self.prints:
            if fingerprint.count() == 0:
                continue
            if fingerprint in cur:
                continue

            fp_matches = fingerprint.num_matches(globals)
            print(" " * (len(cur) + 1) + "Matched {}/{} with {}".format(fp_matches, len(fingerprint), fingerprint.filename))
            if fp_matches == len(fingerprint):
                # print("Matched with {}".format(fingerprint))
                reduced_globals = globals.reduce(fingerprint)

                # Match the remaining variables
                self.matching_fingerprints(reduced_globals, cur + [fingerprint], solutions, matched + fp_matches)
        return match_list


class GlobalSet:
    def __init__(self, values, filename=None):
        self.values = values
        self.filename = filename

        self.dict = {}
        for val in values:
            if val not in self.dict:
                self.dict[val] = 0

            self.dict[val] += 1

    def count(self):
        count = 0
        for val in self.dict:
            count += self.dict[val]
        return count

    def reduce(self, other_set):
        # Copy the dictionary to reduced
        reduced = {}
        for val in self.dict:
            reduced[val] = self.dict[val]

        # Remove entries from the other dict
        for var in other_set.dict:
            assert var in self.dict

            reduced[var] -= other_set.dict[var]
            if reduced[var] == 0:
                del reduced[var]

        reduced_set = GlobalSet([])
        reduced_set.dict = reduced

        return reduced_set

    def num_matches(self, other_set):
        # Find the number of items in this set which are also
        # contained in the other set
        matches = 0
        total = 0
        printed = False
        for var in self.dict:
            total += self.dict[var]

            if var in other_set.dict:
                matches += min(self.dict[var], other_set.dict[var])
                # print("Var {} in me {} times, other {} times".format(var, self.dict[var], other_set.dict[var]))
            elif not printed:
                printed = True
                print("Var {} not in other".format(var))
        return matches

    def __len__(self):
        return self.count()

    def __str__(self):
        return self.filename.split("/")[-1]


def read_nss(filename, lexer, parser):
    with open(filename) as f:
        txt = f.read()

    program = parser.parse(lexer.lex(txt))

    values = []
    for line in program.body:
        if type(line) is script.DefinedConstant:
            # Get the variable type
            # This is a global variable definition
            # var_type = line.var_type.txt
            # var_name = line.var_name.getstr()
            if type(line.var_expression) in (script.Integer, script.String):
                var_exp = line.var_expression.value.getstr()
            else:
                var_exp = None

            if var_exp is not None:
                values.append(str(var_exp).lower())

    return GlobalSet(values, filename)


if __name__ == "__main__":
    main()
