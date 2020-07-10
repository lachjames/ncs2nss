// Global Variables
int GLOBAL_0 = 1;
int GLOBAL_1 = 2;
int GLOBAL_2 = 3;
int GLOBAL_3 = 4;
int GLOBAL_4 = 5;
int GLOBAL_5 = 6;
int GLOBAL_6 = 3;
int GLOBAL_7 = 4;
int GLOBAL_8 = 5;
int GLOBAL_9 = 6;
int GLOBAL_10 = 7;
int GLOBAL_11 = 8;
int GLOBAL_12 = 9;
int GLOBAL_13 = 10;
int GLOBAL_14 = 11;
int GLOBAL_15 = 1;
int GLOBAL_16 = 2;
int GLOBAL_17 = 3;
int GLOBAL_18 = 4;
int GLOBAL_19 = 5;
int GLOBAL_20 = 6;
int GLOBAL_21 = 7;
int GLOBAL_22 = 8;
int GLOBAL_23 = 9;
int GLOBAL_24 = 10;
int GLOBAL_25 = 11;
int GLOBAL_26 = 12;
int GLOBAL_27 = 13;
int GLOBAL_28 = 14;
int GLOBAL_29 = 15;
int GLOBAL_30 = 16;
int GLOBAL_31 = 17;
int GLOBAL_32 = 18;
int GLOBAL_33 = 19;
int GLOBAL_34 = 20;
int GLOBAL_35 = 21;
int GLOBAL_36 = 22;
int GLOBAL_37 = 23;
int GLOBAL_38 = 24;
int GLOBAL_39 = 25;
int GLOBAL_40 = 26;
int GLOBAL_41 = 27;
int GLOBAL_42 = 28;
int GLOBAL_43 = 29;
int GLOBAL_44 = 30;
int GLOBAL_45 = 31;
int GLOBAL_46 = 32;
int GLOBAL_47 = 84;


// Signatures
void StartingConditional();

// Actual code
// StartingConditional
int StartingConditional() {
    float VAR_0 = 35.000000;
    float VAR_1 = 60.000000;
    float VAR_2 = 100.000000;
    float VAR_3 = 150.000000;
    float VAR_4 = 210.000000;
    float VAR_20;
    int VAR_5 = GetGlobalNumber("MIN_RACE_GEAR");
    float VAR_6 = IntToFloat(GetGlobalNumber("MIN_TENTH_GEAR"));
    object VAR_21;
    float VAR_7 = SWMG_GetPosition(OBJECT_SELF).z;
    int VAR_8 = GetTimeHour();
    if (None) {
    }
    if (((GetTimeHour() < 24) && (VAR_5 == (-5)))) {
        SetGlobalNumber("MIN_TIME_MIL", (GetTimeMillisecond() / 10));
        SetGlobalNumber("MIN_TIME_SEC", GetTimeSecond());
        SetGlobalNumber("MIN_TIME_MIN", GetTimeMinute());
        SetGlobalNumber("MIN_TIME_HOUR", GetTimeHour());
        VAR_5 = (-4);
        SetGlobalNumber("MIN_RACE_GEAR", VAR_5);
    }
    VAR_8 = GetGlobalNumber("MIN_TIME_MIL");
    int VAR_9 = GetGlobalNumber("MIN_TIME_SEC");
    int VAR_10 = GetGlobalNumber("MIN_TIME_MIN");
    int VAR_11 = GetGlobalNumber("MIN_TIME_HOUR");
    int VAR_12 = GetGlobalNumber("MIN_RACE_LAP");
    int VAR_13 = (GetTimeMillisecond() / 10);
    int VAR_14 = GetTimeSecond();
    int VAR_15 = GetTimeMinute();
    int VAR_16 = GetTimeHour();
    float VAR_17 = (VAR_17 + ((((VAR_8 / 100.000000) + VAR_9) + (VAR_10 * 60)) + ((VAR_11 * 2) * 60)));
    float VAR_18 = 0.000000;
    if ((VAR_16 < VAR_11)) {
        VAR_16 = (VAR_16 + 24);
    }
    VAR_18 = (VAR_18 + ((((VAR_13 / 100.000000) + VAR_14) + (VAR_15 * 60)) + ((VAR_16 * 2) * 60)));
    float VAR_19 = GetObjectByTag("Wind", 0);
    int VAR_22 = FloatToInt((VAR_20 / 4.000000));
    SoundObjectSetVolume(VAR_21, VAR_22);
    None VAR_24;
    if (GLOBAL_1) {
    }
    if (((GLOBAL_2 > 1.000000) && (GLOBAL_18 >= 1))) {
        SetLocalNumber(GetObjectByTag("racedialog", 0), 12, 1);
    }
    VAR_32 = (((GLOBAL_31 - 50.000000) / 150.000000) * 5);
    if ((GLOBAL_28 < 1.000000)) {
        VAR_32 = 1.000000;
    } else if ((GLOBAL_28 > 5.000000)) {
        VAR_32 = 5.000000;
    }
    if ((GLOBAL_31 < 0.000000)) {
        SWMG_SetLateralAccelerationPerSecond((-GLOBAL_31));
    } else if ((GLOBAL_31 < 300.000000)) {
        SWMG_SetLateralAccelerationPerSecond(GLOBAL_31);

    } else {
        SWMG_SetLateralAccelerationPerSecond(300.000000);
    }
    if ((GLOBAL_31 < 150.000000)) {
        SWMG_SetSpeedBlurEffect(0, 0.000000);

    } else {
        SWMG_SetSpeedBlurEffect(1, ((GLOBAL_31 - 149.000000) / 350.000000));
    }
    VAR_30 = ("camshake" + FloatToString(GLOBAL_31, 1, 0));
    VAR_30 = GetSubString(GLOBAL_26, 0, (GetStringLength(GLOBAL_24) - 1));
    SWMG_PlayAnimation(OBJECT_SELF, GLOBAL_27, 1, 0, 0);
    if ((6000.000000 > GLOBAL_15)) {
        VAR_30 = ("cDistL" + FloatToString(GLOBAL_31, 1, 0));
        VAR_30 = GetSubString(GLOBAL_26, 0, (GetStringLength(GLOBAL_24) - 1));
        SWMG_PlayAnimation(OBJECT_SELF, GLOBAL_27, 1, 0, 1);
    }
    VAR_33 = 0;
    return;
    return;
}

