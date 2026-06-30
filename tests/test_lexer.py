"""Unit tests for the lexer."""

import pytest
from aicc.lexer import Lexer, LexerError
from aicc.tokens import TokenType


def tokenize(source: str):
    """Helper to tokenize source code."""
    lexer = Lexer(source)
    return list(lexer.tokenize())


def test_lexer_integers():
    """Test integer literal tokenization."""
    tokens = tokenize("42 123 0")
    assert len(tokens) == 4  # 3 integers + EOF
    assert tokens[0].type == TokenType.INTEGER
    assert tokens[0].value == 42
    assert tokens[1].value == 123
    assert tokens[2].value == 0
    assert tokens[3].type == TokenType.EOF


def test_lexer_keywords():
    """Test keyword recognition."""
    tokens = tokenize("int return if else while for")
    assert tokens[0].type == TokenType.INT
    assert tokens[1].type == TokenType.RETURN
    assert tokens[2].type == TokenType.IF
    assert tokens[3].type == TokenType.ELSE
    assert tokens[4].type == TokenType.WHILE
    assert tokens[5].type == TokenType.FOR


def test_lexer_identifiers():
    """Test identifier tokenization."""
    tokens = tokenize("x foo bar_123 _test")
    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[0].value == "x"
    assert tokens[1].value == "foo"
    assert tokens[2].value == "bar_123"
    assert tokens[3].value == "_test"


def test_lexer_operators():
    """Test operator tokenization."""
    tokens = tokenize("+ - * / % == != < > <= >= && || !")
    expected = [
        TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH,
        TokenType.PERCENT, TokenType.EQ, TokenType.NE, TokenType.LT,
        TokenType.GT, TokenType.LE, TokenType.GE, TokenType.AND,
        TokenType.OR, TokenType.NOT, TokenType.EOF
    ]
    assert [t.type for t in tokens] == expected


def test_lexer_delimiters():
    """Test delimiter tokenization."""
    tokens = tokenize("( ) { } [ ] ; ,")
    expected = [
        TokenType.LPAREN, TokenType.RPAREN, TokenType.LBRACE, TokenType.RBRACE,
        TokenType.LBRACKET, TokenType.RBRACKET, TokenType.SEMICOLON,
        TokenType.COMMA, TokenType.EOF
    ]
    assert [t.type for t in tokens] == expected


def test_lexer_line_comment():
    """Test line comment handling."""
    tokens = tokenize("int x; // this is a comment\nint y;")
    assert len(tokens) == 7  # int, x, ;, int, y, ;, EOF
    assert tokens[0].type == TokenType.INT
    assert tokens[3].type == TokenType.INT


def test_lexer_block_comment():
    """Test block comment handling."""
    tokens = tokenize("int x; /* this is a\n multi-line comment */ int y;")
    assert len(tokens) == 7  # int, x, ;, int, y, ;, EOF


def test_lexer_position_tracking():
    """Test line and column tracking."""
    tokens = tokenize("int\nx")
    assert tokens[0].line == 1
    assert tokens[0].col == 1
    assert tokens[1].line == 2
    assert tokens[1].col == 1


def test_lexer_simple_program():
    """Test tokenizing a simple program."""
    source = """
    int main() {
        return 42;
    }
    """
    tokens = tokenize(source)
    assert tokens[0].type == TokenType.INT
    assert tokens[1].type == TokenType.IDENTIFIER
    assert tokens[1].value == "main"
    assert tokens[2].type == TokenType.LPAREN
    assert tokens[3].type == TokenType.RPAREN
    assert tokens[4].type == TokenType.LBRACE
    assert tokens[5].type == TokenType.RETURN
    assert tokens[6].type == TokenType.INTEGER
    assert tokens[6].value == 42
    assert tokens[7].type == TokenType.SEMICOLON
    assert tokens[8].type == TokenType.RBRACE


def test_lexer_unterminated_comment():
    """Test error on unterminated block comment."""
    with pytest.raises(LexerError, match="Unterminated block comment"):
        tokenize("/* this comment never ends")


def test_lexer_unexpected_character():
    """Test error on unexpected character."""
    with pytest.raises(LexerError, match="Unexpected character"):
        tokenize("int x @ 5;")
