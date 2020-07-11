void main () {
    int x = 0;
    int y = 1;
    if (x < 2) {
        x += 1;
    } else if (x > 5) {
        if (y > 10) {
            y -= 4;
        } else {
            x += 5;
        }
    } else {
        x = 0;
    }
    //if (y < -1) {
    //    y += 1;
    //}
}