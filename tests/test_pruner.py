"""Unit tests for ast-semantic-diff-pruner."""
import unittest
from ast_semantic_diff_pruner.pruner import ASTDiffPruner


class TestASTDiffPruner(unittest.TestCase):
    def setUp(self):
        self.pruner = ASTDiffPruner()

    def test_pruning_collapses_untouched(self):
        code = """import sys

def helper():
    a = 1
    b = 2
    return a + b

def target():
    c = 99
    return c
"""
        # Line 10 is inside target()
        res = self.pruner.prune_code_by_modified_lines(code, {10})
        self.assertIn("target", res.modified_functions)
        self.assertNotIn("helper", res.modified_functions)
        self.assertIn("# ... [unmodified code collapsed] ...", res.skeletal_code)
        self.assertLess(res.pruned_lines, res.original_lines)
