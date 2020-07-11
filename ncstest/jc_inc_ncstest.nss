int FUN_False() {
	return FALSE;
}

int FUN_Pow(int base, int exp) {
	int i;
	int num = base;

	for( i = 0; i < exp; ++i )
		num *= num;

	return num;
}

float FUN_Abs(float num) {
	if( num < 0.0f )
		return -num;
	return num;
}