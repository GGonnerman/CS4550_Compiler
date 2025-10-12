from compiler.programs.ast_lister import print_klein_ast
from compiler.programs.token_lister import list_tokens
from compiler.programs.validator import validate_klein_program


def klein_list_tokens():
    return list_tokens()


def klein_parse_program():
    return validate_klein_program()


def klein_print_ast():
    return print_klein_ast()
