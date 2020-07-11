import os
import sys
import subprocess
import shutil
import preprocessing

max_N = 100


def main():
    passed = 0
    N = 0
    for file in os.listdir("bank"):
        if N >= max_N:
            break

        filename = "bank/" + file

        result = test(filename)
        if result is None:
            # Test passed
            passed += 1
        N += 1

    print("{}/{} passed".format(passed, N))


def test(infile):
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
        return e

    return None


if __name__ == "__main__":
    main()
