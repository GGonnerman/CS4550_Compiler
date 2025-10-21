import sys

from compiler.klein_errors import LexicalError, ParseError
from compiler.parser import Parser
from compiler.scanner import Scanner


def validate_klein_program():
    program = sys.argv[1] if len(sys.argv) > 1 else ""
    scanner = Scanner(program)
    parser = Parser(scanner)

    try:
        _ = parser.parse()
        print("valid program")
    except LexicalError as e:
        print(e)
    except ParseError as e:
        print(e)
    except Exception:  # noqa: BLE001
        print("Klein Error: unable to continue processing")


if __name__ == "__main__":
    validate_klein_program()
