import sys

from compiler.klein_errors import LexicalError, ParseError, SemanticError
from compiler.parser import Parser
from compiler.scanner import Scanner
from compiler.semantic_analyzer import SemanticAnalyzer


def display_symbol_table():
    program = sys.argv[1] if len(sys.argv) > 1 else ""
    scanner = Scanner(program)
    parser = Parser(scanner)

    try:
        ast = parser.parse()
    except LexicalError as e:
        print(e)
        return
    except ParseError as e:
        print(e)
        return
    except Exception:
        print("Klein Error: unable to continue processing")
        return

    analyzer = SemanticAnalyzer(ast)
    try:
        analyzer.annotate()
        print(analyzer.symbol_table)
        analyzer.display_issues()
    except SemanticError as e:
        analyzer.display_issues()
        print(e)
    except Exception:
        print("Klein Error: unable to continue processing")


if __name__ == "__main__":
    display_symbol_table()
