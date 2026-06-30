"""Unit tests for the parser."""

import pytest
from aicc.lexer import Lexer
from aicc.parser import Parser, ParseError
from aicc.tokens import TokenType
from aicc.ast_nodes import *


def parse(source: str):
    """Helper to parse source code."""
    lexer = Lexer(source)
    tokens = list(lexer.tokenize())
    parser = Parser(tokens)
    return parser.parse()


def test_parse_return_constant():
    """Test parsing a simple return statement."""
    ast = parse("int main() { return 42; }")
    assert isinstance(ast, Program)
    assert len(ast.functions) == 1

    func = ast.functions[0]
    assert func.name == "main"
    assert func.return_type == "int"
    assert len(func.params) == 0

    body = func.body
    assert isinstance(body, CompoundStmt)
    assert len(body.statements) == 1

    ret = body.statements[0]
    assert isinstance(ret, ReturnStmt)
    assert isinstance(ret.value, IntLiteral)
    assert ret.value.value == 42


def test_parse_variable_declaration():
    """Test parsing variable declarations."""
    ast = parse("int main() { int x; int y = 10; return 0; }")
    func = ast.functions[0]

    decl1 = func.body.statements[0]
    assert isinstance(decl1, VarDecl)
    assert decl1.var_type == "int"
    assert decl1.name == "x"
    assert decl1.init is None

    decl2 = func.body.statements[1]
    assert isinstance(decl2, VarDecl)
    assert decl2.name == "y"
    assert isinstance(decl2.init, IntLiteral)
    assert decl2.init.value == 10


def test_parse_assignment():
    """Test parsing assignment statements."""
    ast = parse("int main() { int x; x = 42; return x; }")
    func = ast.functions[0]

    assign = func.body.statements[1]
    assert isinstance(assign, Assignment)
    assert assign.name == "x"
    assert isinstance(assign.value, IntLiteral)
    assert assign.value.value == 42


def test_parse_arithmetic_expression():
    """Test parsing arithmetic expressions."""
    ast = parse("int main() { return 2 + 3 * 4; }")
    func = ast.functions[0]
    ret = func.body.statements[0]

    # Should parse as 2 + (3 * 4) due to precedence
    assert isinstance(ret.value, BinaryOp)
    assert ret.value.op == TokenType.PLUS
    assert isinstance(ret.value.left, IntLiteral)
    assert ret.value.left.value == 2

    # Right side should be 3 * 4
    assert isinstance(ret.value.right, BinaryOp)
    assert ret.value.right.op == TokenType.STAR
    assert ret.value.right.left.value == 3
    assert ret.value.right.right.value == 4


def test_parse_comparison():
    """Test parsing comparison expressions."""
    ast = parse("int main() { return 5 > 3; }")
    func = ast.functions[0]
    ret = func.body.statements[0]

    assert isinstance(ret.value, BinaryOp)
    assert ret.value.op == TokenType.GT
    assert ret.value.left.value == 5
    assert ret.value.right.value == 3


def test_parse_logical_expression():
    """Test parsing logical expressions."""
    ast = parse("int main() { return 1 && 0 || 1; }")
    func = ast.functions[0]
    ret = func.body.statements[0]

    # Should parse as (1 && 0) || 1
    assert isinstance(ret.value, BinaryOp)
    assert ret.value.op == TokenType.OR


def test_parse_unary_expression():
    """Test parsing unary expressions."""
    ast = parse("int main() { return -42; }")
    func = ast.functions[0]
    ret = func.body.statements[0]

    assert isinstance(ret.value, UnaryOp)
    assert ret.value.op == TokenType.MINUS
    assert isinstance(ret.value.operand, IntLiteral)
    assert ret.value.operand.value == 42


def test_parse_if_statement():
    """Test parsing if statements."""
    ast = parse("int main() { if (1) { return 42; } return 0; }")
    func = ast.functions[0]

    if_stmt = func.body.statements[0]
    assert isinstance(if_stmt, IfStmt)
    assert isinstance(if_stmt.condition, IntLiteral)
    assert if_stmt.condition.value == 1
    assert isinstance(if_stmt.then_body, CompoundStmt)
    assert if_stmt.else_body is None


