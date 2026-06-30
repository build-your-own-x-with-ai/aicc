"""Simple preprocessor for AICC compiler."""

import re
from pathlib import Path
from typing import List, Set


class PreprocessorError(Exception):
    """Preprocessor error."""
    pass


class Preprocessor:
    """Simple C preprocessor."""

    def __init__(self):
        self.included_files: Set[str] = set()
        self.defines: dict = {}
        self.include_paths = [
            Path("/usr/include"),
            Path("/usr/local/include"),
        ]

    def process(self, source: str, source_file: Path = None) -> str:
        """Process source code through preprocessor."""
        if source_file:
            self.include_paths.insert(0, source_file.parent)

        lines = source.split('\n')
        output_lines = []

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # Handle preprocessor directives
            if stripped.startswith('#'):
                directive = self._parse_directive(stripped)

                if directive['type'] == 'include':
                    # For now, skip includes - we'll provide built-in functions
                    i += 1
                    continue
                elif directive['type'] == 'define':
                    self.defines[directive['name']] = directive.get('value', '1')
                    i += 1
                    continue
                elif directive['type'] == 'ifdef':
                    # Simple ifdef support
                    if directive['name'] not in self.defines:
                        # Skip until endif
                        i = self._skip_to_endif(lines, i)
                    i += 1
                    continue
                elif directive['type'] == 'ifndef':
                    if directive['name'] in self.defines:
                        i = self._skip_to_endif(lines, i)
                    i += 1
                    continue
                elif directive['type'] == 'endif':
                    i += 1
                    continue
                else:
                    # Unknown directive, skip
                    i += 1
                    continue

            # Replace defined macros
            for name, value in self.defines.items():
                line = re.sub(r'\b' + name + r'\b', value, line)

            output_lines.append(line)
            i += 1

        return '\n'.join(output_lines)

    def _parse_directive(self, line: str) -> dict:
        """Parse a preprocessor directive."""
        line = line[1:].strip()  # Remove '#'

        # #include
        match = re.match(r'include\s+[<"](.+)[>"]', line)
        if match:
            return {'type': 'include', 'file': match.group(1)}

        # #define
        match = re.match(r'define\s+(\w+)(?:\s+(.+))?', line)
        if match:
            return {
                'type': 'define',
                'name': match.group(1),
                'value': match.group(2) if match.group(2) else '1'
            }

        # #ifdef
        match = re.match(r'ifdef\s+(\w+)', line)
        if match:
            return {'type': 'ifdef', 'name': match.group(1)}

        # #ifndef
        match = re.match(r'ifndef\s+(\w+)', line)
        if match:
            return {'type': 'ifndef', 'name': match.group(1)}

        # #endif
        if line.startswith('endif'):
            return {'type': 'endif'}

        return {'type': 'unknown'}

    def _skip_to_endif(self, lines: List[str], start: int) -> int:
        """Skip lines until #endif."""
        depth = 1
        i = start + 1
        while i < len(lines) and depth > 0:
            stripped = lines[i].strip()
            if stripped.startswith('#ifdef') or stripped.startswith('#ifndef'):
                depth += 1
            elif stripped.startswith('#endif'):
                depth -= 1
            i += 1
        return i - 1
