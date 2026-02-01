int add(int a, int b) {
    return a + b;
}

int complex_function(int x) {
    int result = 0;
    
    if (x > 0) {
        for (int i = 0; i < x; i++) {
            if (i % 2 == 0) {
                result += i;
            } else {
                result -= i;
            }
        }
    } else {
        while (x < 0) {
            result += x;
            x++;
        }
    }
    
    return result;
}
