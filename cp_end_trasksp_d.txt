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
void sub00000472();

// Actual code
// main
void main() {
    int VAR_0 = GetUserDefinedEventNumber();
    if ((VAR_0 == 50)) {
        object VAR_1 = GetPartyMemberByIndex(1);
        object VAR_2 = GetFirstPC();
        location VAR_3 = Location(Vector(16.340000, 20.500000, (-1.270000)), 180.000000);
        DelayCommand(0.100000, sub00000472());
        DelayCommand(0.250000, AssignCommand(VAR_3, ActionDoCommand(SetFacingPoint(GetPosition(VAR_3)))));
        DelayCommand(0.600000, AssignCommand(VAR_3, ActionStartConversation(VAR_3, "", 0, 0, 1, "", "", "", "", "", "", 0)));
        SetGlobalFadeIn(0.900000, 0.500000, 0.000000, 0.000000, 0.000000);

    } else {
    }
    return;
}

// sub00000472
void sub00000472() {
    AssignCommand(None, ClearAllActions());
    AssignCommand(None, ActionDoCommand(SetCommandable(1, GLOBAL_1)));
    AssignCommand(None, ActionJumpToLocation(GLOBAL_2));
    return;
}

