"""ARM64 (AArch64) code generator for the AICC compiler."""

from typing import Dict, Optional, List
from .codegen import CodeGenerator
from .ast_nodes import *
from .tokens import TokenType
from .semantic import SemanticAnalyzer, Symbol, SymbolTable


class CodeGenARM64(CodeGenerator):
    """Code generator for ARM64 (AArch64) architecture."""

    def __init__(self, analyzer: SemanticAnalyzer):
        super().__init__(analyzer)
        self.current_function: Optional[str] = None
        self.stack_offset = 0
        self.break_label_stack: List[str] = []
        self.continue_label_stack: List[str] = []
        self.current_scope: Optional[SymbolTable] = None
        self.local_vars: Dict[str, int] = {}  # Variable name -> stack offset
        self.string_literals: Dict[str, str] = {}  # String value -> label
        self.string_counter = 0

    def generate(self, program: Program) -> str:
        """Generate ARM64 assembly code for the entire program."""
        # First pass: collect all string literals
        self.collect_strings(program)

        # Generate data section for strings
        if self.string_literals:
            self.emit(".data")
            self.emit(".align 3")
            for string_val, label in self.string_literals.items():
                self.emit(f"{label}:")
                # Escape string for assembly
                escaped = self.escape_string(string_val)
                self.emit(f'    .asciz "{escaped}"')
            self.emit("")

        # Generate assembly header
        self.emit(".text")
        self.emit(".align 2")
        self.emit("")

        # Generate built-in functions
        self.generate_builtin_printf()
        self.emit("")

        # Generate code for each function
        for func in program.functions:
            self.generate_function(func)
            self.emit("")

        return self.get_output()

    def escape_string(self, s: str) -> str:
        """Escape a string for assembly output."""
        result = []
        for char in s:
            if char == '\n':
                result.append('\\n')
            elif char == '\t':
                result.append('\\t')
            elif char == '\r':
                result.append('\\r')
            elif char == '\\':
                result.append('\\\\')
            elif char == '"':
                result.append('\\"')
            elif char == '\0':
                result.append('\\0')
            elif ord(char) < 32 or ord(char) > 126:
                result.append(f'\\{ord(char):03o}')
            else:
                result.append(char)
        return ''.join(result)

    def collect_strings(self, node) -> None:
        """Collect all string literals in the AST."""
        if isinstance(node, StringLiteral):
            if node.value not in self.string_literals:
                label = f".str{self.string_counter}"
                self.string_counter += 1
                self.string_literals[node.value] = label
        elif isinstance(node, Program):
            for func in node.functions:
                self.collect_strings(func)
        elif isinstance(node, Function):
            self.collect_strings(node.body)
        elif isinstance(node, CompoundStmt):
            for stmt in node.statements:
                self.collect_strings(stmt)
        elif isinstance(node, (VarDecl, Assignment, ReturnStmt, ExprStmt)):
            if hasattr(node, 'init') and node.init:
                self.collect_strings(node.init)
            if hasattr(node, 'value') and node.value:
                self.collect_strings(node.value)
            if hasattr(node, 'expr') and node.expr:
                self.collect_strings(node.expr)
        elif isinstance(node, (IfStmt, WhileStmt, ForStmt)):
            if hasattr(node, 'condition') and node.condition:
                self.collect_strings(node.condition)
            if hasattr(node, 'then_body'):
                self.collect_strings(node.then_body)
            if hasattr(node, 'else_body') and node.else_body:
                self.collect_strings(node.else_body)
            if hasattr(node, 'body'):
                self.collect_strings(node.body)
            if hasattr(node, 'init') and node.init:
                self.collect_strings(node.init)
            if hasattr(node, 'update') and node.update:
                self.collect_strings(node.update)
        elif isinstance(node, (BinaryOp, UnaryOp)):
            if hasattr(node, 'left'):
                self.collect_strings(node.left)
            if hasattr(node, 'right'):
                self.collect_strings(node.right)
            if hasattr(node, 'operand'):
                self.collect_strings(node.operand)
        elif isinstance(node, FunctionCall):
            for arg in node.args:
                self.collect_strings(arg)

    def generate_builtin_printf(self) -> None:
        """Generate built-in printf function (simplified version)."""
        self.emit("// Built-in printf function")
        self.emit(".global _printf")
        self.emit("_printf:")
        self.emit("    stp x29, x30, [sp, #-16]!")
        self.emit("    mov x29, sp")
        self.emit("")
        self.emit("    // x0 contains the string pointer")
        self.emit("    mov x19, x0             // Save string pointer to callee-saved register")
        self.emit("")
        self.emit("    // Calculate string length")
        self.emit("    mov x1, #0")
        self.emit(".strlen_loop:")
        self.emit("    ldrb w2, [x19, x1]")
        self.emit("    cbz w2, .strlen_done")
        self.emit("    add x1, x1, #1")
        self.emit("    b .strlen_loop")
        self.emit("")
        self.emit(".strlen_done:")
        self.emit("    // write(1, string, length)")
        self.emit("    mov x2, x1              // length")
        self.emit("    mov x1, x19             // string pointer")
        self.emit("    mov x0, #1              // stdout")
        self.emit("    mov x16, #4             // write syscall")
        self.emit("    svc #0")
        self.emit("")
        self.emit("    mov x0, #0              // Return 0")
        self.emit("    ldp x29, x30, [sp], #16")
        self.emit("    ret")
        self.emit("")

    def generate_function(self, func: Function) -> None:
        """Generate code for a function."""
        self.current_function = func.name
        self.local_vars = {}  # Reset local variables
        self.stack_offset = 16  # Start after saved fp and lr

        # Function label
        if func.name == "main":
            self.emit(".global _main")
            self.emit("_main:")
        else:
            self.emit(f".global _{func.name}")
            self.emit(f"_{func.name}:")

        # Function prologue
        self.emit("    stp x29, x30, [sp, #-16]!")  # Save frame pointer and link register
        self.emit("    mov x29, sp")  # Set up frame pointer

        # Calculate stack space needed for local variables
        local_space = 64  # 64 bytes for local variables (simplified)
        if local_space > 0:
            self.emit(f"    sub sp, sp, #{local_space}")

        # Save parameters to stack and record their offsets
        for i, (param_type, param_name) in enumerate(func.params):
            if i < 8:
                # Store parameter from register to stack
                self.local_vars[param_name] = self.stack_offset
                self.emit(f"    str x{i}, [x29, #-{self.stack_offset}]")
                self.stack_offset += 8

        # Generate function body
        self.generate_compound_stmt(func.body)

        # Function epilogue (in case no return statement)
        self.emit(f".{func.name}_epilogue:")
        if local_space > 0:
            self.emit(f"    add sp, sp, #{local_space}")
        self.emit("    ldp x29, x30, [sp], #16")  # Restore frame pointer and link register
        self.emit("    ret")

    def generate_compound_stmt(self, stmt: CompoundStmt) -> None:
        """Generate code for a compound statement."""
        for statement in stmt.statements:
            self.generate_statement(statement)

    def generate_statement(self, stmt: Statement) -> None:
        """Generate code for a statement."""
        if isinstance(stmt, VarDecl):
            self.generate_var_decl(stmt)
        elif isinstance(stmt, Assignment):
            self.generate_assignment(stmt)
        elif isinstance(stmt, ReturnStmt):
            self.generate_return(stmt)
        elif isinstance(stmt, ExprStmt):
            self.generate_expression(stmt.expr)
        elif isinstance(stmt, IfStmt):
            self.generate_if_stmt(stmt)
        elif isinstance(stmt, WhileStmt):
            self.generate_while_stmt(stmt)
        elif isinstance(stmt, ForStmt):
            self.generate_for_stmt(stmt)
        elif isinstance(stmt, BreakStmt):
            self.generate_break_stmt()
        elif isinstance(stmt, ContinueStmt):
            self.generate_continue_stmt()
        elif isinstance(stmt, CompoundStmt):
            self.generate_compound_stmt(stmt)

    def generate_var_decl(self, stmt: VarDecl) -> None:
        """Generate code for variable declaration."""
        # Allocate space for variable
        self.local_vars[stmt.name] = self.stack_offset
        self.stack_offset += 8

        if stmt.init:
            # Generate initializer expression
            self.generate_expression(stmt.init)
            # Result is in x0, store to variable location
            offset = self.local_vars[stmt.name]
            self.emit(f"    str x0, [x29, #-{offset}]")

    def generate_assignment(self, stmt: Assignment) -> None:
        """Generate code for assignment."""
        # Generate value expression
        self.generate_expression(stmt.value)
        # Result is in x0, store to variable
        if stmt.name in self.local_vars:
            offset = self.local_vars[stmt.name]
            self.emit(f"    str x0, [x29, #-{offset}]")
        else:
            raise RuntimeError(f"Variable '{stmt.name}' not found in local vars")

    def generate_return(self, stmt: ReturnStmt) -> None:
        """Generate code for return statement."""
        if stmt.value:
            # Generate return value expression
            self.generate_expression(stmt.value)
            # Result is already in x0 (return register)

        # Jump to function epilogue
        self.emit(f"    b .{self.current_function}_epilogue")

    def generate_if_stmt(self, stmt: IfStmt) -> None:
        """Generate code for if statement."""
        else_label = self.new_label("else")
        end_label = self.new_label("endif")

        # Generate condition
        self.generate_expression(stmt.condition)
        # Compare with 0 (false)
        self.emit("    cmp x0, #0")

        if stmt.else_body:
            self.emit(f"    b.eq {else_label}")
        else:
            self.emit(f"    b.eq {end_label}")

        # Generate then body
        self.generate_compound_stmt(stmt.then_body)

        if stmt.else_body:
            self.emit(f"    b {end_label}")
            self.emit_label(else_label)
            self.generate_compound_stmt(stmt.else_body)

        self.emit_label(end_label)

    def generate_while_stmt(self, stmt: WhileStmt) -> None:
        """Generate code for while loop."""
        start_label = self.new_label("while_start")
        end_label = self.new_label("while_end")

        # Push break/continue labels
        self.break_label_stack.append(end_label)
        self.continue_label_stack.append(start_label)

        self.emit_label(start_label)

        # Generate condition
        self.generate_expression(stmt.condition)
        self.emit("    cmp x0, #0")
        self.emit(f"    b.eq {end_label}")

        # Generate body
        self.generate_compound_stmt(stmt.body)

        # Jump back to start
        self.emit(f"    b {start_label}")
        self.emit_label(end_label)

        # Pop break/continue labels
        self.break_label_stack.pop()
        self.continue_label_stack.pop()

    def generate_for_stmt(self, stmt: ForStmt) -> None:
        """Generate code for for loop."""
        start_label = self.new_label("for_start")
        end_label = self.new_label("for_end")
        continue_label = self.new_label("for_continue")

        # Push break/continue labels
        self.break_label_stack.append(end_label)
        self.continue_label_stack.append(continue_label)

        # Generate init
        if stmt.init:
            self.generate_statement(stmt.init)

        self.emit_label(start_label)

        # Generate condition
        if stmt.condition:
            self.generate_expression(stmt.condition)
            self.emit("    cmp x0, #0")
            self.emit(f"    b.eq {end_label}")

        # Generate body
        self.generate_compound_stmt(stmt.body)

        # Continue label (for continue statements)
        self.emit_label(continue_label)

        # Generate update
        if stmt.update:
            if isinstance(stmt.update, Assignment):
                self.generate_assignment(stmt.update)
            elif isinstance(stmt.update, Expression):
                self.generate_expression(stmt.update)

        # Jump back to start
        self.emit(f"    b {start_label}")
        self.emit_label(end_label)

        # Pop break/continue labels
        self.break_label_stack.pop()
        self.continue_label_stack.pop()

    def generate_break_stmt(self) -> None:
        """Generate code for break statement."""
        if self.break_label_stack:
            self.emit(f"    b {self.break_label_stack[-1]}")

    def generate_continue_stmt(self) -> None:
        """Generate code for continue statement."""
        if self.continue_label_stack:
            self.emit(f"    b {self.continue_label_stack[-1]}")

    def generate_expression(self, expr: Expression) -> None:
        """Generate code for an expression. Result is left in x0."""
        if isinstance(expr, IntLiteral):
            # Load immediate value into x0
            self.emit(f"    mov x0, #{expr.value}")

        elif isinstance(expr, StringLiteral):
            # Load string address into x0
            label = self.string_literals[expr.value]
            self.emit(f"    adrp x0, {label}@PAGE")
            self.emit(f"    add x0, x0, {label}@PAGEOFF")

        elif isinstance(expr, CharLiteral):
            # Load character value (ASCII) into x0
            self.emit(f"    mov x0, #{expr.value}")

        elif isinstance(expr, Variable):
            # Load variable value into x0
            if expr.name in self.local_vars:
                offset = self.local_vars[expr.name]
                self.emit(f"    ldr x0, [x29, #-{offset}]")
            else:
                raise RuntimeError(f"Variable '{expr.name}' not found in local vars")

        elif isinstance(expr, BinaryOp):
            self.generate_binary_op(expr)

        elif isinstance(expr, UnaryOp):
            self.generate_unary_op(expr)

        elif isinstance(expr, FunctionCall):
            self.generate_function_call(expr)

    def generate_binary_op(self, expr: BinaryOp) -> None:
        """Generate code for binary operation."""
        # Generate left operand
        self.generate_expression(expr.left)
        # Save left result on stack
        self.emit("    str x0, [sp, #-16]!")

        # Generate right operand
        self.generate_expression(expr.right)
        # Move right to x1
        self.emit("    mov x1, x0")
        # Load left from stack to x0
        self.emit("    ldr x0, [sp], #16")

        # Perform operation
        if expr.op == TokenType.PLUS:
            self.emit("    add x0, x0, x1")
        elif expr.op == TokenType.MINUS:
            self.emit("    sub x0, x0, x1")
        elif expr.op == TokenType.STAR:
            self.emit("    mul x0, x0, x1")
        elif expr.op == TokenType.SLASH:
            self.emit("    sdiv x0, x0, x1")
        elif expr.op == TokenType.PERCENT:
            # x0 = x0 % x1
            # ARM64 doesn't have a modulo instruction, so we compute: x0 - (x0/x1)*x1
            self.emit("    sdiv x2, x0, x1")  # x2 = x0 / x1
            self.emit("    msub x0, x2, x1, x0")  # x0 = x0 - x2 * x1
        elif expr.op == TokenType.EQ:
            self.emit("    cmp x0, x1")
            self.emit("    cset x0, eq")
        elif expr.op == TokenType.NE:
            self.emit("    cmp x0, x1")
            self.emit("    cset x0, ne")
        elif expr.op == TokenType.LT:
            self.emit("    cmp x0, x1")
            self.emit("    cset x0, lt")
        elif expr.op == TokenType.GT:
            self.emit("    cmp x0, x1")
            self.emit("    cset x0, gt")
        elif expr.op == TokenType.LE:
            self.emit("    cmp x0, x1")
            self.emit("    cset x0, le")
        elif expr.op == TokenType.GE:
            self.emit("    cmp x0, x1")
            self.emit("    cset x0, ge")
        elif expr.op == TokenType.AND:
            # Logical AND: both operands must be non-zero
            self.emit("    cmp x0, #0")
            self.emit("    cset x0, ne")
            self.emit("    cmp x1, #0")
            self.emit("    cset x1, ne")
            self.emit("    and x0, x0, x1")
        elif expr.op == TokenType.OR:
            # Logical OR: at least one operand must be non-zero
            self.emit("    cmp x0, #0")
            self.emit("    cset x0, ne")
            self.emit("    cmp x1, #0")
            self.emit("    cset x1, ne")
            self.emit("    orr x0, x0, x1")

    def generate_unary_op(self, expr: UnaryOp) -> None:
        """Generate code for unary operation."""
        self.generate_expression(expr.operand)

        if expr.op == TokenType.MINUS:
            self.emit("    neg x0, x0")
        elif expr.op == TokenType.PLUS:
            # Unary plus is a no-op
            pass
        elif expr.op == TokenType.NOT:
            # Logical NOT: 0 becomes 1, non-zero becomes 0
            self.emit("    cmp x0, #0")
            self.emit("    cset x0, eq")

    def generate_function_call(self, expr: FunctionCall) -> None:
        """Generate code for function call."""
        # Generate arguments in reverse order and save on stack
        for i in range(len(expr.args) - 1, -1, -1):
            self.generate_expression(expr.args[i])
            self.emit(f"    str x0, [sp, #-16]!")

        # Pop arguments from stack to registers
        for i in range(len(expr.args)):
            if i < 8:
                self.emit(f"    ldr x{i}, [sp], #16")

        # Call function
        self.emit(f"    bl _{expr.name}")
        # Result is in x0
