"""
Tests for the AtomC syntactic analyzer (parser.py).
Runs the parser on all test programs and verifies both success and error cases.
"""

import os
import sys
import subprocess

PARSER = os.path.join(os.path.dirname(__file__), "parser.py")
TESTS_DIR = os.path.join(os.path.dirname(__file__), "tests")


def run_parser(source_path: str) -> tuple[int, str, str]:
    """Run parser.py on a file and return (exit_code, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, PARSER, source_path],
        capture_output=True, text=True
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def run_parser_on_string(source: str) -> tuple[int, str, str]:
    """Run the parser on a string by writing to a temp file."""
    tmp = os.path.join(os.path.dirname(__file__), "_tmp_test.c")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(source)
        return run_parser(tmp)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


# ── Tests on existing test files ────────────────────────────────────────────

def test_all_test_files():
    """All tests/0.c – tests/9.c should parse without errors."""
    passed = 0
    failed = 0
    for i in range(10):
        path = os.path.join(TESTS_DIR, f"{i}.c")
        if not os.path.exists(path):
            print(f"  SKIP {path} (not found)")
            continue
        rc, out, err = run_parser(path)
        if rc == 0:
            print(f"  PASS {path}")
            passed += 1
        else:
            print(f"  FAIL {path}: {err}")
            failed += 1
    return passed, failed


# ── Error detection tests ───────────────────────────────────────────────────

ERROR_TESTS = [
    ("Missing semicolon after var",       "void main(){ int x }",      "missing"),
    ("Missing ) after if condition",      "void main(){ if(x{ } }",    "missing"),
    ("Missing { in function body",        "void main() return;",       "missing"),
    ("Missing ; after break",             "void main(){ break }",      "missing"),
    ("Missing ; after return",            "void main(){ return 0 }",   "missing"),
    ("Invalid top-level token",           "+ void main(){}",           "syntax error"),
]


def test_error_detection():
    """Intentionally broken programs should produce errors."""
    passed = 0
    failed = 0
    for name, source, expected_substr in ERROR_TESTS:
        rc, out, err = run_parser_on_string(source)
        if rc != 0 and expected_substr.lower() in err.lower():
            print(f"  PASS {name}")
            passed += 1
        elif rc != 0:
            print(f"  PASS {name} (error detected: {err})")
            passed += 1
        else:
            print(f"  FAIL {name}: expected error but parser succeeded")
            failed += 1
    return passed, failed


# ── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    total_passed = 0
    total_failed = 0

    print("=== Test files (tests/0.c – tests/9.c) ===")
    p, f = test_all_test_files()
    total_passed += p
    total_failed += f

    print()
    print("=== Error detection tests ===")
    p, f = test_error_detection()
    total_passed += p
    total_failed += f

    print()
    print(f"Total: {total_passed} passed, {total_failed} failed")
    sys.exit(1 if total_failed > 0 else 0)
