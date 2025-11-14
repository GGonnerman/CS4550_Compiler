from dataclasses import dataclass
from typing import Literal

from compiler.ast_nodes import (
    Body,
    Definition,
    Expression,
    FunctionAnnotation,
    IntegerLiteral,
    Program,
)
from compiler.symbol_table import SymbolTable
from compiler.tm import (
    AddCommand,
    Comment,
    HaltCommand,
    LdaCommand,
    LdcCommand,
    LdCommand,
    OutCommand,
    StCommand,
    TMLine,
)

REG_ZERO = 0
REG_RETURN_VALUE = 4
REG_STATUS = 5
REG_TOP = 6
REG_PC = 7


@dataclass
class MemoryLocation:
    location: Literal["register", "dmem"]
    position: int


class CodeGenerator:
    def __init__(self, ast: Program, symbol_table: SymbolTable):
        self._ast: Program = ast
        self._symbol_table: SymbolTable = symbol_table
        self._code: list[TMLine] = []

    def _get_parameter_count(self, name: str) -> int:
        fn = self._symbol_table.scope_lookup(name)
        if fn is None:
            raise ValueError(f"Missing {name} function")
        fn_type = fn.symbol_type
        if not isinstance(fn_type, FunctionAnnotation):
            raise TypeError(f"{name} function symbol type is not a function")
        return len(fn_type.source)

    def _generate_setup(self) -> list[TMLine]:
        code: list[TMLine] = [
            LdcCommand(5, 1),
            LdcCommand(6, 2),
        ]

        code.extend(
            [
                *self._generate_function_call(
                    "main",
                    23,
                    [],
                ),
                # grab return value
                OutCommand(REG_RETURN_VALUE, "Printing main return value"),
                # halt
                HaltCommand(),
            ],
        )
        return code

    def _calling_sequence_calling_fn(
        self,
        destination_addr: int,
        params: list[MemoryLocation],
    ) -> list[TMLine]:
        status_offset_from_top = len(params) + 5
        top_offset_from_top = status_offset_from_top + 1
        return_addr_offset_from_top = 1 + len(params)
        code: list[TMLine] = []

        code.extend(
            [
                StCommand(
                    REG_STATUS,
                    status_offset_from_top,
                    REG_TOP,
                    "Store current status",
                ),
                StCommand(
                    REG_TOP,
                    top_offset_from_top,
                    REG_TOP,
                    "Store current top",
                ),
            ],
        )

        has_changed_status = False
        for i, param in enumerate(reversed(params)):
            param_offset_in_dmem = i + 1
            if param.location == "register":
                code.append(
                    StCommand(
                        param.position,
                        param_offset_in_dmem,
                        REG_TOP,
                        "Load value from register into arg slot",
                    ),
                )
            elif param.location == "dmem":
                code.append(Comment("Load value from memory into arg slot"))
                if has_changed_status:
                    code.append(
                        LdCommand(
                            REG_STATUS,
                            status_offset_from_top,
                            REG_TOP,
                        ),
                    )
                # Use reg status as in between variable, knowing it gets restored if
                # it has been changed
                code.append(LdCommand(REG_STATUS, param.position, REG_STATUS))
                code.append(StCommand(REG_STATUS, param_offset_in_dmem, REG_TOP))

        code.extend(
            [
                LdaCommand(
                    REG_STATUS,
                    return_addr_offset_from_top,
                    REG_TOP,
                    "Update status",
                ),
                Comment(
                    "Do some math to get correct return addr (uses top reg but restores it)",
                ),
                LdcCommand(REG_TOP, 3),
                AddCommand(REG_TOP, REG_TOP, REG_PC),
                StCommand(REG_TOP, 0, REG_STATUS, "Store return address"),
                LdaCommand(REG_TOP, 6, REG_STATUS, "Restore top reg to its real value"),
                LdcCommand(7, destination_addr),
            ],
        )
        return code

    def _calling_sequence_called_fn(self) -> list[TMLine]:
        return [
            *self._store_gp_registers(),
        ]

    def _return_sequence_called_fn(self, param_count: int) -> list[TMLine]:
        return_addr_offset_from_top = 1 + param_count
        return [
            *self._restore_gp_registers(),
            LdCommand(REG_TOP, 5, REG_STATUS, "Restore top pointer"),
            LdCommand(REG_STATUS, 4, REG_STATUS, "Restore top pointer"),
            LdCommand(
                REG_PC,
                return_addr_offset_from_top,
                REG_TOP,
                "Restore the pc",
            ),
        ]

    def _return_sequence_calling_fn(self) -> list[TMLine]:
        # I don't think there really is one...?
        # Maybe depending on how we deal with return value there could be
        return []

    def _store_gp_registers(self) -> list[TMLine]:
        commands: list[TMLine] = []
        for reg_num in range(1, 4):  # Just save the three "general purpose registers"
            commands.append(StCommand(reg_num, reg_num, REG_STATUS))  # noqa: PERF401
        return commands

    def _restore_gp_registers(self) -> list[TMLine]:
        commands: list[TMLine] = []
        for reg_num in range(1, 4):  # Just save the three "general purpose registers"
            commands.append(LdCommand(reg_num, reg_num, REG_STATUS))  # noqa: PERF401
        return commands

    def _generate_print_fn(self) -> list[TMLine]:
        param_count = self._get_parameter_count("print")
        commands: list[TMLine] = [
            Comment(""),
            Comment("Print function"),
            Comment(""),
            *self._calling_sequence_called_fn(),
            LdCommand(1, -1, REG_STATUS, "Load argument"),
            OutCommand(1, "Print value"),
            Comment("Nothing to do with return value"),
            *self._return_sequence_called_fn(param_count),
        ]
        return commands

    def _generate_function_call(
        self,
        function_name: str,
        destination_addr: int,
        params: list[MemoryLocation],
    ) -> list[TMLine]:
        return [
            Comment(f"Calling {function_name}"),
            *self._calling_sequence_calling_fn(
                destination_addr,
                params,
            ),
            *self._return_sequence_calling_fn(),
            Comment(f"Returning from {function_name}"),
        ]

    def _generate_function(self, definition: Definition) -> list[TMLine]:
        code: list[TMLine] = []
        code.append(Comment(""))
        code.append(Comment(f"Function: {definition.name.value}"))
        code.append(Comment(""))
        param_count = len(definition.parameters.parameters)
        code.extend(self._calling_sequence_called_fn())
        body: Body = definition.body
        for print_expr in body.print_expressions:
            argument_code: list[TMLine] = self._generate_expression(
                print_expr.argument_list.arguments[0].value,
                1,
            )
            code.extend(argument_code)

            code.extend(
                self._generate_function_call(
                    "print",
                    12,
                    [MemoryLocation("register", 1)],
                ),
            )
        code.extend(self._generate_expression(body.body, REG_RETURN_VALUE))
        code.append(
            StCommand(
                REG_RETURN_VALUE,
                -1 - len(definition.parameters.parameters),
                REG_STATUS,
            ),
        )
        code.extend(self._return_sequence_called_fn(param_count))

        return code

    def _generate_expression(
        self,
        expression: Expression,
        into_reg: int,
    ) -> list[TMLine]:
        if isinstance(expression, IntegerLiteral):
            return [LdcCommand(into_reg, int(expression.value))]
        raise NotImplementedError(
            f"Generating code for expression of type {expression.__class__.__name__} is not yet implemented",
        )

    def generate(self):
        self._code: list[TMLine] = [
            *self._generate_setup(),
            *self._generate_print_fn(),
        ]
        for definition in self._ast.definition_list:
            self._code.extend(self._generate_function(definition))

        for line in self._code:
            line.print()
