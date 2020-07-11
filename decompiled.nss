// Global Variables
int GLOBAL_0 = 1
int GLOBAL_1 = 2
int GLOBAL_2 = 3
int GLOBAL_3 = 4
int GLOBAL_4 = 5
int GLOBAL_5 = 6
int GLOBAL_6 = 3
int GLOBAL_7 = 4
int GLOBAL_8 = 5
int GLOBAL_9 = 6
int GLOBAL_10 = 7
int GLOBAL_11 = 1
int GLOBAL_12 = 2
int GLOBAL_13 = 3
int GLOBAL_14 = 4
int GLOBAL_15 = 5
int GLOBAL_16 = 6
int GLOBAL_17 = 7
int GLOBAL_18 = 8
int GLOBAL_19 = 9
int GLOBAL_20 = 10
int GLOBAL_21 = 11
int GLOBAL_22 = 12
int GLOBAL_23 = 13
int GLOBAL_24 = 14
int GLOBAL_25 = 15
int GLOBAL_26 = 16
int GLOBAL_27 = 17
int GLOBAL_28 = 18
int GLOBAL_29 = 19
int GLOBAL_30 = 20
int GLOBAL_31 = 21
int GLOBAL_32 = 22
int GLOBAL_33 = 23
int GLOBAL_34 = 24
int GLOBAL_35 = 25
int GLOBAL_36 = 26
int GLOBAL_37 = 27
int GLOBAL_38 = 28
int GLOBAL_39 = 29
int GLOBAL_40 = 30
int GLOBAL_41 = 59
int GLOBAL_42 = 0
int GLOBAL_43 = 1
int GLOBAL_44 = 2
int GLOBAL_45 = 29
int GLOBAL_46 = 30
int GLOBAL_47 = 34
int GLOBAL_48 = 35
int GLOBAL_49 = 36
int GLOBAL_50 = 37
int GLOBAL_51 = 38
int GLOBAL_52 = 39
int GLOBAL_53 = 41
int GLOBAL_54 = 42
int GLOBAL_55 = 46
int GLOBAL_56 = 47
int GLOBAL_57 = 15
int GLOBAL_58 = 10
int GLOBAL_59 = 5
int GLOBAL_60 = 2
int GLOBAL_61 = 1
int GLOBAL_62 = 2
int GLOBAL_63 = 3
int GLOBAL_64 = 20
int GLOBAL_65 = 21
int GLOBAL_66 = 22
int GLOBAL_67 = 23
int GLOBAL_68 = 24
int GLOBAL_69 = 25
int GLOBAL_70 = 26
int GLOBAL_71 = 27
int GLOBAL_72 = 28
int GLOBAL_73 = 31
int GLOBAL_74 = 32
int GLOBAL_75 = 33
int GLOBAL_76 = 40
int GLOBAL_77 = 43
int GLOBAL_78 = 44
int GLOBAL_79 = 45
int GLOBAL_80 = 48
int GLOBAL_81 = 49
int GLOBAL_82 = 50
int GLOBAL_83 = 51
int GLOBAL_84 = 52
int GLOBAL_85 = 53
int GLOBAL_86 = 54
int GLOBAL_87 = 55
int GLOBAL_88 = 56
int GLOBAL_89 = 57
int GLOBAL_90 = 58
int GLOBAL_91 = 60
int GLOBAL_92 = 61
int GLOBAL_93 = 62
int GLOBAL_94 = 63
int GLOBAL_95 = 64
int GLOBAL_96 = 65
int GLOBAL_97 = 66
int GLOBAL_98 = 67
int GLOBAL_99 = 68
int GLOBAL_100 = 69
int GLOBAL_101 = 70
int GLOBAL_102 = 71
int GLOBAL_103 = 72
int GLOBAL_104 = 1
int GLOBAL_105 = 2
int GLOBAL_106 = 3
int GLOBAL_107 = 4
int GLOBAL_108 = 0
int GLOBAL_109 = 1
int GLOBAL_110 = 2
int GLOBAL_111 = 3
int GLOBAL_112 = 4
int GLOBAL_113 = 5
int GLOBAL_114 = 6
int GLOBAL_115 = 7
int GLOBAL_116 = 8
int GLOBAL_117 = 9
int GLOBAL_118 = 10
int GLOBAL_119 = 11
int GLOBAL_120 = 12
int GLOBAL_121 = 13
int GLOBAL_122 = 14
int GLOBAL_123 = 15
int GLOBAL_124 = 16
int GLOBAL_125 = 17
int GLOBAL_126 = 18
int GLOBAL_127 = 19
int GLOBAL_128 = 1100
int GLOBAL_129 = (-6)
int GLOBAL_130 = (-5)
int GLOBAL_131 = (-4)
int GLOBAL_132 = (-2)
int GLOBAL_133 = (-1)
int GLOBAL_134 = 0

