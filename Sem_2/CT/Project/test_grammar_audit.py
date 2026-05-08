"""
Systematic grammar audit: test every grammar rule from the AtomC PDF
against the parser to ensure correctness and completeness.
"""
import sys
from parser import parse

tests = {
    # ── unit ──
    "empty_program": "",
    "only_vardef": "int x;",
    "only_fndef": "void main() {}",
    "multiple_top_level": "int x; double y; void main() {}",

    # ── structDef ──
    "struct_basic": "struct Point { int x; int y; }; void main() {}",
    "struct_empty": "struct Empty { }; void main() {}",
    "struct_as_type_var": "struct Point { int x; }; struct Point p; void main() {}",
    "struct_as_type_fn_param": "struct S { int v; }; void f(struct S s) {} void main() {}",

    # ── varDef ──
    "var_int": "int x; void main() {}",
    "var_double": "double d; void main() {}",
    "var_char": "char c; void main() {}",
    "var_array": "int v[10]; void main() {}",
    "var_multi": "int a, b, c; void main() {}",
    "var_multi_array": "int a, v[5], b; void main() {}",

    # ── typeBase ──
    "type_int": "int x; void main() {}",
    "type_double": "double x; void main() {}",
    "type_char": "char x; void main() {}",
    "type_struct": "struct S { int v; }; struct S x; void main() {}",

    # ── arrayDecl ──
    "array_with_size": "int v[10]; void main() {}",
    "array_empty_bracket": "void f(int v[]) {} void main() {}",
    "array_expr_size": "int v[20/4+5]; void main() {}",

    # ── fnDef ──
    "fn_void_noparams": "void main() {}",
    "fn_int_noparams": "int f() { return 0; } void main() {}",
    "fn_with_params": "int add(int a, int b) { return a + b; } void main() {}",
    "fn_array_param": "void f(int arr[]) {} void main() {}",
    "fn_multiple_params": "void f(int a, double b, char c) {} void main() {}",

    # ── stm: stmCompound ──
    "compound_empty": "void main() { {} }",
    "compound_nested": "void main() { { { int x; x = 1; } } }",

    # ── stm: if/else ──
    "if_simple": "void main() { if(x) y=1; }",
    "if_else": "void main() { if(x) y=1; else y=2; }",
    "if_compound": "void main() { if(x) { y=1; z=2; } }",
    "if_nested": "void main() { if(a) if(b) x=1; else x=2; }",

    # ── stm: while ──
    "while_simple": "void main() { while(x) x=x-1; }",
    "while_compound": "void main() { while(x) { x=x-1; } }",

    # ── stm: for ──
    "for_full": "void main() { for(i=0;i<10;i=i+1) x=x+1; }",
    "for_empty_parts": "void main() { for(;;) break; }",
    "for_partial": "void main() { for(i=0;;) break; }",
    "for_compound": "void main() { for(i=0;i<5;i=i+1) { x=x+1; } }",

    # ── stm: break ──
    "break_stm": "void main() { break; }",

    # ── stm: return ──
    "return_void": "void main() { return; }",
    "return_expr": "int f() { return 42; } void main() {}",
    "return_complex": "int f(int x) { return x + 1; } void main() {}",

    # ── stm: expr? SEMICOLON ──
    "expr_stm": "void main() { x = 1; }",
    "empty_stm": "void main() { ; }",

    # ── expr: exprAssign ──
    "assign_simple": "void main() { x = 1; }",
    "assign_chain": "void main() { a = b = c = 1; }",

    # ── exprOr ──
    "or_expr": "void main() { x = a || b; }",
    "or_chain": "void main() { x = a || b || c; }",

    # ── exprAnd ──
    "and_expr": "void main() { x = a && b; }",
    "and_chain": "void main() { x = a && b && c; }",

    # ── exprEq ──
    "eq_equal": "void main() { x = a == b; }",
    "eq_noteq": "void main() { x = a != b; }",

    # ── exprRel ──
    "rel_less": "void main() { x = a < b; }",
    "rel_lesseq": "void main() { x = a <= b; }",
    "rel_greater": "void main() { x = a > b; }",
    "rel_greatereq": "void main() { x = a >= b; }",

    # ── exprAdd ──
    "add_expr": "void main() { x = a + b; }",
    "sub_expr": "void main() { x = a - b; }",
    "add_chain": "void main() { x = a + b - c + d; }",

    # ── exprMul ──
    "mul_expr": "void main() { x = a * b; }",
    "div_expr": "void main() { x = a / b; }",
    "mul_chain": "void main() { x = a * b / c; }",

    # ── exprCast ──
    "cast_int": "void main() { x = (int)y; }",
    "cast_double": "void main() { x = (double)y; }",

    # ── exprUnary ──
    "unary_neg": "void main() { x = -a; }",
    "unary_not": "void main() { x = !a; }",
    "unary_double_neg": "void main() { x = - -a; }",

    # ── exprPostfix ──
    "postfix_array": "void main() { x = v[i]; }",
    "postfix_dot": "void main() { x = p.y; }",
    "postfix_chain": "void main() { x = pts[i].x; }",
    "postfix_multi_index": "void main() { x = m[i][j]; }",

    # ── exprPrimary ──
    "primary_id": "void main() { x = y; }",
    "primary_fn_call_noargs": "void main() { f(); }",
    "primary_fn_call_args": "void main() { f(1, 2, 3); }",
    "primary_int": "void main() { x = 42; }",
    "primary_real": "void main() { x = 3.14; }",
    "primary_char": "void main() { x = 'a'; }",
    "primary_string": 'void main() { x = "hello"; }',
    "primary_paren": "void main() { x = (a + b); }",

    # ── Complex combinations ──
    "complex_precedence": "void main() { x = a + b * (c - d) / e; }",
    "complex_logic": "void main() { x = a < b && c > d || e == f; }",
    "complex_postfix_assign": "void main() { p.x = v[i] + 1; }",
    "fn_call_in_expr": "void main() { x = f(a + b, c * d); }",
    "nested_fn_call": "void main() { x = f(g(1)); }",
}

passed = 0
failed = 0
for name, src in tests.items():
    try:
        parse(src)
        print(f"  PASS {name}")
        passed += 1
    except SystemExit:
        print(f"  FAIL {name}")
        failed += 1

print(f"\nTotal: {passed} passed, {failed} failed")
sys.exit(1 if failed > 0 else 0)
