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
        analyzer = SemanticAnalyzer(ast)
        analyzer.annotate()
        print(analyzer.symbol_table)
    except LexicalError as e:
        print(e)
    except ParseError as e:
        print(e)
    except SemanticError as e:
        print(e)
    except Exception:
        print("Klein Error: unable to continue processing")


if __name__ == "__main__":
    display_symbol_table()
