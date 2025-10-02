from compiler.token_lister import list_tokens
from compiler.validator import validate_klein_program


def klein_list_tokens():
    return list_tokens()


def klein_parse_program():
    return validate_klein_program()
