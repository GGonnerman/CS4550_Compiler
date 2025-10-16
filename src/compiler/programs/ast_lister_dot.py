import sys

from compiler.ast import astnode_to_dot
from compiler.klein_errors import LexicalError, ParseError
from compiler.parser import Parser
from compiler.scanner import Scanner


def ast_to_dot():
    program = sys.argv[1] if len(sys.argv) > 1 else ""
    scanner = Scanner(program)
    parser = Parser(scanner)

    try:
        ast = parser.parse()
        astnode_to_dot(ast)
    except LexicalError as e:
        print(e)
    except ParseError as e:
        print(e)
    except Exception:
        print("Klein Error: unable to continue processing")