// Signatures
void main();
void sub00000D42(int arg0);
void sub00000D4A();
void sub000012AE();
int sub000014FF(object arg0);
void sub00001613(object arg0);
void sub000017F7();
void sub00001CD3();
void sub000020DC();
void sub00002114();
int sub0000233D(int arg0);
void sub000023CA();
int sub00002C19(int arg0,  int arg1);
void sub00002D99(int arg0,  int arg1);
void sub00002DBC();
int sub00003103(object arg0,  int arg1);

// Actual code
// main
void main() {
    sub00000D42(GLOBAL_72);
    sub00000D4A();
    sub000023CA();
    ApplyEffectToObject(0, EffectDamage(50, 8, 0), OBJECT_SELF, 0.000000);
    if ((sub00003103(GetArea(OBJECT_SELF), GLOBAL_9) == 1)) {
    }
    if ((sub00003103(GetArea(OBJECT_SELF), GLOBAL_11) == 1)) {
        effect VAR_0 = EffectDamageIncrease(8, 4096);
        ApplyEffectToObject(2, VAR_0, OBJECT_SELF, 0.000000);
    }
    if ((sub00003103(GetArea(OBJECT_SELF), GLOBAL_10) == 1)) {
        VAR_0 = EffectAttackIncrease(4, 0);
        ApplyEffectToObject(2, VAR_0, OBJECT_SELF, 0.000000);
        return;
    }
    return;
}

// sub00000D42
void sub00000D42(int arg0) {
    return;
}

// sub00000D4A
void sub00000D4A() {
    SetListening(OBJECT_SELF, 1);
    SetListenPattern(OBJECT_SELF, "GEN_I_WAS_ATTACKED", 1);
    SetListenPattern(OBJECT_SELF, "GEN_I_AM_DEAD", 3);
    SetListenPattern(OBJECT_SELF, "GEN_CALL_TO_ARMS", 6);
    if ((GetHasSpell(48, OBJECT_SELF) || GetHasSpell(19, OBJECT_SELF))) {
        SetListenPattern(OBJECT_SELF, "GEN_SUPRESS_FORCE", 9);
    }
    SetListenPattern(OBJECT_SELF, "GEN_GRENADE_TOSSED", 12);
    SetListenPattern(OBJECT_SELF, "GEN_I_SEE_AN_ENEMY", 14);
    SetListenPattern(OBJECT_SELF, "GEN_COMBAT_ACTIVE", 15);
    sub000012AE();
    string VAR_0 = GetTag(OBJECT_SELF);
    if (None) {
    }
    if (None) {
    }
    if (None) {
    }
    if (None) {
    }
    if (None) {
    }
    if (None) {
    }
    if (None) {
    }
    if (None) {
    }
    if (None) {
    }
    if (((((((((((VAR_0 != "Carth") && (VAR_0 != "Bastila")) && (VAR_0 != "Cand")) && (VAR_0 != "HK47")) && (VAR_0 != "Jolee")) && (VAR_0 != "Juhani")) && (VAR_0 != "Mission")) && (VAR_0 != "T3M4")) && (VAR_0 != "Zaalbar")) && (!GetIsPC(OBJECT_SELF)))) {
        sub000014FF(OBJECT_SELF);
    }
    if ((sub0000233D(GLOBAL_33) || GetIsEncounterCreature(OBJECT_SELF))) {
        string VAR_3;
        int VAR_1 = 1;
        object VAR_6;
        object VAR_4;
        float VAR_5;
        float VAR_2 = 100.000000;
        while ((VAR_1 < 40)) {
            if ((VAR_1 < 10)) {
                VAR_3 = (("ZoneController" + "0") + IntToString(VAR_1));

            } else {
                VAR_3 = ("ZoneController" + IntToString(VAR_1));
            }
            VAR_4 = GetObjectByTag(VAR_3, 0);
            (VAR_1++);
        }
        if (None) {
        }
        if ((GetIsObjectValid(VAR_4) && (VAR_5 < 30.000000))) {
            int VAR_7 = StringToInt(GetStringRight(GetTag(VAR_4), 2));
            SetLocalNumber(OBJECT_SELF, GLOBAL_135, VAR_7);
        }
    }
    return;
}

