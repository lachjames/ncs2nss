//:: k_hmis_Talk0+
/*
    Checks if Mis_MissionTalk is greater than 0
*/
//:: Created By:  Drew K
//:: Copyright (c) 2002 Bioware Corp.
#include "k_inc_debug"


int StartingConditional()
{
    int iResult;

    iResult = GetGlobalNumber("Mis_MissionTalk")>=1;
    return iResult;
}


