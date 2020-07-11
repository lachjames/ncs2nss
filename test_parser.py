# import sys
# import subprocess
# import shutil
# import preprocessing
#
# infile = sys.argv[1]
#
# if infile.endswith(".pcode"):
#     with open(infile, "r") as f:
#         txt = f.read()
# else:
#     # Compile first if ends with nss
#     if infile.endswith("nss"):
#         # subprocess.run("nwnnsscomp.exe -c --optimize -o tmp.ncs {}".format(infile), shell=True)
#         subprocess.run("nwnnsscomp.exe -c -o tmp.ncs {}".format(infile), shell=True)
#     else:
#         shutil.copy(infile, "tmp.ncs")
#
#     process = subprocess.Popen("xt\\ncsdis.exe --assembly --kotor tmp.ncs".format(infile), shell=True, stdout=subprocess.PIPE)
#     txt = process.communicate()[0].decode()
#
#     with open("raw.pcode", "w") as f:
#         f.write("\n".join([x.strip() for x in txt.split("\n")]))
#
# # line_map = parsing.line_map(txt)
# # txt, labels = parsing.preprocess(txt)
#
# ncs_program = preprocessing.NCSProgram(txt)
#
# # print()
# # for sub_name in ncs_program.subs:
# #     print("*** SUBROUTINE {} ***".format(sub_name))
# #     sub = ncs_program.subs[sub_name]
# #     for i, line in enumerate(sub.lines):
# #         print("{}: {}".format(i, line), end="")
# #         for label in sub.labels:
# #             if sub.labels[label] == i:
# #                 print(" <- " + label, end="")
# #                 break
# #         print()
# #     print()
#
# nss_code = ncs_program.to_nss()
#
# with open("decompiled.nss", "w") as f:
#     f.write(nss_code)
# # exit()
# #
# # print("*** PREPROCESSED CODE ***")
# # for i, line in enumerate(txt.split("\n")):
# #     print("{}: {}".format(i, line))
# #
# # print()
# # print()
# #
# # print("*** LABELS ***")
# # lines = txt.split("\n")
# # for lbl in labels:
# #     print("{}: {}".format(lbl, lines[labels[lbl]]))
# #
# # lexer = parsing.Lexer()
# # parser = parsing.Parser(lexer)
# # p = parser.get_parser()
# #
# # # for token in lexer.lex(txt):
# # #     print(token)
# #
# # program = p.parse(lexer.lex(txt))
# #
# # main_sub = control_flow.Subroutine(2, program.subroutines[0], labels)
# # # main_sub = control_flow.Subroutine(2+len(program.subroutines[0].commands), program.subroutines[1], labels)
# # # main_sub = data_flow.compress_subroutine(program.subroutines[0], labels)
# #
# # df = data_flow.DataFlow(main_sub.asm_subroutine)
# # main_sub.asm_subroutine.commands = df.blocks
# #
# # for i, line in enumerate(main_sub.asm_subroutine.commands):
# #     print("{}: {}".format(i, line))
# #
# # main_sub = control_flow.Subroutine(2, main_sub.asm_subroutine, labels)
# # cfg = control_flow.ControlFlowAnalysis(main_sub)
# #
# # # blocks = control_flow.sub_basic_blocks(main_sub)
# # #
# # # print("Blocks found at:")
# # # for block in blocks:
# # #     print("  -", block.address)
# # #
# # # for block in control_flow.forward_visit(blocks):
# # #     print("Block: ", block.address)
# # #
# # # control_flow.compute_dominators(blocks)
# # # for block in blocks:
# # #     for dom in block.dominators:
# # #         print("{} dominates {}".format(dom.address, block.address))
# # #
# # # loops = control_flow.compute_natural_loops(blocks)
# # # for loop in loops.get_loops():
# # #     print("Loop starting at", loop.header.address)
# # #     for block in loop.blocks:
# # #         print("  -", block.address)
# # #
# # # control_flow.plot_blocks(blocks)
# # #
# # inv_labels = {v: k for k, v in labels.items()}
# #
# # for block in cfg.blocks:
# #     print("-- Block --")
# #     for i in range(block.nodes[0].address, block.nodes[0].address + block.nodes[0].length):
# #         if i in inv_labels:
# #             lbl = " <--  " + inv_labels[i]
# #         else:
# #             lbl = ""
# #         print("{}: {}{}".format(i, df.blocks[i - 2], lbl))
# #         # print("{}: {}{}".format(i, lines[i], lbl))
# #
# # code = backend.backend(df.blocks)
# # print(code)
#
# # analysis.graph(program, line_map)
#
# # print("Success!")
#
# # print(program.convert("test"))
# #
# # void main () {
# #     SetGlobalFadeIn(0.0, 0.0, 0.0, 1.0, 0.0);
# #     SetLockOrientationInDialog(GetObjectByTag("raceannoun031", 0), 1);
# #
# #     int i = 0;
# #     AssignCommand(GetFirstPC(), JumpToLocation(GetLocation(GetObjectByTag("tar03_wpraceover2", 0))));
# #
# #     string name = "tar03_wpswoopie";
# #
# #     while (GetIsObjectValid(name)) {
# #         GetObjectByTag("tar03_wpswoopie", i);
# #
# #         i += 1;
# #     }
# # }
