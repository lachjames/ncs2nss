import assembly as s

PRODUCTIONS = {}
OP_TYPES = []


def register_production(name, *args):
    OP_TYPES.append(name)

    def decorator_fn(f):
        for arg in args:
            def func(p):
                # obj = f(p[1:])
                # obj.line_num = hex_int(p[0].getstr())
                #
                # return obj
                return f(p)

            # PRODUCTIONS[name + " : VALUE " + arg] = func
            PRODUCTIONS[name + " : " + arg] = func
        return f

    return decorator_fn


def hex_int(x):
    # ncsdis.exe already does this conversion for us (yay!)
    return int(x)
    # return int(x, 16)


@register_production(
    "cond_jump",
    "JZ VALUE SEMI",
    "JNZ VALUE SEMI"
)
def cond_jump(p):
    return s.ConditionalJump(p[1].getstr())


@register_production(
    "jump_command",
    "JMP VALUE SEMI"
)
def jump(p):
    return s.Jump(p[1].getstr())  # hex_int(p[1].getstr()))


@register_production(
    "jump_to_subroutine",
    "JSR VALUE SEMI"
)
def jsr(p):
    return s.JumpSubroutine(p[1].getstr())  # hex_int(p[1].getstr()))


@register_production(
    "copy_down_sp",
    "CPDOWNSP VALUE VALUE SEMI"
)
def cp_down_sp(p):
    return s.CPDownSP(
        hex_int(p[1].getstr()),
        hex_int(p[2].getstr()),
    )


@register_production(
    "copy_top_sp",
    "CPTOPSP VALUE VALUE SEMI"
)
def copy_top_sp(p):
    return s.CPTopSP(
        hex_int(p[1].getstr()),
        hex_int(p[2].getstr()),
    )


@register_production(
    "copy_down_bp",
    "CPDOWNBP VALUE VALUE SEMI"
)
def copy_down_bp(p):
    return s.CPDownBP(
        hex_int(p[1].getstr()),
        hex_int(p[2].getstr()),
    )


@register_production(
    "copy_top_bp",
    "CPTOPBP VALUE VALUE SEMI"
)
def copy_top_bp(p):
    return s.CPTopBP(
        hex_int(p[1].getstr()),
        hex_int(p[2].getstr()),
    )


@register_production(
    "move_sp_command",
    "MOVSP VALUE SEMI"
)
def move_sp(p):
    return s.MoveSP(hex_int(p[1].getstr()))


@register_production(
    "rsadd_command",
    "RSADDI SEMI",
    "RSADDF SEMI",
    "RSADDS SEMI",
    "RSADDO SEMI",
    "RSADDLOC SEMI"
)
def rsadd_command(p):
    return s.RSAdd(p[0].getstr())


@register_production(
    "const",
    "CONSTI VALUE SEMI",
    "CONSTF VALUE SEMI",
    "CONSTS STRING SEMI",
    "CONSTO VALUE SEMI"
)
def const(p):
    return s.Const(
        p[0].getstr(),
        p[1].getstr()
    )


@register_production(
    "action",
    "ACTION VALUE VALUE SEMI"
)
def action(p):
    return s.Action(
        p[1].getstr(),
        int(p[2].getstr())
        # hex_int(p[3].getstr()),
        # hex_int(p[5].getstr())
    )

@register_production(
    "action",
    "SSACTION VALUE VALUE SEMI"
)
def ssaction(p):
    return s.SSAction(
        p[1].getstr(),
        int(p[2].getstr())
        # hex_int(p[3].getstr()),
        # hex_int(p[5].getstr())
    )




@register_production(
    "log_op",
    "LOGANDII SEMI",
    "LOGORII SEMI"
)
def logii(p):
    return s.Logical(p[0].getstr())


binary_ops = [
    "BOOLANDII",
    "EQII", "EQFF", "EQSS", "EQOO",
    "EQTT",
    "NEQII", "NEQFF", "NEQSS", "NEQOO",
    "NEQTT",
    "GEQII", "GEQFF",
    "GTII", "GTFF",
    "LTII", "LTFF",
    "LEQII", "LEQFF",
    "SHLEFTII", "SHRIGHTII", "USHRIGHTII",
    "ADDII", "ADDIF", "ADDFI", "ADDFF", "ADDSS", "ADDVV",
    "SUBII", "SUBIF", "SUBFI", "SUBFF", "SUBVV",
    "MULII", "MULIF", "MULFI", "MULFF", "MULVF", "MULFV",
    "DIVII", "DIVIF", "DIVFI", "DIVFF", "DIVVF",
    "MODII",
]

bops_two_VALUEs = [
    x + " SEMI" for x in binary_ops
]
bops_three_VALUEs = [
    x + " VALUE SEMI" for x in binary_ops
]


@register_production(
    "binary_op",
    *bops_two_VALUEs,
    *bops_three_VALUEs
)
def binary_ops(p):
    if len(p) == 2:
        return s.BinaryOp(p[0].getstr(), None)
    return s.BinaryOp(p[0].getstr(), hex_int(p[1].getstr()))


unary_ops = [
    "NEGI", "NEGF",
    "COMPI",
    "NOTI"
]

uops = [
    x + " SEMI" for x in unary_ops
]


@register_production(
    "unary_op",
    *uops
)
def unary_ops(p):
    return s.UnaryOp(p[0].getstr())


stack_ops = [
    "DECSPI", "INCSPI",
    "DECBPI", "INCBPI"
]
sops = [
    x + " VALUE SEMI" for x in stack_ops
]


@register_production(
    "stack_op",
    *sops
)
def stack_op(p):
    return s.StackOp(p[0].getstr(), hex_int(p[1].getstr()))


@register_production(
    "destruct",
    "DESTRUCT VALUE VALUE SEMI"
)
def destruct(p):
    # raise NotImplementedError()
    return s.Destruct()


base_ops = [
    "SAVEBP", "RESTOREBP",
]
bops = [
    x + " SEMI" for x in base_ops
]


@register_production(
    "bp_cmd",
    *bops
)
def bp_cmd(p):
    # raise NotImplementedError()
    return s.BaseCmd(p[0].getstr())


@register_production(
    "store_state_cmd",
    "STORESTATE VALUE VALUE VALUE SEMI"
)
def store_state(p):
    return s.StoreState(
        p[1].getstr(),
        hex_int(p[2].getstr()),
        hex_int(p[3].getstr())
    )


@register_production(
    "store_state_return",
    "STORESTATERETURN VALUE SEMI"
)
def store_state_return(p):
    return s.StoreStateReturn(
        p[1].getstr()
    )


@register_production(
    "noop",
    "NOOP SEMI"
)
def noop(p):
    return s.NoOp()

@register_production(
    "size",
    "T VALUE SEMI"
)
def size(p):
    return s.Size(hex_int(p[1].getstr()))
