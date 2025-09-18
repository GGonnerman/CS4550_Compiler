import sys

from klein_errors import KleinError
from scanner import Scanner

if __name__ == "__main__":
    program = sys.argv[1]
    scanner = Scanner(program)

    try:
        for token in scanner:
            print(token)
    except KleinError as e:
        print(e)
    except Exception:
        print("Klein Lexical Error: unable to continue")