// sub000012AE
void sub000012AE() {
    string VAR_2;
    int VAR_0 = GetLocalNumber(OBJECT_SELF, GLOBAL_101);
    if ((VAR_0 > 0)) {
        string VAR_1;
        if ((VAR_0 < 10)) {
            VAR_1 = ("0" + IntToString(VAR_0));

        } else {
            VAR_1 = IntToString(VAR_0);
        }
        VAR_2 = ("WP_" + VAR_1);

    } else {
        VAR_2 = ("WP_" + GetTag(OBJECT_SELF));
    }
    VAR_1 = 1;
    string VAR_3 = (VAR_2 + "_01");
    object VAR_4 = GetWaypointByTag(VAR_3);
    while (GetIsObjectValid(VAR_4)) {
        (VAR_1++);
        if ((VAR_1 < 10)) {
            VAR_3 = ((VAR_2 + "_0") + IntToString(VAR_1));

        } else {
            VAR_3 = ((VAR_2 + "_") + IntToString(VAR_1));
        }
        VAR_4 = GetWaypointByTag(VAR_3);
    }
    VAR_1 = (VAR_1 - 1);
    if ((VAR_1 > 0)) {
        SetLocalNumber(OBJECT_SELF, GLOBAL_102, VAR_1);
    }
    return;
}

// sub000014FF
int sub000014FF(object arg0) {
    int VAR_0 = GetRacialType(arg0);
    int VAR_1 = GetStandardFaction(arg0);
    int VAR_2 = GetSubRace(arg0);
    if (None) {
    }
    if (None) {
    }
    if ((((Random(4) == 0) && (VAR_0 != 5)) && (VAR_2 != GLOBAL_85))) {
        sub00001613(arg0);
        VAR_3 = 1;

    } else {
        VAR_3 = 0;
    }
    return 0;
}

// sub00001613
void sub00001613(object arg0) {
    int VAR_0 = GetHitDice(arg0);
    if ((VAR_0 > GLOBAL_88)) {
        sub000017F7();
        if ((Random(2) == 0)) {
            sub000017F7();
        }
        if ((Random(2) == 0)) {
            sub00001CD3();
        }

    } else {
        if (None) {
        }
        if (((VAR_0 <= GLOBAL_88) && (VAR_0 > GLOBAL_87))) {
            sub00001CD3();
            if ((Random(3) == 0)) {
                sub000017F7();
            }
            if ((Random(2) == 0)) {
                sub00001CD3();
            }
            return;

        } else {
            if (None) {
            }
            if (((VAR_0 <= GLOBAL_87) && (VAR_0 > GLOBAL_86))) {
                sub00001CD3();
                if ((Random(2) == 0)) {
                    sub00002114();
                }

            } else {
                sub00002114();
                if ((Random(3) == 0)) {
                    sub00002114();
                }
                if ((Random(4) == 0)) {
                    sub00001CD3();

                } else {
                }
            }
        }
    }
}

