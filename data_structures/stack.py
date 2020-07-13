from data_flow_types import ObjectType
from data_structures.propagate import PropagateVector, PropagateMatrix
from colorama import init, Fore
from data_structures.util import HTMLColors

init()


def test_matrix():
    pass


class StackMatrix:
    def __init__(self, num_commands, stack_size, sub):
        self.num_commands = num_commands
        self.stack_size = stack_size
        self.sub = sub

        self.matrix = PropagateMatrix((num_commands, stack_size))  # [[None for _ in range(stack_size)] for _ in range(num_commands)]
        self.var_names = PropagateMatrix((num_commands, stack_size))  # [[None for _ in range(stack_size)] for _ in range(num_commands)]
        self.types = PropagateMatrix((num_commands, stack_size))  # [[None for _ in range(stack_size)] for _ in range(num_commands)]

        self.fresh = [[False for _ in range(stack_size)] for _ in range(num_commands)]

        self.sps = PropagateVector(num_commands, default_value=0)  # [0 for _ in range(num_commands)]
        self.bps = PropagateVector(num_commands, default_value=0)  # [0 for _ in range(num_commands)]

        self.num_vars = 0

        self.defines_local = [None for _ in range(num_commands)]

        self.return_value = None

    def __getitem__(self, pos):
        return self.matrix[pos[0], pos[1]]

    def __setitem__(self, pos, value):
        self.matrix[pos[0], pos[1]] = value

    def push(self, obj_value, obj_type, start_command):
        self.fresh[start_command][self._top_of_stack(start_command)] = True
        self._modify_sp(start_command, 1)
        self.propagate(obj_value, obj_type, start_command, -4)

    def pop(self, i):
        if self.get_type(i, -4) is ObjectType.VECTOR:
            value = self.get_value(i, -4)
            self._modify_sp(i, -3)
        else:
            value = self.get_value(i, -4)
            self._modify_sp(i, -1)

        return value

    def get_value(self, start_command, offset):
        # We need to mark this as having been used like a local variable
        pos = self.sp_offset_to_pos(start_command, offset)
        return self.matrix[start_command, pos]

    def get_type(self, i, offset):
        return self.types[i, self.sp_offset_to_pos(i, offset)]

    def propagate(self, obj, obj_type, start_command, offset):
        pos = self.sp_offset_to_pos(start_command, offset)
        # for cmd in range(start_command, self.num_commands):
        self[start_command, pos] = obj
        self.types[start_command, pos] = obj_type

    def set_local(self, start_command, offset):
        pos = self.sp_offset_to_pos(start_command, offset)
        has_set = False
        if self.var_names[start_command, pos] is None:
            if self.sub.name == "global":
                name = "GLOBAL_{}".format(self.num_vars)
            else:
                name = "VAR_{}".format(self.num_vars)

            if self.get_type(start_command, offset) is ObjectType.VECTOR:
                self.var_names[start_command, pos] = name
                self.var_names[start_command, pos + 1] = name
                self.var_names[start_command, pos + 2] = name
            else:
                self.var_names[start_command, pos] = name
            has_set = True

        if has_set:
            self.num_vars += 1

    def modify_sp(self, start_command, value):
        self._modify_sp(start_command, value // 4)

    def sp_offset_to_pos(self, i, offset):
        return self._top_of_stack(i) + (offset // 4)

    def destruct(self, command_start, size, save_start, save_length):
        saved_items = []

        while save_length > 0:
            offset = (save_start - save_length) - 4
            # print("Saving item from offset {}".format(offset))
            saved_items.append(
                (self.get_value(command_start, offset), self.get_type(command_start, offset))
            )
            save_length -= 4

        # print("Saved {} item(s): {}".format(len(saved_items), saved_items))
        #
        # print("Taking {} items off stack".format(destruct_size // 4))

        self.modify_sp(command_start, -size // 4)

        # print("Putting {} items on stack".format(len(saved_items)))

        while len(saved_items) > 0:
            item, item_type = saved_items.pop()
            pos = self._top_of_stack(command_start)
            self.propagate(item, item_type, command_start, pos)
            self.modify_sp(command_start, 1)

    def get_assignments(self):
        # print(self.var_names)
        var_assignments = {i: [] for i in range(self.num_commands)}

        for stack_pos in range(self.stack_size):
            pos_assigns = self.var_names.values[stack_pos]
            # cmd_assigns is a dict from stack_pos -> value
            for cmd in pos_assigns:
                var_assignments[cmd].append((stack_pos, self.var_names[cmd, stack_pos]))

        # print("VAR ASSIGNMENTS")
        # print(var_assignments)
        return var_assignments

    def match_assignments(self, subroutine, subroutines, global_data):
        assigns = self.get_assignments()

        assignment_dict = {}
        for cmd_idx in range(self.num_commands):
            cmd_assigns = assigns[cmd_idx]
            if len(cmd_assigns) == 0:
                continue
            for stack_pos, var_name in cmd_assigns:
                # print("Assigned variable {} (stack pos {}) at cmd {}".format(var_name, stack_pos, cmd_idx))
                # The variable named "var_name" was assigned somewhere before this point
                # We need to find that point by going backwards
                i = cmd_idx
                while i >= 0:
                    # We need to find the last time space was allocated to the stack
                    # at this stack position
                    if i == 0:
                        if self._top_of_stack(0) > 0:
                            break
                        else:
                            raise Exception("Variable {} used without being pushed to the stack first".format(var_name))

                    if self.fresh[i][stack_pos]:
                        # print("{} first fresh at {}".format(stack_pos, i))
                        break

                    i -= 1

                # At this point, i = the index of the command which should be marked as creating the variable

                # print("Found {} defined at {}".format(var_name, i))
                # We need to try to infer the variable type
                var_type = self.infer_type(i, cmd_idx, stack_pos, subroutine, subroutines, global_data)

                assignment_dict[var_name] = (var_type, i)

        return assignment_dict

    def infer_type(self, i, j, stack_pos, subroutine, subroutines, global_data):
        # print("Inferring type of variable declared at {}, assigned at {}, at pos {}".format(i, j, stack_pos))
        # print(self.types)
        if self.types[j, stack_pos] is not None:
            var_type = ObjectType.NAME_MAP[self.types[j, stack_pos]]
        elif self.types[i, stack_pos] is not None:
            var_type = ObjectType.NAME_MAP[self.types[i, stack_pos]]
        elif stack_pos < 0:
            arg_types = subroutines[subroutine.name].arg_types
            if -stack_pos <= len(arg_types):
                var_type = ObjectType.NAME_MAP[arg_types[-stack_pos + 1]]
            else:
                assert global_data is not None
                # Get a global variable
                _, var_type = global_data.from_offset((-stack_pos + 1 - len(arg_types)) * 4)
        else:
            var_type = "unknown"
            print("Warning: failed type inference on cmd {} ({}), getting from pos {}".format(
                subroutine.commands[i],
                i,
                stack_pos)
            )
            print(self.matrix.get_frame(i))
            with open("html/dump.html", "w") as f:
                f.write(self.html())
            # exit()
            # raise Exception("Failed to calculate type of block {} = {} with sp = {}".format(i, blocks[i], pos - 1))

        return var_type

    def _top_of_stack(self, i):
        return self.sps[i]

    def _modify_sp(self, i, offset):
        self.sps[i] = self.sps[i] + offset

    def html(self):
        preamble = """
        <style>
        table, th, td {
            border: 1px dotted grey;
        }
        body {
            background-color:black;
        }
        </style>
        """
        string = [preamble, "<table style=\"color:white\">"]

        # Header row
        string.append("<tr><td></td>")
        for i in range(self.num_commands):
            string.append("<th>" + str(i) + "</th>")
        string.append("</tr>")

        for stack_pos in range(self.stack_size):
            string.append("<tr><td><b>" + str(stack_pos) + "</b></td>")
            changed = False
            for cmd in range(self.num_commands):
                if stack_pos >= self._top_of_stack(cmd):
                    col = HTMLColors.RED
                else:
                    col = HTMLColors.GREEN
                string.append("<td style=\"color:{}\">".format(col))
                item = self.matrix[cmd, stack_pos]
                if item is None:
                    string.append("--")
                else:
                    changed = True
                    val = str(item)
                    if len(val) > 13:
                        val = val[:10] + "..."
                    string.append(val)
                string.append("</td>")

            string.append("</tr>")
            if not changed:
                break

        string.append("<tr style=\"color:{}\">".format(HTMLColors.DARKBLUE) + "<td>SP</td>")
        for idx in range(self.num_commands):
            string.append("<td>" + str(self.sps[idx]) + "</td>")
        string.append("</tr>")

        var_assignments = self.get_assignments()

        string.append("<tr style=\"color:{}\">".format(HTMLColors.DARKBLUE) + "<td>Names</td>")
        for idx in range(self.num_commands):
            if len(var_assignments[idx]) == 0:
                string.append("<td>--</td>")
            else:
                string.append("<td>" + str(var_assignments[idx][0])[1:-1] + "</td>")
        string.append("</tr>")

        string.append("</table>")
        return "".join(string)

# if __name__ == "__main__":
#     main()
