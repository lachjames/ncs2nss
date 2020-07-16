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
int sub0000034E(int arg0, int arg1);
void sub00000452(int arg0);
void sub0000058A(object arg0, int arg1, int arg2);
void sub00000856(string arg0);

// Actual code
// main
void main() {
    int VAR_0 = sub0000034E(8, 0);
    sub00000452(VAR_0);
    sub0000058A(GetModule(), GLOBAL_13, 1);
    sub00000856("unk44_sithptla");
    sub00000856("unk44_sithptlb");
    sub00000856("unk44_sithptlc");
    sub00000856("unk44_sithptld");
    sub00000856("unk44_sithptle");
    return;
}

// sub0000034E
int sub0000034E(int arg0, int arg1) {
    float VAR_0 = (VAR_0 / 4.000000);
    int VAR_1 = (arg0 - FloatToInt(VAR_0));
    if ((VAR_1 < 1)) {
        if ((VAR_1 <= (-3))) {
            VAR_1 = 0;

        } else {
            VAR_1 = 1;
        }
    }
    return VAR_1;
    return VAR_1;
}

// sub00000452
void sub00000452(int arg0) {
    object VAR_0 = GetItemPossessedBy(GetFirstPC(), "K_COMPUTER_SPIKE");
    if (GetIsObjectValid(VAR_0)) {
        int VAR_1 = GetItemStackSize(VAR_0);
        if ((arg0 < VAR_1)) {
            arg0 = (VAR_1 - arg0);
            SetItemStackSize(VAR_0, arg0);

        } else {
            if (((arg0 > VAR_1) || (arg0 == VAR_1))) {
                DestroyObject(VAR_0, 0.000000, 0, 0.000000);
                return;
                return;

            } else {
            }
        }
    }
}

// sub0000058A
void sub0000058A(object arg0, int arg1, int arg2) {
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

// sub00000856
void sub00000856(string arg0) {
    effect VAR_0 = EffectDroidStun();
    int VAR_1 = 1;
    object VAR_2 = GetNearestObjectByTag(arg0, OBJECT_SELF, 1);
    while (GetIsObjectValid(VAR_2)) {
        ApplyEffectToObject(2, VAR_0, VAR_2, 0.000000);
        (VAR_1++);
        VAR_2 = GetNearestObjectByTag(arg0, OBJECT_SELF, VAR_1);
    }
    return;
}

