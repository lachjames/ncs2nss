vector func (float a, float b, float c) {
    return Vector(a, b, c);
}

void main () {
    float x = 0.0;
    float y = 1.0;
    float z = 2.0;

    vector a = func(x, y, z);
}