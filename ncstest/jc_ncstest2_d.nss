// Prototypes
int sub1(int intParam1, int intParam2);

int sub1(int intParam1, int intParam2) {
	int int1;
	int int2 = intParam1;
	int1 = 0;
	while ((int1 < intParam2)) {
		int2 = (int2 * int2);
		(++int1);
	}
	return int2;
}

void main() {
	sub1(2, 3);
}

