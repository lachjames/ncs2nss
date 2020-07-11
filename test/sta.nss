void main () {
    float k = 1.0;
    DelayCommand(k, SpeakString("This is a string"));

    float t = 1.0;
    AssignCommand(OBJECT_SELF, DelayCommand(t, SpeakString("String")));
}