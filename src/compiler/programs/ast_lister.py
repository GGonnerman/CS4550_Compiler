import sys

from compiler.klein_errors import LexicalError, ParseError
from compiler.parser import Parser
from compiler.scanner import Scanner


def print_klein_ast():
    program = sys.argv[1] if len(sys.argv) > 1 else ""
    scanner = Scanner(program)
    parser = Parser(scanner)

    try:
        ast = parser.parse()
        print(ast)
    except LexicalError as e:
        print(e)
    except ParseError as e:
        print(e)
    except Exception:
        print("Klein Error: unable to continue processing")


if __name__ == "__main__":
    print_klein_ast()
