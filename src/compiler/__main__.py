import sys

from compiler.klein_errors import KleinError
from compiler.parser import Parser
from compiler.scanner import Scanner
from compiler.token_lister import list_tokens


def klein_list_tokens():
    return list_tokens()


def klein_parse_program():
    program = sys.argv[1] if len(sys.argv) > 1 else ""
    scanner = Scanner(program)
    parser = Parser(scanner)

    try:
        is_valid_program = parser.parse()
        if is_valid_program:
            print("The provided Klein program is valid")
        else:
            print("The provided Klein program is not valid")
    except KleinError as e:
        print(e)
    except Exception:
        print("Klein Lexical Error: unable to continue scanning")
