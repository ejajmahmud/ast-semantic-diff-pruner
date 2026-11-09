"""Core AST Semantic Diff Pruner implementation."""
import ast
import re
from typing import Dict, List, Set, Optional, Tuple, Any


class PrunedDiff:
    def __init__(self, original_lines: int, pruned_lines: int, skeletal_code: str, modified_functions: List[str]):
        self.original_lines = original_lines
        self.pruned_lines = pruned_lines
        self.skeletal_code = skeletal_code
        self.modified_functions = modified_functions
        self.reduction_ratio = 1.0 - (pruned_lines / max(1, original_lines))


class ASTDiffPruner:
    def __init__(self, context_lines: int = 2):
        self.context_lines = context_lines

    def find_modified_line_numbers(self, patch: str) -> Set[int]:
        modified = set()
        current_line = 0
        hunk_header_re = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")

        for line in patch.splitlines():
            m = hunk_header_re.match(line)
            if m:
                current_line = int(m.group(2))
            elif line.startswith("+") and not line.startswith("+++"):
                modified.add(current_line)
                current_line += 1
            elif line.startswith(" ") or line.startswith("-"):
                if not line.startswith("---") and not line.startswith("-"):
                    current_line += 1
        return modified

    def prune_code_by_modified_lines(self, source_code: str, modified_lines: Set[int]) -> PrunedDiff:
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            # Fallback to returning original
            lines = source_code.splitlines()
            return PrunedDiff(len(lines), len(lines), source_code, [])

        lines = source_code.splitlines()
        modified_functions = []
        keep_lines = set()

        # Always keep top-level imports
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for l in range(node.lineno, (node.end_lineno or node.lineno) + 1):
                    keep_lines.add(l)

        # Inspect top-level functions and classes
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                start = node.lineno
                end = node.end_lineno or start
                node_lines = set(range(start, end + 1))
                if node_lines.intersection(modified_lines):
                    # Modified node: keep signature and modified lines with padding
                    modified_functions.append(node.name)
                    # Keep signature
                    keep_lines.add(start)
                    for ml in node_lines.intersection(modified_lines):
                        for pad in range(max(start, ml - self.context_lines), min(end, ml + self.context_lines) + 1):
                            keep_lines.add(pad)
                else:
                    # Unmodified node: keep signature line only + collapsed comment
                    keep_lines.add(start)

        output_lines = []
        i = 1
        total_len = len(lines)
        while i <= total_len:
            if i in keep_lines:
                output_lines.append(lines[i - 1])
                i += 1
            else:
                # Collapse block
                output_lines.append("    # ... [unmodified code collapsed] ...")
                while i <= total_len and i not in keep_lines:
                    i += 1

        skeletal = "\n".join(output_lines)
        return PrunedDiff(len(lines), len(output_lines), skeletal, modified_functions)
