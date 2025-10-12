import os
from enum import StrEnum, auto
from io import TextIOWrapper

from typing_extensions import override

from compiler.ast import SemanticAction
from compiler.tokens import TokenType


class NonTerminal(StrEnum):
    PROGRAM = auto()
    DEFINITION_LIST = auto()
    DEFINITION = auto()
    PARAMETER_LIST = auto()
    FORMAL_PARAMETERS = auto()
    FORMAL_PARAMETERS_REST = auto()
    ID_WITH_TYPE = auto()
    TYPE = auto()
    BODY = auto()
    PRINT_EXPRESSION = auto()
    EXPRESSION = auto()
    EXPRESSION_REST = auto()
    SIMPLE_EXPRESSION = auto()
    SIMPLE_EXPRESSION_REST = auto()
    TERM = auto()
    TERM_REST = auto()
    FACTOR = auto()
    FACTOR_REST = auto()
    ARGUMENT_LIST = auto()
    FORMAL_ARGUMENTS = auto()
    FORMAL_ARGUMENTS_REST = auto()
    LITERAL = auto()

    @override
    def __str__(self):
        return self.name.upper()


def clean_csv_file(csvfile: TextIOWrapper) -> list[list[str]]:
    table: list[list[str]] = []
    for raw_row in csvfile:
        row: str = raw_row.strip()
        cells: list[str] = row.split(",")
        table.append(cells)
    return table


def read_csv_to_table(filename: str) -> list[list[str]]:
    file_dir = os.path.dirname(__file__)
    parse_table_path = os.path.join(file_dir, filename)
    with open(parse_table_path) as csvfile:
        table: list[list[str]] = clean_csv_file(csvfile)
    return table


# TODO: In theory here we could have allow creating custom "error values" which
# would be parsed from cells within the original spreadsheet
def parse_cell(cell: str) -> list[NonTerminal | TokenType | SemanticAction]:
    # None is episilon so there would be nothing returned in that case
    if cell == "None":
        return []

    out: list[NonTerminal | TokenType | SemanticAction] = []
    for raw_value in cell.split(" "):
        if raw_value in NonTerminal._value2member_map_:
            out.append(NonTerminal(raw_value))
        elif raw_value in TokenType._value2member_map_:
            out.append(TokenType(raw_value))
        elif raw_value in SemanticAction._value2member_map_:
            out.append(SemanticAction(raw_value))
        else:
            raise ValueError(
                f'Found invalid value in cell "{cell}", specifically "{raw_value}"',
            )

    return out


def process_table_into_parsetable(table: list[list[str]]):
    parse_table: dict[
        tuple[NonTerminal, TokenType],
        list[NonTerminal | TokenType | SemanticAction],
    ] = {}
    header_row: list[str] = table.pop(0)[1:]
    headers: list[TokenType] = [TokenType(header) for header in header_row]
    for row in table:
        nonterminal: NonTerminal = NonTerminal(row.pop(0))
        for idx, value in enumerate[str](row):
            pair: TokenType = headers[idx]
            if value == "":
                continue
            parse_table[(nonterminal, pair)] = parse_cell(value)
    return parse_table


def generate_parse_table(filename: str):
    csvtable: list[list[str]] = read_csv_to_table(filename)
    return process_table_into_parsetable(csvtable)


if __name__ == "__main__":
    print(generate_parse_table("parse-table.csv"))
