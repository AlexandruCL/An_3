import importlib.util
import unittest
from pathlib import Path


def load_lexer_module():
    lexer_path = Path(__file__).with_name("lexer.py")
    spec = importlib.util.spec_from_file_location("student_lexer", lexer_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load lexer module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


lexer = load_lexer_module()


def lex(source: str):
    lexer.tokenize(source)
    items = []
    tk = lexer.tokens
    while tk is not None:
        items.append(
            {
                "name": lexer.TokenCode(tk.code).name,
                "line": tk.line,
                "text": tk.text,
                "i": tk.i,
                "r": tk.r,
            }
        )
        tk = tk.next
    return items


def names(source: str):
    return [x["name"] for x in lex(source)]


class LexerTests(unittest.TestCase):
    def test_keywords_vs_id(self):
        source = "break char double else for if int return struct void while whilex"
        got = names(source)
        expected = [
            "BREAK",
            "CHAR",
            "DOUBLE",
            "ELSE",
            "FOR",
            "IF",
            "INT",
            "RETURN",
            "STRUCT",
            "VOID",
            "WHILE",
            "ID",
            "END",
        ]
        self.assertEqual(got, expected)

    def test_delimiters_and_single_char_operators(self):
        source = ", ; ( ) [ ] { } + - * / ."
        got = names(source)
        expected = [
            "COMMA",
            "SEMICOLON",
            "LPAR",
            "RPAR",
            "LBRACKET",
            "RBRACKET",
            "LACC",
            "RACC",
            "ADD",
            "SUB",
            "MUL",
            "DIV",
            "DOT",
            "END",
        ]
        self.assertEqual(got, expected)

    def test_compound_and_relational_operators(self):
        source = "&& || ! != < <= > >= = =="
        got = names(source)
        expected = [
            "AND",
            "OR",
            "NOT",
            "NOTEQ",
            "LESS",
            "LESSEQ",
            "GREATER",
            "GREATEREQ",
            "ASSIGN",
            "EQUAL",
            "END",
        ]
        self.assertEqual(got, expected)

    def test_integer_literal_paths(self):
        source = "0 7 08 077 0x1f 123"
        tokens = lex(source)
        ints = [t["i"] for t in tokens if t["name"] == "CT_INT"]
        self.assertEqual(ints, [0, 7, 8, 63, 31, 123])
        self.assertEqual(tokens[-1]["name"], "END")

    def test_real_literal_paths(self):
        source = "3.14 2e3 2E+3 2E-2 0.5 0e2"
        tokens = [t for t in lex(source) if t["name"] == "CT_REAL"]
        got = [t["r"] for t in tokens]
        expected = [3.14, 2000.0, 2000.0, 0.02, 0.5, 0.0]
        self.assertEqual(got, expected)

    def test_char_and_string_literals(self):
        source = "'a' \"hello\""
        tokens = lex(source)
        self.assertEqual(tokens[0]["name"], "CT_CHAR")
        self.assertEqual(tokens[0]["i"], ord("a"))
        self.assertEqual(tokens[1]["name"], "CT_STRING")
        self.assertEqual(tokens[1]["text"], "hello")
        self.assertEqual(tokens[2]["name"], "END")

    def test_line_comment_is_consumed(self):
        source = "int x; // comment here\nreturn x;"
        tokens = lex(source)
        got = [t["name"] for t in tokens]
        self.assertEqual(got, ["INT", "ID", "SEMICOLON", "RETURN", "ID", "SEMICOLON", "END"])
        self.assertEqual(tokens[3]["line"], 2)

    def test_invalid_character_raises(self):
        with self.assertRaises(SystemExit):
            lex("@")

    def test_invalid_hex_raises(self):
        with self.assertRaises(SystemExit):
            lex("0x")

    def test_unterminated_string_raises(self):
        with self.assertRaises(SystemExit):
            lex("\"abc")

    def test_unterminated_char_raises(self):
        with self.assertRaises(SystemExit):
            lex("'a")

    def test_all_emitted_tokens_are_reachable(self):
        source = (
            "break char double else for if int return struct void while id "
            ", ; ( ) [ ] { } "
            "+ - * / . && || ! != < <= > >= = == "
            "0 123 077 0x1f 3.14 0e2 'a' \"s\""
        )
        got_names = set(names(source))
        expected = {code.name for code in lexer.TokenCode if code.name != "LINECOMMENT"}
        missing = expected - got_names
        self.assertFalse(missing, f"Missing token kinds in test source: {sorted(missing)}")


if __name__ == "__main__":
    unittest.main()
