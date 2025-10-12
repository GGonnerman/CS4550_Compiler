import sys

from compiler.klein_errors import KleinError
from compiler.scanner import Scanner


def list_tokens():
    program = sys.argv[1] if len(sys.argv) > 1 else ""
    scanner = Scanner(program)

    try:
        for token in scanner:
            print(token)
    except KleinError as e:
        print(e)
    except Exception:
        print("Klein Lexical Error: unable to continue scanning")


if __name__ == "__main__":
    list_tokens()
