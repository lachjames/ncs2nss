import assembly as asm


def compress(program):
    pass


def graph(program, line_map):
    lines_to_subroutines, call_graph = generate_call_graph(program, line_map)
    plot_call_graph(call_graph)

    for subroutine in program.subroutines:
        generate_loop_graph(subroutine, line_map)


def generate_call_graph(program, line_map):
    lines_to_subroutines = {}

    call_graph = {}

    # The first three lines just call main()
    if program.rsadd_command:
        i = 4
    else:
        i = 3

    for subroutine in program.subroutines:
        print("Subroutine at line {}".format(i))
        lines_to_subroutines[i] = subroutine
        i += len(subroutine.commands) + 1

    for subroutine in program.subroutines:
        call_graph[subroutine] = []
        for line in subroutine.commands:
            if type(line) is asm.JumpSubroutine:
                line_number = line_map[line.line]
                print("References subroutine {}".format(line_number))
                # This is a subroutine call
                call_graph[subroutine].append(lines_to_subroutines[line_number])

            # This is a new line
            i += 1

    return lines_to_subroutines, call_graph


def generate_loop_graph(subroutine, line_map):
    for line in subroutine.commands:
        if type(line) is asm.ConditionalJump:
            pass


def plot_call_graph(call_graph):
    from graphviz import Digraph

    graph = Digraph("call_graph")
    sub_names = {}

    for i, sub in enumerate(call_graph):
        if i == 0:
            sub_name = "main"
        else:
            sub_name = "sub_{}".format(i)
        sub_names[sub] = i

        graph.node(str(sub_name))

    for i, sub in enumerate(call_graph):
        for called_sub in call_graph[sub]:
            if i == 0:
                graph.edge("main", str(sub_names[called_sub]))
            else:
                graph.edge(str(i), str(sub_names[called_sub]))

    graph.view()
