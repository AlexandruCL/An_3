# AtomC Syntactic Analyzer — Complete Explanation

## Table of Contents
1. [What is a Syntactic Analyzer?](#1-what-is-a-syntactic-analyzer)
2. [How Lexer and Parser Work Together](#2-how-lexer-and-parser-work-together)
3. [The Recursive Descent Parser (RDP) Method](#3-the-recursive-descent-parser-rdp-method)
4. [Core Infrastructure (Lines 1–24)](#4-core-infrastructure)
5. [Top-Level Rules (Lines 31–161)](#5-top-level-rules)
6. [Statement Rules (Lines 163–261)](#6-statement-rules)
7. [Expression Rules (Lines 264–494)](#7-expression-rules)
8. [Left-Recursion Elimination](#8-left-recursion-elimination)
9. [Backtracking](#9-backtracking)
10. [Entry Point (Lines 497–522)](#10-entry-point)
11. [Complete Trace Example](#11-complete-trace-example)

---

## 1. What is a Syntactic Analyzer?

The **lexer** (lexical analyzer) breaks source code into **tokens** — small meaningful pieces like keywords (`int`, `while`), identifiers (`x`, `sum`), operators (`+`, `=`), etc.

The **parser** (syntactic analyzer) checks if those tokens are arranged in a **valid order** according to the language grammar. It answers: *"Is this sequence of tokens a valid program?"*

**Analogy:** The lexer is like recognizing individual words in English. The parser checks if those words form valid sentences with correct grammar.

```
Source:  int x = 5;

Lexer output:   INT  ID("x")  ASSIGN  CT_INT(5)  SEMICOLON

Parser checks:  Is "INT ID ASSIGN CT_INT SEMICOLON" a valid structure?
                → Yes! It matches: typeBase ID = expr ;
```

---

## 2. How Lexer and Parser Work Together

```
┌─────────────┐     tokenize()     ┌─────────────────────────┐
│  Source Code │ ──────────────────→│  Token Linked List       │
│  "int x;"   │                    │  INT → ID("x") → ; → END│
└─────────────┘                    └────────────┬────────────┘
                                                │
                                          crt_tk walks
                                          through this list
                                                │
                                   ┌────────────▼────────────┐
                                   │  Parser (unit())         │
                                   │  Checks grammar rules    │
                                   │  Returns True or Error   │
                                   └─────────────────────────┘
```

The lexer produces a **linked list** of `Token` objects. Each token has:
- `.code` — what type it is (INT, ID, SEMICOLON, etc.)
- `.next` — pointer to the next token
- `.line` — source line number (for error messages)
- `.text`, `.i`, `.r` — the actual value

The parser walks through this list one token at a time using the global pointer `crt_tk`.

---

## 3. The Recursive Descent Parser (RDP) Method

The grammar of AtomC is a set of **rules** (also called **productions**). Each rule describes what a valid construct looks like:

```
varDef:  typeBase  ID  arrayDecl?  SEMICOLON
         ────────  ──  ─────────   ─────────
         "int"     "x" "[5]"       ";"
```

**RDP implements each grammar rule as a Python function** (called a **predicate**). Each predicate:

| If it matches... | It does... |
|---|---|
| ✅ Tokens match the rule | Consumes all matched tokens, advances `crt_tk`, returns `True` |
| ❌ Tokens don't match | Leaves `crt_tk` unchanged, returns `False` |
| ⚠️ Partial match (started but can't finish) | Calls `tkerr()` → prints error and exits |

### The `consume()` function (Lines 14–24)

This is the fundamental building block. It checks **one token**:

```python
def consume(code: int) -> bool:
    global crt_tk, consumed_tk
    if crt_tk.code == code:       # Does current token match?
        consumed_tk = crt_tk      # Save it (useful later for getting values)
        crt_tk = crt_tk.next      # Move to next token
        return True               # "Yes, I consumed it"
    return False                  # "No match, I didn't touch anything"
```

**Example:** If `crt_tk` points to an `INT` token:
- `consume(INT)` → returns `True`, `crt_tk` now points to the next token
- `consume(DOUBLE)` → returns `False`, `crt_tk` is unchanged

---

## 4. Core Infrastructure

### Lines 1–5: Imports

```python
from lexer import TokenCode, Token, tokenize, tokens, tkerr
```

We import from the lexer without modifying it:
- `TokenCode` — the enum with all token types (INT, ID, SEMICOLON, etc.)
- `Token` — the token class
- `tokenize()` — runs the lexer on source code, builds the token list
- `tokens` — head of the token linked list
- `tkerr()` — prints an error with line number and exits

### Lines 8–10: Global State

```python
crt_tk: Optional[Token] = None       # WHERE we are in the token list
consumed_tk: Optional[Token] = None  # LAST token we consumed
```

`crt_tk` is the "cursor" that walks through the token list. Every `consume()` call moves it forward by one.

---

## 5. Top-Level Rules

### `unit()` — Lines 33–46

```
Grammar: unit: ( structDef | fnDef | varDef )* END
```

This is the **entry point** — it defines what a valid AtomC program looks like: zero or more struct definitions, function definitions, or variable definitions, followed by END.

```python
def unit() -> bool:
    while True:                    # Keep trying to match things
        if struct_def():           # Try struct definition first
            pass
        elif fn_def():             # Then function definition
            pass
        elif var_def():            # Then variable definition
            pass
        else:
            break                  # Nothing matched → stop the loop
    if not consume(TokenCode.END): # Must end with END token
        tkerr(crt_tk, "syntax error at top level")
    return True
```

**Why this order matters:** `struct_def` is tried first because `STRUCT ID {` is unambiguous. `fn_def` is tried before `var_def` because both start with `typeBase ID`, but `fn_def` continues with `(` while `var_def` continues with `;`. The parser uses **backtracking** to handle this (explained in Section 9).

### `struct_def()` — Lines 51–69

```
Grammar: structDef: STRUCT ID LACC varDef* RACC SEMICOLON
Example: struct Pt { int x; int y; };
```

```python
def struct_def() -> bool:
    start_tk = crt_tk                          # Save position for backtracking
    if not consume(TokenCode.STRUCT):
        return False                           # Doesn't start with 'struct' → not a structDef
    if not consume(TokenCode.ID):
        tkerr(crt_tk, "missing identifier")    # struct without a name → ERROR
    if not consume(TokenCode.LACC):            # No '{' after 'struct Name'
        crt_tk = start_tk                      # → backtrack! Could be "struct Pt x;"
        return False
    while var_def(): pass                      # Parse member variables
    if not consume(TokenCode.RACC):
        tkerr(crt_tk, "missing }")
    if not consume(TokenCode.SEMICOLON):
        tkerr(crt_tk, "missing ;")
    return True
```

**Key insight:** If we see `struct Pt` but no `{`, this isn't a struct definition — it's a type name (like `struct Pt points[10];`). So we **backtrack** by restoring `crt_tk = start_tk`.

### `var_def()` — Lines 74–90

```
Grammar: typeBase ID arrayDecl? ( COMMA ID arrayDecl? )* SEMICOLON
Example: int i, v[5], s;
```

```python
def var_def() -> bool:
    start_tk = crt_tk
    if not type_base(): return False          # Must start with a type
    if not consume(TokenCode.ID):
        tkerr(crt_tk, "missing identifier")
    array_decl()                               # Optional: [5]
    while consume(TokenCode.COMMA):            # More variables: , v[5], s
        if not consume(TokenCode.ID):
            tkerr(crt_tk, "missing identifier after ,")
        array_decl()
    if not consume(TokenCode.SEMICOLON):       # No semicolon?
        crt_tk = start_tk                      # → could be fnDef, backtrack
        return False
    return True
```

**Why backtrack on missing `;`?** Because `int sum(` starts exactly like a variable def (`int sum`) but is actually a function definition. If we don't find `;`, we restore and let `fn_def()` try.

### `type_base()` — Lines 95–107

```
Grammar: typeBase: INT | DOUBLE | CHAR | STRUCT ID
```

This is a pure **alternative** — try each option, return True on first match:

```python
def type_base() -> bool:
    if consume(TokenCode.INT):    return True
    if consume(TokenCode.DOUBLE): return True
    if consume(TokenCode.CHAR):   return True
    if consume(TokenCode.STRUCT):
        if not consume(TokenCode.ID):
            tkerr(crt_tk, "missing identifier after struct")
        return True
    return False
```

### `array_decl()` — Lines 112–119

```
Grammar: arrayDecl: LBRACKET expr? RBRACKET
Example: [5]  or  [20/4+5]  or  []
```

### `fn_def()` — Lines 126–148

```
Grammar: fnDef: ( typeBase | VOID ) ID LPAR ( fnParam ( COMMA fnParam )* )? RPAR stmCompound
Example: int sum() { ... }
```

```python
def fn_def() -> bool:
    start_tk = crt_tk
    if not type_base():                   # Try typeBase first (int, char, etc.)
        if not consume(TokenCode.VOID):   # Then try void
            return False
    if not consume(TokenCode.ID):         # Must have a name
        crt_tk = start_tk; return False   # Backtrack
    if not consume(TokenCode.LPAR):       # Must have (
        crt_tk = start_tk; return False   # "int x" without ( → not a fnDef
    # ... parse parameters ...
    if not stm_compound():                # Must have { ... } body
        tkerr(crt_tk, "missing function body")
    return True
```

**Three backtrack points:** After consuming `typeBase`, `ID`, and `LPAR`, each failure means this isn't a function definition.

---

## 6. Statement Rules

### `stm()` — Lines 171–243

A statement is one of 7 alternatives. The parser tries each one in order:

```python
def stm() -> bool:
    # 1. Compound statement: { ... }
    if stm_compound(): return True

    # 2. If: if (expr) stm else stm
    if consume(TokenCode.IF):
        # Once we consumed IF, we're committed — errors from here
        if not consume(TokenCode.LPAR): tkerr(...)    # Must have (
        if not expr(): tkerr(...)                      # Must have condition
        if not consume(TokenCode.RPAR): tkerr(...)     # Must have )
        if not stm(): tkerr(...)                       # Must have body
        if consume(TokenCode.ELSE):                    # Optional else
            if not stm(): tkerr(...)
        return True

    # 3. While: while (expr) stm
    if consume(TokenCode.WHILE): ...

    # 4. For: for (expr?; expr?; expr?) stm
    if consume(TokenCode.FOR): ...

    # 5. Break: break;
    if consume(TokenCode.BREAK): ...

    # 6. Return: return expr?;
    if consume(TokenCode.RETURN): ...

    # 7. Expression statement: expr; or just ;
    if expr():
        if not consume(TokenCode.SEMICOLON): tkerr(...)
        return True
    if consume(TokenCode.SEMICOLON):         # Empty statement: just ";"
        return True

    return False  # Nothing matched
```

**Error generation rule (from CT-L4):**
- If the **first token** of an alternative doesn't match → just return `False` (try next alternative)
- If the first token **does** match but the rest is wrong → generate an **error** (we're committed)

For example: if we see `WHILE` we're committed to parsing a while-statement. After that, `(` **must** follow — its absence is an error.

### `stm_compound()` — Lines 248–261

```
Grammar: stmCompound: LACC ( varDef | stm )* RACC
Example: { int x; x = 5; return x; }
```

```python
def stm_compound() -> bool:
    if not consume(TokenCode.LACC): return False  # Must start with {
    while True:                                    # Loop: varDef or stm
        if var_def(): pass
        elif stm(): pass
        else: break
    if not consume(TokenCode.RACC):                # Must end with }
        tkerr(crt_tk, "missing }")
    return True
```

---

## 7. Expression Rules

Expressions follow a **precedence hierarchy**. Each level calls the next-higher-precedence level:

```
expr           (top level)
  └→ exprAssign    =        (lowest precedence — right-to-left)
      └→ exprOr        ||
          └→ exprAnd       &&
              └→ exprEq        ==  !=
                  └→ exprRel       <  <=  >  >=
                      └→ exprAdd       +  -
                          └→ exprMul       *  /
                              └→ exprCast      (type)
                                  └→ exprUnary     -x  !x
                                      └→ exprPostfix  x[i]  x.y
                                          └→ exprPrimary   x  42  "hi"  (expr)
                                                              (highest precedence)
```

This hierarchy ensures that `2 + 3 * 4` is parsed as `2 + (3 * 4)` because `*` (exprMul) binds tighter than `+` (exprAdd).

### `expr_primary()` — Lines 469–494

The **atoms** — the simplest expressions:

```python
def expr_primary() -> bool:
    # Variable or function call: x  or  sum(a, b)
    if consume(TokenCode.ID):
        if consume(TokenCode.LPAR):        # Function call?
            if expr():                      # First argument
                while consume(TokenCode.COMMA):
                    if not expr(): tkerr(...)  # More arguments
            if not consume(TokenCode.RPAR): tkerr(...)
        return True

    # Literals
    if consume(TokenCode.CT_INT):    return True   # 42
    if consume(TokenCode.CT_REAL):   return True   # 3.14
    if consume(TokenCode.CT_CHAR):   return True   # 'a'
    if consume(TokenCode.CT_STRING): return True   # "hello"

    # Parenthesized expression: (expr)
    if consume(TokenCode.LPAR):
        if not expr(): tkerr(...)
        if not consume(TokenCode.RPAR): tkerr(...)
        return True

    return False
```

### `expr_unary()` — Lines 428–434

Unary operators (`-x`, `!flag`):

```python
def expr_unary() -> bool:
    if consume(TokenCode.SUB) or consume(TokenCode.NOT):
        if not expr_unary(): tkerr(...)    # Recursive: handles --x, !!x
        return True
    return expr_postfix()                   # No unary op → try postfix
```

### `expr_postfix()` / `expr_postfix1()` — Lines 445–463

Array indexing (`v[i]`) and member access (`pt.x`):

```python
# exprPostfix: exprPrimary exprPostfix1
def expr_postfix() -> bool:
    if not expr_primary(): return False
    return expr_postfix1()

# exprPostfix1: [expr] exprPostfix1 | .ID exprPostfix1 | ε
def expr_postfix1() -> bool:
    if consume(TokenCode.LBRACKET):        # v[i]
        if not expr(): tkerr(...)
        if not consume(TokenCode.RBRACKET): tkerr(...)
        return expr_postfix1()              # Chain: v[i][j]
    if consume(TokenCode.DOT):             # pt.x
        if not consume(TokenCode.ID): tkerr(...)
        return expr_postfix1()              # Chain: pt.x.y
    return True                             # ε — no more postfix ops
```

### Binary operator rules (exprAdd, exprMul, etc.)

All binary operator rules follow the **same pattern** after left-recursion elimination. Here's `exprAdd` as the example:

```python
# exprAdd: exprMul exprAdd1
def expr_add() -> bool:
    if not expr_mul(): return False    # Parse left operand (higher precedence)
    return expr_add1()                  # Parse optional + or - chain

# exprAdd1: (ADD | SUB) exprMul exprAdd1 | ε
def expr_add1() -> bool:
    if consume(TokenCode.ADD) or consume(TokenCode.SUB):
        if not expr_mul(): tkerr(...)  # Must have right operand
        return expr_add1()              # Recursion handles: a + b + c
    return True                         # ε — no more + or -
```

**How `2 + 3 + 4` is parsed:**

```
expr_add()
  → expr_mul() matches "2" ✓
  → expr_add1()
      → consume(ADD) ✓ (the first +)
      → expr_mul() matches "3" ✓
      → expr_add1()
          → consume(ADD) ✓ (the second +)
          → expr_mul() matches "4" ✓
          → expr_add1()
              → consume(ADD) ✗ (no more +)
              → return True (ε)
```

---

## 8. Left-Recursion Elimination

### The Problem

The grammar has rules like:

```
exprOr: exprOr OR exprAnd | exprAnd
```

If we implemented this directly:

```python
def expr_or():
    if expr_or():    # ← CALLS ITSELF FIRST!
        ...          # This is infinite recursion — never terminates
```

### The Solution

We apply the transformation from CT-L4:

```
A  → A α | β          becomes:
A  → β A'
A' → α A' | ε
```

For `exprOr`:

```
Original:    exprOr  → exprOr OR exprAnd | exprAnd
                        ~~~~~~                        (A → A α)
                                            ~~~~~~~~  (A → β)

Transformed: exprOr  → exprAnd exprOr1               (A → β A')
             exprOr1 → OR exprAnd exprOr1 | ε         (A'→ α A' | ε)
```

In code:
```python
def expr_or():
    if not expr_and(): return False   # β — parse the base case first
    return expr_or1()                  # A' — then the recursive tail

def expr_or1():
    if consume(TokenCode.OR):          # α — found OR operator
        if not expr_and(): tkerr(...)  #     parse right operand
        return expr_or1()              #     recurse for more ORs
    return True                        # ε — no more ORs, that's OK
```

**All 7 left-recursive rules use this same pattern:**

| Rule | Base (β) | Operator (α) |
|---|---|---|
| `exprOr` | `exprAnd` | `OR` |
| `exprAnd` | `exprEq` | `AND` |
| `exprEq` | `exprRel` | `EQUAL \| NOTEQ` |
| `exprRel` | `exprAdd` | `LESS \| LESSEQ \| GREATER \| GREATEREQ` |
| `exprAdd` | `exprMul` | `ADD \| SUB` |
| `exprMul` | `exprCast` | `MUL \| DIV` |
| `exprPostfix` | `exprPrimary` | `[expr] \| .ID` |

---

## 9. Backtracking

**Backtracking** means: "I tried something, it didn't work, let me undo and try something else."

We save the current position with `start_tk = crt_tk` and restore it with `crt_tk = start_tk`.

### Case 1: `expr_assign()` (Lines 279–290)

```
exprAssign: exprUnary ASSIGN exprAssign | exprOr
```

Both alternatives can start with the same tokens. For `x = 5`, the `x` could be:
- `exprUnary` (for assignment: `x = 5`)
- The beginning of `exprOr` (for just reading `x`)

```python
def expr_assign():
    start_tk = crt_tk
    if expr_unary():               # Try parsing exprUnary
        if consume(TokenCode.ASSIGN):   # Found '='?
            if not expr_assign(): tkerr(...)
            return True            # ✓ It was an assignment!
        crt_tk = start_tk          # No '=' → undo everything
    return expr_or()               # Try the other alternative
```

### Case 2: `expr_cast()` (Lines 412–423)

```
exprCast: LPAR typeBase arrayDecl? RPAR exprCast | exprUnary
```

A `(` could start a cast `(int)x` or a parenthesized expression `(x+1)`.

```python
def expr_cast():
    start_tk = crt_tk
    if consume(TokenCode.LPAR):
        if type_base():            # Is it a type name after (?
            array_decl()
            if consume(TokenCode.RPAR):
                if expr_cast():
                    return True    # ✓ It was a cast!
        crt_tk = start_tk          # Not a cast → undo
    return expr_unary()            # Try the other alternative
```

### Case 3: `struct_def()` and `var_def()`

Both restore `crt_tk` when they realize the tokens don't fully match their pattern, allowing the caller (`unit()`) to try the next alternative.

---

## 10. Entry Point

### `parse()` — Lines 501–507

```python
def parse(source: str):
    global crt_tk
    tokenize(source)               # Step 1: Run the lexer → build token list
    from lexer import tokens as tk_head
    crt_tk = tk_head               # Step 2: Point to the first token
    unit()                         # Step 3: Start parsing from the top rule
```

### `__main__` — Lines 511–521

```bash
python parser.py tests/0.c
# Output: tests/0.c: syntactic analysis passed
```

---

## 11. Complete Trace Example

Let's trace how the parser handles this tiny program:

```c
int x;
```

**Token list from lexer:** `INT → ID("x") → SEMICOLON → END`

```
parse("int x;")
  tokenize() → builds token list
  crt_tk = INT
  unit()
    while loop:
      struct_def()
        consume(STRUCT)? NO (crt_tk=INT) → return False
      fn_def()
        type_base()
          consume(INT)? YES → crt_tk moves to ID("x")
          return True
        consume(ID)? YES → crt_tk moves to SEMICOLON
        consume(LPAR)? NO (crt_tk=SEMICOLON)
          → crt_tk = start_tk (back to INT)   ← BACKTRACK!
          → return False
      var_def()
        type_base()
          consume(INT)? YES → crt_tk moves to ID("x")
          return True
        consume(ID)? YES → crt_tk moves to SEMICOLON
        array_decl()
          consume(LBRACKET)? NO → return False  (no array)
        consume(SEMICOLON)? YES → crt_tk moves to END
        return True                              ← MATCHED!
    while loop next iteration:
      struct_def() → False
      fn_def() → False
      var_def() → type_base() → False (END is not a type)
      → break
    consume(END)? YES → return True              ← DONE!
```

**The program is syntactically correct! ✓**

---

## Summary of Key Concepts

| Concept | What it means |
|---|---|
| **Predicate** | A function that returns `True` if its grammar rule matches |
| **consume(X)** | "Is the current token X? If yes, eat it and move forward" |
| **Backtracking** | Save position → try something → if it fails, restore position |
| **Left-recursion elimination** | Transform `A → Aα \| β` into `A → β A'` / `A' → αA' \| ε` |
| **ε (epsilon)** | "Nothing" — a rule that always succeeds without consuming tokens |
| **tkerr()** | Fatal error — prints message with line number and exits |
| **Return False** | "This rule didn't match, but that's OK — try something else" |
| **Error vs False** | Error = impossible state; False = just didn't match this alternative |
