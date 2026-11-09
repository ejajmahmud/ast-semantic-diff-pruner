"""CLI for ast-semantic-diff-pruner."""
import sys
import argparse
from .pruner import ASTDiffPruner


def main():
    parser = argparse.ArgumentParser(description="AST Semantic Diff Pruner CLI")
    parser.add_argument("--demo", action="store_true", help="Run semantic AST diff pruning demo")
    args = parser.parse_args()

    if args.demo:
        sample_code = """import os
import sys

def untouched_helper():
    x = 10
    y = 20
    return x + y

def target_function(val):
    result = val * 2
    # Modified line here
    return result + 42
"""
        pruner = ASTDiffPruner()
        # Pretend line 12 was modified
        res = pruner.prune_code_by_modified_lines(sample_code, {12})
        print(f"Pruned lines: {res.original_lines} -> {res.pruned_lines} ({res.reduction_ratio:.1%} reduction)")
        print(f"Modified Functions: {res.modified_functions}")
        print("
Skeletal Code:
" + res.skeletal_code)
    else:
        parser.print_help()
    sys.exit(0)


if __name__ == "__main__":
    main()
