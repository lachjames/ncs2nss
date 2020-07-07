void main () {
    SetGlobalFadeIn(0.0, 1.0, 0.0, 0.0, 0.0);
    SetLockOrientationInDialog(GetObjectByTag("raceannoun031", 0), 1);

    int i = 0;
    AssignCommand(
        GetFirstPC(),
        JumpToLocation(
            GetLocation(
                GetObjectByTag(
                    "tar03_wpraceover2", 0
                )
            )
        )
    );
    while (GetIsObjectValid(GetObjectByTag("tar03_wpswoopie", i))) {
        CreateObject(1, "tar03_swoopie" +  IntToString(i), GetLocation(GetObjectByTag("tar03_wpswoopie", i)), 0);
        i++;
    }
}
