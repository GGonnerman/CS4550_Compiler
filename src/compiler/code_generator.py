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

    def _select_tmp_register(self) -> int:
        return 2

    # NOTE: Technically, this code is very similar to the "_generate_function_call"
    # method, with the main difference being the loading of arguments. However,
    # I think breaking it into smaller function risks obscuring the flow too much
    # such that repeated code is acceptable in this case.
    def _generate_setup(self) -> list[TMLine]:
        param_count: int = self._get_parameter_count("main")

        # In theory, this section would be somehow extracted during the function
        # generation process, though that seems to be part of the "next steps".
        main_location_imem = 21 + 2 * param_count
        # Explanation: Moving each param for main costs 2 lines (load into reg + store to new dmem slot)

        top_offset_from_top: int = param_count + REG_TOP
        return_addr_offset_from_top: int = 1 + param_count
        return [
            LdcCommand(REG_TOP, 1),
            StCommand(REG_TOP, top_offset_from_top, REG_TOP, "Store current top"),
            # TODO: Code here to move the arguments down 1 spot in dmem, skipped for
            # testing purposes.
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
            StCommand(REG_TOP, 0, REG_STATUS, "Store the return address"),
            LdaCommand(REG_TOP, 6, REG_STATUS, "Set the new top pointer"),
            LdcCommand(7, main_location_imem, "Jump to main"),
            # grab return value
            OutCommand(REG_RETURN_VALUE, "Printing main return value"),
            # halt
            HaltCommand(),
        ]

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
            LdCommand(REG_STATUS, 4, REG_STATUS, "Restore status pointer"),
            LdCommand(
                REG_PC,
                return_addr_offset_from_top,
                REG_TOP,
                "Restore program counter",
            ),
        ]

    def _return_sequence_calling_fn(self) -> list[TMLine]:
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
        selected_reg = self._select_tmp_register()
        commands: list[TMLine] = [
            Comment(""),
            Comment("Function: print"),
            Comment(""),
            *self._calling_sequence_called_fn(),
            LdCommand(selected_reg, -1, REG_STATUS, "Load argument"),
            OutCommand(selected_reg, "Print value"),
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
        main_param_count = self._get_parameter_count("main")
        print_location_imem = 10 + 2 * main_param_count
        code: list[TMLine] = []
        code.append(Comment(""))
        code.append(Comment(f"Function: {definition.name.value}"))
        code.append(Comment(""))
        param_count = len(definition.parameters.parameters)
        code.extend(self._calling_sequence_called_fn())
        # This is likely the main section of code that will be re-written for next
        # module. This only works in limited use case of any number of print calls
        # with integer literal arguments and a return value
        body: Body = definition.body
        for print_expr in body.print_expressions:
            selected_reg = self._select_tmp_register()
            argument_code: list[TMLine] = self._generate_expression(
                print_expr.argument_list.arguments[0].value,
                selected_reg,
            )
            code.extend(argument_code)

            code.extend(
                self._generate_function_call(
                    "print",
                    print_location_imem,
                    [MemoryLocation("register", selected_reg)],
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
