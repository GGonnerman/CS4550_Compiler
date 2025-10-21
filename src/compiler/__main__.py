from compiler.programs.ast_lister import ast_to_text
from compiler.programs.ast_lister_dot import ast_to_dot
from compiler.programs.display_symbol_table import display_symbol_table
from compiler.programs.token_lister import list_tokens
from compiler.programs.validator import validate_klein_program


def klein_list_tokens():
    return list_tokens()


def klein_parse_program():
    return validate_klein_program()


def klein_ast_to_text():
    return ast_to_text()


def klein_ast_to_dot():
    return ast_to_dot()


def klein_display_symbol_table():
    return display_symbol_table()
