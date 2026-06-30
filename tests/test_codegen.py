"""Unit tests for the code generator."""

import pytest
import subprocess
import tempfile
import os
from pathlib import Path
from aicc.lexer import Lexer
from aicc.parser import Parser
from aicc.semantic import SemanticAnalyzer
from aicc.codegen_arm64 import CodeGenARM64


def compile_and_run(source: str) -> int:
    """Compile C source code and run it, returning the exit code."""
    # Parse and analyze
    lexer = Lexer(source)
    tokens = list(lexer.tokenize())
    parser = Parser(tokens)
    ast = parser.parse()

    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)

    # Generate code
    codegen = CodeGenARM64(analyzer)
    asm_code = codegen.generate(ast)

    # Write assembly to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.s', delete=False) as f:
        asm_file = f.name
        f.write(asm_code)

    try:
        # Assemble
        obj_file = asm_file.replace('.s', '.o')
        result = subprocess.run(
            ['as', '-o', obj_file, asm_file],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print("Assembly failed:")
            print(result.stderr)
            raise RuntimeError(f"Assembly failed: {result.stderr}")

        # Link
        exe_file = asm_file.replace('.s', '')
        result = subprocess.run(
            ['ld', '-o', exe_file, obj_file, '-lSystem', '-syslibroot',
             '/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk',
             '-e', '_main', '-arch', 'arm64'],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print("Linking failed:")
            print(result.stderr)
            raise RuntimeError(f"Linking failed: {result.stderr}")

        # Run
        result = subprocess.run([exe_file], capture_output=True)
        return result.returncode

    finally:
        # Clean up
        for f in [asm_file, obj_file, exe_file]:
            if os.path.exists(f):
                os.remove(f)


def test_return_constant():
    """Test returning a constant."""
    source = """
    int main() {
        return 42;
    }
    """
    exit_code = compile_and_run(source)
    assert exit_code == 42


def test_simple_arithmetic():
    """Test simple arithmetic."""
    source = """
    int main() {
        int x = 10;
        int y = 20;
        return x + y;
    }
    """
    exit_code = compile_and_run(source)
    assert exit_code == 30


def test_subtraction():
    """Test subtraction."""
    source = """
    int main() {
        int x = 50;
        int y = 8;
        return x - y;
    }
    """
    exit_code = compile_and_run(source)
    assert exit_code == 42


def test_multiplication():
    """Test multiplication."""
    source = """
    int main() {
        int x = 6;
        int y = 7;
        return x * y;
    }
    """
    exit_code = compile_and_run(source)
    assert exit_code == 42


def test_division():
    """Test division."""
    source = """
    int main() {
        int x = 84;
        int y = 2;
        return x / y;
    }
    """
    exit_code = compile_and_run(source)
    assert exit_code == 42


def test_modulo():
    """Test modulo operation."""
    source = """
    int main() {
        int x = 50;
        int y = 8;
        return x % y;
    }
    """
    exit_code = compile_and_run(source)
    assert exit_code == 2  # 50 % 8 = 2


def test_comparison_equal():
    """Test equality comparison."""
    source = """
    int main() {
        int x = 42;
        int y = 42;
        return x == y;
    }
    """
    exit_code = compile_and_run(source)
    assert exit_code == 1  # true


def test_comparison_not_equal():
    """Test not equal comparison."""
    source = """
    int main() {
        int x = 42;
        int y = 10;
        return x != y;
    }
    """
    exit_code = compile_and_run(source)
    assert exit_code == 1  # true


def test_if_statement():
    """Test if statement."""
    source = """
    int main() {
        int x = 10;
        if (x > 5) {
            return 42;
        }
        return 0;
    }
    """
    exit_code = compile_and_run(source)
    assert exit_code == 42


def test_if_else_statement():
    """Test if-else statement."""
    source = """
    int main() {
        int x = 3;
        if (x > 5) {
            return 1;
        } else {
            return 42;
        }
    }
    """
    exit_code = compile_and_run(source)
    assert exit_code == 42


def test_while_loop():
    """Test while loop."""
    source = """
    int main() {
        int x = 0;
        int i = 0;
        while (i < 10) {
            x = x + 1;
            i = i + 1;
        }
        return x;
    }
    """
    exit_code = compile_and_run(source)
    assert exit_code == 10


def test_for_loop():
    """Test for loop."""
    source = """
    int main() {
        int sum = 0;
        for (int i = 1; i <= 10; i = i + 1) {
            sum = sum + i;
        }
        return sum;
    }
    """
    exit_code = compile_and_run(source)
    assert exit_code == 55  # 1+2+...+10 = 55


def test_function_call():
    """Test function call with parameters."""
    source = """
    int add(int a, int b) {
        return a + b;
    }

    int main() {
        return add(20, 22);
    }
    """
    exit_code = compile_and_run(source)
    assert exit_code == 42


def test_recursive_function():
    """Test recursive function (factorial)."""
    source = """
    int factorial(int n) {
        if (n <= 1) {
            return 1;
        }
        return n * factorial(n - 1);
    }

    int main() {
        return factorial(5);
    }
    """
    exit_code = compile_and_run(source)
    assert exit_code == 120  # 5! = 120


def test_complex_expression():
    """Test complex expression with operator precedence."""
    source = """
    int main() {
        return 2 + 3 * 4 - 6 / 2;
    }
    """
    exit_code = compile_and_run(source)
    assert exit_code == 11  # 2 + 12 - 3 = 11
