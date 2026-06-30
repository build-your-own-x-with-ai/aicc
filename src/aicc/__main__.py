"""Command-line interface for the AICC compiler."""

import sys
import argparse
import subprocess
import tempfile
import os
from pathlib import Path
from .lexer import Lexer, LexerError
from .parser import Parser, ParseError
from .semantic import SemanticAnalyzer, SemanticError
from .codegen_arm64 import CodeGenARM64
from .preprocessor import Preprocessor
from .builtins import BUILTIN_FUNCTIONS


def compile_file(source_path: str, output_path: str = None,
                 lex_only: bool = False, parse_only: bool = False,
                 asm_only: bool = False, verbose: bool = False,
                 no_preprocess: bool = False) -> int:
    """Compile a C source file."""
    try:
        # Read source file
        with open(source_path, 'r') as f:
            source = f.read()

        if verbose:
            print(f"Compiling {source_path}...")

        # Preprocessing (unless disabled)
        if not no_preprocess:
            preprocessor = Preprocessor()
            source = preprocessor.process(source, Path(source_path))

            # Add built-in function declarations
            source = BUILTIN_FUNCTIONS + "\n" + source

            if verbose:
                print("Preprocessing complete")

        # Lexical analysis
        lexer = Lexer(source)
        tokens = list(lexer.tokenize())

        if lex_only:
            print("Tokens:")
            for token in tokens:
                print(f"  {token}")
            return 0

        # Parsing
        parser = Parser(tokens)
        ast = parser.parse()

        if parse_only:
            print("AST:")
            print_ast(ast)
            return 0

        # Semantic analysis
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)

        if verbose:
            print("Semantic analysis passed")

        # Code generation
        codegen = CodeGenARM64(analyzer)
        asm_code = codegen.generate(ast)

        # Determine output path
        if not output_path:
            output_path = Path(source_path).stem

        asm_path = output_path if asm_only else output_path + '.s'

        # Write assembly file
        with open(asm_path, 'w') as f:
            f.write(asm_code)

        if verbose:
            print(f"Assembly written to {asm_path}")

        if asm_only:
            return 0

        # Assemble
        obj_path = output_path + '.o'
        result = subprocess.run(
            ['as', '-o', obj_path, asm_path],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"Assembly failed: {result.stderr}", file=sys.stderr)
            return 1

        if verbose:
            print(f"Object file created: {obj_path}")

        # Link
        result = subprocess.run(
            ['ld', '-o', output_path, obj_path, '-lSystem', '-syslibroot',
             '/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk',
             '-e', '_main', '-arch', 'arm64'],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"Linking failed: {result.stderr}", file=sys.stderr)
            return 1

        if verbose:
            print(f"Executable created: {output_path}")

        # Clean up intermediate files if not verbose
        if not verbose:
            os.remove(asm_path)
            os.remove(obj_path)

        print(f"Successfully compiled {source_path} -> {output_path}")
        return 0

    except FileNotFoundError:
        print(f"Error: File not found: {source_path}", file=sys.stderr)
        return 1
    except LexerError as e:
        print(f"Lexer error: {e}", file=sys.stderr)
        return 1
    except ParseError as e:
        print(f"Parse error: {e}", file=sys.stderr)
        return 1
    except SemanticError as e:
        print(f"Semantic error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if verbose:
            import traceback
            traceback.print_exc()
        return 1


def print_ast(ast, indent=0):
    """Pretty print the AST."""
    prefix = "  " * indent
    if isinstance(ast, Program):
        print(f"{prefix}Program:")
        for func in ast.functions:
            print_ast(func, indent + 1)
    elif isinstance(ast, Function):
        params = ", ".join(f"{t} {n}" for t, n in ast.params)
        print(f"{prefix}Function {ast.return_type} {ast.name}({params}):")
        print_ast(ast.body, indent + 1)
    elif isinstance(ast, CompoundStmt):
        print(f"{prefix}Block:")
        for stmt in ast.statements:
            print_ast(stmt, indent + 1)
    elif isinstance(ast, ReturnStmt):
        print(f"{prefix}Return:")
        if ast.value:
            print_ast(ast.value, indent + 1)
    elif isinstance(ast, VarDecl):
        print(f"{prefix}VarDecl {ast.var_type} {ast.name}")
        if ast.init:
            print_ast(ast.init, indent + 1)
    elif isinstance(ast, IntLiteral):
        print(f"{prefix}IntLiteral {ast.value}")
    elif isinstance(ast, BinaryOp):
        print(f"{prefix}BinaryOp {ast.op.name}")
        print_ast(ast.left, indent + 1)
        print_ast(ast.right, indent + 1)
    else:
        print(f"{prefix}{type(ast).__name__}")


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description='AICC - ASCII C Compiler',
        epilog='Example: aicc hello.c -o hello'
    )
    parser.add_argument('input', help='Input C source file')
    parser.add_argument('-o', '--output', help='Output file name')
    parser.add_argument('--lex-only', action='store_true',
                        help='Only perform lexical analysis')
    parser.add_argument('--parse-only', action='store_true',
                        help='Only perform parsing (print AST)')
    parser.add_argument('-S', '--asm-only', action='store_true',
                        help='Generate assembly only (do not assemble/link)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output')
    parser.add_argument('--version', action='version', version='AICC 0.1.0')

    args = parser.parse_args()

    return compile_file(
        args.input,
        args.output,
        args.lex_only,
        args.parse_only,
        args.asm_only,
        args.verbose
    )


if __name__ == '__main__':
    sys.exit(main())
