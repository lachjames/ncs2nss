using System;
using UnityEngine;

namespace KotOR
{
    public class DefBuff : AuroraScript {
        public static void main ()
        {
            int nCharLevel = NWScript.GetHitDice (NWScript.GetFirstPC ());
            int bValid = NWScript.TRUE;
            AuroraEffect eStatA, eStatB, eFP, eVP, eLink;
            int nVP = 0;

            if (B (I (I (NWScript.GetLevelByClass (NWScript.CLASS_TYPE_JEDICONSULAR)) > I (I (B (0) || B (I (I (NWScript.GetLevelByClass (NWScript.CLASS_TYPE_JEDIGUARDIAN)) > I (I (B (0) || B (I (I (NWScript.GetLevelByClass (NWScript.CLASS_TYPE_JEDISENTINEL)) > I (0)))))))))))) {
                if (B (I (I (nCharLevel) >= I (I (B (12) && B (I (I (nCharLevel) <= I (14)))))))) {
                    eStatA = NWScript.EffectAbilityIncrease (NWScript.ABILITY_WISDOM, 4);
                    eStatB = NWScript.EffectAbilityIncrease (NWScript.ABILITY_DEXTERITY, 4);
                    eFP = NWScript.EffectTemporaryForcePoints (50);
                    nVP = 50;
                }
                else if (B (I (I (nCharLevel) >= I (15)))) {
                    eStatA = NWScript.EffectAbilityIncrease (NWScript.ABILITY_WISDOM, 6);
                    eStatB = NWScript.EffectAbilityIncrease (NWScript.ABILITY_DEXTERITY, 6);
                    eFP = NWScript.EffectTemporaryForcePoints (100);
                    nVP = 100;
                }
                else {
                    bValid = NWScript.FALSE;
                };
                if (B (bValid == NWScript.TRUE)) {
                    eLink = NWScript.EffectLinkEffects (eStatA, eStatB);
                    eLink = NWScript.EffectLinkEffects (eLink, eFP);
                }
                ;
            }
            else if (B (NWScript.GetSubRace (AuroraObject.GetObjectSelf ()) == 2)) {
                if (B (I (I (nCharLevel) >= I (I (B (12) && B (I (I (nCharLevel) <= I (14)))))))) {
                    eStatA = NWScript.EffectAbilityIncrease (NWScript.ABILITY_STRENGTH, 6);
                    nVP = 60;
                }
                else if (B (I (I (nCharLevel) >= I (15)))) {
                    eStatA = NWScript.EffectAbilityIncrease (NWScript.ABILITY_STRENGTH, 10);
                    nVP = 100;
                }
                else {
                    bValid = NWScript.FALSE;
                };
                if (B (bValid == NWScript.TRUE)) {
                    eLink = eStatA;
                }
                ;
            }
            else if (B (NWScript.GetRacialType (AuroraObject.GetObjectSelf ()) == NWScript.RACIAL_TYPE_DROID)) {
                if (B (I (I (nCharLevel) >= I (I (B (12) && B (I (I (nCharLevel) <= I (14)))))))) {
                    eStatA = NWScript.EffectAbilityIncrease (NWScript.ABILITY_DEXTERITY, 6);
                    nVP = 60;
                }
                else if (B (I (I (nCharLevel) >= I (15)))) {
                    eStatA = NWScript.EffectAbilityIncrease (NWScript.ABILITY_DEXTERITY, 10);
                    nVP = 100;
                }
                else {
                    bValid = NWScript.FALSE;
                };
                if (B (bValid == NWScript.TRUE)) {
                    eLink = eStatA;
                }
                ;
            }
            else {
                if (B (I (I (nCharLevel) >= I (I (B (12) && B (I (I (nCharLevel) <= I (14)))))))) {
                    eStatA = NWScript.EffectAbilityIncrease (NWScript.ABILITY_STRENGTH, 4);
                    eStatB = NWScript.EffectAbilityIncrease (NWScript.ABILITY_DEXTERITY, 4);
                    nVP = 50;
                }
                else if (B (I (I (nCharLevel) >= I (15)))) {
                    eStatA = NWScript.EffectAbilityIncrease (NWScript.ABILITY_STRENGTH, 6);
                    eStatB = NWScript.EffectAbilityIncrease (NWScript.ABILITY_DEXTERITY, 6);
                    nVP = 100;
                }
                else {
                    bValid = NWScript.FALSE;
                };
                if (B (bValid == NWScript.TRUE)) {
                    eLink = NWScript.EffectLinkEffects (eStatA, eStatB);
                }
                ;
            }
            if (B (I (I (nVP) > I (0)))) {
                nVP = NWScript.GetMaxHitPoints (AuroraObject.GetObjectSelf ()) + nVP;
                NWScript.SetMaxHitPoints (AuroraObject.GetObjectSelf (), nVP);
            }
            if (B (bValid == NWScript.TRUE)) {
                NWScript.ApplyEffectToObject (NWScript.DURATION_TYPE_PERMANENT, eLink, AuroraObject.GetObjectSelf ());
            }
        }
    }
}