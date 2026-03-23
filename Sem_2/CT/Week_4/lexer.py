
import sys
from enum import IntEnum
from typing import Optional


# ── Token codes ──────────────────────────────────────────────────────────────
class TokenCode(IntEnum):
    # codes aligned with FSM final-state ids from the diagram
    ID         = 2
    END        = 31
    CT_INT     = 4
    CT_REAL    = 14
    CT_CHAR    = 19
    CT_STRING  = 21
    # delimiters
    COMMA      = 22
    SEMICOLON  = 23
    LPAR       = 24
    RPAR       = 25
    LBRACKET   = 26
    RBRACKET   = 27
    LACC       = 28
    RACC       = 29
    # operators
    ADD        = 33
    SUB        = 34
    MUL        = 35
    DIV        = 54
    DOT        = 36
    AND        = 38
    OR         = 40
    NOT        = 42
    NOTEQ      = 43
    LESS       = 48
    LESSEQ     = 49
    GREATER    = 51
    GREATEREQ  = 52
    ASSIGN     = 45
    EQUAL      = 46
    # keywords
    BREAK      = 57
    CHAR       = 58
    DOUBLE     = 59
    ELSE       = 60
    FOR        = 61
    IF         = 62
    INT        = 63
    RETURN     = 64
    STRUCT     = 65
    VOID       = 66
    WHILE      = 67
    # line comment (consumed, not emitted as token)
    LINECOMMENT = 56


# ── Token class ──────────────────────────────────────────────────────────────
class Token:
    def __init__(self, code: int, line: int):
        self.code = code
        self.line = line
        self.next: Optional["Token"] = None  # link to the next token
        # union-like fields
        self.text: Optional[str]   = None   # used for ID, CT_STRING
        self.i:    Optional[int]   = None   # used for CT_INT, CT_CHAR
        self.r:    Optional[float] = None   # used for CT_REAL


# ── Global state ─────────────────────────────────────────────────────────────
tokens: Optional[Token]     = None   # head of the token list
last_token: Optional[Token] = None   # tail of the token list
p_crt_ch: int   = 0      # current position index in input buffer
line: int       = 1      # current line number
input_buf: str  = ""     # the entire input source as a string


# ── Error helpers ────────────────────────────────────────────────────────────
def err(msg: str):
    """Print an error message and exit."""
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(-1)


def tkerr(tk: Token, msg: str):
    """Print an error tied to a specific token (includes line number) and exit."""
    print(f"error in line {tk.line}: {msg}", file=sys.stderr)
    sys.exit(-1)


# ── Token list management ───────────────────────────────────────────────────
def add_tk(code: int) -> Token:
    """Create a new token, append it to the token list, and return it."""
    global tokens, last_token
    tk = Token(code, line)
    if last_token:
        last_token.next = tk
    else:
        tokens = tk
    last_token = tk
    return tk


# ── Helper: create a substring ──────────────────────────────────────────────
def create_string(start: int, end: int) -> str:
    """Return the slice input_buf[start:end]."""
    return input_buf[start:end]


