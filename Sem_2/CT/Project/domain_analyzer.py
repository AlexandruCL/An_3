
import sys
import copy
from typing import Optional

from lexer import TokenCode, Token, tokenize, tokens, tkerr


# ═════════════════════════════════════════════════════════════════════════════
#  Enums (from LFTC-L5.pdf)
# ═════════════════════════════════════════════════════════════════════════════

# Type base kinds
TB_INT    = 0
TB_DOUBLE = 1
TB_CHAR   = 2
TB_STRUCT = 3
TB_VOID   = 4

# Symbol classification
CLS_VAR     = 0
CLS_FUNC    = 1
CLS_EXTFUNC = 2
CLS_STRUCT  = 3

# Memory scope
MEM_GLOBAL = 0
MEM_ARG    = 1
MEM_LOCAL  = 2


# ═════════════════════════════════════════════════════════════════════════════
#  Data Structures (from LFTC-L5.pdf)
# ═════════════════════════════════════════════════════════════════════════════

class Type:
    """Represents the type of a symbol in AtomC."""
    def __init__(self):
        self.tb: int = -1          # type base: TB_*
        self.s: Optional['Symbol'] = None  # struct definition (for TB_STRUCT)
        self.n: int = -1           # nElements: >0 array, 0=array no size, <0=scalar


class Symbol:
    """Represents a symbol (variable, function, struct) in the symbol table."""
    def __init__(self, name: str, cls: int):
        self.name: str = name
        self.cls: int = cls        # CLS_*
        self.mem: int = MEM_GLOBAL # MEM_*
        self.type: Type = Type()
        self.depth: int = 0        # 0=global, 1=in function, 2+=nested blocks
        # For CLS_FUNC / CLS_EXTFUNC
        self.args: list['Symbol'] = []     # parameter symbols (fn.params)
        self.locals: list['Symbol'] = []   # local variable symbols (fn.locals)
        # For CLS_STRUCT
        self.members: list['Symbol'] = []  # struct member symbols


# ═════════════════════════════════════════════════════════════════════════════
#  Helper functions
# ═════════════════════════════════════════════════════════════════════════════

def copy_type(t: Type) -> Type:
    """Create a deep copy of a Type."""
    new = Type()
    new.tb = t.tb
    new.s = t.s
    new.n = t.n
    return new


def dup_symbol(s: Symbol) -> Symbol:
    """Create a duplicate of a Symbol (for sub-lists)."""
    d = Symbol(s.name, s.cls)
    d.mem = s.mem
    d.type = copy_type(s.type)
    d.depth = s.depth
    d.args = list(s.args)
    d.locals = list(s.locals)
    d.members = list(s.members)
    return d


# ═════════════════════════════════════════════════════════════════════════════
#  Symbol Table Operations (from LFTC-L5.pdf)
# ═════════════════════════════════════════════════════════════════════════════

symbols: list[Symbol] = []       # the main symbol table (flat list)
crt_depth: int = 0               # current domain depth
owner: Optional[Symbol] = None   # current struct or function being defined


def addSymbol(name: str, cls: int) -> Symbol:
    """Create a new Symbol at current depth, append to symbol table, return it."""
    s = Symbol(name, cls)
    s.depth = crt_depth
    symbols.append(s)
    return s


def findSymbol(name: str) -> Optional[Symbol]:
    """Search symbols right-to-left for name. Returns symbol or None."""
    for i in range(len(symbols) - 1, -1, -1):
        if symbols[i].name == name:
            return symbols[i]
    return None


def findSymbolInDomain(name: str) -> Optional[Symbol]:
    """Search symbols right-to-left, only at crt_depth. Returns symbol or None."""
    for i in range(len(symbols) - 1, -1, -1):
        if symbols[i].depth < crt_depth:
            break
        if symbols[i].depth == crt_depth and symbols[i].name == name:
            return symbols[i]
    return None


def pushDomain():
    """Enter a new (deeper) domain."""
    global crt_depth
    crt_depth += 1


def dropDomain():
    """Remove all symbols at current depth, then decrement depth."""
    global crt_depth
    while symbols and symbols[-1].depth == crt_depth:
        symbols.pop()
    crt_depth -= 1


# ═════════════════════════════════════════════════════════════════════════════
#  Predefined External Functions
# ═════════════════════════════════════════════════════════════════════════════

def _make_arg(name: str, tb: int, n: int = -1) -> Symbol:
    """Helper: create a parameter symbol for an external function."""
    p = Symbol(name, CLS_VAR)
    p.mem = MEM_ARG
    p.type = Type()
    p.type.tb = tb
    p.type.n = n
    return p


def addExtFn(name: str, ret_tb: int, params: list[Symbol]):
    """Register a predefined external function."""
    fn = addSymbol(name, CLS_EXTFUNC)
    fn.type.tb = ret_tb
    fn.type.n = -1
    fn.args = params


