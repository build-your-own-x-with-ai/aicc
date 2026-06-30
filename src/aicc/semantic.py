"""Semantic analyzer for the AICC compiler."""

from typing import Dict, Optional, List
from dataclasses import dataclass
from .ast_nodes import *
from .tokens import TokenType


class SemanticError(Exception):
    """Exception raised for semantic analysis errors."""

    def __init__(self, message: str, line: int, col: int):
        self.message = message
        self.line = line
        self.col = col
        super().__init__(f"{message} at line {line}, column {col}")


@dataclass
class Type:
    """Represents a type in the type system."""
    name: str  # 'int', 'char', 'void', etc.

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Type):
            return False
        return self.name == other.name

    def __repr__(self) -> str:
        return f"Type({self.name})"


@dataclass
class Symbol:
    """Represents a symbol in the symbol table."""
    name: str
    type: Type
    is_function: bool = False
    param_types: Optional[List[Type]] = None  # For functions
    offset: int = 0  # Stack offset for local variables
    is_global: bool = False


class SymbolTable:
    """Symbol table with support for nested scopes."""

    def __init__(self, parent: Optional['SymbolTable'] = None):
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}
        self.next_offset = 0  # For stack frame management

    def define(self, name: str, symbol: Symbol) -> None:
        """Define a symbol in the current scope."""
        if name in self.symbols:
            raise ValueError(f"Symbol '{name}' already defined in current scope")
        self.symbols[name] = symbol

    def lookup(self, name: str) -> Optional[Symbol]:
        """Look up a symbol in current scope or parent scopes."""
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

    def lookup_local(self, name: str) -> Optional[Symbol]:
        """Look up a symbol only in the current scope."""
        return self.symbols.get(name)

    def enter_scope(self) -> 'SymbolTable':
        """Enter a new nested scope."""
        return SymbolTable(parent=self)

    def exit_scope(self) -> Optional['SymbolTable']:
        """Exit the current scope and return to parent."""
        return self.parent


