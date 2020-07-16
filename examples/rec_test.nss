
int fact (int x);

int fact (int x) {
    if (x == 1) {
        return 1;
    }
    return fact(x - 1) * x;
}

void main () {
    fact(5);
}