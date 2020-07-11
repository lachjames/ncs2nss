// Prototypes
float sub3(float floatParam1);
int sub2(int intParam1, int intParam2);
int sub1();

float sub3(float floatParam1) {
	if ((floatParam1 < 0.0)) {
		return (-floatParam1);
	}
	return floatParam1;
}

int sub2(int intParam1, int intParam2) {
	int int1;
	int int2 = intParam1;
	int1 = 0;
	while ((int1 < intParam2)) {
		int2 = (int2 * int2);
		(++int1);
	}
	return int2;
}

int sub1() {
	return 0;
}

void main() {
	SendMessageToPC(GetFirstPC(), IntToString(sub1()));
	SendMessageToPC(GetFirstPC(), IntToString(sub2(2, 3)));
	SendMessageToPC(GetFirstPC(), FloatToString(sub3((-3.14159)), 18, 9));
}

