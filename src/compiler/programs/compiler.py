import sys

from compiler.code_generator import CodeGenerator
from compiler.klein_errors import KleinError, LexicalError, ParseError, SemanticError
from compiler.parser import Parser
from compiler.scanner import Scanner
from compiler.semantic_analyzer import SemanticAnalyzer


def compiler():
    program = sys.argv[1] if len(sys.argv) > 1 else ""
    scanner = Scanner(program)
    parser = Parser(scanner)

    try:
        ast = parser.parse()
        semantic_analyzer = SemanticAnalyzer(ast)
        semantic_analyzer.annotate()
        symbol_table = semantic_analyzer.symbol_table
        code_generator = CodeGenerator(ast, symbol_table)
        code_generator.generate()
        return
    except LexicalError as e:
        print(e)
    except ParseError as e:
        print(e)
    except SemanticError as e:
        print(e)
    except KleinError:
        print("Klein Error: unable to continue processing")
    except Exception:
        print("Klein Error: unable to continue processing")

    sys.exit(1)


if __name__ == "__main__":
    compiler()
