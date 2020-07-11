import os
import sys
import subprocess
import shutil
import preprocessing
import tqdm
from multiprocessing import Pool as Pool
from multiprocessing import Queue

max_N = 100

import os, sys


class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


total = 0
succs = 0


def make_callback(pbar):
    def update(result):
        global total, succs
        pbar.update(1)
        total += 1
        if result:
            succs += 1
            pbar.set_description("Succs: {}/{}".format(succs, total))

    return update


def main():
    files = list(os.listdir("bank"))
    num_files = len(files)

    paths = ["bank/" + x for x in files if x.endswith(".ncs")]
    pbar = tqdm.tqdm(total=num_files)

    succs = 0
    total = 0

    pool = Pool(4)
    for path in paths:
        pool.apply_async(test_infile, args=(path,), callback=make_callback(pbar))
    pool.close()
    pool.join()


def test_infile(infile):
    with HiddenPrints():
        try:
            shutil.copy(infile, "tmp.ncs")

            process = subprocess.Popen(
                "xt\\ncsdis.exe --assembly --kotor tmp.ncs".format(infile),
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )
            txt = process.communicate()[0].decode()

            ncs_program = preprocessing.NCSProgram(txt)
            ncs_program.to_nss()
        except Exception as e:
            return False

    return True


if __name__ == "__main__":
    main()
