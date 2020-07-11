#include "jc_inc_ncstest"

void main() {
	SendMessageToPC(GetFirstPC(), IntToString(FUN_False()));
	SendMessageToPC(GetFirstPC(), IntToString(FUN_Pow(2, 3)));
	SendMessageToPC(GetFirstPC(), FloatToString(FUN_Abs(-3.14159)));
}