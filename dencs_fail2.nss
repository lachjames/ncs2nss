void main () {
    sub1(3, 0.0);
}

void sub1 (float1, float2) {

}
main: ; void main()
  pause_conversation(3.0f);

  DelayCommand(AssignCommand(GetFirstPC(), PlayAnimation(105, 1.0, 0.0)), 1.0f);

  int i = 0;
  while (GetIsObjectValid(GetObjectByTag("tar03_swoopie", i))) {
    SignalEvent(EventUserDefined(2000));
    DelayCommand(PlaySound("cs_swoopcheer"), 0.0f);

  }
loc_0000030D:
  CPTOPSP -12 4
  CONSTS "tar03_swoopie"
  ACTION GetObjectByTag 2
  CPDOWNSP -12 4
  ACTION GetIsObjectValid 1
  JZ loc_000003E2
  STORESTATE sta_0000034E 108 12
  JMP loc_00000368

sta_0000034E:
  CONSTI 2000
  ACTION EventUserDefined 1
  CPTOPSP -12 4
  ACTION SignalEvent 2
  RETN

loc_00000368:
  CPTOPSP -4 4
  ACTION DelayCommand 2
  STORESTATE sta_00000385 108 12
  JMP loc_0000039D

sta_00000385:
  CONSTS "cs_swoopcheer"
  ACTION PlaySound 1
  RETN

loc_0000039D:
  CPTOPSP -4 4
  ACTION DelayCommand 2
  CPTOPSP -4 4
  CONSTF 0.300000
  ADDFF
  CPDOWNSP -8 4
  MOVSP -4
  CPTOPSP -12 4
  INCSPI -16
  MOVSP -4
  JMP loc_0000030D

loc_000003E2:
  MOVSP -12
  RETN

void pause_conversation(float duration) {
    ActionPauseConversation();
    DelayCommand(ActionResumeConversation(), duration);
}