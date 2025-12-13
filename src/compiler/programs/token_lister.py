import sys

from compiler.klein_errors import KleinError
from compiler.scanner import Scanner

# Converts a klein program (stdin) to a list of identified tokens (stdout)


def list_tokens():
    program = sys.argv[1] if len(sys.argv) > 1 else ""
    scanner = Scanner(program)

    try:
        for token in scanner:
            print(token)
    except KleinError as e:
        print(e)
    except Exception:  # noqa: BLE001
        print("Klein Lexical Error: unable to continue scanning")


if __name__ == "__main__":
    list_tokens()
