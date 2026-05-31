# AtomC Domain Analyzer — Complete Explanation

## Table of Contents
1. [What is Domain Analysis?](#1-what-is-domain-analysis)
2. [Where it Fits in the Compiler Pipeline](#2-where-it-fits-in-the-compiler-pipeline)
3. [Data Structures](#3-data-structures)
4. [Symbol Table Operations](#4-symbol-table-operations)
5. [Domain (Scope) Management](#5-domain-scope-management)
6. [Predefined External Functions](#6-predefined-external-functions)
7. [Semantic Actions in Grammar Rules](#7-semantic-actions-in-grammar-rules)
8. [The stmCompound newDomain Distinction](#8-the-stmcompound-newdomain-distinction)
9. [Error Detection Rules](#9-error-detection-rules)
10. [Complete Trace Example](#10-complete-trace-example)
11. [Summary](#11-summary)

---

## 1. What is Domain Analysis?

The **lexer** breaks source code into tokens. The **parser** checks if those tokens form valid grammar. But a syntactically correct program can still be **semantically wrong**:

```c
struct Pt p;          // ERROR: struct Pt doesn't exist yet
int x;
int x;                // ERROR: x is already defined in this scope
void f(int a, int a)  // ERROR: parameter 'a' defined twice
{
    int a;            // ERROR: 'a' already exists (as a parameter)
    {
        int a;        // OK: inner block can shadow outer names
        double a;     // ERROR: 'a' already defined in THIS block
    }
}
```

**Domain Analysis (AD)** determines which symbols (variables, functions, structs) are **visible** at each point in the program. It:
1. Collects all symbol definitions into a **Symbol Table (TS)**
2. Manages nested **domains/scopes** (global → function → nested blocks)
3. Detects errors: redefinitions, undefined types, vectors without size

---

## 2. Where it Fits in the Compiler Pipeline

```
┌──────────┐    tokenize()    ┌──────────────┐    domain analysis    ┌────────────────┐
│  Source   │ ───────────────→ │  Token List  │ ───────────────────→  │  Symbol Table  │
│  Code    │                  │ INT→ID→;→END │                      │  + error check │
└──────────┘                  └──────────────┘                      └────────────────┘
                                     │                                      │
                                     └──────── same token list ─────────────┘
```

The domain analyzer **re-uses the same recursive descent parser logic** but embeds **semantic actions** (code in `{ }` blocks from the documentation) at specific points. It walks the same token list produced by the lexer.

---

## 3. Data Structures

### Enums (from LFTC-L5.pdf)

```python
# Type base kinds
TB_INT, TB_DOUBLE, TB_CHAR, TB_STRUCT, TB_VOID = 0, 1, 2, 3, 4

# Symbol classification
CLS_VAR     = 0   # variable (local, global, or parameter)
CLS_FUNC    = 1   # user-defined function
CLS_EXTFUNC = 2   # predefined external function (put_i, get_d, etc.)
CLS_STRUCT  = 3   # struct type definition

# Memory scope
MEM_GLOBAL = 0    # global variable or struct member
MEM_ARG    = 1    # function parameter
MEM_LOCAL  = 2    # local variable inside a function
```

### Type (from LFTC-L5.pdf)

```python
class Type:
    tb: int           # TB_INT, TB_DOUBLE, TB_CHAR, TB_STRUCT, TB_VOID
    s:  Symbol|None   # for TB_STRUCT: points to the struct's Symbol
    n:  int           # >0 = array[n], 0 = array[], <0 = scalar (not array)
```

| Example | `tb` | `s` | `n` |
|---|---|---|---|
| `int x` | TB_INT | None | -1 |
| `int v[10]` | TB_INT | None | 10 |
| `struct Pt p` | TB_STRUCT | →Pt symbol | -1 |
| `char s[]` (param) | TB_CHAR | None | 0 |

### Symbol (from LFTC-L5.pdf)

```python
class Symbol:
    name:    str          # identifier name (from token)
    cls:     int          # CLS_VAR, CLS_FUNC, CLS_EXTFUNC, CLS_STRUCT
    mem:     int          # MEM_GLOBAL, MEM_ARG, MEM_LOCAL
    type:    Type         # the symbol's type
    depth:   int          # 0=global, 1=inside function, 2+=nested blocks
    args:    list[Symbol] # CLS_FUNC: function parameters
    locals:  list[Symbol] # CLS_FUNC: local variables
    members: list[Symbol] # CLS_STRUCT: struct member fields
```

---

## 4. Symbol Table Operations

The symbol table is a **flat list** (`symbols: list[Symbol]`). Symbols are appended as they're defined and removed (from the end) when a scope closes.

### `addSymbol(name, cls)` → Symbol

Creates a new Symbol at the current depth, appends it to `symbols`, returns it.

```python
def addSymbol(name, cls):
    s = Symbol(name, cls)
    s.depth = crt_depth
    symbols.append(s)
    return s
```

### `findSymbol(name)` → Symbol | None

Searches **right to left** (newest first). Returns the most recent symbol with that name, regardless of depth. Used when we need any visible definition (e.g., checking if a struct type exists).

```python
def findSymbol(name):
    for i in range(len(symbols) - 1, -1, -1):
        if symbols[i].name == name:
            return symbols[i]
    return None
```

**Why right-to-left?** Inner scopes can shadow outer definitions. `findSymbol("x")` returns the innermost `x`.

### `findSymbolInDomain(name)` → Symbol | None

Searches right to left, but **only at the current depth**. Stops when it hits a symbol with depth < crt_depth. Used to check for **redefinition within the same scope**.

```python
def findSymbolInDomain(name):
    for i in range(len(symbols) - 1, -1, -1):
        if symbols[i].depth < crt_depth:
            break  # no more symbols in current domain
        if symbols[i].depth == crt_depth and symbols[i].name == name:
            return symbols[i]
    return None
```

**Key difference:**
- `findSymbol("x")` → "does `x` exist anywhere visible?" (for usage)
- `findSymbolInDomain("x")` → "is `x` already defined in THIS scope?" (for redefinition check)

---

## 5. Domain (Scope) Management

```python
crt_depth: int = 0           # current nesting level
owner: Symbol | None = None  # struct or function currently being defined
```

### `pushDomain()`

Increments `crt_depth`. All symbols added after this will be at the new, deeper level.

### `dropDomain()`

Removes all symbols at `crt_depth` from the end of the list, then decrements `crt_depth`. This makes local symbols invisible after their scope closes.

```python
def dropDomain():
    global crt_depth
    while symbols and symbols[-1].depth == crt_depth:
        symbols.pop()
    crt_depth -= 1
```

### Visual Example

```c
int x;                    // depth=0, symbols: [x]
void f(int a)             // depth=0, symbols: [x, f]
                          //   pushDomain() → depth=1
                          //   param 'a': depth=1, symbols: [x, f, a]
{
    int y;                // depth=1, symbols: [x, f, a, y]
    {                     // pushDomain() → depth=2
        int z;            // depth=2, symbols: [x, f, a, y, z]
    }                     // dropDomain(): remove z → depth=1
}                         // dropDomain(): remove a,y → depth=0
                          // symbols: [x, f]  ← a,y are gone but f.args still has 'a'
```

**Important:** When parameters/locals are added, they're also `dup_symbol()`'d into `owner.args` or `owner.locals`. So even after `dropDomain()` removes them from the main table, the function symbol still knows its parameters.

---

## 6. Predefined External Functions

Before analysis begins, 8 built-in I/O functions are registered as `CLS_EXTFUNC`:

| Function | Return Type | Parameters |
|---|---|---|
| `put_s(char s[])` | void | s: char[] |
| `get_s(char s[])` | void | s: char[] |
| `put_i(int i)` | void | i: int |
| `get_i()` | int | (none) |
| `put_d(double d)` | void | d: double |
| `get_d()` | double | (none) |
| `put_c(char c)` | void | c: char |
| `get_c()` | char | (none) |

These exist at depth=0 and are always visible, allowing test programs to call them.

---

## 7. Semantic Actions in Grammar Rules

Each grammar rule from the parser is augmented with semantic actions from **"AtomC - analiza de domeniu.pdf"**. The parsing logic is identical; only `{ }` blocks are added.

### `typeBase` → returns `(bool, Type)`

```
typeBase[out Type *t]: {t.n = -1}
  INT      {t.tb = TB_INT}
| DOUBLE   {t.tb = TB_DOUBLE}
| CHAR     {t.tb = TB_CHAR}
| STRUCT ID[tkName]
    {
        t.tb = TB_STRUCT
        t.s = findSymbol(tkName.text)
        if not t.s → ERROR "undefined struct"     ← struct must exist
    }
```

**Key rule:** When using `struct Pt` as a type, `Pt` must already be defined. `findSymbol` (not `findSymbolInDomain`) is used because the struct could be defined in any outer scope.

### `arrayDecl` — modifies Type.n

```
arrayDecl[inout Type *t]: LBRACKET
  ( CT_INT[tkSize] {t.n = tkSize.i}    ← array with size
  | {t.n = 0}                          ← array without size
  ) RBRACKET
```

### `structDef`

```python
def struct_def():
    # ... consume STRUCT ID LACC ...
    # ── after LACC (committed) ──
    s = findSymbolInDomain(tkName.text)
    if s: ERROR "symbol redefinition"       # struct name must be unique
    s = addSymbol(tkName.text, CLS_STRUCT)
    s.type.tb = TB_STRUCT
    s.type.s = s                            # self-reference
    s.type.n = -1
    pushDomain()                            # new scope for members
    owner = s                               # varDef will add to s.members
    # ... parse varDef* RACC SEMICOLON ...
    owner = None
    dropDomain()                            # remove member symbols from table
```

**Why `s.type.s = s`?** The struct symbol's type points back to itself. This is how `struct Pt p` links `p.type.s` → the `Pt` symbol (which has `.members`).

### `varDef`

```python
def var_def():
    # ... type_base() → t, consume ID → tkName, array_decl(t) ...
    if t.n == 0: ERROR "vector must have specified dimension"  # int v[] is invalid
    # ... consume SEMICOLON (backtrack if missing) ...
    # ── after SEMICOLON (committed) ──
    var = findSymbolInDomain(tkName.text)
    if var: ERROR "symbol redefinition"
    var = addSymbol(tkName.text, CLS_VAR)
    var.type = copy_type(t)
    if owner:
        if owner.cls == CLS_FUNC:
            var.mem = MEM_LOCAL              # local variable of function
            owner.locals.append(dup(var))    # stored in function's locals list
        elif owner.cls == CLS_STRUCT:
            owner.members.append(dup(var))   # stored in struct's members list
    else:
        var.mem = MEM_GLOBAL                 # global variable
```

**owner** determines where the variable belongs:
- `owner = None` → global scope
- `owner.cls == CLS_FUNC` → local variable of a function
- `owner.cls == CLS_STRUCT` → member field of a struct

### `fnDef`

```python
def fn_def():
    # ... type_base()|VOID → t, consume ID → tkName, consume LPAR ...
    # ── after LPAR (committed) ──
    fn = findSymbolInDomain(tkName.text)
    if fn: ERROR "symbol redefinition"
    fn = addSymbol(tkName.text, CLS_FUNC)
    fn.type = copy_type(t)
    owner = fn                               # fnParam and varDef will use this
    pushDomain()                             # domain for params + locals
    # ... parse params, RPAR ...
    stm_compound(new_domain=False)           # body does NOT create new subdomain
    # ── after body ──
    dropDomain()                             # remove params + locals from table
    owner = None
```

**Critical:** `pushDomain()` happens after `LPAR`, not after `LACC`. The function's local domain starts at the parameter list. This means `stm_compound` is called with `new_domain=False` because the domain is already open.

### `fnParam`

```python
def fn_param():
    # ... type_base() → t, consume ID → tkName, array_decl(t)? ...
    if array_decl matched:
        t.n = 0                              # array params lose their dimension
    # ── semantic action ──
    param = findSymbolInDomain(tkName.text)
    if param: ERROR "symbol redefinition"
    param = addSymbol(tkName.text, CLS_VAR)
    param.type = copy_type(t)
    param.mem = MEM_ARG
    owner.args.append(dup(param))            # stored in function's args list
```

**Array parameter rule:** `int v[10]` as a parameter becomes `int v[]` (dimension erased, `t.n = 0`). This follows C conventions where array parameters decay to pointers.

---

## 8. The stmCompound newDomain Distinction

This is the most subtle part of the domain analyzer, explicitly stated in the documentation:

```
// corpul functiei {...} nu defineste un nou subdomeniu
fnDef: ... stmCompound[false]

// corpul compus {...} al instructiunilor defineste un nou domeniu
stm: stmCompound[true] ...
```

```python
def stm_compound(new_domain: bool):
    # consume LACC
    if new_domain: pushDomain()     # only if called from stm()
    # ... parse varDef | stm ...
    # consume RACC
    if new_domain: dropDomain()     # only if called from stm()
```

### Why?

The function **already pushed its domain** after `LPAR`. The `{ }` body is part of that same scope. But a `{ }` block inside a statement (like inside `if` or standalone) creates its own sub-scope:

```c
void f(int a)           // pushDomain() → depth=1
{                       // stmCompound(false) → NO push (still depth=1)
    int x;              // depth=1, same scope as param 'a'
    int a;              // ERROR: 'a' already at depth=1
    {                   // stmCompound(true) → pushDomain() → depth=2
        int a;          // OK: depth=2, shadows param 'a'
        int x;          // OK: depth=2, shadows local 'x'
    }                   // dropDomain() → depth=1
}                       // NO drop here (fn_def does dropDomain later)
                        // dropDomain() → depth=0
```

---

## 9. Error Detection Rules

| Error | When | Check |
|---|---|---|
| Symbol redefinition | `structDef`, `varDef`, `fnDef`, `fnParam` | `findSymbolInDomain(name)` returns non-None |
| Undefined struct | `typeBase` with `STRUCT ID` | `findSymbol(name)` returns None |
| Vector without size | `varDef` with `arrayDecl` | `t.n == 0` after arrayDecl |

### Redefinition rules summarized:

```c
int x;
int x;                  // ERROR: same domain (global)

void f(int a, int a){}  // ERROR: same domain (function params)

void f(int a){
    int a;              // ERROR: function body is SAME domain as params
    {
        int a;          // OK: inner block is a NEW domain
        int a;          // ERROR: same inner domain
    }
}

int x;
void f(int x){}         // OK: 'x' param is in domain depth=1, global 'x' is depth=0
```

---

## 10. Complete Trace Example

```c
struct Pt{ int x; int y; };
struct Pt p;
int f(int a){ return a; }
```

```
analyze("struct Pt{int x;int y;};struct Pt p;int f(int a){return a;}")
  addPredefinedFunctions()   → symbols: [put_s, get_s, put_i, get_i, put_d, get_d, put_c, get_c]
  crt_tk = STRUCT            → depth=0

  unit()
    struct_def()
      consume(STRUCT) ✓     → crt_tk = ID("Pt")
      consume(ID) ✓         → tkName = "Pt", crt_tk = LACC
      consume(LACC) ✓       → committed to structDef
        findSymbolInDomain("Pt") → None (not redefined) ✓
        addSymbol("Pt", CLS_STRUCT)
        pushDomain()         → depth=1
        owner = Pt
      var_def()              → "int x;"
        type_base() → t={tb=TB_INT, n=-1}
        consume(ID) → tkName="x"
        consume(SEMICOLON) ✓
        findSymbolInDomain("x") → None ✓
        addSymbol("x", CLS_VAR) at depth=1
        owner=Pt(CLS_STRUCT) → Pt.members.append(dup(x))
      var_def()              → "int y;"
        (same as above, adds y to Pt.members)
      var_def()              → False (crt_tk = RACC, not a type)
      consume(RACC) ✓
      consume(SEMICOLON) ✓
        owner = None
        dropDomain()         → removes x,y from symbols; depth=0
        symbols: [...extfns, Pt]  (but Pt.members still has x,y copies)

    var_def()                → "struct Pt p;"
      type_base()
        consume(STRUCT) ✓
        consume(ID) ✓ → tkName="Pt"
        findSymbol("Pt") → found! ✓
        t = {tb=TB_STRUCT, s=→Pt, n=-1}
      consume(ID) ✓ → tkName="p"
      consume(SEMICOLON) ✓
      findSymbolInDomain("p") → None ✓
      addSymbol("p", CLS_VAR), type=struct Pt, mem=MEM_GLOBAL
      symbols: [...extfns, Pt, p]

    fn_def()                 → "int f(int a){return a;}"
      type_base() → t={tb=TB_INT, n=-1}
      consume(ID) ✓ → tkName="f"
      consume(LPAR) ✓ → committed
        findSymbolInDomain("f") → None ✓
        addSymbol("f", CLS_FUNC), type=int
        owner = f
        pushDomain()         → depth=1
      fn_param()             → "int a"
        type_base() → t={tb=TB_INT, n=-1}
        consume(ID) ✓ → tkName="a"
        findSymbolInDomain("a") → None ✓
        addSymbol("a", CLS_VAR), mem=MEM_ARG, depth=1
        f.args.append(dup(a))
      consume(RPAR) ✓
      stm_compound(false)    → "{return a;}"
        consume(LACC) ✓
        new_domain=false → NO pushDomain (still depth=1)
        stm() → "return a;"
          consume(RETURN) ✓
          expr() → "a" → expr_primary → consume(ID) ✓
          consume(SEMICOLON) ✓
        consume(RACC) ✓
        new_domain=false → NO dropDomain
      dropDomain()           → removes 'a' from symbols; depth=0
      owner = None
      symbols: [...extfns, Pt, p, f]  (f.args still has 'a')

    consume(END) ✓ → DONE!
```

Final symbol table:
```
put_s    cls=extfunc  mem=global  type=void      arg: s type=char[]
get_s    cls=extfunc  mem=global  type=void      arg: s type=char[]
put_i    cls=extfunc  mem=global  type=void      arg: i type=int
get_i    cls=extfunc  mem=global  type=int
put_d    cls=extfunc  mem=global  type=void      arg: d type=double
get_d    cls=extfunc  mem=global  type=double
put_c    cls=extfunc  mem=global  type=void      arg: c type=char
get_c    cls=extfunc  mem=global  type=char
Pt       cls=struct   mem=global  type=struct Pt  member: x type=int, member: y type=int
p        cls=var      mem=global  type=struct Pt
f        cls=func     mem=global  type=int        arg: a type=int
```

---

## 12. Beyond the Documentation — What a Full Domain Analyzer Would Add

The current implementation strictly follows the "AtomC - analiza de domeniu.pdf" documentation, which only specifies semantic actions for **definitions** (structDef, varDef, fnDef, fnParam). However, a complete domain analyzer would also check **usage** — verifying that symbols are valid when they appear in expressions. Below are the extensions a professor might ask about, with exact code changes.

---

### 12.1 Check that variables/functions used in expressions are defined

**Problem:** Currently, `expr_primary()` consumes an `ID` without checking if that name exists in the symbol table. This means `x = undefinedVar;` would pass silently.

**Where to change:** `expr_primary()` in `domain_analyzer.py` (line ~664)

**Current code:**
```python
def expr_primary() -> bool:
    global crt_tk
    if consume(TokenCode.ID):
        if consume(TokenCode.LPAR):
            ...
        return True
```

**Changed code:**
```python
def expr_primary() -> bool:
    global crt_tk
    if consume(TokenCode.ID):
        tk_name = consumed_tk
        s = findSymbol(tk_name.text)
        if not s:
            tkerr(crt_tk, f"undefined identifier: {tk_name.text}")
        if consume(TokenCode.LPAR):
            # It's a function call — verify it's actually a function
            if s.cls != CLS_FUNC and s.cls != CLS_EXTFUNC:
                tkerr(crt_tk, f"{tk_name.text} is not a function")
            if expr():
                while consume(TokenCode.COMMA):
                    if not expr():
                        tkerr(crt_tk, "invalid expression after , in function call")
            if not consume(TokenCode.RPAR):
                tkerr(crt_tk, "missing ) in function call")
        return True
```

**What it does:** After consuming an ID, we call `findSymbol()` (searches all depths, right-to-left) to verify the name exists. If followed by `(`, we also verify it's classified as a function.

---

### 12.2 Check function call argument count

**Problem:** `put_i(1, 2, 3)` would pass silently even though `put_i` takes exactly 1 argument.

**Where to change:** Same `expr_primary()` function, inside the function call branch.

**Changed code (extending 12.1):**
```python
        if consume(TokenCode.LPAR):
            if s.cls != CLS_FUNC and s.cls != CLS_EXTFUNC:
                tkerr(crt_tk, f"{tk_name.text} is not a function")
            # Count arguments
            arg_count = 0
            if expr():
                arg_count = 1
                while consume(TokenCode.COMMA):
                    if not expr():
                        tkerr(crt_tk, "invalid expression after , in function call")
                    arg_count += 1
            if not consume(TokenCode.RPAR):
                tkerr(crt_tk, "missing ) in function call")
            # Verify argument count
            expected = len(s.args)
            if arg_count != expected:
                tkerr(crt_tk, f"{tk_name.text} expects {expected} args, got {arg_count}")
```

**What it does:** Counts the comma-separated expressions in the call and compares against `len(s.args)`.

---

### 12.3 Check struct member access (dot operator)

**Problem:** `p.nonexistent` would pass silently. We should verify that after `.`, the member name actually exists in the struct definition.

**Where to change:** `expr_postfix1()` in `domain_analyzer.py` (line ~655)

**Current code:**
```python
def expr_postfix1() -> bool:
    global crt_tk
    ...
    if consume(TokenCode.DOT):
        if not consume(TokenCode.ID):
            tkerr(crt_tk, "missing identifier after .")
        return expr_postfix1()
    return True
```

**Changed code:**
```python
    if consume(TokenCode.DOT):
        if not consume(TokenCode.ID):
            tkerr(crt_tk, "missing identifier after .")
        # To fully validate, we would need the type of the left-hand
        # expression. This requires type propagation (see 12.5).
        # A simpler check: verify the member name exists in SOME struct:
        tk_member = consumed_tk
        # Full version (with type propagation) would be:
        # if left_type.tb != TB_STRUCT:
        #     tkerr(crt_tk, "dot operator requires struct type")
        # found = False
        # for m in left_type.s.members:
        #     if m.name == tk_member.text:
        #         found = True; break
        # if not found:
        #     tkerr(crt_tk, f"struct has no member '{tk_member.text}'")
        return expr_postfix1()
```

**Why it's hard:** The dot check requires knowing the **type** of the expression to the left of `.`. This means every expression rule would need to return/propagate a `Type` — which leads to section 12.5.

---

### 12.4 Track varIdx and typeSize (memory layout)

**Problem:** The documentation mentions `varIdx`, `typeSize()`, and `allocInGlobalMemory()` for computing memory offsets, but we skipped them since they're code-generation concerns. A professor might ask to add them.

**Where to add:** New helper function + modifications to `var_def()`.

**New helper — add after the Symbol Table Operations section:**
```python
# Global memory offset tracker
global_mem_offset: int = 0

def typeSize(t: Type) -> int:
    """Return the size in bytes of a Type."""
    BASE_SIZES = {TB_INT: 4, TB_DOUBLE: 8, TB_CHAR: 1, TB_VOID: 0}
    if t.n < 0:  # scalar
        if t.tb == TB_STRUCT:
            # sum of all member sizes
            return sum(typeSize(m.type) for m in t.s.members)
        return BASE_SIZES.get(t.tb, 0)
    else:  # array
        elem_t = Type()
        elem_t.tb = t.tb
        elem_t.s = t.s
        elem_t.n = -1
        return t.n * typeSize(elem_t) if t.n > 0 else 0

def allocInGlobalMemory(size: int) -> int:
    """Allocate `size` bytes in global memory, return the start offset."""
    global global_mem_offset
    offset = global_mem_offset
    global_mem_offset += size
    return offset
```

**Changes in `var_def()` — replace the owner block with:**
```python
    var = addSymbol(tk_name.text, CLS_VAR)
    var.type = copy_type(t)
    if owner:
        if owner.cls == CLS_FUNC:
            var.mem = MEM_LOCAL
            var.varIdx = len(owner.locals)       # ← NEW
            owner.locals.append(dup_symbol(var))
        elif owner.cls == CLS_STRUCT:
            var.varIdx = typeSize(owner.type)     # ← NEW
            owner.members.append(dup_symbol(var))
    else:
        var.mem = MEM_GLOBAL
        var.varIdx = allocInGlobalMemory(typeSize(t))  # ← NEW
```

**Changes in `fn_param()` — add paramIdx:**
```python
    param = addSymbol(tk_name.text, CLS_VAR)
    param.type = copy_type(t)
    param.mem = MEM_ARG
    param.paramIdx = len(owner.args)             # ← NEW
    owner.args.append(dup_symbol(param))
```

**Also add `varIdx` and `paramIdx` fields to the `Symbol.__init__`:**
```python
    self.varIdx: int = 0      # memory offset / index
    self.paramIdx: int = 0    # parameter index (for MEM_ARG)
```

---

### 12.5 Full type propagation in expressions (advanced)

**Problem:** To do proper type checking (type compatibility in assignments, return types, struct member validation), every expression function would need to return not just `bool` but also the resulting `Type`.

**Approach:** Change every `expr_*` function signature from `-> bool` to `-> Optional[Type]`, where `None` means "didn't match" and a `Type` means "matched, and here's the type of the result."

**Example — `expr_primary` with type propagation:**
```python
def expr_primary() -> Optional[Type]:
    global crt_tk
    if consume(TokenCode.ID):
        tk_name = consumed_tk
        s = findSymbol(tk_name.text)
        if not s:
            tkerr(crt_tk, f"undefined: {tk_name.text}")
        if consume(TokenCode.LPAR):
            # function call — return type is the function's return type
            ...
            return copy_type(s.type)  # return type of the function
        # variable — return the variable's type
        return copy_type(s.type)
    if consume(TokenCode.CT_INT):
        t = Type(); t.tb = TB_INT; t.n = -1
        return t
    if consume(TokenCode.CT_REAL):
        t = Type(); t.tb = TB_DOUBLE; t.n = -1
        return t
    if consume(TokenCode.CT_CHAR):
        t = Type(); t.tb = TB_CHAR; t.n = -1
        return t
    if consume(TokenCode.CT_STRING):
        t = Type(); t.tb = TB_CHAR; t.n = 0
        return t
    ...
    return None  # didn't match
```

**Impact:** This is a large refactor — every `expr_*` function and every call site would need updating. The `bool` checks (`if not expr()`) become `if expr() is None`. This is typically done in a separate **type analysis** phase rather than inside domain analysis.

---

### Quick Reference — What to add if asked

| Question from professor | Section | Difficulty | Lines to change |
|---|---|---|---|
| "Check if variables are defined when used" | 12.1 | Easy | ~5 lines in `expr_primary` |
| "Check if functions are called correctly" | 12.2 | Easy | ~10 lines in `expr_primary` |
| "Validate struct member access" | 12.3 | Hard | Needs type propagation (12.5) |
| "Add memory layout / varIdx" | 12.4 | Medium | ~15 lines + new functions |
| "Full type checking" | 12.5 | Hard | Refactor all expr_* functions |

---

## 13. Summary

| Concept | What it means |
|---|---|
| **Symbol Table** | Flat list of all symbols, appended as defined, popped when scope closes |
| **Domain/Scope** | Nesting level tracked by `crt_depth`; `pushDomain` enters, `dropDomain` exits |
| **owner** | The struct or function currently being defined; determines where `varDef` adds symbols |
| **findSymbol** | Search right-to-left across ALL depths — "is this name visible anywhere?" |
| **findSymbolInDomain** | Search right-to-left at CURRENT depth only — "is this name already defined HERE?" |
| **Redefinition error** | `findSymbolInDomain` finds existing symbol → error |
| **Undefined struct** | `findSymbol` returns None for a struct type → error |
| **stmCompound(false)** | Function body — domain already opened by fnDef |
| **stmCompound(true)** | Statement block — creates its own sub-scope |
| **dup_symbol** | Copy symbol into args/locals/members so it survives dropDomain |
| **CLS_EXTFUNC** | Predefined I/O functions added before analysis starts |
