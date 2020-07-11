//:: k_pdan_juhani07
/*
    Checks to see if DAN_JUHANI_PLOT is 2 (meaning that
    the player killed Juhani) and DAN_VANDARJ_DONE is
    FALSE (meaning the player has not spoken to Vandar
    about Juhani yet). This conversation will not repeat
    since DAN_VANDARJ_DONE is set to TRUE to show that
    this conversation has taken place.
*/
//:: Created By: Peter T
//:: Copyright (c) 2002 Bioware Corp.
#include "k_inc_debug"

int StartingConditional()
{
    int iResult;

    iResult = ((GetGlobalNumber("DAN_JUHANI_PLOT") == 2) && (GetGlobalBoolean("DAN_VANDARJ_DONE") == FALSE));
    if (iResult)
        SetGlobalBoolean("DAN_VANDARJ_DONE", TRUE);

    return iResult;
}

