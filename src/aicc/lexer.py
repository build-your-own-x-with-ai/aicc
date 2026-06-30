"""Lexical analyzer for the AICC compiler."""

from typing import Iterator, Optional
from .tokens import Token, TokenType, KEYWORDS


class LexerError(Exception):
    """Exception raised for lexical analysis errors."""

    def __init__(self, message: str, line: int, col: int):
        self.message = message
        self.line = line
        self.col = col
        super().__init__(f"{message} at line {line}, column {col}")


class Lexer:
    """Lexical analyzer that converts source code into a stream of tokens."""

    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1

    def current_char(self) -> Optional[str]:
        """Return the current character, or None if at EOF."""
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]

    def peek_char(self, offset: int = 1) -> Optional[str]:
        """Peek ahead at a character without consuming it."""
        peek_pos = self.pos + offset
        if peek_pos >= len(self.source):
            return None
        return self.source[peek_pos]

    def advance(self) -> None:
        """Move to the next character and update position tracking."""
        if self.pos < len(self.source):
            if self.source[self.pos] == '\n':
                self.line += 1
                self.col = 1
            else:
                self.col += 1
            self.pos += 1

    def skip_whitespace(self) -> None:
        """Skip whitespace characters."""
        while self.current_char() and self.current_char() in ' \t\n\r':
            self.advance()

    def skip_line_comment(self) -> None:
        """Skip // style line comments."""
        # Skip the //
        self.advance()
        self.advance()
        # Skip until newline or EOF
        while self.current_char() and self.current_char() != '\n':
            self.advance()

    def skip_block_comment(self) -> None:
        """Skip /* */ style block comments."""
        start_line = self.line
        start_col = self.col
        # Skip the /*
        self.advance()
        self.advance()

        while self.current_char():
            if self.current_char() == '*' and self.peek_char() == '/':
                # Skip the */
                self.advance()
                self.advance()
                return
            self.advance()

        raise LexerError("Unterminated block comment", start_line, start_col)

    def read_integer(self) -> Token:
        """Read an integer literal."""
        start_line = self.line
        start_col = self.col
        num_str = ''

        while self.current_char() and self.current_char().isdigit():
            num_str += self.current_char()
            self.advance()

        return Token(TokenType.INTEGER, int(num_str), start_line, start_col)

    def read_identifier(self) -> Token:
        """Read an identifier or keyword."""
        start_line = self.line
        start_col = self.col
        ident = ''

        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            ident += self.current_char()
            self.advance()

        # Check if it's a keyword
        token_type = KEYWORDS.get(ident, TokenType.IDENTIFIER)
        return Token(token_type, ident, start_line, start_col)

    def tokenize(self) -> Iterator[Token]:
        """Generate a stream of tokens from the source code."""
        while self.current_char() is not None:
            # Skip whitespace
            if self.current_char() in ' \t\n\r':
                self.skip_whitespace()
                continue

            # Comments
            if self.current_char() == '/' and self.peek_char() == '/':
                self.skip_line_comment()
                continue

            if self.current_char() == '/' and self.peek_char() == '*':
                self.skip_block_comment()
                continue

            # Numbers
            if self.current_char().isdigit():
                yield self.read_integer()
                continue

            # Identifiers and keywords
            if self.current_char().isalpha() or self.current_char() == '_':
                yield self.read_identifier()
                continue

            # Two-character operators
            line, col = self.line, self.col
            char = self.current_char()
            next_char = self.peek_char()

            if char == '=' and next_char == '=':
                self.advance()
                self.advance()
                yield Token(TokenType.EQ, '==', line, col)
                continue

            if char == '!' and next_char == '=':
                self.advance()
                self.advance()
                yield Token(TokenType.NE, '!=', line, col)
                continue

            if char == '<' and next_char == '=':
                self.advance()
                self.advance()
                yield Token(TokenType.LE, '<=', line, col)
                continue

            if char == '>' and next_char == '=':
                self.advance()
                self.advance()
                yield Token(TokenType.GE, '>=', line, col)
                continue

            if char == '&' and next_char == '&':
                self.advance()
                self.advance()
                yield Token(TokenType.AND, '&&', line, col)
                continue

            if char == '|' and next_char == '|':
                self.advance()
                self.advance()
                yield Token(TokenType.OR, '||', line, col)
                continue

            # Single-character operators and delimiters
            single_char_tokens = {
                '+': TokenType.PLUS,
                '-': TokenType.MINUS,
                '*': TokenType.STAR,
                '/': TokenType.SLASH,
                '%': TokenType.PERCENT,
                '<': TokenType.LT,
                '>': TokenType.GT,
                '!': TokenType.NOT,
                '=': TokenType.ASSIGN,
                ';': TokenType.SEMICOLON,
                ',': TokenType.COMMA,
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                '{': TokenType.LBRACE,
                '}': TokenType.RBRACE,
                '[': TokenType.LBRACKET,
                ']': TokenType.RBRACKET,
            }

            if char in single_char_tokens:
                token_type = single_char_tokens[char]
                self.advance()
                yield Token(token_type, char, line, col)
                continue

            # Unknown character
            raise LexerError(f"Unexpected character '{char}'", line, col)

        # EOF token
        yield Token(TokenType.EOF, None, self.line, self.col)
