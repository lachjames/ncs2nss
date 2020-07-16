
int is_even(int x);
int is_odd(int x);

int is_even (int x) {
    if (x == 0) {
        return TRUE;
    }
    return is_odd(x - 1);
}
int is_odd (int x) {
    if (x == 0) {
        return FALSE;
    }
    return is_even(x - 1);
}

void main () {
    is_even(5);
}