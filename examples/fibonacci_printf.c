int fib(int n) {
    if (n <= 1) {
        return n;
    }
    return fib(n - 1) + fib(n - 2);
}

int main() {
    printf("Fibonacci sequence:\n");
    printf("fib(0) = 0\n");
    printf("fib(1) = 1\n");
    printf("fib(2) = 1\n");
    printf("fib(3) = 2\n");
    printf("fib(4) = 3\n");
    printf("fib(5) = 5\n");
    printf("fib(10) = 55\n");
    
    printf("\nComputing fib(10)...\n");
    return fib(10);
}
