"""Integration test that runs full pipeline: lexer -> parser -> semantic."""

import pytest
from aicc.lexer import Lexer
from aicc.parser import Parser
from aicc.semantic import SemanticAnalyzer


def compile_program(source: str):
    """Run the full compilation pipeline."""
    # Lexical analysis
    lexer = Lexer(source)
    tokens = list(lexer.tokenize())

    # Parsing
    parser = Parser(tokens)
    ast = parser.parse()

    # Semantic analysis
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)

    return analyzer


def test_hello_world():
    """Test compiling hello world (return value)."""
    source = """
    int main() {
        return 42;
    }
    """
    analyzer = compile_program(source)
    assert analyzer.global_scope.lookup("main") is not None


def test_fibonacci():
    """Test compiling recursive fibonacci."""
    source = """
    int fib(int n) {
        if (n <= 1) {
            return n;
        }
        return fib(n - 1) + fib(n - 2);
    }

    int main() {
        return fib(10);
    }
    """
    analyzer = compile_program(source)
    assert analyzer.global_scope.lookup("fib") is not None
    assert analyzer.global_scope.lookup("main") is not None


def test_factorial():
    """Test compiling factorial."""
    source = """
    int factorial(int n) {
        if (n <= 1) {
            return 1;
        }
        return n * factorial(n - 1);
    }

    int main() {
        int x = 5;
        int result = factorial(x);
        return result;
    }
    """
    analyzer = compile_program(source)


def test_complex_expressions():
    """Test compiling complex expressions and control flow."""
    source = """
    int main() {
        int x = 10;
        int y = 20;
        int z = x + y * 2;

        if (z > 40) {
            for (int i = 0; i < 5; i = i + 1) {
                if (i > 2) {
                    break;
                }
                x = x + i;
            }
        } else {
            while (y > 0) {
                y = y - 1;
                if (y == 10) {
                    continue;
                }
                x = x + 1;
            }
        }

        return x;
    }
    """
    analyzer = compile_program(source)


def test_multiple_functions():
    """Test program with multiple functions."""
    source = """
    int add(int a, int b) {
        return a + b;
    }

    int multiply(int a, int b) {
        int result = 0;
        for (int i = 0; i < b; i = i + 1) {
            result = add(result, a);
        }
        return result;
    }

    int main() {
        int x = multiply(3, 4);
        return x;
    }
    """
    analyzer = compile_program(source)
    assert analyzer.global_scope.lookup("add") is not None
    assert analyzer.global_scope.lookup("multiply") is not None
    assert analyzer.global_scope.lookup("main") is not None


def test_nested_scopes_complex():
    """Test complex nested scopes."""
    source = """
    int main() {
        int x = 1;
        {
            int y = 2;
            {
                int z = 3;
                x = x + y + z;
            }
            x = x + y;
        }
        return x;
    }
    """
    analyzer = compile_program(source)


def test_all_operators():
    """Test all supported operators."""
    source = """
    int main() {
        int a = 10;
        int b = 5;

        int add = a + b;
        int sub = a - b;
        int mul = a * b;
        int div = a / b;
        int mod = a % b;

        int eq = a == b;
        int ne = a != b;
        int lt = a < b;
        int gt = a > b;
        int le = a <= b;
        int ge = a >= b;

        int and = a && b;
        int or = a || b;
        int not = !a;

        int neg = -a;

        return add + sub + mul + div + mod + eq + ne + lt + gt + le + ge + and + or + not + neg;
    }
    """
    analyzer = compile_program(source)
