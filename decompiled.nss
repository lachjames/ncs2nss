// Global Variables
int GLOBAL_0 = 0
int GLOBAL_1 = 1
int GLOBAL_2 = 2
int GLOBAL_3 = 3
int GLOBAL_4 = 4
int GLOBAL_5 = 5
int GLOBAL_6 = 6
int GLOBAL_7 = 7
int GLOBAL_8 = 8
int GLOBAL_9 = 9
int GLOBAL_10 = 10
int GLOBAL_11 = 11
int GLOBAL_12 = 12
int GLOBAL_13 = 13
int GLOBAL_14 = 14
int GLOBAL_15 = 15
int GLOBAL_16 = 16
int GLOBAL_17 = 17
int GLOBAL_18 = 18
int GLOBAL_19 = 19
int GLOBAL_20 = 1100
int GLOBAL_21 = (-6)
int GLOBAL_22 = (-5)
int GLOBAL_23 = (-4)
int GLOBAL_24 = (-2)
int GLOBAL_25 = (-1)
int GLOBAL_26 = 0

// Signatures
void main();
void sub000004EC(object arg0, int arg1, int arg2);

// Actual code
// main
void main() {
    BarkString(1, 42423);
    return;
}

// sub000004EC
void sub000004EC(object arg0, int arg1, int arg2) {
    int VAR_0 = GetHitDice(GetFirstPC());
    if ((arg2 == 1)) {
        if (((((arg1 == GLOBAL_16) || (arg1 == GLOBAL_11)) || (arg1 == GLOBAL_10)) || (arg1 == GLOBAL_9))) {
            GiveXPToCreature(GetFirstPC(), (VAR_0 * 15));

        } else {
            if ((((arg1 == GLOBAL_15) || (arg1 == GLOBAL_8)) || (arg1 == GLOBAL_12))) {
                GiveXPToCreature(GetFirstPC(), (VAR_0 * 20));
                if ((((arg1 >= 0) && (arg1 <= 19)) && GetIsObjectValid(arg0))) {
                    if (((arg2 == 1) || (arg2 == 0))) {
                        SetLocalBoolean(arg0, arg1, arg2);
                    }
                    return;
                }
                return;

            } else {
                if (((arg1 == GLOBAL_14) || (arg1 == GLOBAL_13))) {
                    GiveXPToCreature(GetFirstPC(), (VAR_0 * 10));

                } else {
                }
            }
        }
    }
}

