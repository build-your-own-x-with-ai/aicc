"""Recursive descent parser for the AICC compiler."""

from typing import List, Optional
from .tokens import Token, TokenType
from .ast_nodes import *


class ParseError(Exception):
    """Exception raised for syntax errors during parsing."""

    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"{message} at line {token.line}, column {token.col}")


class Parser:
    """Recursive descent parser that builds an AST from tokens."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def current_token(self) -> Token:
        """Get the current token."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]  # Return EOF if past end

    def peek_token(self, offset: int = 1) -> Token:
        """Peek ahead at a token."""
        peek_pos = self.pos + offset
        if peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return self.tokens[-1]

    def advance(self) -> Token:
        """Consume and return the current token."""
        token = self.current_token()
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return token

    def expect(self, token_type: TokenType) -> Token:
        """Consume a token of the expected type, or raise an error."""
        token = self.current_token()
        if token.type != token_type:
            raise ParseError(
                f"Expected {token_type.name}, got {token.type.name}",
                token
            )
        return self.advance()

    def match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types."""
        return self.current_token().type in token_types

    # Operator precedence table (higher number = higher precedence)
    PRECEDENCE = {
        TokenType.OR: 1,
        TokenType.AND: 2,
        TokenType.EQ: 3,
        TokenType.NE: 3,
        TokenType.LT: 4,
        TokenType.GT: 4,
        TokenType.LE: 4,
        TokenType.GE: 4,
        TokenType.PLUS: 5,
        TokenType.MINUS: 5,
        TokenType.STAR: 6,
        TokenType.SLASH: 6,
        TokenType.PERCENT: 6,
    }

    def get_precedence(self, token_type: TokenType) -> int:
        """Get the precedence of a binary operator."""
        return self.PRECEDENCE.get(token_type, 0)

    # Parsing methods
    def parse(self) -> Program:
        """Parse the entire program."""
        functions = []
        while not self.match(TokenType.EOF):
            functions.append(self.parse_function())

        # Use the position of the first function or (1, 1) if no functions
        line = functions[0].line if functions else 1
        col = functions[0].col if functions else 1
        return Program(functions=functions, line=line, col=col)

    def parse_function(self) -> Function:
        """Parse a function definition."""
        # Return type
        return_type_token = self.expect(TokenType.INT)
        return_type = return_type_token.value

        # Function name
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value

        # Parameters
        self.expect(TokenType.LPAREN)
        params = self.parse_parameter_list()
        self.expect(TokenType.RPAREN)

        # Function body
        body = self.parse_compound_stmt()

        return Function(
            return_type=return_type,
            name=name,
            params=params,
            body=body,
            line=return_type_token.line,
            col=return_type_token.col
        )

    def parse_parameter_list(self) -> List[tuple[str, str]]:
        """Parse function parameter list."""
        params = []

        # Empty parameter list
        if self.match(TokenType.RPAREN):
            return params

        # First parameter
        param_type = self.expect(TokenType.INT).value
        param_name = self.expect(TokenType.IDENTIFIER).value
        params.append((param_type, param_name))

        # Additional parameters
        while self.match(TokenType.COMMA):
            self.advance()
            param_type = self.expect(TokenType.INT).value
            param_name = self.expect(TokenType.IDENTIFIER).value
            params.append((param_type, param_name))

        return params

    def parse_compound_stmt(self) -> CompoundStmt:
        """Parse a compound statement (block)."""
        lbrace = self.expect(TokenType.LBRACE)
        statements = []

        while not self.match(TokenType.RBRACE):
            statements.append(self.parse_statement())

        self.expect(TokenType.RBRACE)
        return CompoundStmt(statements=statements, line=lbrace.line, col=lbrace.col)

    def parse_statement(self) -> Statement:
        """Parse a statement."""
        token = self.current_token()

        # Variable declaration
        if self.match(TokenType.INT, TokenType.CHAR):
            return self.parse_var_decl()

        # Return statement
        if self.match(TokenType.RETURN):
            return self.parse_return_stmt()

        # If statement
        if self.match(TokenType.IF):
            return self.parse_if_stmt()

        # While statement
        if self.match(TokenType.WHILE):
            return self.parse_while_stmt()

        # For statement
        if self.match(TokenType.FOR):
            return self.parse_for_stmt()

        # Break statement
        if self.match(TokenType.BREAK):
            self.advance()
            self.expect(TokenType.SEMICOLON)
            return BreakStmt(line=token.line, col=token.col)

        # Continue statement
        if self.match(TokenType.CONTINUE):
            self.advance()
            self.expect(TokenType.SEMICOLON)
            return ContinueStmt(line=token.line, col=token.col)

        # Compound statement
        if self.match(TokenType.LBRACE):
            return self.parse_compound_stmt()

        # Assignment or expression statement
        if self.match(TokenType.IDENTIFIER):
            # Look ahead to distinguish assignment from expression
            if self.peek_token().type == TokenType.ASSIGN:
                return self.parse_assignment()
            else:
                return self.parse_expr_stmt()

        # Expression statement
        return self.parse_expr_stmt()

    def parse_var_decl(self) -> VarDecl:
        """Parse a variable declaration."""
        var_type_token = self.advance()
        var_type = var_type_token.value

        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value

        init = None
        if self.match(TokenType.ASSIGN):
            self.advance()
            init = self.parse_expression()

        self.expect(TokenType.SEMICOLON)
        return VarDecl(
            var_type=var_type,
            name=name,
            init=init,
            line=var_type_token.line,
            col=var_type_token.col
        )

    def parse_assignment(self) -> Assignment:
        """Parse an assignment statement."""
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value

        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()
        self.expect(TokenType.SEMICOLON)

        return Assignment(name=name, value=value, line=name_token.line, col=name_token.col)

    def parse_return_stmt(self) -> ReturnStmt:
        """Parse a return statement."""
        return_token = self.expect(TokenType.RETURN)

        value = None
        if not self.match(TokenType.SEMICOLON):
            value = self.parse_expression()

        self.expect(TokenType.SEMICOLON)
        return ReturnStmt(value=value, line=return_token.line, col=return_token.col)

    def parse_if_stmt(self) -> IfStmt:
        """Parse an if statement."""
        if_token = self.expect(TokenType.IF)
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)

        then_body = self.parse_compound_stmt()

        else_body = None
        if self.match(TokenType.ELSE):
            self.advance()
            else_body = self.parse_compound_stmt()

        return IfStmt(
            condition=condition,
            then_body=then_body,
            else_body=else_body,
            line=if_token.line,
            col=if_token.col
        )

    def parse_while_stmt(self) -> WhileStmt:
        """Parse a while statement."""
        while_token = self.expect(TokenType.WHILE)
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)

        body = self.parse_compound_stmt()
        return WhileStmt(condition=condition, body=body, line=while_token.line, col=while_token.col)

    def parse_for_stmt(self) -> ForStmt:
        """Parse a for statement."""
        for_token = self.expect(TokenType.FOR)
        self.expect(TokenType.LPAREN)

        # Init
        init = None
        if not self.match(TokenType.SEMICOLON):
            if self.match(TokenType.INT, TokenType.CHAR):
                init = self.parse_var_decl()
                # var_decl already consumed semicolon
            else:
                if self.match(TokenType.IDENTIFIER) and self.peek_token().type == TokenType.ASSIGN:
                    name_token = self.advance()
                    self.advance()  # consume =
                    value = self.parse_expression()
                    self.expect(TokenType.SEMICOLON)
                    init = Assignment(name=name_token.value, value=value, line=name_token.line, col=name_token.col)
                else:
                    self.expect(TokenType.SEMICOLON)
        else:
            self.advance()  # consume semicolon

        # Condition
        condition = None
        if not self.match(TokenType.SEMICOLON):
            condition = self.parse_expression()
        self.expect(TokenType.SEMICOLON)

        # Update - this is just an expression, not a full statement
        update = None
        if not self.match(TokenType.RPAREN):
            # For the update part, we need to handle assignment expressions
            # Check if it's an assignment
            if self.match(TokenType.IDENTIFIER) and self.peek_token().type == TokenType.ASSIGN:
                name_token = self.current_token()
                self.advance()  # consume identifier
                self.advance()  # consume =
                value = self.parse_expression()
                # Create an assignment expression (we'll represent it as BinaryOp for now)
                # Actually, we need to store it as an expression, so we'll use a special handling
                update = Assignment(name=name_token.value, value=value, line=name_token.line, col=name_token.col)
            else:
                update = self.parse_expression()
        self.expect(TokenType.RPAREN)

        body = self.parse_compound_stmt()
        return ForStmt(
            init=init,
            condition=condition,
            update=update,
            body=body,
            line=for_token.line,
            col=for_token.col
        )

    def parse_expr_stmt(self) -> ExprStmt:
        """Parse an expression statement."""
        expr_start = self.current_token()
        expr = self.parse_expression()
        self.expect(TokenType.SEMICOLON)
        return ExprStmt(expr=expr, line=expr_start.line, col=expr_start.col)

    def parse_expression(self, min_prec: int = 0) -> Expression:
        """Parse an expression using precedence climbing."""
        left = self.parse_unary()

        while True:
            token = self.current_token()
            prec = self.get_precedence(token.type)

            if prec == 0 or prec < min_prec:
                break

            op = token.type
            self.advance()

            # Right-associative operators would use prec instead of prec + 1
            right = self.parse_expression(prec + 1)
            left = BinaryOp(left=left, op=op, right=right, line=token.line, col=token.col)

        return left

    def parse_unary(self) -> Expression:
        """Parse a unary expression."""
        token = self.current_token()

        if self.match(TokenType.MINUS, TokenType.PLUS, TokenType.NOT):
            op = token.type
            self.advance()
            operand = self.parse_unary()
            return UnaryOp(op=op, operand=operand, line=token.line, col=token.col)

        return self.parse_primary()

    def parse_primary(self) -> Expression:
        """Parse a primary expression."""
        token = self.current_token()

        # Integer literal
        if self.match(TokenType.INTEGER):
            self.advance()
            return IntLiteral(value=token.value, line=token.line, col=token.col)

        # Identifier (variable or function call)
        if self.match(TokenType.IDENTIFIER):
            name = token.value
            self.advance()

            # Function call
            if self.match(TokenType.LPAREN):
                self.advance()
                args = self.parse_argument_list()
                self.expect(TokenType.RPAREN)
                return FunctionCall(name=name, args=args, line=token.line, col=token.col)

            # Variable
            return Variable(name=name, line=token.line, col=token.col)

        # Parenthesized expression
        if self.match(TokenType.LPAREN):
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr

        raise ParseError(f"Unexpected token {token.type.name}", token)

    def parse_argument_list(self) -> List[Expression]:
        """Parse function call argument list."""
        args = []

        if self.match(TokenType.RPAREN):
            return args

        args.append(self.parse_expression())

        while self.match(TokenType.COMMA):
            self.advance()
            args.append(self.parse_expression())

        return args