def addPredefinedFunctions():
    """Add the built-in I/O functions used in AtomC test programs."""
    addExtFn("put_s", TB_VOID, [_make_arg("s", TB_CHAR, 0)])
    addExtFn("get_s", TB_VOID, [_make_arg("s", TB_CHAR, 0)])
    addExtFn("put_i", TB_VOID, [_make_arg("i", TB_INT)])
    addExtFn("get_i", TB_INT,  [])
    addExtFn("put_d", TB_VOID, [_make_arg("d", TB_DOUBLE)])
    addExtFn("get_d", TB_DOUBLE, [])
    addExtFn("put_c", TB_VOID, [_make_arg("c", TB_CHAR)])
    addExtFn("get_c", TB_CHAR, [])


# ═════════════════════════════════════════════════════════════════════════════
#  Global parser state
# ═════════════════════════════════════════════════════════════════════════════

crt_tk: Optional[Token] = None
consumed_tk: Optional[Token] = None


# ── Token consumer (identical to parser.py) ─────────────────────────────────
def consume(code: int) -> bool:
    global crt_tk, consumed_tk
    if crt_tk.code == code:
        consumed_tk = crt_tk
        crt_tk = crt_tk.next
        return True
    return False


# ═════════════════════════════════════════════════════════════════════════════
#  Grammar predicates with semantic actions
#  (from "AtomC - analiza de domeniu.pdf")
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
# Semantic: struct name unique in domain; pushDomain; set owner; dropDomain
def struct_def() -> bool:
    global crt_tk, owner
    start_tk = crt_tk
    if not consume(TokenCode.STRUCT):
        return False
    if not consume(TokenCode.ID):
        tkerr(crt_tk, "missing identifier after struct")
    tk_name = consumed_tk
    if not consume(TokenCode.LACC):
        crt_tk = start_tk
        return False
    # ── semantic action (after LACC — committed to structDef) ──
    s = findSymbolInDomain(tk_name.text)
    if s:
        tkerr(crt_tk, f"symbol redefinition: {tk_name.text}")
    s = addSymbol(tk_name.text, CLS_STRUCT)
    s.type.tb = TB_STRUCT
    s.type.s = s
    s.type.n = -1
    pushDomain()
    owner = s
    # ── end semantic action ──
    while var_def():
        pass
    if not consume(TokenCode.RACC):
        tkerr(crt_tk, "missing } in struct definition")
    if not consume(TokenCode.SEMICOLON):
        tkerr(crt_tk, "missing ; after struct definition")
    # ── semantic action ──
    owner = None
    dropDomain()
    # ── end semantic action ──
    return True


# ── varDef ───────────────────────────────────────────────────────────────────
# varDef: typeBase ID arrayDecl? SEMICOLON
# Semantic: var name unique in domain; vector must have size; add to owner
def var_def() -> bool:
    global crt_tk, owner
    start_tk = crt_tk
    # {Type t;}
    matched, t = type_base()
    if not matched:
        return False
    if not consume(TokenCode.ID):
        tkerr(crt_tk, "missing identifier in variable definition")
    tk_name = consumed_tk
    if array_decl(t):
        # vector variables must have specified dimension
        if t.n == 0:
            tkerr(crt_tk, "a vector variable must have a specified dimension")
    if not consume(TokenCode.SEMICOLON):
        crt_tk = start_tk
        return False
    # ── semantic action (after SEMICOLON — committed) ──
    var = findSymbolInDomain(tk_name.text)
    if var:
        tkerr(crt_tk, f"symbol redefinition: {tk_name.text}")
    var = addSymbol(tk_name.text, CLS_VAR)
    var.type = copy_type(t)
    if owner:
        if owner.cls == CLS_FUNC:
            var.mem = MEM_LOCAL
            owner.locals.append(dup_symbol(var))
        elif owner.cls == CLS_STRUCT:
            var.mem = MEM_GLOBAL  # struct members stored globally in concept
            owner.members.append(dup_symbol(var))
    else:
        var.mem = MEM_GLOBAL
    # ── end semantic action ──
    return True


# ── typeBase ─────────────────────────────────────────────────────────────────
# typeBase: INT | DOUBLE | CHAR | STRUCT ID
# Semantic: if struct, it must be already defined; returns Type
def type_base():
    """Returns (True, Type) if matched, (False, None) if not."""
    global crt_tk
    t = Type()
    t.n = -1
    if consume(TokenCode.INT):
        t.tb = TB_INT
        return True, t
    if consume(TokenCode.DOUBLE):
        t.tb = TB_DOUBLE
        return True, t
    if consume(TokenCode.CHAR):
        t.tb = TB_CHAR
        return True, t
    if consume(TokenCode.STRUCT):
        if not consume(TokenCode.ID):
            tkerr(crt_tk, "missing identifier after struct")
        tk_name = consumed_tk
        # ── semantic action ──
        t.tb = TB_STRUCT
        t.s = findSymbol(tk_name.text)
        if not t.s:
            tkerr(crt_tk, f"undefined struct: {tk_name.text}")
        # ── end semantic action ──
        return True, t
    return False, None