def test_parse_if_else_statement():
    """Test parsing if-else statements."""
    ast = parse("int main() { if (0) { return 1; } else { return 2; } }")
    func = ast.functions[0]

    if_stmt = func.body.statements[0]
    assert isinstance(if_stmt, IfStmt)
    assert if_stmt.else_body is not None
    assert isinstance(if_stmt.else_body, CompoundStmt)


def test_parse_while_statement():
    """Test parsing while statements."""
    ast = parse("int main() { while (1) { return 0; } return 1; }")
    func = ast.functions[0]

    while_stmt = func.body.statements[0]
    assert isinstance(while_stmt, WhileStmt)
    assert isinstance(while_stmt.condition, IntLiteral)
    assert isinstance(while_stmt.body, CompoundStmt)


def test_parse_for_statement():
    """Test parsing for statements."""
    ast = parse("int main() { for (int i = 0; i < 10; i = i + 1) { return i; } return 0; }")
    func = ast.functions[0]

    for_stmt = func.body.statements[0]
    assert isinstance(for_stmt, ForStmt)
    assert isinstance(for_stmt.init, VarDecl)
    assert isinstance(for_stmt.condition, BinaryOp)
    assert isinstance(for_stmt.update, Assignment)
    assert isinstance(for_stmt.body, CompoundStmt)


def test_parse_function_with_params():
    """Test parsing function with parameters."""
    ast = parse("int add(int a, int b) { return a + b; }")
    func = ast.functions[0]

    assert func.name == "add"
    assert len(func.params) == 2
    assert func.params[0] == ("int", "a")
    assert func.params[1] == ("int", "b")


def test_parse_function_call():
    """Test parsing function calls."""
    ast = parse("int main() { return add(1, 2); }")
    func = ast.functions[0]
    ret = func.body.statements[0]

    assert isinstance(ret.value, FunctionCall)
    assert ret.value.name == "add"
    assert len(ret.value.args) == 2
    assert isinstance(ret.value.args[0], IntLiteral)
    assert ret.value.args[0].value == 1


def test_parse_nested_blocks():
    """Test parsing nested compound statements."""
    ast = parse("int main() { { int x = 1; } return 0; }")
    func = ast.functions[0]

    nested = func.body.statements[0]
    assert isinstance(nested, CompoundStmt)
    assert len(nested.statements) == 1


def test_parse_break_continue():
    """Test parsing break and continue statements."""
    ast = parse("int main() { while (1) { break; } while (0) { continue; } return 0; }")
    func = ast.functions[0]

    break_stmt = func.body.statements[0].body.statements[0]
    assert isinstance(break_stmt, BreakStmt)

    continue_stmt = func.body.statements[1].body.statements[0]
    assert isinstance(continue_stmt, ContinueStmt)


def test_parse_parenthesized_expression():
    """Test parsing parenthesized expressions."""
    ast = parse("int main() { return (2 + 3) * 4; }")
    func = ast.functions[0]
    ret = func.body.statements[0]

    # Should parse as (2 + 3) * 4
    assert isinstance(ret.value, BinaryOp)
    assert ret.value.op == TokenType.STAR
    assert isinstance(ret.value.left, BinaryOp)
    assert ret.value.left.op == TokenType.PLUS


def test_parse_multiple_functions():
    """Test parsing multiple function definitions."""
    ast = parse("""
        int add(int a, int b) { return a + b; }
        int main() { return add(1, 2); }
    """)
    assert len(ast.functions) == 2
    assert ast.functions[0].name == "add"
    assert ast.functions[1].name == "main"


def test_parse_error_missing_semicolon():
    """Test error on missing semicolon."""
    with pytest.raises(ParseError, match="Expected SEMICOLON"):
        parse("int main() { return 42 }")


def test_parse_error_unexpected_token():
    """Test error on unexpected token in expression."""
    with pytest.raises(ParseError):
        parse("int main() { int x = ; }")  # Missing expression after =
