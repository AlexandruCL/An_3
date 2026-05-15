
import sys
from typing import Optional

from lexer import TokenCode, Token, tokenize, tokens, tkerr


# ── Global parser state ─────────────────────────────────────────────────────
crt_tk: Optional[Token] = None       # current token (walks the linked list)
consumed_tk: Optional[Token] = None  # last consumed token


# ── Token consumer ──────────────────────────────────────────────────────────
def consume(code: int) -> bool:
    """
    If the current token matches `code`, consume it (advance crt_tk)
    and return True.  Otherwise leave crt_tk unchanged and return False.
    """
    global crt_tk, consumed_tk
    if crt_tk.code == code:
        consumed_tk = crt_tk
        crt_tk = crt_tk.next
        return True
    return False


# ═════════════════════════════════════════════════════════════════════════════
#  Grammar predicates
# ═════════════════════════════════════════════════════════════════════════════

# ── unit ─────────────────────────────────────────────────────────────────────
# unit: ( structDef | fnDef | varDef )* END
def unit() -> bool:
    global crt_tk
    while True:
        if struct_def():
            pass
        elif fn_def():
            pass
        elif var_def():
            pass
        else:
            break
    if not consume(TokenCode.END):
        tkerr(crt_tk, "syntax error at top level")
    return True


# ── structDef ────────────────────────────────────────────────────────────────
# structDef: STRUCT ID LACC varDef* RACC SEMICOLON
def struct_def() -> bool:
    global crt_tk
    start_tk = crt_tk
    if not consume(TokenCode.STRUCT):
        return False
    if not consume(TokenCode.ID):
        tkerr(crt_tk, "missing identifier after struct")
    if not consume(TokenCode.LACC):
        # STRUCT ID without '{' is not a struct definition —
        # it could be a typeBase for varDef or fnDef; backtrack.
        crt_tk = start_tk
        return False
    while var_def():
        pass
    if not consume(TokenCode.RACC):
        tkerr(crt_tk, "missing } in struct definition")
    if not consume(TokenCode.SEMICOLON):
        tkerr(crt_tk, "missing ; after struct definition")
    return True


# ── varDef ───────────────────────────────────────────────────────────────────
# varDef: typeBase ID arrayDecl? SEMICOLON
def var_def() -> bool:
    global crt_tk
    start_tk = crt_tk
    if not type_base():
        return False
    if not consume(TokenCode.ID):
        tkerr(crt_tk, "missing identifier in variable definition")
    array_decl()  # optional
    if not consume(TokenCode.SEMICOLON):
        # not a varDef — could be fnDef; restore and return False
        crt_tk = start_tk
        return False
    return True


# ── typeBase ─────────────────────────────────────────────────────────────────
# typeBase: INT | DOUBLE | CHAR | STRUCT ID
def type_base() -> bool:
    global crt_tk
    if consume(TokenCode.INT):
        return True
    if consume(TokenCode.DOUBLE):
        return True
    if consume(TokenCode.CHAR):
        return True
    if consume(TokenCode.STRUCT):
        if not consume(TokenCode.ID):
            tkerr(crt_tk, "missing identifier after struct")
        return True
    return False


# ── arrayDecl ────────────────────────────────────────────────────────────────
# arrayDecl: LBRACKET CT_INT? RBRACKET
def array_decl() -> bool:
    global crt_tk
    if not consume(TokenCode.LBRACKET):
        return False
    consume(TokenCode.CT_INT)  # optional integer constant size
    if not consume(TokenCode.RBRACKET):
        tkerr(crt_tk, "missing ] in array declaration")
    return True


# ── fnDef ────────────────────────────────────────────────────────────────────
# fnDef: ( typeBase | VOID ) ID
#        LPAR ( fnParam ( COMMA fnParam )* )? RPAR
#        stmCompound
def fn_def() -> bool:
    global crt_tk
    start_tk = crt_tk
    if not type_base():
        if not consume(TokenCode.VOID):
            return False
    if not consume(TokenCode.ID):
        # not a fnDef (could be varDef after typeBase); restore
        crt_tk = start_tk
        return False
    if not consume(TokenCode.LPAR):
        # has typeBase ID but no '(' → not a fnDef; restore
        crt_tk = start_tk
        return False
    if fn_param():
        while consume(TokenCode.COMMA):
            if not fn_param():
                tkerr(crt_tk, "missing parameter after ,")
    if not consume(TokenCode.RPAR):
        tkerr(crt_tk, "missing ) in function definition")
    if not stm_compound():
        tkerr(crt_tk, "missing function body")
    return True


