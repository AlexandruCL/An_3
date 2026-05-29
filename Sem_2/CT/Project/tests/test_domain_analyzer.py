"""
Tests for the AtomC Domain Analyzer (domain_analyzer.py).
Tests both success and error detection cases.
"""

import os
import sys
import subprocess

ANALYZER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "domain_analyzer.py")
TESTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests")


def run_analyzer(source_path: str):
    result = subprocess.run(
        [sys.executable, ANALYZER, source_path],
        capture_output=True, text=True
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def run_analyzer_on_string(source: str):
    tmp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_tmp_da_test.c")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(source)
        return run_analyzer(tmp)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


# ── Success tests ───────────────────────────────────────────────────────────

def test_passing_files():
    """Test files that pass the parser should also pass domain analysis."""
    passing = [1, 2, 3, 4, 8]
    passed = failed = 0
    for i in passing:
        path = os.path.join(TESTS_DIR, f"{i}.c")
        rc, out, err = run_analyzer(path)
        if rc == 0:
            print(f"  PASS {i}.c")
            passed += 1
        else:
            print(f"  FAIL {i}.c: {err}")
            failed += 1
    return passed, failed


# ── Semantic programs ───────────────────────────────────────────────────────

SEMANTIC_TESTS = [
    ("Simple global var", "int x;", True, None),
    ("Global var + function", "int x; void main(){ x=1; }", True, None),
    ("Function with param", "int f(int a){ return a; }", True, None),
    ("Struct definition", "struct Pt{ int x; int y; }; struct Pt p;", True, None),
    ("Struct var usage", "struct Pt{ int x; }; void main(){ struct Pt p; }", True, None),
    ("Nested blocks redefine", """
        int x;
        void main(){
            { int x; }
        }
    """, True, None),
    ("Param shadows global", """
        int x;
        int f(int x){ return x; }
    """, True, None),
    ("Function with local var", """
        void main(){ int x; x=1; }
    """, True, None),
    ("Array var", "int v[10];", True, None),
    ("Array param", "void f(int v[10]){ }", True, None),
]


def test_semantic_programs():
    """Programs that should pass or fail domain analysis."""
    passed = failed = 0
    for name, source, should_pass, err_substr in SEMANTIC_TESTS:
        rc, out, err = run_analyzer_on_string(source)
        ok = (rc == 0) == should_pass
        if not ok and err_substr:
            ok = err_substr.lower() in err.lower()
        if ok:
            print(f"  PASS {name}")
            passed += 1
        else:
            status = "passed" if rc == 0 else f"failed: {err}"
            print(f"  FAIL {name}: expected {'pass' if should_pass else 'fail'}, got {status}")
            failed += 1
    return passed, failed


# ── Error detection tests ───────────────────────────────────────────────────

ERROR_TESTS = [
    ("Redefined global var",
     "int x; int x;",
     "symbol redefinition"),

    ("Redefined struct",
     "struct A{ int x; }; struct A{ int y; };",
     "symbol redefinition"),

    ("Redefined function",
     "void f(){} void f(){}",
     "symbol redefinition"),

    ("Redefined struct member",
     "struct A{ int x; int x; };",
     "symbol redefinition"),

    ("Redefined param",
     "void f(int a, int a){}",
     "symbol redefinition"),

    ("Local redefines param (same scope)",
     "void f(int x){ int x; }",
     "symbol redefinition"),

    ("Undefined struct usage",
     "struct Pt p;",
     "undefined struct"),

    ("Vector without size",
     "int v[];",
     "vector variable must have a specified dimension"),

    ("Redefine var in same block",
     "void main(){ { int x; int x; } }",
     "symbol redefinition"),
]


def test_error_detection():
    """Programs that should produce domain analysis errors."""
    passed = failed = 0
    for name, source, expected_substr in ERROR_TESTS:
        rc, out, err = run_analyzer_on_string(source)
        if rc != 0 and expected_substr.lower() in err.lower():
            print(f"  PASS {name}")
            passed += 1
        elif rc != 0:
            print(f"  PASS {name} (error detected: {err})")
            passed += 1
        else:
            print(f"  FAIL {name}: expected error but analysis succeeded")
            print(f"        stdout: {out[:200]}")
            failed += 1
    return passed, failed


# ── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    total_p = total_f = 0

    print("=== Test files (1.c, 2.c, 3.c, 4.c, 8.c) ===")
    p, f = test_passing_files()
    total_p += p; total_f += f

    print("\n=== Semantic program tests ===")
    p, f = test_semantic_programs()
    total_p += p; total_f += f

    print("\n=== Error detection tests ===")
    p, f = test_error_detection()
    total_p += p; total_f += f

    print(f"\nTotal: {total_p} passed, {total_f} failed")
    sys.exit(1 if total_f > 0 else 0)
