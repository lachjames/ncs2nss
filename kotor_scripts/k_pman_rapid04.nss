#include "k_inc_man"
void main()
{
    if(GetIsPC(GetEnteringObject()))
    {
        if(GetGlobalBoolean("K_MAN_SWOOP_POINT_04") == FALSE)
        {
            SetGlobalBoolean("K_MAN_SWOOP_POINT_04",TRUE);
        }
        UT_SpawnMessenger();
    }
}