# ── fnParam ──────────────────────────────────────────────────────────────────
# fnParam: typeBase ID arrayDecl?
def fn_param() -> bool:
    global crt_tk
    if not type_base():
        return False
    if not consume(TokenCode.ID):
        tkerr(crt_tk, "missing identifier in parameter")
    array_decl()  # optional
    return True


# ── stm ──────────────────────────────────────────────────────────────────────
# stm: stmCompound
#    | IF LPAR expr RPAR stm ( ELSE stm )?
#    | WHILE LPAR expr RPAR stm
#    | FOR LPAR expr? SEMICOLON expr? SEMICOLON expr? RPAR stm
#    | BREAK SEMICOLON
#    | RETURN expr? SEMICOLON
#    | expr? SEMICOLON
def stm() -> bool:
    global crt_tk

    # stmCompound
    if stm_compound():
        return True

    # IF LPAR expr RPAR stm ( ELSE stm )?
    if consume(TokenCode.IF):
        if not consume(TokenCode.LPAR):
            tkerr(crt_tk, "missing ( after if")
        if not expr():
            tkerr(crt_tk, "invalid expression after (")
        if not consume(TokenCode.RPAR):
            tkerr(crt_tk, "missing ) after if condition")
        if not stm():
            tkerr(crt_tk, "missing statement after if")
        if consume(TokenCode.ELSE):
            if not stm():
                tkerr(crt_tk, "missing statement after else")
        return True

    # WHILE LPAR expr RPAR stm
    if consume(TokenCode.WHILE):
        if not consume(TokenCode.LPAR):
            tkerr(crt_tk, "missing ( after while")
        if not expr():
            tkerr(crt_tk, "invalid expression after (")
        if not consume(TokenCode.RPAR):
            tkerr(crt_tk, "missing ) after while condition")
        if not stm():
            tkerr(crt_tk, "missing while body statement")
        return True

    # FOR LPAR expr? SEMICOLON expr? SEMICOLON expr? RPAR stm
    if consume(TokenCode.FOR):
        if not consume(TokenCode.LPAR):
            tkerr(crt_tk, "missing ( after for")
        expr()  # optional init
        if not consume(TokenCode.SEMICOLON):
            tkerr(crt_tk, "missing ; after for initializer")
        expr()  # optional condition
        if not consume(TokenCode.SEMICOLON):
            tkerr(crt_tk, "missing ; after for condition")
        expr()  # optional increment
        if not consume(TokenCode.RPAR):
            tkerr(crt_tk, "missing ) after for clauses")
        if not stm():
            tkerr(crt_tk, "missing for body statement")
        return True

    # BREAK SEMICOLON
    if consume(TokenCode.BREAK):
        if not consume(TokenCode.SEMICOLON):
            tkerr(crt_tk, "missing ; after break")
        return True

    # RETURN expr? SEMICOLON
    if consume(TokenCode.RETURN):
        expr()  # optional
        if not consume(TokenCode.SEMICOLON):
            tkerr(crt_tk, "missing ; after return")
        return True

    # expr? SEMICOLON
    if expr():
        if not consume(TokenCode.SEMICOLON):
            tkerr(crt_tk, "missing ; after expression")
        return True
    if consume(TokenCode.SEMICOLON):
        return True

    return False


# ── stmCompound ──────────────────────────────────────────────────────────────
# stmCompound: LACC ( varDef | stm )* RACC
def stm_compound() -> bool:
    global crt_tk
    if not consume(TokenCode.LACC):
        return False
    while True:
        if var_def():
            pass
        elif stm():
            pass
        else:
            break
    if not consume(TokenCode.RACC):
        tkerr(crt_tk, "missing } or syntax error in compound statement")
    return True


# ═════════════════════════════════════════════════════════════════════════════
#  Expression rules
# ═════════════════════════════════════════════════════════════════════════════

# ── expr ─────────────────────────────────────────────────────────────────────
# expr: exprAssign
def expr() -> bool:
    return expr_assign()


