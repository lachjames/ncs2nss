void main() {
	int x = 0;
	int y = 0;
	while (x < 10) {
	    x += 1;
	    if (x > y) {
	        break;
	    }
	    do {
	        y += 1;
	    } while (y <= x);
	}

	int z = 10;
	while (z > 0) {
	    z += 1;
	}
}