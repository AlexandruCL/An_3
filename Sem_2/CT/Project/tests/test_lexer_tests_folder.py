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
    out = []
    tk = lexer.tokens
    while tk is not None:
        out.append(
            {
                "name": lexer.TokenCode(tk.code).name,
                "line": tk.line,
                "text": tk.text,
                "i": tk.i,
                "r": tk.r,
            }
        )
        tk = tk.next
    return out


EXPECTED_TOKEN_NAMES = {
    "0.c": [
        "INT", "ID", "LPAR", "RPAR", "LACC",
        "INT", "ID", "COMMA", "ID", "LBRACKET", "CT_INT", "RBRACKET", "COMMA", "ID", "SEMICOLON",
        "ID", "ASSIGN", "CT_INT", "SEMICOLON",
        "FOR", "LPAR", "ID", "ASSIGN", "CT_INT", "SEMICOLON", "ID", "LESS", "CT_INT", "SEMICOLON", "ID", "ASSIGN", "ID", "ADD", "CT_INT", "RPAR", "LACC",
        "ID", "LBRACKET", "ID", "RBRACKET", "ASSIGN", "ID", "SEMICOLON",
        "ID", "ASSIGN", "ID", "ADD", "ID", "LBRACKET", "ID", "RBRACKET", "SEMICOLON",
        "RACC",
        "RETURN", "ID", "SEMICOLON",
        "RACC",
        "VOID", "ID", "LPAR", "RPAR", "LACC",
        "INT", "ID", "COMMA", "ID", "SEMICOLON",
        "FOR", "LPAR", "ID", "ASSIGN", "CT_INT", "SEMICOLON", "ID", "LESS", "CT_INT", "SEMICOLON", "ID", "ASSIGN", "ID", "ADD", "CT_INT", "RPAR",
        "ID", "ASSIGN", "ID", "LPAR", "RPAR", "SEMICOLON",
        "ID", "LPAR", "ID", "RPAR", "SEMICOLON",
        "RACC", "END",
    ],
    "1.c": [
        "VOID", "ID", "LPAR", "RPAR", "LACC",
        "ID", "LPAR", "CT_STRING", "RPAR", "SEMICOLON",
        "RACC", "END",
    ],
    "2.c": [
        "VOID", "ID", "LPAR", "RPAR", "LACC",
        "INT", "ID", "SEMICOLON",
        "ID", "LPAR", "CT_STRING", "RPAR", "SEMICOLON",
        "ID", "ASSIGN", "ID", "LPAR", "RPAR", "SEMICOLON",
        "ID", "LPAR", "ID", "RPAR", "SEMICOLON",
        "RACC", "END",
    ],
    "3.c": [
        "VOID", "ID", "LPAR", "RPAR", "LACC",
        "INT", "ID", "SEMICOLON",
        "ID", "LPAR", "CT_STRING", "RPAR", "SEMICOLON",
        "ID", "ASSIGN", "ID", "LPAR", "RPAR", "SEMICOLON",
        "IF", "LPAR", "ID", "LESS", "CT_INT", "RPAR", "ID", "LPAR", "CT_STRING", "RPAR", "SEMICOLON",
        "ELSE", "ID", "LPAR", "CT_STRING", "RPAR", "SEMICOLON",
        "RACC", "END",
    ],
    "4.c": [
        "INT", "ID", "LPAR", "CHAR", "ID", "RPAR", "LACC",
        "RETURN", "ID", "GREATEREQ", "CT_CHAR", "AND", "ID", "LESSEQ", "CT_CHAR", "SEMICOLON",
        "RACC",
        "VOID", "ID", "LPAR", "RPAR", "LACC",
        "CHAR", "ID", "SEMICOLON",
        "ID", "LPAR", "CT_STRING", "RPAR", "SEMICOLON",
        "ID", "ASSIGN", "ID", "LPAR", "RPAR", "SEMICOLON",
        "ID", "LPAR", "ID", "LPAR", "ID", "RPAR", "RPAR", "SEMICOLON",
        "RACC", "END",
    ],
    "5.c": [
        "VOID", "ID", "LPAR", "RPAR", "LACC",
        "INT", "ID", "COMMA", "ID", "SEMICOLON",
        "DOUBLE", "ID", "SEMICOLON",
        "ID", "ASSIGN", "CT_REAL", "SEMICOLON",
        "ID", "LPAR", "CT_STRING", "RPAR", "SEMICOLON",
        "ID", "ASSIGN", "ID", "LPAR", "RPAR", "SEMICOLON",
        "FOR", "LPAR", "ID", "ASSIGN", "CT_INT", "SEMICOLON", "ID", "LESS", "ID", "SEMICOLON", "ID", "ASSIGN", "ID", "ADD", "CT_INT", "RPAR", "LACC",
        "ID", "ASSIGN", "ID", "ADD", "ID", "LPAR", "RPAR", "SEMICOLON",
        "RACC",
        "ID", "LPAR", "CT_STRING", "RPAR", "SEMICOLON",
        "ID", "LPAR", "ID", "DIV", "ID", "RPAR", "SEMICOLON",
        "RACC", "END",
    ],
    "6.c": [
        "VOID", "ID", "LPAR", "RPAR", "LACC",
        "INT", "ID", "COMMA", "ID", "COMMA", "ID", "SEMICOLON",
        "INT", "ID", "LBRACKET", "CT_INT", "RBRACKET", "SEMICOLON",
        "ID", "LPAR", "CT_STRING", "RPAR", "SEMICOLON",
        "ID", "ASSIGN", "ID", "LPAR", "RPAR", "SEMICOLON",
        "FOR", "LPAR", "ID", "ASSIGN", "CT_INT", "SEMICOLON", "ID", "LESS", "ID", "SEMICOLON", "ID", "ASSIGN", "ID", "ADD", "CT_INT", "RPAR", "LACC",
        "ID", "LBRACKET", "ID", "RBRACKET", "ASSIGN", "ID", "LPAR", "RPAR", "SEMICOLON",
        "RACC",
        "FOR", "LPAR", "ID", "ASSIGN", "CT_INT", "SEMICOLON", "ID", "LESS", "ID", "DIV", "CT_INT", "SEMICOLON", "ID", "ASSIGN", "ID", "ADD", "CT_INT", "RPAR", "LACC",
        "ID", "ASSIGN", "ID", "LBRACKET", "ID", "RBRACKET", "SEMICOLON",
        "ID", "LBRACKET", "ID", "RBRACKET", "ASSIGN", "ID", "LBRACKET", "ID", "SUB", "ID", "SUB", "CT_INT", "RBRACKET", "SEMICOLON",
        "ID", "LBRACKET", "ID", "SUB", "ID", "SUB", "CT_INT", "RBRACKET", "ASSIGN", "ID", "SEMICOLON",
        "RACC",
        "FOR", "LPAR", "ID", "ASSIGN", "CT_INT", "SEMICOLON", "ID", "LESS", "ID", "SEMICOLON", "ID", "ASSIGN", "ID", "ADD", "CT_INT", "RPAR", "LACC",
        "ID", "LPAR", "CT_CHAR", "RPAR", "SEMICOLON",
        "ID", "LPAR", "ID", "LBRACKET", "ID", "RBRACKET", "RPAR", "SEMICOLON",
        "RACC",
        "RACC", "END",
    ],
    "7.c": [
        "VOID", "ID", "LPAR", "RPAR", "LACC",
        "DOUBLE", "ID", "COMMA", "ID", "SEMICOLON",
        "ID", "ASSIGN", "CT_REAL", "SEMICOLON",
        "ID", "LPAR", "CT_STRING", "RPAR", "SEMICOLON",
        "ID", "ASSIGN", "ID", "LPAR", "RPAR", "SEMICOLON",
        "ID", "LPAR", "CT_STRING", "RPAR", "SEMICOLON",
        "ID", "LPAR", "CT_REAL", "MUL", "ID", "MUL", "ID", "RPAR", "SEMICOLON",
        "ID", "LPAR", "CT_STRING", "RPAR", "SEMICOLON",
        "ID", "LPAR", "ID", "MUL", "ID", "MUL", "ID", "RPAR", "SEMICOLON",
        "RACC", "END",
    ],
    "8.c": [
        "VOID", "ID", "LPAR", "RPAR", "LACC",
        "IF", "LPAR", "CT_INT", "EQUAL", "CT_INT", "RPAR", "ID", "LPAR", "CT_STRING", "RPAR", "SEMICOLON",
        "ELSE", "ID", "LPAR", "CT_STRING", "RPAR", "SEMICOLON",
        "IF", "LPAR", "CT_REAL", "EQUAL", "CT_REAL", "AND", "CT_REAL", "EQUAL", "CT_INT", "RPAR", "ID", "LPAR", "CT_CHAR", "RPAR", "SEMICOLON",
        "ELSE", "ID", "LPAR", "CT_CHAR", "RPAR", "SEMICOLON",
        "RACC", "END",
    ],
    "9.c": [
        "STRUCT", "ID", "LACC",
        "INT", "ID", "COMMA", "ID", "SEMICOLON",
        "RACC", "SEMICOLON",
        "STRUCT", "ID", "ID", "LBRACKET", "CT_INT", "DIV", "CT_INT", "ADD", "CT_INT", "RBRACKET", "SEMICOLON",
        "INT", "ID", "LPAR", "RPAR", "LACC",
        "INT", "ID", "COMMA", "ID", "SEMICOLON",
        "FOR", "LPAR", "ID", "ASSIGN", "ID", "ASSIGN", "CT_INT", "SEMICOLON", "ID", "LESS", "CT_INT", "SEMICOLON", "ID", "ASSIGN", "ID", "ADD", "CT_INT", "RPAR", "LACC",
        "IF", "LPAR", "ID", "LBRACKET", "ID", "RBRACKET", "DOT", "ID", "GREATEREQ", "CT_INT", "AND", "ID", "LBRACKET", "ID", "RBRACKET", "DOT", "ID", "GREATEREQ", "CT_INT", "RPAR", "ID", "ASSIGN", "ID", "ADD", "CT_INT", "SEMICOLON",
        "RACC",
        "RETURN", "ID", "SEMICOLON",
        "RACC",
        "VOID", "ID", "LPAR", "RPAR", "LACC",
        "ID", "LPAR", "ID", "LPAR", "RPAR", "RPAR", "SEMICOLON",
        "RACC", "END",
    ],
}


class LexerTestsFolderTests(unittest.TestCase):
    def test_every_c_file_in_tests_folder(self):
        tests_dir = Path(__file__).with_name("tests")
        program_files = sorted(
            tests_dir.glob("*.c"),
            key=lambda p: (not p.stem.isdigit(), int(p.stem) if p.stem.isdigit() else p.stem),
        )

        self.assertTrue(program_files, "No .c files found in tests folder")

        discovered = {p.name for p in program_files}
        expected = set(EXPECTED_TOKEN_NAMES)
        self.assertEqual(discovered, expected, "Expected-token map does not match tests folder files")

        for program_file in program_files:
            with self.subTest(program=program_file.name):
                src = program_file.read_text(encoding="utf-8")
                tokens = lex(src)
                names = [token["name"] for token in tokens]
                self.assertEqual(
                    names,
                    EXPECTED_TOKEN_NAMES[program_file.name],
                    f"Token sequence mismatch for {program_file.name}",
                )


if __name__ == "__main__":
    unittest.main()