// sub000017F7
void sub000017F7() {
    string VAR_2;
    int VAR_0 = 1;
    int VAR_1 = Random(16);
    if ((VAR_1 == 0)) {
        VAR_2 = "g_i_drdrepeqp003";
    } else if ((VAR_1 == 1)) {
        VAR_2 = "g_w_thermldet01";
    } else if ((VAR_1 == 2)) {
        VAR_2 = "g_i_medeqpmnt03";
    } else if ((VAR_1 == 3)) {
        VAR_2 = "g_i_cmbtshot003";
    } else if ((VAR_1 == 4)) {
        VAR_2 = "g_i_cmbtshot002";
    } else if ((VAR_1 == 5)) {
        VAR_2 = "g_i_adrnaline006";
    } else if ((VAR_1 == 6)) {
        VAR_2 = "g_i_adrnaline005";
    } else if ((VAR_1 == 7)) {
        VAR_2 = "g_i_adrnaline004";
    } else if ((VAR_1 == 8)) {
        VAR_2 = "g_w_poisngren01";
        VAR_0 = 2;
    } else if ((VAR_1 == 9)) {
        VAR_2 = "g_w_sonicgren01";
        VAR_0 = 2;
    } else if ((VAR_1 == 10)) {
        VAR_2 = "g_w_adhsvgren001";
        VAR_0 = 2;
    } else if ((VAR_1 == 11)) {
        VAR_2 = "g_w_cryobgren001";
        VAR_0 = 2;
    } else if ((VAR_1 == 12)) {
        VAR_2 = "g_w_firegren001";
        VAR_0 = 2;
    } else if ((VAR_1 == 13)) {
        VAR_2 = "g_w_iongren01";
        VAR_0 = 2;
    } else if ((VAR_1 == 14)) {
        VAR_2 = "g_i_credits015";
        VAR_0 = (Random(50) + 50);
    } else if ((VAR_1 == 15)) {
        VAR_2 = "g_w_firegren001";

    } else {
    }
    CreateItemOnObject(VAR_2, OBJECT_SELF, VAR_0);
    return;
}

// sub00001CD3
void sub00001CD3() {
    string VAR_2;
    int VAR_0 = 1;
    int VAR_1 = Random(15);
    if ((VAR_1 == 0)) {
        VAR_2 = "g_i_drdrepeqp002";
    } else if ((VAR_1 == 1)) {
        VAR_2 = "g_i_credits004";
        VAR_0 = 50;
        sub000020DC();
    } else if ((VAR_1 == 2)) {
        VAR_2 = "g_i_medeqpmnt02";
    } else if ((VAR_1 == 3)) {
        VAR_2 = "g_i_cmbtshot001";
    } else if ((VAR_1 == 4)) {
        VAR_2 = "g_i_adrnaline003";
    } else if ((VAR_1 == 5)) {
        VAR_2 = "g_i_adrnaline002";
    } else if ((VAR_1 == 6)) {
        VAR_2 = "g_i_adrnaline001";
    } else if ((VAR_1 == 7)) {
        VAR_2 = "g_w_stungren01";
        VAR_0 = 2;
    } else if ((VAR_1 == 8)) {
        VAR_2 = "g_w_fraggren01";
        VAR_0 = 2;
    } else if ((VAR_1 == 9)) {
        VAR_2 = "g_w_poisngren01";
    } else if ((VAR_1 == 10)) {
        VAR_2 = "g_w_sonicgren01";
    } else if ((VAR_1 == 11)) {
        VAR_2 = "g_w_adhsvgren001";
    } else if ((VAR_1 == 12)) {
        VAR_2 = "g_w_cryobgren001";
    } else if ((VAR_1 == 13)) {
        VAR_2 = "g_w_iongren01";

    } else {
    }
    CreateItemOnObject(VAR_2, OBJECT_SELF, VAR_0);
    return;
}

// sub000020DC
void sub000020DC() {
    CreateItemOnObject("g_i_credits015", OBJECT_SELF, (Random(4) + 1));
    return;
}

