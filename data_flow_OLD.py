

def compress_subroutine(sub, labels):
    commands = sub.commands

    changed = True
    while changed:
        changed = False

        for idiom_name in IDIOMS:
            idiom_obj = IDIOMS[idiom_name]()
            i = 0
            while i < len(commands):
                if idiom_obj.recognize(i, commands, None):
                    changed = True

                    replace_lines, replacement = idiom_obj.convert(i, commands, None)

                    cur_pointer = i + sub.start_line
                    # Move labels
                    for label_name in labels:
                        label_pointer = labels[label_name]
                        assert not (i < label_pointer <= i + replace_lines), "Trying to replace code which a label points to on line {}".format(i)

                        if label_pointer <= i:
                            continue
                        new_pointer = label_pointer - replace_lines + 1  # TODO: Allow for multi-line replacements

                        labels[label_name] = new_pointer

                    del commands[i:i + replace_lines]
                    commands.insert(i, replacement)
                else:
                    i += 1

    sub.commands = commands
    return sub
