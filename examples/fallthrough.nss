void main () {
    int x = 0;
    switch (x) {
    case 0:
        PrintInteger(x);
        break;
    case 1:
    case 2:
    case 3:
        x += 1;
        PrintInteger(x);
        break;
    default:
        break;
    }
}