// Calculates the first 15 fibonacci numbers

int nth_fib(int n) {
    int a = 0;
    int b = 1;
    int tmp;
    int i;

    for (i = 0; i < n; i++) {
        tmp = b;
        b += a;
        a = tmp;
    }

    return b;
}

void main() {
    int n;
    for (n = 0; n < 15; n++) {
        int fib_n = nth_fib(n);
        PrintInteger(fib_n);
    }
}