// sub00002114
void sub00002114() {
    string VAR_2;
    int VAR_0 = 1;
    int VAR_1 = Random(6);
    if ((VAR_1 == 0)) {
        VAR_2 = "g_i_drdrepeqp001";
    } else if ((VAR_1 == 1)) {
        VAR_2 = "g_i_credits001";
        VAR_0 = 5;
        sub000020DC();
    } else if ((VAR_1 == 2)) {
        VAR_2 = "g_i_credits002";
        VAR_0 = 10;
        sub000020DC();
    } else if ((VAR_1 == 3)) {
        VAR_2 = "g_i_credits003";
        VAR_0 = 25;
        sub000020DC();
    } else if ((VAR_1 == 4)) {
        VAR_2 = "g_i_medeqpmnt01";
    } else if ((VAR_1 == 5)) {
        VAR_2 = "g_w_fraggren01";

    } else {
    }
    CreateItemOnObject(VAR_2, OBJECT_SELF, VAR_0);
    return;
}

// sub0000233D
int sub0000233D(int arg0) {
    int VAR_0 = GetLocalBoolean(OBJECT_SELF, arg0);
    if ((VAR_0 > 0)) {
        VAR_1 = 1;

    } else {
        VAR_1 = 0;
    }
    return 0;
}

// sub000023CA
void sub000023CA() {
    return;
}

// sub00002C19
int sub00002C19(int arg0,  int arg1) {
    int VAR_1;
    int VAR_0 = sub0000233D(GLOBAL_92);
    if (None) {
    }
    if (((arg0 == arg1) && (sub0000233D(GLOBAL_92) == 0))) {
        VAR_1 = (-1);
        sub00002D99(GLOBAL_92, 1);

    } else {
        if (None) {
        }
        if (((arg1 == 1) && (sub0000233D(GLOBAL_92) == 1))) {
            VAR_1 = 1;
            sub00002D99(GLOBAL_92, 0);
            VAR_2 = VAR_1;
            return VAR_1;
        } else if ((sub0000233D(GLOBAL_92) == 0)) {
            VAR_1 = 1;
        } else if ((sub0000233D(GLOBAL_92) == 1)) {
            VAR_1 = (-1);

        } else {
        }
    }
}

// sub00002D99
void sub00002D99(int arg0,  int arg1) {
    SetLocalBoolean(OBJECT_SELF, arg0, arg1);
    return;
}

// sub00002DBC
void sub00002DBC() {
    int VAR_0 = d8(1);
    if ((VAR_0 == 1)) {
        ActionPlayAnimation(103, 1.000000, 0.000000);
    } else if ((VAR_0 == 2)) {
        ActionPlayAnimation(102, 1.000000, 0.000000);
    } else if ((VAR_0 == 3)) {
        ActionPlayAnimation(1, 1.000000, 3.000000);

    } else {
        if (None) {
        }
        if ((((VAR_0 == 4) || (VAR_0 == 5)) && (GetRacialType(OBJECT_SELF) != 5))) {
            if ((GetGender(OBJECT_SELF) == 0)) {
                sub00002D99(GLOBAL_100, 0);
                ActionPlayAnimation(24, 1.000000, 20.400000);
                ActionDoCommand(sub00002D99(GLOBAL_100, 1));
            } else if ((GetGender(OBJECT_SELF) == 1)) {
                sub00002D99(GLOBAL_100, 0);
                ActionPlayAnimation(24, 1.000000, 13.300000);
                ActionDoCommand(sub00002D99(GLOBAL_100, 1));
            }
            return;

        } else {
            if ((((VAR_0 == 6) || (VAR_0 == 4)) || (VAR_0 == 5))) {
                ActionPlayAnimation(100, 1.000000, 0.000000);
            } else if ((VAR_0 == 7)) {
                ActionPlayAnimation(101, 1.000000, 0.000000);
            } else if ((VAR_0 == 8)) {
                sub00002D99(GLOBAL_100, 0);
                ActionPlayAnimation(1, 1.000000, 5.000000);
                ActionDoCommand(sub00002D99(GLOBAL_100, 1));

            } else {
            }
        }
    }
}

// sub00003103
int sub00003103(object arg0,  int arg1) {
    int VAR_0;
    if (None) {
    }
    if (None) {
    }
    if ((((arg1 >= 0) && (arg1 <= 19)) && GetIsObjectValid(arg0))) {
        VAR_0 = GetLocalBoolean(arg0, arg1);
        } else if ((VAR_0 > 0)) {
            VAR_1 = 1;

        } else {
            VAR_1 = 0;
        }

    } else {
    }
    return 0;
}