# ── exprAssign ───────────────────────────────────────────────────────────────
# exprAssign: exprUnary ASSIGN exprAssign | exprOr
#
# Because exprUnary is a prefix of exprOr, we use backtracking:
# try the assignment form first; if ASSIGN is not found, restore and try exprOr.
def expr_assign() -> bool:
    global crt_tk
    start_tk = crt_tk
    if expr_unary():
        if consume(TokenCode.ASSIGN):
            if not expr_assign():
                tkerr(crt_tk, "invalid expression after =")
            return True
        # no ASSIGN found — this was not an assignment; backtrack
        crt_tk = start_tk
    # try exprOr (which starts from exprAnd, etc.)
    return expr_or()


# ── exprOr (left-recursion eliminated) ──────────────────────────────────────
# Original:  exprOr: exprOr OR exprAnd | exprAnd
# Rewritten: exprOr: exprAnd exprOr1
#            exprOr1: OR exprAnd exprOr1 | ε
def expr_or() -> bool:
    if not expr_and():
        return False
    return expr_or1()


def expr_or1() -> bool:
    global crt_tk
    if consume(TokenCode.OR):
        if not expr_and():
            tkerr(crt_tk, "invalid expression after ||")
        return expr_or1()
    return True  # ε


# ── exprAnd (left-recursion eliminated) ─────────────────────────────────────
# Original:  exprAnd: exprAnd AND exprEq | exprEq
# Rewritten: exprAnd: exprEq exprAnd1
#            exprAnd1: AND exprEq exprAnd1 | ε
def expr_and() -> bool:
    if not expr_eq():
        return False
    return expr_and1()


def expr_and1() -> bool:
    global crt_tk
    if consume(TokenCode.AND):
        if not expr_eq():
            tkerr(crt_tk, "invalid expression after &&")
        return expr_and1()
    return True  # ε


# ── exprEq (left-recursion eliminated) ──────────────────────────────────────
# Original:  exprEq: exprEq ( EQUAL | NOTEQ ) exprRel | exprRel
# Rewritten: exprEq: exprRel exprEq1
#            exprEq1: ( EQUAL | NOTEQ ) exprRel exprEq1 | ε
def expr_eq() -> bool:
    if not expr_rel():
        return False
    return expr_eq1()


def expr_eq1() -> bool:
    global crt_tk
    if consume(TokenCode.EQUAL) or consume(TokenCode.NOTEQ):
        if not expr_rel():
            tkerr(crt_tk, "invalid expression after == or !=")
        return expr_eq1()
    return True  # ε


# ── exprRel (left-recursion eliminated) ─────────────────────────────────────
# Original:  exprRel: exprRel ( LESS | LESSEQ | GREATER | GREATEREQ ) exprAdd | exprAdd
# Rewritten: exprRel: exprAdd exprRel1
#            exprRel1: ( LESS | LESSEQ | GREATER | GREATEREQ ) exprAdd exprRel1 | ε
def expr_rel() -> bool:
    if not expr_add():
        return False
    return expr_rel1()


def expr_rel1() -> bool:
    global crt_tk
    if (consume(TokenCode.LESS) or consume(TokenCode.LESSEQ)
            or consume(TokenCode.GREATER) or consume(TokenCode.GREATEREQ)):
        if not expr_add():
            tkerr(crt_tk, "invalid expression after relational operator")
        return expr_rel1()
    return True  # ε


# ── exprAdd (left-recursion eliminated) ─────────────────────────────────────
# Original:  exprAdd: exprAdd ( ADD | SUB ) exprMul | exprMul
# Rewritten: exprAdd: exprMul exprAdd1
#            exprAdd1: ( ADD | SUB ) exprMul exprAdd1 | ε
def expr_add() -> bool:
    if not expr_mul():
        return False
    return expr_add1()


def expr_add1() -> bool:
    global crt_tk
    if consume(TokenCode.ADD) or consume(TokenCode.SUB):
        if not expr_mul():
            tkerr(crt_tk, "invalid expression after + or -")
        return expr_add1()
    return True  # ε


