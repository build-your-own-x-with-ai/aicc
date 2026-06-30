"""Token types and Token data structure for the AICC lexer."""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any


class TokenType(Enum):
    """Enumeration of all token types in the C subset."""

    # Literals
    INTEGER = auto()

    # Keywords
    INT = auto()
    RETURN = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    BREAK = auto()
    CONTINUE = auto()
    CHAR = auto()

    # Identifiers
    IDENTIFIER = auto()

    # Operators
    PLUS = auto()           # +
    MINUS = auto()          # -
    STAR = auto()           # *
    SLASH = auto()          # /
    PERCENT = auto()        # %

    # Comparison
    EQ = auto()             # ==
    NE = auto()             # !=
    LT = auto()             # <
    GT = auto()             # >
    LE = auto()             # <=
    GE = auto()             # >=

    # Logical
    AND = auto()            # &&
    OR = auto()             # ||
    NOT = auto()            # !

    # Assignment
    ASSIGN = auto()         # =

    # Delimiters
    SEMICOLON = auto()      # ;
    COMMA = auto()          # ,
    LPAREN = auto()         # (
    RPAREN = auto()         # )
    LBRACE = auto()         # {
    RBRACE = auto()         # }
    LBRACKET = auto()       # [
    RBRACKET = auto()       # ]

    # Special
    EOF = auto()


@dataclass
class Token:
    """Represents a single token from the source code."""

    type: TokenType
    value: Any
    line: int
    col: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.col})"


# Keyword mapping
KEYWORDS = {
    'int': TokenType.INT,
    'return': TokenType.RETURN,
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'while': TokenType.WHILE,
    'for': TokenType.FOR,
    'break': TokenType.BREAK,
    'continue': TokenType.CONTINUE,
    'char': TokenType.CHAR,
}
