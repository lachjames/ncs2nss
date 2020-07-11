int sub1(int x, int y) {
    return x + y;
}

void sub2 (int a) {
    if (sub1(a, 2) || sub1(a, -1)) {
        a += 1;
    }
}

void main () {
    sub2(5);
}