class SemanticAnalyzer:
    """Semantic analyzer that performs type checking and builds symbol table."""

    def __init__(self):
        self.global_scope = SymbolTable()
        self.current_scope = self.global_scope
        self.current_function: Optional[Symbol] = None
        self.in_loop = False  # Track if we're inside a loop (for break/continue)

    def analyze(self, program: Program) -> None:
        """Analyze the entire program."""
        # First pass: collect all function declarations
        for func in program.functions:
            self.declare_function(func)

        # Second pass: analyze function bodies
        for func in program.functions:
            self.analyze_function(func)

    def declare_function(self, func: Function) -> None:
        """Declare a function in the global scope."""
        # Check for duplicate function definition
        if self.global_scope.lookup_local(func.name):
            raise SemanticError(
                f"Function '{func.name}' already defined",
                func.line,
                func.col
            )

        # Parse parameter types
        param_types = [self.parse_type(ptype) for ptype, _ in func.params]

        # Create function symbol
        return_type = self.parse_type(func.return_type)
        symbol = Symbol(
            name=func.name,
            type=return_type,
            is_function=True,
            param_types=param_types,
            is_global=True
        )

        self.global_scope.define(func.name, symbol)

    def analyze_function(self, func: Function) -> None:
        """Analyze a function body."""
        # Enter function scope
        self.current_scope = self.current_scope.enter_scope()

        # Set current function for return type checking
        func_symbol = self.global_scope.lookup(func.name)
        self.current_function = func_symbol

        # Add parameters to function scope
        for param_type, param_name in func.params:
            ptype = self.parse_type(param_type)
            symbol = Symbol(
                name=param_name,
                type=ptype,
                offset=self.current_scope.next_offset
            )
            self.current_scope.next_offset += 8  # Assuming 8-byte stack slots

            try:
                self.current_scope.define(param_name, symbol)
            except ValueError:
                raise SemanticError(
                    f"Duplicate parameter name '{param_name}'",
                    func.line,
                    func.col
                )

        # Analyze function body
        self.analyze_compound_stmt(func.body)

        # Exit function scope
        self.current_scope = self.current_scope.exit_scope()
        self.current_function = None

    def analyze_compound_stmt(self, stmt: CompoundStmt) -> None:
        """Analyze a compound statement (block)."""
        # Enter new scope for block
        self.current_scope = self.current_scope.enter_scope()

        for statement in stmt.statements:
            self.analyze_statement(statement)

        # Exit block scope
        self.current_scope = self.current_scope.exit_scope()

    def analyze_statement(self, stmt: Statement) -> None:
        """Analyze a statement."""
        if isinstance(stmt, VarDecl):
            self.analyze_var_decl(stmt)
        elif isinstance(stmt, Assignment):
            self.analyze_assignment(stmt)
        elif isinstance(stmt, ReturnStmt):
            self.analyze_return_stmt(stmt)
        elif isinstance(stmt, ExprStmt):
            self.analyze_expression(stmt.expr)
        elif isinstance(stmt, IfStmt):
            self.analyze_if_stmt(stmt)
        elif isinstance(stmt, WhileStmt):
            self.analyze_while_stmt(stmt)
        elif isinstance(stmt, ForStmt):
            self.analyze_for_stmt(stmt)
        elif isinstance(stmt, BreakStmt):
            self.analyze_break_stmt(stmt)
        elif isinstance(stmt, ContinueStmt):
            self.analyze_continue_stmt(stmt)
        elif isinstance(stmt, CompoundStmt):
            self.analyze_compound_stmt(stmt)
        else:
            raise SemanticError(
                f"Unknown statement type: {type(stmt).__name__}",
                stmt.line,
                stmt.col
            )

    def analyze_var_decl(self, stmt: VarDecl) -> None:
        """Analyze a variable declaration."""
        var_type = self.parse_type(stmt.var_type)

        # Check for duplicate definition in current scope
        if self.current_scope.lookup_local(stmt.name):
            raise SemanticError(
                f"Variable '{stmt.name}' already defined in current scope",
                stmt.line,
                stmt.col
            )

        # Analyze initializer if present
        if stmt.init:
            init_type = self.analyze_expression(stmt.init)
            if init_type != var_type:
                raise SemanticError(
                    f"Type mismatch in initialization: expected {var_type.name}, got {init_type.name}",
                    stmt.line,
                    stmt.col
                )

        # Add variable to symbol table
        symbol = Symbol(
            name=stmt.name,
            type=var_type,
            offset=self.current_scope.next_offset
        )
        self.current_scope.next_offset += 8  # 8-byte stack slots
        self.current_scope.define(stmt.name, symbol)

    def analyze_assignment(self, stmt: Assignment) -> None:
        """Analyze an assignment statement."""
        # Look up variable
        symbol = self.current_scope.lookup(stmt.name)
        if not symbol:
            raise SemanticError(
                f"Undefined variable '{stmt.name}'",
                stmt.line,
                stmt.col
            )

        if symbol.is_function:
            raise SemanticError(
                f"Cannot assign to function '{stmt.name}'",
                stmt.line,
                stmt.col
            )

        # Check value type
        value_type = self.analyze_expression(stmt.value)
        if value_type != symbol.type:
            raise SemanticError(
                f"Type mismatch in assignment: expected {symbol.type.name}, got {value_type.name}",
                stmt.line,
                stmt.col
            )

    def analyze_return_stmt(self, stmt: ReturnStmt) -> None:
        """Analyze a return statement."""
        if not self.current_function:
            raise SemanticError(
                "Return statement outside function",
                stmt.line,
                stmt.col
            )

        if stmt.value:
            return_type = self.analyze_expression(stmt.value)
            if return_type != self.current_function.type:
                raise SemanticError(
                    f"Return type mismatch: expected {self.current_function.type.name}, got {return_type.name}",
                    stmt.line,
                    stmt.col
                )
        else:
            # Empty return - only valid for void functions (not supported yet)
            if self.current_function.type.name != "void":
                raise SemanticError(
                    f"Missing return value for function returning {self.current_function.type.name}",
                    stmt.line,
                    stmt.col
                )

    def analyze_if_stmt(self, stmt: IfStmt) -> None:
        """Analyze an if statement."""
        # Condition should be int (we treat as boolean)
        cond_type = self.analyze_expression(stmt.condition)
        if cond_type.name != "int":
            raise SemanticError(
                f"Condition must be int type, got {cond_type.name}",
                stmt.line,
                stmt.col
            )

        # Analyze branches
        self.analyze_compound_stmt(stmt.then_body)
        if stmt.else_body:
            self.analyze_compound_stmt(stmt.else_body)

    def analyze_while_stmt(self, stmt: WhileStmt) -> None:
        """Analyze a while statement."""
        cond_type = self.analyze_expression(stmt.condition)
        if cond_type.name != "int":
            raise SemanticError(
                f"Condition must be int type, got {cond_type.name}",
                stmt.line,
                stmt.col
            )

        # Mark that we're in a loop (for break/continue)
        old_in_loop = self.in_loop
        self.in_loop = True
        self.analyze_compound_stmt(stmt.body)
        self.in_loop = old_in_loop

    def analyze_for_stmt(self, stmt: ForStmt) -> None:
        """Analyze a for statement."""
        # Enter scope for loop (init variable is scoped to loop)
        self.current_scope = self.current_scope.enter_scope()

        # Analyze init
        if stmt.init:
            self.analyze_statement(stmt.init)

        # Analyze condition
        if stmt.condition:
            cond_type = self.analyze_expression(stmt.condition)
            if cond_type.name != "int":
                raise SemanticError(
                    f"Loop condition must be int type, got {cond_type.name}",
                    stmt.line,
                    stmt.col
                )

        # Analyze update
        if stmt.update:
            if isinstance(stmt.update, Assignment):
                self.analyze_assignment(stmt.update)
            elif isinstance(stmt.update, Expression):
                self.analyze_expression(stmt.update)

        # Analyze body
        old_in_loop = self.in_loop
        self.in_loop = True
        self.analyze_compound_stmt(stmt.body)
        self.in_loop = old_in_loop

        # Exit loop scope
        self.current_scope = self.current_scope.exit_scope()

    def analyze_break_stmt(self, stmt: BreakStmt) -> None:
        """Analyze a break statement."""
        if not self.in_loop:
            raise SemanticError(
                "Break statement outside loop",
                stmt.line,
                stmt.col
            )

    def analyze_continue_stmt(self, stmt: ContinueStmt) -> None:
        """Analyze a continue statement."""
        if not self.in_loop:
            raise SemanticError(
                "Continue statement outside loop",
                stmt.line,
                stmt.col
            )

    def analyze_expression(self, expr: Expression) -> Type:
        """Analyze an expression and return its type."""
        if isinstance(expr, IntLiteral):
            return Type("int")

        elif isinstance(expr, Variable):
            symbol = self.current_scope.lookup(expr.name)
            if not symbol:
                raise SemanticError(
                    f"Undefined variable '{expr.name}'",
                    expr.line,
                    expr.col
                )
            if symbol.is_function:
                raise SemanticError(
                    f"Function '{expr.name}' used as variable",
                    expr.line,
                    expr.col
                )
            return symbol.type

        elif isinstance(expr, BinaryOp):
            return self.analyze_binary_op(expr)

        elif isinstance(expr, UnaryOp):
            return self.analyze_unary_op(expr)

        elif isinstance(expr, FunctionCall):
            return self.analyze_function_call(expr)

        else:
            raise SemanticError(
                f"Unknown expression type: {type(expr).__name__}",
                expr.line,
                expr.col
            )

    def analyze_binary_op(self, expr: BinaryOp) -> Type:
        """Analyze a binary operation."""
        left_type = self.analyze_expression(expr.left)
        right_type = self.analyze_expression(expr.right)

        # For now, all binary operations are on ints and return int
        if left_type.name != "int":
            raise SemanticError(
                f"Left operand must be int, got {left_type.name}",
                expr.line,
                expr.col
            )
        if right_type.name != "int":
            raise SemanticError(
                f"Right operand must be int, got {right_type.name}",
                expr.line,
                expr.col
            )

        return Type("int")

    def analyze_unary_op(self, expr: UnaryOp) -> Type:
        """Analyze a unary operation."""
        operand_type = self.analyze_expression(expr.operand)

        if operand_type.name != "int":
            raise SemanticError(
                f"Unary operand must be int, got {operand_type.name}",
                expr.line,
                expr.col
            )

        return Type("int")

    def analyze_function_call(self, expr: FunctionCall) -> Type:
        """Analyze a function call."""
        # Look up function
        symbol = self.current_scope.lookup(expr.name)
        if not symbol:
            raise SemanticError(
                f"Undefined function '{expr.name}'",
                expr.line,
                expr.col
            )

        if not symbol.is_function:
            raise SemanticError(
                f"'{expr.name}' is not a function",
                expr.line,
                expr.col
            )

        # Check argument count
        if len(expr.args) != len(symbol.param_types):
            raise SemanticError(
                f"Function '{expr.name}' expects {len(symbol.param_types)} arguments, got {len(expr.args)}",
                expr.line,
                expr.col
            )

        # Check argument types
        for i, (arg, expected_type) in enumerate(zip(expr.args, symbol.param_types)):
            arg_type = self.analyze_expression(arg)
            if arg_type != expected_type:
                raise SemanticError(
                    f"Argument {i+1} type mismatch: expected {expected_type.name}, got {arg_type.name}",
                    expr.line,
                    expr.col
                )

        return symbol.type

    def parse_type(self, type_str: str) -> Type:
        """Parse a type string into a Type object."""
        if type_str in ("int", "char", "void"):
            return Type(type_str)
        else:
            raise ValueError(f"Unknown type: {type_str}")
