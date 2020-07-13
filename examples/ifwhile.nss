void main () {
    int i = 0;
    if (i < 10) {
        while (i < 10) {
            i++;
            if (i > 5) {
                i += 1;
            }
        }
    } else {
        while (i > 10) {
            i--;
        }
    }
}