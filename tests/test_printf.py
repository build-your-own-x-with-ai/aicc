"""Tests for printf and string support."""

import pytest
import subprocess
import tempfile
import os
from pathlib import Path
from aicc.lexer import Lexer
from aicc.parser import Parser
from aicc.semantic import SemanticAnalyzer
from aicc.codegen_arm64 import CodeGenARM64


def compile_and_run_with_output(source: str) -> tuple:
    """Compile C source code and run it, returning (stdout, exit_code)."""
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
            raise RuntimeError(f"Linking failed: {result.stderr}")

        # Run
        result = subprocess.run([exe_file], capture_output=True, text=True)
        return (result.stdout, result.returncode)

    finally:
        # Clean up
        for f in [asm_file, obj_file, exe_file]:
            if os.path.exists(f):
                os.remove(f)


def test_simple_printf():
    """Test simple printf."""
    source = """
    int main() {
        printf("Hello, World!\\n");
        return 0;
    }
    """
    stdout, exit_code = compile_and_run_with_output(source)
    assert stdout == "Hello, World!\n"
    assert exit_code == 0


def test_multiple_printf():
    """Test multiple printf calls."""
    source = """
    int main() {
        printf("Line 1\\n");
        printf("Line 2\\n");
        printf("Line 3\\n");
        return 42;
    }
    """
    stdout, exit_code = compile_and_run_with_output(source)
    assert stdout == "Line 1\nLine 2\nLine 3\n"
    assert exit_code == 42


def test_printf_in_if():
    """Test printf in conditional."""
    source = """
    int main() {
        int x = 10;
        if (x > 5) {
            printf("x is greater than 5\\n");
        } else {
            printf("x is not greater than 5\\n");
        }
        return 0;
    }
    """
    stdout, exit_code = compile_and_run_with_output(source)
    assert stdout == "x is greater than 5\n"
    assert exit_code == 0


def test_printf_in_loop():
    """Test printf in loop."""
    source = """
    int main() {
        int i = 0;
        while (i < 3) {
            printf("Iteration\\n");
            i = i + 1;
        }
        return 0;
    }
    """
    stdout, exit_code = compile_and_run_with_output(source)
    assert stdout == "Iteration\nIteration\nIteration\n"
    assert exit_code == 0


def test_printf_with_function_call():
    """Test printf with function calls."""
    source = """
    int compute() {
        printf("Computing...\\n");
        return 42;
    }

    int main() {
        printf("Start\\n");
        int result = compute();
        printf("End\\n");
        return result;
    }
    """
    stdout, exit_code = compile_and_run_with_output(source)
    assert stdout == "Start\nComputing...\nEnd\n"
    assert exit_code == 42


def test_string_literal():
    """Test string literal parsing."""
    source = """
    int main() {
        printf("Test string");
        return 0;
    }
    """
    stdout, exit_code = compile_and_run_with_output(source)
    assert stdout == "Test string"
    assert exit_code == 0


def test_escape_sequences():
    """Test escape sequences in strings."""
    source = """
    int main() {
        printf("Tab:\\there\\n");
        printf("Quote:\\"\\n");
        printf("Backslash:\\\\\\n");
        return 0;
    }
    """
    stdout, exit_code = compile_and_run_with_output(source)
    assert stdout == "Tab:\there\nQuote:\"\nBackslash:\\\n"
    assert exit_code == 0


def test_char_literal():
    """Test character literal."""
    source = """
    int main() {
        int c = 'A';
        return c;
    }
    """
    stdout, exit_code = compile_and_run_with_output(source)
    assert exit_code == 65  # ASCII of 'A'


def test_char_literal_escape():
    """Test character literal with escape."""
    source = """
    int main() {
        int newline = '\\n';
        return newline;
    }
    """
    stdout, exit_code = compile_and_run_with_output(source)
    assert exit_code == 10  # ASCII of newline
