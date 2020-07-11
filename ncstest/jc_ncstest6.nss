#include "jc_inc_ncstest"

void main() {
	int bool = FALSE;
	string message;

	if( bool )
		SendMessageToPC(GetFirstPC(), "Hello world");
}