# ── arrayDecl ────────────────────────────────────────────────────────────────
# arrayDecl: LBRACKET ( CT_INT | ε ) RBRACKET
# Semantic: sets t.n to array size or 0
def array_decl(t: Type) -> bool:
    global crt_tk
    if not consume(TokenCode.LBRACKET):
        return False
    if consume(TokenCode.CT_INT):
        # ── semantic action ──
        t.n = consumed_tk.i
        # ── end semantic action ──
    else:
        # ── semantic action ──
        t.n = 0
        # ── end semantic action ──
    if not consume(TokenCode.RBRACKET):
        tkerr(crt_tk, "missing ] in array declaration")
    return True


# ── fnDef ────────────────────────────────────────────────────────────────────
# fnDef: ( typeBase | VOID ) ID LPAR ( fnParam ( COMMA fnParam )* )? RPAR
#        stmCompound[false]
# Semantic: fn name unique; pushDomain after LPAR; dropDomain at end
def fn_def() -> bool:
    global crt_tk, owner
    start_tk = crt_tk
    # {Type t;}
    matched, t = type_base()
    if not matched:
        if consume(TokenCode.VOID):
            t = Type()
            t.tb = TB_VOID
            t.n = -1
        else:
            return False
    if not consume(TokenCode.ID):
        crt_tk = start_tk
        return False
    tk_name = consumed_tk
    if not consume(TokenCode.LPAR):
        crt_tk = start_tk
        return False
    # ── semantic action (after LPAR — committed to fnDef) ──
    fn = findSymbolInDomain(tk_name.text)
    if fn:
        tkerr(crt_tk, f"symbol redefinition: {tk_name.text}")
    fn = addSymbol(tk_name.text, CLS_FUNC)
    fn.type = copy_type(t)
    owner = fn
    pushDomain()
    # ── end semantic action ──
    if fn_param():
        while consume(TokenCode.COMMA):
            if not fn_param():
                tkerr(crt_tk, "missing parameter after ,")
    if not consume(TokenCode.RPAR):
        tkerr(crt_tk, "missing ) in function definition")
    # stmCompound[false] — function body does NOT create a new subdomain
    if not stm_compound(False):
        tkerr(crt_tk, "missing function body")
    # ── semantic action ──
    dropDomain()
    owner = None
    # ── end semantic action ──
    return True


# ── fnParam ──────────────────────────────────────────────────────────────────
# fnParam: typeBase ID arrayDecl?
# Semantic: param name unique; add to owner.args; array params lose dimension
def fn_param() -> bool:
    global crt_tk, owner
    matched, t = type_base()
    if not matched:
        return False
    if not consume(TokenCode.ID):
        tkerr(crt_tk, "missing identifier in parameter")
    tk_name = consumed_tk
    if array_decl(t):
        # parameters: array dimension is erased (int v[10] -> int v[])
        t.n = 0
    # ── semantic action ──
    param = findSymbolInDomain(tk_name.text)
    if param:
        tkerr(crt_tk, f"symbol redefinition: {tk_name.text}")
    param = addSymbol(tk_name.text, CLS_VAR)
    param.type = copy_type(t)
    param.mem = MEM_ARG
    # add to owner's parameter list
    owner.args.append(dup_symbol(param))
    # ── end semantic action ──
    return True


# ── stm ──────────────────────────────────────────────────────────────────────
# stm: stmCompound[true]
#    | IF LPAR expr RPAR stm ( ELSE stm )?
#    | WHILE LPAR expr RPAR stm
#    | FOR LPAR expr? SEMICOLON expr? SEMICOLON expr? RPAR stm
#    | BREAK SEMICOLON
#    | RETURN expr? SEMICOLON
#    | expr? SEMICOLON
def stm() -> bool:
    global crt_tk
    # stmCompound[true] — compound blocks in statements create new domains
    if stm_compound(True):
        return True
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
    if consume(TokenCode.FOR):
        if not consume(TokenCode.LPAR):
            tkerr(crt_tk, "missing ( after for")
        expr()
        if not consume(TokenCode.SEMICOLON):
            tkerr(crt_tk, "missing ; after for initializer")
        expr()
        if not consume(TokenCode.SEMICOLON):
            tkerr(crt_tk, "missing ; after for condition")
        expr()
        if not consume(TokenCode.RPAR):
            tkerr(crt_tk, "missing ) after for clauses")
        if not stm():
            tkerr(crt_tk, "missing for body statement")
        return True
    if consume(TokenCode.BREAK):
        if not consume(TokenCode.SEMICOLON):
            tkerr(crt_tk, "missing ; after break")
        return True
    if consume(TokenCode.RETURN):
        expr()
        if not consume(TokenCode.SEMICOLON):
            tkerr(crt_tk, "missing ; after return")
        return True
    if expr():
        if not consume(TokenCode.SEMICOLON):
            tkerr(crt_tk, "missing ; after expression")
        return True
    if consume(TokenCode.SEMICOLON):
        return True
    return False


