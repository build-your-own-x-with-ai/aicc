"""Unit tests for the semantic analyzer."""

import pytest
from aicc.lexer import Lexer
from aicc.parser import Parser
from aicc.semantic import SemanticAnalyzer, SemanticError, Type, Symbol


def analyze(source: str):
    """Helper to parse and analyze source code."""
    lexer = Lexer(source)
    tokens = list(lexer.tokenize())
    parser = Parser(tokens)
    ast = parser.parse()

    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    return analyzer


def test_simple_function():
    """Test analyzing a simple function."""
    source = "int main() { return 42; }"
    analyzer = analyze(source)

    # Check that main is in global scope
    main_symbol = analyzer.global_scope.lookup("main")
    assert main_symbol is not None
    assert main_symbol.name == "main"
    assert main_symbol.type == Type("int")
    assert main_symbol.is_function


def test_variable_declaration():
    """Test variable declaration and initialization."""
    source = """
    int main() {
        int x;
        int y = 10;
        return y;
    }
    """
    analyzer = analyze(source)
    # Should not raise any errors


def test_undefined_variable():
    """Test error on undefined variable."""
    source = """
    int main() {
        return x;
    }
    """
    with pytest.raises(SemanticError, match="Undefined variable 'x'"):
        analyze(source)


def test_duplicate_variable():
    """Test error on duplicate variable definition."""
    source = """
    int main() {
        int x = 1;
        int x = 2;
        return 0;
    }
    """
    with pytest.raises(SemanticError, match="already defined"):
        analyze(source)


def test_type_mismatch_initialization():
    """Test type mismatch in variable initialization."""
    # For now, we only have int type, so this test is placeholder
    # Will be useful when we add more types
    source = """
    int main() {
        int x = 42;
        return x;
    }
    """
    analyzer = analyze(source)
    # Should pass since both are int


def test_assignment_to_undefined_variable():
    """Test assignment to undefined variable."""
    source = """
    int main() {
        x = 42;
        return 0;
    }
    """
    with pytest.raises(SemanticError, match="Undefined variable 'x'"):
        analyze(source)


def test_valid_assignment():
    """Test valid assignment."""
    source = """
    int main() {
        int x = 10;
        x = 20;
        return x;
    }
    """
    analyzer = analyze(source)


def test_return_type_mismatch():
    """Test return type checking."""
    # This test is conceptual since we only have int for now
    source = """
    int main() {
        return 42;
    }
    """
    analyzer = analyze(source)
    # Should pass


def test_function_call():
    """Test function call with correct arguments."""
    source = """
    int add(int a, int b) {
        return a + b;
    }

    int main() {
        return add(1, 2);
    }
    """
    analyzer = analyze(source)


def test_undefined_function():
    """Test call to undefined function."""
    source = """
    int main() {
        return foo(1, 2);
    }
    """
    with pytest.raises(SemanticError, match="Undefined function 'foo'"):
        analyze(source)


def test_wrong_argument_count():
    """Test function call with wrong number of arguments."""
    source = """
    int add(int a, int b) {
        return a + b;
    }

    int main() {
        return add(1);
    }
    """
    with pytest.raises(SemanticError, match="expects 2 arguments, got 1"):
        analyze(source)


def test_duplicate_function():
    """Test duplicate function definition."""
    source = """
    int foo() { return 1; }
    int foo() { return 2; }
    """
    with pytest.raises(SemanticError, match="already defined"):
        analyze(source)


def test_duplicate_parameter():
    """Test duplicate parameter name."""
    source = """
    int foo(int x, int x) {
        return x;
    }
    """
    with pytest.raises(SemanticError, match="Duplicate parameter"):
        analyze(source)


def test_nested_scopes():
    """Test nested scope variable resolution."""
    source = """
    int main() {
        int x = 10;
        {
            int y = 20;
            x = x + y;
        }
        return x;
    }
    """
    analyzer = analyze(source)


def test_variable_shadowing():
    """Test variable shadowing in nested scope."""
    source = """
    int main() {
        int x = 10;
        {
            int x = 20;
            x = x + 1;
        }
        return x;
    }
    """
    analyzer = analyze(source)


def test_break_outside_loop():
    """Test break statement outside loop."""
    source = """
    int main() {
        break;
        return 0;
    }
    """
    with pytest.raises(SemanticError, match="Break statement outside loop"):
        analyze(source)


def test_continue_outside_loop():
    """Test continue statement outside loop."""
    source = """
    int main() {
        continue;
        return 0;
    }
    """
    with pytest.raises(SemanticError, match="Continue statement outside loop"):
        analyze(source)


def test_break_in_loop():
    """Test valid break in loop."""
    source = """
    int main() {
        while (1) {
            break;
        }
        return 0;
    }
    """
    analyzer = analyze(source)


def test_for_loop_scope():
    """Test that for loop variable is scoped to the loop."""
    source = """
    int main() {
        for (int i = 0; i < 10; i = i + 1) {
            int x = i;
        }
        return 0;
    }
    """
    analyzer = analyze(source)


def test_function_used_as_variable():
    """Test error when function is used as variable."""
    source = """
    int foo() { return 42; }

    int main() {
        return foo;
    }
    """
    with pytest.raises(SemanticError, match="used as variable"):
        analyze(source)


def test_variable_used_as_function():
    """Test error when variable is used as function."""
    source = """
    int main() {
        int x = 10;
        return x(1, 2);
    }
    """
    with pytest.raises(SemanticError, match="not a function"):
        analyze(source)


def test_recursive_function():
    """Test recursive function."""
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
    analyzer = analyze(source)


def test_mutual_recursion():
    """Test mutually recursive functions."""
    # Note: Without forward declarations, we need to define functions in order
    # For now, we'll test that functions can call other functions defined earlier
    source = """
    int is_odd(int n) {
        if (n == 0) {
            return 0;
        }
        if (n == 1) {
            return 1;
        }
        return is_odd(n - 2);
    }

    int main() {
        return is_odd(5);
    }
    """
    analyzer = analyze(source)


def test_expression_in_condition():
    """Test complex expression in condition."""
    source = """
    int main() {
        int x = 10;
        int y = 20;
        if (x + y > 25) {
            return 1;
        }
        return 0;
    }
    """
    analyzer = analyze(source)


def test_assignment_to_function():
    """Test that we cannot assign to a function name."""
    source = """
    int foo() { return 42; }

    int main() {
        foo = 10;
        return 0;
    }
    """
    with pytest.raises(SemanticError, match="Cannot assign to function"):
        analyze(source)


def test_complex_program():
    """Test a more complex program."""
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
    analyzer = analyze(source)
