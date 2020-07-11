// Prototypes
float sub1(float floatParam1);

float sub1(float floatParam1) {
	if ((floatParam1 < 0.0)) {
		return (-floatParam1);
	}
	return floatParam1;
}

void main() {
	sub1((-3.14159));
}

