"""Abstract Syntax Tree (AST) node definitions for the AICC compiler."""

from dataclasses import dataclass
from typing import List, Optional
from .tokens import TokenType


# Base class for all AST nodes
class ASTNode:
    """Base class for all AST nodes."""
    pass


# Expressions
class Expression(ASTNode):
    """Base class for all expression nodes."""
    pass


@dataclass
class IntLiteral(Expression):
    """Integer literal expression."""
    value: int
    line: int
    col: int


@dataclass
class Variable(Expression):
    """Variable reference expression."""
    name: str
    line: int
    col: int


@dataclass
class BinaryOp(Expression):
    """Binary operation expression."""
    left: Expression
    op: TokenType
    right: Expression
    line: int
    col: int


@dataclass
class UnaryOp(Expression):
    """Unary operation expression."""
    op: TokenType
    operand: Expression
    line: int
    col: int


@dataclass
class FunctionCall(Expression):
    """Function call expression."""
    name: str
    args: List[Expression]
    line: int
    col: int


# Statements
class Statement(ASTNode):
    """Base class for all statement nodes."""
    pass


@dataclass
class VarDecl(Statement):
    """Variable declaration statement."""
    var_type: str  # 'int', 'char', etc.
    name: str
    init: Optional[Expression]
    line: int
    col: int


@dataclass
class Assignment(Statement):
    """Assignment statement."""
    name: str
    value: Expression
    line: int
    col: int


@dataclass
class ReturnStmt(Statement):
    """Return statement."""
    value: Optional[Expression]
    line: int
    col: int


@dataclass
class ExprStmt(Statement):
    """Expression statement (e.g., function call as a statement)."""
    expr: Expression
    line: int
    col: int


@dataclass
class IfStmt(Statement):
    """If-else statement."""
    condition: Expression
    then_body: 'CompoundStmt'
    else_body: Optional['CompoundStmt']
    line: int
    col: int


@dataclass
class WhileStmt(Statement):
    """While loop statement."""
    condition: Expression
    body: 'CompoundStmt'
    line: int
    col: int


@dataclass
class ForStmt(Statement):
    """For loop statement."""
    init: Optional[Statement]  # Can be VarDecl or Assignment
    condition: Optional[Expression]
    update: Optional['Expression | Statement']  # Can be Expression or Assignment
    body: 'CompoundStmt'
    line: int
    col: int


@dataclass
class BreakStmt(Statement):
    """Break statement."""
    line: int
    col: int


@dataclass
class ContinueStmt(Statement):
    """Continue statement."""
    line: int
    col: int


@dataclass
class CompoundStmt(Statement):
    """Compound statement (block with braces)."""
    statements: List[Statement]
    line: int
    col: int


# Top-level declarations
@dataclass
class Function(ASTNode):
    """Function definition."""
    return_type: str
    name: str
    params: List[tuple[str, str]]  # [(type, name), ...]
    body: CompoundStmt
    line: int
    col: int


@dataclass
class Program(ASTNode):
    """Root node representing the entire program."""
    functions: List[Function]
    line: int
    col: int