# ── Lexer (FSM) ─────────────────────────────────────────────────────────────
def get_next_token() -> int:
    """
    Finite-state-machine lexer.
    Reads characters from `input_buf` starting at `p_crt_ch` and returns the
    code of the next recognised token.
    """
    global p_crt_ch, line

    state = 0
    p_start_ch = 0

    while True:
        if p_crt_ch < len(input_buf):
            ch = input_buf[p_crt_ch]
        else:
            ch = '\0'

        # ═══════════════════════════════════════════════════════════════
        #  STATE 0 — initial state
        # ═══════════════════════════════════════════════════════════════
        if state == 0:
            if ch.isalpha() or ch == '_':
                p_start_ch = p_crt_ch       # memorise the beginning of the ID
                p_crt_ch += 1               # consume the character
                state = 1
            elif ch == '0':
                p_start_ch = p_crt_ch
                p_crt_ch += 1
                state = 5
            elif ch.isdigit():              # 1-9
                p_start_ch = p_crt_ch
                p_crt_ch += 1
                state = 3
            elif ch == '\'':
                p_crt_ch += 1
                state = 17
            elif ch == '"':
                p_start_ch = p_crt_ch + 1   # after the opening quote
                p_crt_ch += 1
                state = 20
            elif ch == ',':
                p_crt_ch += 1
                state = 22
            elif ch == ';':
                p_crt_ch += 1
                state = 23
            elif ch == '(':
                p_crt_ch += 1
                state = 24
            elif ch == ')':
                p_crt_ch += 1
                state = 25
            elif ch == '[':
                p_crt_ch += 1
                state = 26
            elif ch == ']':
                p_crt_ch += 1
                state = 27
            elif ch == '{':
                p_crt_ch += 1
                state = 28
            elif ch == '}':
                p_crt_ch += 1
                state = 29
            elif ch == '+':
                p_crt_ch += 1
                state = 33
            elif ch == '-':
                p_crt_ch += 1
                state = 34
            elif ch == '*':
                p_crt_ch += 1
                state = 35
            elif ch == '.':
                p_crt_ch += 1
                state = 36
            elif ch == '&':
                p_crt_ch += 1
                state = 37
            elif ch == '|':
                p_crt_ch += 1
                state = 39
            elif ch == '!':
                p_crt_ch += 1
                state = 41
            elif ch == '<':
                p_crt_ch += 1
                state = 47
            elif ch == '=':
                p_crt_ch += 1
                state = 44
            elif ch == '>':
                p_crt_ch += 1
                state = 50
            elif ch == '/':
                p_crt_ch += 1
                state = 53
            elif ch in (' ', '\r', '\t', '\n'):
                state = 32                 # SPACE state
            elif ch == '\0':                # end of input
                state = 30                 # END pre-final state
            else:
                tkerr(add_tk(TokenCode.END), f"invalid character: {ch!r}")

        # ═══════════════════════════════════════════════════════════════
        #  STATES 1–2 — identifier / keyword
        # ═══════════════════════════════════════════════════════════════
        elif state == 1:
            if ch.isalnum() or ch == '_':
                p_crt_ch += 1
            else:
                state = 2

        elif state == 2:
            word = input_buf[p_start_ch:p_crt_ch]
            # keyword tests
            if   word == "break":   tk = add_tk(TokenCode.BREAK)
            elif word == "char":    tk = add_tk(TokenCode.CHAR)
            elif word == "double":  tk = add_tk(TokenCode.DOUBLE)
            elif word == "else":    tk = add_tk(TokenCode.ELSE)
            elif word == "for":     tk = add_tk(TokenCode.FOR)
            elif word == "if":      tk = add_tk(TokenCode.IF)
            elif word == "int":     tk = add_tk(TokenCode.INT)
            elif word == "return":  tk = add_tk(TokenCode.RETURN)
            elif word == "struct":  tk = add_tk(TokenCode.STRUCT)
            elif word == "void":    tk = add_tk(TokenCode.VOID)
            elif word == "while":   tk = add_tk(TokenCode.WHILE)
            else:
                tk = add_tk(TokenCode.ID)
                tk.text = create_string(p_start_ch, p_crt_ch)
            return tk.code

        # ═══════════════════════════════════════════════════════════════
        #  STATES 3–7 — integer paths (decimal/octal/hex) ending in state 4
        # ═══════════════════════════════════════════════════════════════
        elif state == 3:                    # decimal integer body (started with 1-9)
            if ch.isdigit():
                p_crt_ch += 1
            elif ch == '.':
                p_crt_ch += 1
                state = 8
            elif ch in ('e', 'E'):
                p_crt_ch += 1
                state = 9
            else:
                state = 4

        elif state == 4:                    # CT_INT final (shared final state in diagram)
            lexeme = input_buf[p_start_ch:p_crt_ch]
            tk = add_tk(TokenCode.CT_INT)
            if lexeme.startswith(('0x', '0X')):
                tk.i = int(lexeme, 16)
            elif len(lexeme) > 1 and lexeme.startswith('0') and all('0' <= c <= '7' for c in lexeme):
                tk.i = int(lexeme, 8)
            else:
                tk.i = int(lexeme, 10)
            return tk.code

        elif state == 5:                    # started with 0
            if '0' <= ch <= '7':
                p_crt_ch += 1               # 5 -> 5 (octal loop)
            elif ch in ('8', '9'):
                p_crt_ch += 1
                state = 3                   # 5 -> 3
            elif ch in ('x', 'X'):
                p_crt_ch += 1
                state = 6                   # 5 -> 6 (hex prefix)
            elif ch == '.':
                p_crt_ch += 1
                state = 8                   # 5 -> 8 (real with fractional part)
            elif ch in ('e', 'E'):
                p_crt_ch += 1
                state = 9                   # 5 -> 9 (real with exponent)
            else:
                state = 4                   # 5 -> 4

        elif state == 6:                    # after 0x/0X, require first hex digit
            if ch in '0123456789abcdefABCDEF':
                p_crt_ch += 1
                state = 7
            else:
                tkerr(add_tk(TokenCode.END), "invalid hex literal")

        elif state == 7:                    # hex digits loop
            if ch in '0123456789abcdefABCDEF':
                p_crt_ch += 1
            else:
                state = 4                   # 6 -> 7 -> 4

        # ═══════════════════════════════════════════════════════════════
        #  STATES 8–16 — real number (CT_REAL in state 14)
        # ═══════════════════════════════════════════════════════════════
        elif state == 8:                    # after decimal point
            if ch.isdigit():
                p_crt_ch += 1
                state = 10
            else:
                tkerr(add_tk(TokenCode.END), "expected digit after '.'")

        elif state == 9:                    # exponent path entered directly from int states
            if ch in ('+', '-'):
                p_crt_ch += 1
                state = 15
            elif ch.isdigit():
                p_crt_ch += 1
                state = 16
            else:
                tkerr(add_tk(TokenCode.END), "expected digit or sign after exponent")

        elif state == 10:                   # fractional digits
            if ch.isdigit():
                p_crt_ch += 1
            elif ch in ('e', 'E'):
                p_crt_ch += 1
                state = 11
            else:
                state = 14

        elif state == 11:                   # exponent after fractional part
            if ch in ('+', '-'):
                p_crt_ch += 1
                state = 12
            elif ch.isdigit():
                p_crt_ch += 1
                state = 13
            else:
                tkerr(add_tk(TokenCode.END), "expected digit or sign after exponent")

        elif state == 12:                   # exponent sign after fractional part
            if ch.isdigit():
                p_crt_ch += 1
                state = 13
            else:
                tkerr(add_tk(TokenCode.END), "expected digit after exponent sign")

        elif state == 13:                   # exponent digits after fractional part
            if ch.isdigit():
                p_crt_ch += 1
            else:
                state = 14

        elif state == 14:                   # CT_REAL final
            tk = add_tk(TokenCode.CT_REAL)
            tk.r = float(input_buf[p_start_ch:p_crt_ch])
            return tk.code

        elif state == 15:                   # exponent sign (direct exponent path)
            if ch.isdigit():
                p_crt_ch += 1
                state = 16
            else:
                tkerr(add_tk(TokenCode.END), "expected digit after exponent sign")

        elif state == 16:                   # exponent digits (direct exponent path)
            if ch.isdigit():
                p_crt_ch += 1
            else:
                state = 14

        # ═══════════════════════════════════════════════════════════════
        #  STATES 17–19 — character literal (CT_CHAR)
        # ═══════════════════════════════════════════════════════════════
        elif state == 17:                   # after opening '
            if ch == '\\':                  # escape sequence
                p_crt_ch += 1
                state = 18
            elif ch != '\'' and ch != '\0':
                p_start_ch = p_crt_ch
                p_crt_ch += 1
                state = 18
            else:
                tkerr(add_tk(TokenCode.END), "invalid char literal")

        elif state == 18:                   # read char content, expect closing '
            if ch == '\'':
                tk = add_tk(TokenCode.CT_CHAR)
                tk.i = ord(input_buf[p_start_ch])
                p_crt_ch += 1
                state = 19
            elif ch == '\0':
                tkerr(add_tk(TokenCode.END), "unterminated char literal")
            else:
                # after escape: consume the escaped char
                p_start_ch = p_crt_ch
                p_crt_ch += 1
                # stay in 18, next iteration should find the closing quote

        elif state == 19:                   # CT_CHAR final
            return tk.code

        # ═══════════════════════════════════════════════════════════════
        #  STATES 20–21 — string literal (CT_STRING)
        # ═══════════════════════════════════════════════════════════════
        elif state == 20:                   # reading string content
            if ch == '"':
                tk = add_tk(TokenCode.CT_STRING)
                tk.text = create_string(p_start_ch, p_crt_ch)
                p_crt_ch += 1
                state = 21
            elif ch == '\0':
                tkerr(add_tk(TokenCode.END), "unterminated string literal")
            else:
                p_crt_ch += 1               # consume any char inside string

        elif state == 21:                   # CT_STRING final
            return tk.code

        # ═══════════════════════════════════════════════════════════════
        #  STATES 22–29 — delimiters (single-character tokens)
        # ═══════════════════════════════════════════════════════════════
        elif state == 22:
            add_tk(TokenCode.COMMA);      return TokenCode.COMMA
        elif state == 23:
            add_tk(TokenCode.SEMICOLON);  return TokenCode.SEMICOLON
        elif state == 24:
            add_tk(TokenCode.LPAR);       return TokenCode.LPAR
        elif state == 25:
            add_tk(TokenCode.RPAR);       return TokenCode.RPAR
        elif state == 26:
            add_tk(TokenCode.LBRACKET);   return TokenCode.LBRACKET
        elif state == 27:
            add_tk(TokenCode.RBRACKET);   return TokenCode.RBRACKET
        elif state == 28:
            add_tk(TokenCode.LACC);       return TokenCode.LACC
        elif state == 29:
            add_tk(TokenCode.RACC);       return TokenCode.RACC

        # ═══════════════════════════════════════════════════════════════
        #  STATES 30–32 — END / SPACE
        # ═══════════════════════════════════════════════════════════════
        elif state == 30:
            state = 31

        elif state == 31:
            add_tk(TokenCode.END)
            return TokenCode.END

        elif state == 32:
            if ch == '\n':
                line += 1
                p_crt_ch += 1
            elif ch in (' ', '\r', '\t'):
                p_crt_ch += 1
            else:
                tkerr(add_tk(TokenCode.END), f"invalid space character: {ch!r}")
            state = 0

        # ═══════════════════════════════════════════════════════════════
        #  STATES 33–36 — single-character operators
        # ═══════════════════════════════════════════════════════════════
        elif state == 33:
            add_tk(TokenCode.ADD);  return TokenCode.ADD
        elif state == 34:
            add_tk(TokenCode.SUB);  return TokenCode.SUB
        elif state == 35:
            add_tk(TokenCode.MUL);  return TokenCode.MUL
        elif state == 36:
            add_tk(TokenCode.DOT);  return TokenCode.DOT

        # ═══════════════════════════════════════════════════════════════
        #  STATES 37–38 — && (AND)
        # ═══════════════════════════════════════════════════════════════
        elif state == 37:
            if ch == '&':
                p_crt_ch += 1
                state = 38
            else:
                tkerr(add_tk(TokenCode.END), "expected '&&'")

        elif state == 38:
            add_tk(TokenCode.AND);  return TokenCode.AND

        # ═══════════════════════════════════════════════════════════════
        #  STATES 39–40 — || (OR)
        # ═══════════════════════════════════════════════════════════════
        elif state == 39:
            if ch == '|':
                p_crt_ch += 1
                state = 40
            else:
                tkerr(add_tk(TokenCode.END), "expected '||'")

        elif state == 40:
            add_tk(TokenCode.OR);  return TokenCode.OR

        # ═══════════════════════════════════════════════════════════════
        #  STATES 41–43 — ! / != (NOT / NOTEQ)
        # ═══════════════════════════════════════════════════════════════
        elif state == 41:
            if ch == '=':
                p_crt_ch += 1
                state = 43
            else:
                state = 42

        elif state == 42:
            add_tk(TokenCode.NOT);    return TokenCode.NOT

        elif state == 43:
            add_tk(TokenCode.NOTEQ);  return TokenCode.NOTEQ

        # ═══════════════════════════════════════════════════════════════
        #  STATES 44–46 — = / == (ASSIGN / EQUAL)
        # ═══════════════════════════════════════════════════════════════
        elif state == 44:
            if ch == '=':
                p_crt_ch += 1
                state = 46
            else:
                state = 45

        elif state == 45:
            add_tk(TokenCode.ASSIGN);  return TokenCode.ASSIGN

        elif state == 46:
            add_tk(TokenCode.EQUAL);   return TokenCode.EQUAL

        # ═══════════════════════════════════════════════════════════════
        #  STATES 47–49 — < / <= (LESS / LESSEQ)
        # ═══════════════════════════════════════════════════════════════
        elif state == 47:
            if ch == '=':
                p_crt_ch += 1
                state = 49
            else:
                state = 48

        elif state == 48:
            add_tk(TokenCode.LESS);    return TokenCode.LESS

        elif state == 49:
            add_tk(TokenCode.LESSEQ);  return TokenCode.LESSEQ

        # ═══════════════════════════════════════════════════════════════
        #  STATES 50–52 — > / >= (GREATER / GREATEREQ)
        # ═══════════════════════════════════════════════════════════════
        elif state == 50:
            if ch == '=':
                p_crt_ch += 1
                state = 52
            else:
                state = 51

        elif state == 51:
            add_tk(TokenCode.GREATER);    return TokenCode.GREATER

        elif state == 52:
            add_tk(TokenCode.GREATEREQ);  return TokenCode.GREATEREQ

        # ═══════════════════════════════════════════════════════════════
        #  STATES 53–56 — / and // (DIV / LINECOMMENT)
        # ═══════════════════════════════════════════════════════════════
        elif state == 53:
            if ch == '/':
                p_crt_ch += 1
                state = 55                  # line comment
            else:
                state = 54

        elif state == 54:
            add_tk(TokenCode.DIV);  return TokenCode.DIV

        elif state == 55:                   # consuming line comment
            if ch == '\n' or ch == '\r' or ch == '\0':
                state = 56
            else:
                p_crt_ch += 1               # consume comment characters

        elif state == 56:                   # end of line comment
            if ch == '\n':
                line += 1
                p_crt_ch += 1
            elif ch == '\r':
                p_crt_ch += 1
            # go back to state 0 (no token emitted for comments)
            state = 0

        else:
            err(f"unexpected state {state}")
            return -1

    return -1  # unreachable; keeps the type checker happy


