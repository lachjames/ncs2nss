void main () {
    int i = 0;
    switch (i) {
    case 1:
        i += 2;
        break;
    case 3:
    case 4:
        i = 5;
        break;
    default:
        i = 6;
        break;
    }
    PrintInteger(i);
}