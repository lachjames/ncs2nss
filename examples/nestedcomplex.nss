void main () {
    int i = 0;
    while (i < 10) {
        int j = 0;
        while (j < i) {
            j++;
        }
        i++;
    }

    if (i > 5) {
        i += 10;
    } else {
        i -= 10;
    }
}