# ── Tokenise the whole input ─────────────────────────────────────────────────
def tokenize(source: str):
    """Run the lexer over `source`, building the global token list."""
    global input_buf, p_crt_ch, line, tokens, last_token
    input_buf  = source
    p_crt_ch   = 0
    line       = 1
    tokens     = None
    last_token = None

    while True:
        code = get_next_token()
        if code == TokenCode.END:
            break


# ── Pretty-print helper ─────────────────────────────────────────────────────
def show_tokens():
    """Walk the token list and print each token."""
    tk = tokens
    while tk:
        name = TokenCode(tk.code).name
        extra = ""
        if tk.text is not None:
            extra = f' text="{tk.text}"'
        if tk.i is not None:
            extra = f" int={tk.i}"
        if tk.r is not None:
            extra = f" real={tk.r}"
        print(f"line {tk.line}: {name}{extra}")
        tk = tk.next


# ── Main (quick test) ───────────────────────────────────────────────────────
if __name__ == "__main__":
    test_input = (
        'int main() {\n'
        '  int x = 10;\n'
        '  double pi = 3.14e-2;\n'
        '  if (x >= 5 && x != 0) {\n'
        '    return x + 1;\n'
        '  }\n'
        '  // this is a comment\n'
        '  char c = \'a\';\n'
        '  void *p;\n'
        '}\n'
    )
    print(f"Input:\n{test_input}")
    tokenize(test_input)
    show_tokens()