# ── exprMul (left-recursion eliminated) ─────────────────────────────────────
# Original:  exprMul: exprMul ( MUL | DIV ) exprCast | exprCast
# Rewritten: exprMul: exprCast exprMul1
#            exprMul1: ( MUL | DIV ) exprCast exprMul1 | ε
def expr_mul() -> bool:
    if not expr_cast():
        return False
    return expr_mul1()


def expr_mul1() -> bool:
    global crt_tk
    if consume(TokenCode.MUL) or consume(TokenCode.DIV):
        if not expr_cast():
            tkerr(crt_tk, "invalid expression after * or /")
        return expr_mul1()
    return True  # ε


# ── exprCast ─────────────────────────────────────────────────────────────────
# exprCast: LPAR typeBase arrayDecl? RPAR exprCast | exprUnary
#
# Ambiguity with exprPrimary's LPAR expr RPAR — resolved by backtracking.
def expr_cast() -> bool:
    global crt_tk
    start_tk = crt_tk
    if consume(TokenCode.LPAR):
        if type_base():
            array_decl()  # optional
            if consume(TokenCode.RPAR):
                if expr_cast():
                    return True
        # not a cast; backtrack
        crt_tk = start_tk
    return expr_unary()


# ── exprUnary ────────────────────────────────────────────────────────────────
# exprUnary: ( SUB | NOT ) exprUnary | exprPostfix
def expr_unary() -> bool:
    global crt_tk
    if consume(TokenCode.SUB) or consume(TokenCode.NOT):
        if not expr_unary():
            tkerr(crt_tk, "invalid expression after unary operator")
        return True
    return expr_postfix()


# ── exprPostfix (left-recursion eliminated) ──────────────────────────────────
# Original:  exprPostfix: exprPostfix LBRACKET expr RBRACKET
#                       | exprPostfix DOT ID
#                       | exprPrimary
# Rewritten: exprPostfix: exprPrimary exprPostfix1
#            exprPostfix1: LBRACKET expr RBRACKET exprPostfix1
#                        | DOT ID exprPostfix1
#                        | ε
def expr_postfix() -> bool:
    if not expr_primary():
        return False
    return expr_postfix1()


def expr_postfix1() -> bool:
    global crt_tk
    if consume(TokenCode.LBRACKET):
        if not expr():
            tkerr(crt_tk, "invalid expression inside []")
        if not consume(TokenCode.RBRACKET):
            tkerr(crt_tk, "missing ] in postfix expression")
        return expr_postfix1()
    if consume(TokenCode.DOT):
        if not consume(TokenCode.ID):
            tkerr(crt_tk, "missing identifier after .")
        return expr_postfix1()
    return True  # ε


# ── exprPrimary ──────────────────────────────────────────────────────────────
# exprPrimary: ID ( LPAR ( expr ( COMMA expr )* )? RPAR )?
#            | CT_INT | CT_REAL | CT_CHAR | CT_STRING | LPAR expr RPAR
def expr_primary() -> bool:
    global crt_tk
    if consume(TokenCode.ID):
        if consume(TokenCode.LPAR):
            if expr():
                while consume(TokenCode.COMMA):
                    if not expr():
                        tkerr(crt_tk, "invalid expression after , in function call")
            if not consume(TokenCode.RPAR):
                tkerr(crt_tk, "missing ) in function call")
        return True
    if consume(TokenCode.CT_INT):
        return True
    if consume(TokenCode.CT_REAL):
        return True
    if consume(TokenCode.CT_CHAR):
        return True
    if consume(TokenCode.CT_STRING):
        return True
    start_tk = crt_tk
    if consume(TokenCode.LPAR):
        if expr():
            if not consume(TokenCode.RPAR):
                tkerr(crt_tk, "missing )")
            return True
        # expr() failed — the '(' might be part of a cast like (int)y,
        # which is handled by expr_cast() at a higher level; backtrack.
        crt_tk = start_tk
    return False


# ═════════════════════════════════════════════════════════════════════════════
#  Entry point
# ═════════════════════════════════════════════════════════════════════════════

def parse(source: str):
    """Tokenize and syntactically analyse the given source code."""
    global crt_tk
    tokenize(source)
    from lexer import tokens as tk_head
    crt_tk = tk_head
    unit()


# ── Main ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <input_file>", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    with open(input_path, "r", encoding="utf-8") as f:
        source = f.read()

    parse(source)
    print(f"{input_path}: syntactic analysis passed")
