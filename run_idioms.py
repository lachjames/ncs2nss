def reduce_idioms(blocks, idioms):
    changed = True

    while changed:
        changed = False
        for idiom_cls in idioms:
            idiom = idioms[idiom_cls]()
            i = 0
            while i < len(blocks):
                if idiom.recognize(i, blocks):
                    changed = True

                    conversion = idiom.convert(i, blocks)
                    for convert_idx in conversion:
                        blocks[convert_idx] = conversion[convert_idx]
                i += 1

    return blocks
