//:: k_ptat_dorakwho
/*
     Dorak has not yet reveiled his name to the player.
*/
//:: Created By: John Winski
//:: Copyright (c) 2002 Bioware Corp.

#include "k_inc_tat"

int StartingConditional()
{
    if (GetDorakNamedLocal() == FALSE)
    {
        return TRUE;
    }
    else
    {
        return FALSE;
    }
}
