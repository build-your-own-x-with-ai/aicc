"""Code generator base class for the AICC compiler."""

from typing import List, Optional
from abc import ABC, abstractmethod
from .ast_nodes import *
from .semantic import SemanticAnalyzer


class CodeGenerator(ABC):
    """Abstract base class for code generators."""

    def __init__(self, analyzer: SemanticAnalyzer):
        self.analyzer = analyzer
        self.output: List[str] = []
        self.label_counter = 0

    @abstractmethod
    def generate(self, program: Program) -> str:
        """Generate code for the entire program."""
        pass

    def emit(self, instruction: str) -> None:
        """Emit a single instruction."""
        self.output.append(instruction)

    def emit_label(self, label: str) -> None:
        """Emit a label."""
        self.output.append(f"{label}:")

    def new_label(self, prefix: str = "L") -> str:
        """Generate a new unique label."""
        label = f"{prefix}{self.label_counter}"
        self.label_counter += 1
        return label

    def get_output(self) -> str:
        """Get the generated code as a string."""
        return "\n".join(self.output)
