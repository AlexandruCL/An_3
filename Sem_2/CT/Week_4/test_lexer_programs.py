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


class LexerProgramTests(unittest.TestCase):
    def test_all_program_files_in_tests_folder(self):
        tests_dir = Path(__file__).with_name("tests")
        program_files = sorted(
            tests_dir.glob("*.c"),
            key=lambda p: (not p.stem.isdigit(), int(p.stem) if p.stem.isdigit() else p.stem),
        )

        self.assertTrue(program_files, "No .c files found in tests folder")

        for program_file in program_files:
            with self.subTest(program=program_file.name):
                src = program_file.read_text(encoding="utf-8")
                tokens = lex(src)
                self.assertTrue(tokens, f"No tokens produced for {program_file.name}")
                self.assertEqual(
                    tokens[-1]["name"],
                    "END",
                    f"Missing END token for {program_file.name}",
                )

    # def test_small_function_program(self):
    #     src = (
    #         "int main() {\n"
    #         "  int x = 10;\n"
    #         "  double y = x + 0.5;\n"
    #         "  if (x >= 5 && x != 0) return x;\n"
    #         "}\n"
    #     )
    #     got = [t["name"] for t in lex(src)]
    #     expected = [
    #         "INT", "ID", "LPAR", "RPAR", "LACC",
    #         "INT", "ID", "ASSIGN", "CT_INT", "SEMICOLON",
    #         "DOUBLE", "ID", "ASSIGN", "ID", "ADD", "CT_REAL", "SEMICOLON",
    #         "IF", "LPAR", "ID", "GREATEREQ", "CT_INT", "AND", "ID", "NOTEQ", "CT_INT", "RPAR", "RETURN", "ID", "SEMICOLON",
    #         "RACC", "END",
    #     ]
    #     self.assertEqual(got, expected)

    # def test_struct_and_field_access(self):
    #     src = (
    #         "struct Node { int v; };\n"
    #         "struct Node n;\n"
    #         "n.v = 7;\n"
    #     )
    #     got = [t["name"] for t in lex(src)]
    #     expected = [
    #         "STRUCT", "ID", "LACC", "INT", "ID", "SEMICOLON", "RACC", "SEMICOLON",
    #         "STRUCT", "ID", "ID", "SEMICOLON",
    #         "ID", "DOT", "ID", "ASSIGN", "CT_INT", "SEMICOLON",
    #         "END",
    #     ]
    #     self.assertEqual(got, expected)

    # def test_for_while_break_return(self):
    #     src = (
    #         "int f() {\n"
    #         "  int i = 0;\n"
    #         "  for(i=0;i<10;i=i+1) {\n"
    #         "    while(i<5) break;\n"
    #         "  }\n"
    #         "  return i;\n"
    #         "}\n"
    #     )
    #     got = [t["name"] for t in lex(src)]
    #     expected = [
    #         "INT", "ID", "LPAR", "RPAR", "LACC",
    #         "INT", "ID", "ASSIGN", "CT_INT", "SEMICOLON",
    #         "FOR", "LPAR", "ID", "ASSIGN", "CT_INT", "SEMICOLON", "ID", "LESS", "CT_INT", "SEMICOLON", "ID", "ASSIGN", "ID", "ADD", "CT_INT", "RPAR", "LACC",
    #         "WHILE", "LPAR", "ID", "LESS", "CT_INT", "RPAR", "BREAK", "SEMICOLON",
    #         "RACC",
    #         "RETURN", "ID", "SEMICOLON",
    #         "RACC", "END",
    #     ]
    #     self.assertEqual(got, expected)

    # def test_comments_and_line_numbers(self):
    #     src = (
    #         "int x; // declaration\n"
    #         "// whole line comment\n"
    #         "x = x + 1;\n"
    #     )
    #     tokens = lex(src)
    #     got = [t["name"] for t in tokens]
    #     expected = ["INT", "ID", "SEMICOLON", "ID", "ASSIGN", "ID", "ADD", "CT_INT", "SEMICOLON", "END"]
    #     self.assertEqual(got, expected)

    #     line_map = [(t["name"], t["line"]) for t in tokens]
    #     self.assertIn(("INT", 1), line_map)
    #     self.assertIn(("ASSIGN", 3), line_map)
    #     self.assertIn(("END", 4), line_map)

    # def test_arrays_and_pointers(self):
    #     src = (
    #         "int a[3];\n"
    #         "void *p;\n"
    #         "a[0] = 1;\n"
    #     )
    #     got = [t["name"] for t in lex(src)]
    #     expected = [
    #         "INT", "ID", "LBRACKET", "CT_INT", "RBRACKET", "SEMICOLON",
    #         "VOID", "MUL", "ID", "SEMICOLON",
    #         "ID", "LBRACKET", "CT_INT", "RBRACKET", "ASSIGN", "CT_INT", "SEMICOLON",
    #         "END",
    #     ]
    #     self.assertEqual(got, expected)


if __name__ == "__main__":
    unittest.main()
