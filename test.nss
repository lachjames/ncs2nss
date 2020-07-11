void main () {

    SetGlobalFadeIn(0.0, 1.0);

    SetLockOrientationInDialog(GetObjectByTag("raceannoun031", 0), TRUE);

    int i = 0;

    AssignCommand(GetFirstPC(), JumpToLocation(GetLocation(GetObjectByTag("tar03_wpraceover2", 0))));

    while (GetIsObjectValid(GetObjectByTag("tar03_wpswoopie", i)))
        {
            location lLoc = GetLocation(GetObjectByTag("tar03_wpswoopie", i));
            string sTemplate = "tar03_swoopie" +  IntToString(i);

            CreateObject(OBJECT_TYPE_CREATURE, sTemplate, lLoc, FALSE);

            i++;
        }
}