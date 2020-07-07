int mult2 (int x) {
    return 2 * x;
}

void main () {
    int i = 0;

    while (i < 10) {
        PrintInteger(mult2(i));
        i += 1;
    }
}