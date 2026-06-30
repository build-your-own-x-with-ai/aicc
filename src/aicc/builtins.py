"""Built-in runtime library for AICC."""

# Built-in function declarations that are automatically available
# These are provided as external functions that will be linked
BUILTIN_FUNCTIONS = """
"""

# For now, we'll handle printf/putchar as external declarations
# that get special treatment in the code generator

# Built-in function implementations in ARM64 assembly
BUILTIN_IMPLEMENTATIONS_ARM64 = """
// printf - simplified: prints the integer argument
// For now, we use the exit code to return values
// Real printf would need string support
.global _printf
_printf:
    // Save frame
    stp x29, x30, [sp, #-16]!
    mov x29, sp

    // For now, printf is a no-op in our simple implementation
    // In a real implementation, this would call the C printf

    mov x0, #0  // Return 0 (simplified)

    ldp x29, x30, [sp], #16
    ret

.global _putchar
_putchar:
    // x0 contains the character to print
    stp x29, x30, [sp, #-16]!
    mov x29, sp

    // Use write syscall to print one character
    // write(1, &char, 1)
    str x0, [sp, #-16]!
    mov x0, #1           // stdout
    mov x1, sp           // buffer
    mov x2, #1           // length
    mov x16, #4          // write syscall
    svc #0

    add sp, sp, #16
    ldp x29, x30, [sp], #16
    ret

.global _getchar
_getchar:
    stp x29, x30, [sp, #-16]!
    mov x29, sp

    // Use read syscall to read one character
    sub sp, sp, #16
    mov x0, #0           // stdin
    mov x1, sp           // buffer
    mov x2, #1           // length
    mov x16, #3          // read syscall
    svc #0

    ldr x0, [sp]         // Load character
    add sp, sp, #16

    ldp x29, x30, [sp], #16
    ret
"""