# ── stmCompound ──────────────────────────────────────────────────────────────
# stmCompound[newDomain]: LACC ( varDef | stm )* RACC
# Semantic: pushDomain/dropDomain only if newDomain is True
def stm_compound(new_domain: bool) -> bool:
    global crt_tk
    if not consume(TokenCode.LACC):
        return False
    # ── semantic action ──
    if new_domain:
        pushDomain()
    # ── end semantic action ──
    while True:
        if var_def():
            pass
        elif stm():
            pass
        else:
            break
    if not consume(TokenCode.RACC):
        tkerr(crt_tk, "missing } or syntax error in compound statement")
    # ── semantic action ──
    if new_domain:
        dropDomain()
    # ── end semantic action ──
    return True


# ═════════════════════════════════════════════════════════════════════════════
#  Expression rules (identical logic to parser.py — no semantic actions)
# ═════════════════════════════════════════════════════════════════════════════

def expr() -> bool:
    return expr_assign()


def expr_assign() -> bool:
    global crt_tk
    start_tk = crt_tk
    if expr_unary():
        if consume(TokenCode.ASSIGN):
            if not expr_assign():
                tkerr(crt_tk, "invalid expression after =")
            return True
        crt_tk = start_tk
    return expr_or()


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
    return True


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
    return True


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
    return True


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
    return True


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
    return True


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
    return True


def expr_cast() -> bool:
    global crt_tk
    start_tk = crt_tk
    if consume(TokenCode.LPAR):
        matched, t = type_base()
        if matched:
            array_decl(t) if t else None
            if consume(TokenCode.RPAR):
                if expr_cast():
                    return True
        crt_tk = start_tk
    return expr_unary()


def expr_unary() -> bool:
    global crt_tk
    if consume(TokenCode.SUB) or consume(TokenCode.NOT):
        if not expr_unary():
            tkerr(crt_tk, "invalid expression after unary operator")
        return True
    return expr_postfix()


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
    return True


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
        crt_tk = start_tk
    return False


# ═════════════════════════════════════════════════════════════════════════════
#  Symbol Table Display
# ═════════════════════════════════════════════════════════════════════════════

_TB_NAMES = {TB_INT: "int", TB_DOUBLE: "double", TB_CHAR: "char",
             TB_STRUCT: "struct", TB_VOID: "void"}
_CLS_NAMES = {CLS_VAR: "var", CLS_FUNC: "func",
              CLS_EXTFUNC: "extfunc", CLS_STRUCT: "struct"}
_MEM_NAMES = {MEM_GLOBAL: "global", MEM_ARG: "arg", MEM_LOCAL: "local"}


def type_str(t: Type) -> str:
    """Human-readable representation of a Type."""
    s = _TB_NAMES.get(t.tb, "?")
    if t.tb == TB_STRUCT and t.s:
        s += f" {t.s.name}"
    if t.n >= 0:
        s += f"[{t.n}]" if t.n > 0 else "[]"
    return s


def show_symbols():
    """Print all symbols in the symbol table with cls, mem, type."""
    for s in symbols:
        line = (f"{s.name}  cls={_CLS_NAMES.get(s.cls, '?')}"
                f"  mem={_MEM_NAMES.get(s.mem, '?')}"
                f"  type={type_str(s.type)}"
                f"  depth={s.depth}")
        print(line)
        for a in s.args:
            print(f"    arg: {a.name}  type={type_str(a.type)}")
        for m in s.members:
            print(f"    member: {m.name}  type={type_str(m.type)}")


# ═════════════════════════════════════════════════════════════════════════════
#  Entry Point
# ═════════════════════════════════════════════════════════════════════════════

def analyze(source: str):
    """Tokenize the source, then run domain analysis."""
    global crt_tk, consumed_tk, symbols, crt_depth, owner
    # Reset state
    symbols = []
    crt_depth = 0
    owner = None
    consumed_tk = None
    # Lexer
    tokenize(source)
    from lexer import tokens as tk_head
    crt_tk = tk_head
    # Add predefined external functions before analysis
    addPredefinedFunctions()
    # Run domain analysis (parser with semantic actions)
    unit()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <input_file>", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    with open(input_path, "r", encoding="utf-8") as f:
        source = f.read()

    analyze(source)
    print(f"{input_path}: domain analysis passed")
    print()
    show_symbols()
