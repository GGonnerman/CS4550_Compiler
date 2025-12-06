from dataclasses import dataclass
from math import ceil
from typing import Literal

from compiler.ast_nodes import (
    AndExpression,
    Body,
    BooleanLiteral,
    Definition,
    DivideExpression,
    EqualsExpression,
    Expression,
    FunctionAnnotation,
    FunctionCallExpression,
    Identifier,
    IfExpression,
    IntegerLiteral,
    LessThanExpression,
    MinusExpression,
    NotExpression,
    OrExpression,
    PlusExpression,
    Program,
    TimesExpression,
    UnaryMinusExpression,
)
from compiler.ir import IR, IROperation
from compiler.klein_errors import CodeGenerationError
from compiler.label import Label
from compiler.symbol_table import SymbolTable
from compiler.tm import (
    AddCommand,
    Comment,
    DivCommand,
    HaltCommand,
    JeqCommand,
    JltCommand,
    JneCommand,
    LdaCommand,
    LdcCommand,
    LdCommand,
    MulCommand,
    OutCommand,
    StCommand,
    SubCommand,
    TMCommand,
    TMLine,
)

REG_ZERO = 0
REG_RETURN_VALUE = 4
REG_STATUS = 5
REG_TOP = 6
REG_PC = 7

OFFSET_TO_TEMP = 7


@dataclass
class MemoryLocation:
    location: Literal["register", "dmem"]
    position: int


class CodeGenerator:
    def __init__(self, ast: Program, symbol_table: SymbolTable):
        self._ast: Program = ast
        self._symbol_table: SymbolTable = symbol_table
        self._code: list[TMLine] = []
        self._tmp_count: int = 0
        self._register: int = 0
        self._label_maker: Label = Label()
        self._goto_mapping: dict[str, int] = {}
        # Original IR line, optional conditional register, source position
        self._jumps_to_complete: list[tuple[IR, int | None, int]] = []
        self._current_params: list[MemoryLocation] = []

        self._topoffsets_to_complete: list[tuple[str, int]] = []
        self._topoffsets: dict[str, int] = {}

        self._current_fn_context: dict[str, int] = {}

    # Alternating returning reg 1-2 will work good enough for now
    def _get_register(self) -> int:
        self._register += 1
        return (self._register % 2) + 1

    def _get_parameter_count(self, name: str) -> int:
        fn = self._symbol_table.scope_lookup(name)
        if fn is None:
            raise CodeGenerationError(f"Missing {name} function in symbol table")
        fn_type = fn.symbol_type
        if not isinstance(fn_type, FunctionAnnotation):
            raise CodeGenerationError(
                f"{name} symbol type was expected to be function. Instead found {fn_type.__class__.__name__}",
            )
        return len(fn_type.source)

    def _select_tmp(self) -> int:
        return 2  # Currently constant, but later can be more complicated logic

    def _get_label(self) -> str:
        return self._label_maker.get_label()

    def _generate_setup(self) -> list[TMLine]:
        param_count: int = self._get_parameter_count("main")

        imem_offset_for_params = 0
        if param_count > 0:
            imem_offset_for_params += 2
        if param_count > 1:
            imem_offset_for_params += 4 * ceil((param_count - 2) / 2)
        main_location_imem = 21 + imem_offset_for_params

        top_offset_from_top: int = param_count + REG_TOP
        return_addr_offset_from_top: int = 1 + param_count
        code: list[TMLine] = [
            LdcCommand(REG_TOP, 1),
            StCommand(REG_TOP, top_offset_from_top, REG_TOP, "Store current top"),
        ]
        # Move all arguments down 1 slot in DMEM
        # and reverse the order (so actually move it down via #params - 1)
        if param_count >= 1:
            selected_reg = self._select_tmp()
            code.extend(
                [
                    LdCommand(
                        selected_reg,
                        0,
                        REG_TOP,
                        "Copy arg #0",
                    ),
                    StCommand(
                        selected_reg,
                        param_count,
                        REG_TOP,
                        "Move to opposite position",
                    ),
                ],
            )

        for i in range(1, ceil(param_count / 2)):
            swap_reg_1 = 1
            swap_reg_2 = 2
            # Get the position of the 2 element we're going to swap
            lower_pos = i
            upper_pos = param_count - i
            code.extend(
                [
                    LdCommand(
                        swap_reg_1,
                        lower_pos,
                        REG_TOP,
                        f"Copy arg #{i}",
                    ),
                    LdCommand(
                        swap_reg_2,
                        upper_pos,
                        REG_TOP,
                        f"Copy arg #{param_count - i}",
                    ),
                    StCommand(
                        swap_reg_1,
                        upper_pos,
                        REG_TOP,
                        "Move to opposite position",
                    ),
                    StCommand(
                        swap_reg_2,
                        lower_pos,
                        REG_TOP,
                        "Move to opposite position",
                    ),
                ],
            )

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
                StCommand(REG_TOP, 0, REG_STATUS, "Store the return address"),
            ],
        )

        self._topoffsets_to_complete.append(
            ("main", TMCommand.reserve_line_num()),
        )

        code.extend(
            [
                LdcCommand(7, main_location_imem, "Jump to main"),
                OutCommand(REG_RETURN_VALUE, "Printing main return value"),
                HaltCommand(),
            ],
        )
        return code

    def _calling_sequence_calling_fn(
        self,
        function_name: str,
        destination_addr: int | None,
        params: list[MemoryLocation],
    ) -> list[TMLine]:
        param_count = self._get_parameter_count(function_name)
        status_offset_from_top = param_count + 5
        top_offset_from_top = status_offset_from_top + 1
        return_addr_offset_from_top = 1 + param_count
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
                            "restoring status since it changed",
                        ),
                    )
                # Use reg status as in between variable, knowing it gets restored if
                # it has been changed
                code.append(
                    LdCommand(
                        REG_STATUS,
                        param.position,
                        REG_STATUS,
                    ),
                )
                code.append(
                    StCommand(
                        REG_STATUS,
                        param_offset_in_dmem,
                        REG_TOP,
                    ),
                )
                has_changed_status = True

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
            ],
        )

        self._topoffsets_to_complete.append(
            (
                function_name,
                TMCommand.reserve_line_num(),
            ),
        )

        print(f"* Consider call to {function_name}")

        if isinstance(destination_addr, int):
            print("* Call was direct")
            code.append(
                LdcCommand(7, destination_addr),
            )
        else:
            print("* Call was via name")
            self._jumps_to_complete.append(
                (
                    IR(
                        function_name,
                        None,
                        IROperation.GOTO,
                        None,
                    ),
                    None,
                    TMCommand.reserve_line_num(),
                ),
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
        selected_reg = self._select_tmp()
        self._topoffsets["print"] = 0
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
        destination_addr: int | None,
        params: list[MemoryLocation],
    ) -> list[TMLine]:
        return [
            Comment(f"Calling {function_name}"),
            *self._calling_sequence_calling_fn(
                function_name,
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
        self._goto_mapping[definition.name.value] = TMCommand.current_line_num
        self._current_fn_context = {}
        for idx, param in enumerate(definition.parameters):
            # This corresponds to the offset in memory from status where this variable
            # can be found in the stack frame.
            self._current_fn_context[param.name.value] = -1 - idx

        code.extend(self._calling_sequence_called_fn())
        body: Body = definition.body
        ir: list[IR]
        temp_spots_required: int = 0
        for print_expr in body.print_expressions:
            self._reset_temps()
            ir = []
            self._generate_ir(print_expr.argument_list.arguments[0].value, ir)
            argument_code: list[TMLine] = self._parse_ir(ir)
            temp_spots_required = max(temp_spots_required, self._tmp_count)

            code.extend(argument_code)

            code.append(
                LdCommand(
                    REG_RETURN_VALUE,
                    print_expr.argument_list.arguments[0].value.place + OFFSET_TO_TEMP,
                    REG_STATUS,
                    "Loading result of body into return addr",
                ),
            )

            code.extend(
                self._generate_function_call(
                    "print",
                    print_location_imem,
                    [MemoryLocation("register", REG_RETURN_VALUE)],
                ),
            )
        self._reset_temps()
        ir = []
        self._generate_ir(body.body, ir)
        code.extend(self._parse_ir(ir))
        temp_spots_required = max(temp_spots_required, self._tmp_count)
        self._topoffsets[definition.name.value] = temp_spots_required + 1
        # +1 is required here because we don't use offset 0
        code.append(
            LdCommand(
                REG_RETURN_VALUE,
                body.body.place + OFFSET_TO_TEMP,
                REG_STATUS,
                "Loading result of body into return addr",
            ),
        )
        code.append(
            StCommand(
                REG_RETURN_VALUE,
                -1 - len(definition.parameters.parameters),
                REG_STATUS,
            ),
        )
        code.extend(self._return_sequence_called_fn(param_count))

        return code

    def _reset_temps(self):
        self._tmp_count = 0

    def _make_new_temp(self):
        self._tmp_count += 1
        return self._tmp_count

    # Instead of generating expressions directly as code, we will generate 3AC (3 address code)
    # NOTE: This function *modifies* the argument ir's original list!
    def _generate_ir(  # noqa: C901, PLR0915
        self,
        expression: Expression,
        ir: list[IR],
    ) -> None:
        if isinstance(expression, Identifier):
            expression.set_place(
                self._current_fn_context[expression.value] - OFFSET_TO_TEMP,
            )
            ## Early exit to avoid allocation a new temp when unnecessary
            return
        place = self._make_new_temp()
        if isinstance(expression, IntegerLiteral):
            expression.set_place(place)
            ir.append(IR(place, int(expression.value), IROperation.SET_LITERAL, None))
        elif isinstance(expression, BooleanLiteral):
            # 1 represents true for a boolean; 0 represents false
            value = 1 if expression.value == "true" else 0
            expression.set_place(place)
            ir.append(IR(place, value, IROperation.SET_LITERAL, None))
        elif isinstance(
            expression,
            (
                PlusExpression,
                MinusExpression,
                TimesExpression,
                DivideExpression,
                EqualsExpression,
                LessThanExpression,
            ),
        ):
            expression.set_place(place)
            self._generate_ir(expression.left_side, ir)
            self._generate_ir(expression.right_side, ir)
            operation = {
                PlusExpression: IROperation.PLUS,
                MinusExpression: IROperation.MINUS,
                TimesExpression: IROperation.TIMES,
                DivideExpression: IROperation.DIVIDE,
                EqualsExpression: IROperation.EQUALS,
                LessThanExpression: IROperation.LESS_THAN,
            }[expression.__class__]

            ir.append(
                IR(
                    place,
                    expression.left_side.place,
                    operation,
                    expression.right_side.place,
                ),
            )
        elif isinstance(expression, (AndExpression)):
            expression.set_place(place)
            failed_cond_label = self._get_label()
            end_label = self._get_label()
            self._generate_ir(expression.left_side, ir)
            ir.append(
                IR(
                    failed_cond_label,
                    expression.left_side.place,
                    IROperation.IF_NOT,
                    None,
                ),
            )
            self._generate_ir(expression.right_side, ir)
            ir.extend(
                [
                    IR(
                        failed_cond_label,
                        expression.right_side.place,
                        IROperation.IF_NOT,
                        None,
                    ),
                    IR(
                        expression.place,
                        1,
                        IROperation.SET_LITERAL,
                        None,
                    ),
                    IR(
                        end_label,
                        None,
                        IROperation.GOTO,
                        None,
                    ),
                    IR(
                        failed_cond_label,
                        None,
                        IROperation.LABEL,
                        None,
                    ),
                    IR(
                        expression.place,
                        0,
                        IROperation.SET_LITERAL,
                        None,
                    ),
                    IR(
                        end_label,
                        None,
                        IROperation.LABEL,
                        None,
                    ),
                ],
            )
        elif isinstance(expression, (OrExpression)):
            expression.set_place(place)
            success_cond_label = self._get_label()
            end_label = self._get_label()
            self._generate_ir(expression.left_side, ir)
            ir.append(
                IR(
                    success_cond_label,
                    expression.left_side.place,
                    IROperation.IF,
                    None,
                ),
            )
            self._generate_ir(expression.right_side, ir)
            ir.extend(
                [
                    IR(
                        success_cond_label,
                        expression.right_side.place,
                        IROperation.IF,
                        None,
                    ),
                    IR(
                        expression.place,
                        0,
                        IROperation.SET_LITERAL,
                        None,
                    ),
                    IR(
                        end_label,
                        None,
                        IROperation.GOTO,
                        None,
                    ),
                    IR(
                        success_cond_label,
                        None,
                        IROperation.LABEL,
                        None,
                    ),
                    IR(
                        expression.place,
                        1,
                        IROperation.SET_LITERAL,
                        None,
                    ),
                    IR(
                        end_label,
                        None,
                        IROperation.LABEL,
                        None,
                    ),
                ],
            )
        elif isinstance(
            expression,
            (
                NotExpression,
                UnaryMinusExpression,
            ),
        ):
            expression.set_place(place)
            self._generate_ir(expression.value, ir)
            operation = {
                NotExpression: IROperation.NOT,
                UnaryMinusExpression: IROperation.UNARY_MINUS,
            }[expression.__class__]

            ir.append(
                IR(
                    place,
                    expression.value.place,
                    operation,
                    None,
                ),
            )
        elif isinstance(
            expression,
            IfExpression,
        ):
            expression.set_place(place)

            self._generate_ir(expression.condition, ir)
            else_label = self._get_label()
            done_label = self._get_label()

            ir.append(
                IR(
                    else_label,
                    expression.condition.place,
                    IROperation.IF_NOT,
                    None,
                ),
            )

            self._generate_ir(expression.consequent, ir)

            ir.extend(
                [
                    IR(
                        place,
                        expression.consequent.place,
                        IROperation.COPY,
                        None,
                    ),
                    IR(
                        done_label,
                        expression.condition.place,
                        IROperation.GOTO,
                        None,
                    ),
                    IR(
                        else_label,
                        None,
                        IROperation.LABEL,
                        None,
                    ),
                ],
            )

            self._generate_ir(expression.alternative, ir)

            ir.extend(
                [
                    IR(
                        place,
                        expression.alternative.place,
                        IROperation.COPY,
                        None,
                    ),
                    IR(
                        done_label,
                        None,
                        IROperation.LABEL,
                        None,
                    ),
                ],
            )
        elif isinstance(expression, FunctionCallExpression):
            expression.set_place(place)
            # Generate the values for all arguments
            for argument in expression.argument_list.arguments:
                self._generate_ir(argument.value, ir)

            # Add the arguments as params
            for argument in expression.argument_list.arguments:
                ir.append(  # noqa: PERF401
                    IR(
                        argument.value.place,
                        None,
                        IROperation.PARAM,
                        None,
                    ),
                )

            argument_count = len(expression.argument_list.arguments)

            ir.extend(
                [
                    IR(
                        expression.place,
                        expression.function_name.value,
                        IROperation.CALL,
                        argument_count,
                    ),
                ],
            )
        else:
            raise CodeGenerationError(
                f"Generating code for expression of type {expression.__class__.__name__} is not yet implemented",
            )

    def _parse_ir(self, ir: list[IR]) -> list[TMLine]:  # noqa: C901, PLR0912, PLR0915
        out: list[TMLine] = []
        for line in ir:
            if line.op == IROperation.SET_LITERAL:
                if not isinstance(line.arg1, int):
                    raise CodeGenerationError("Arg1 was None")
                if not isinstance(line.result, int):
                    raise CodeGenerationError("Result was not an int")
                out.append(
                    LdcCommand(REG_RETURN_VALUE, line.arg1, "Loading literal"),
                )
                out.append(
                    StCommand(
                        REG_RETURN_VALUE,
                        line.result + OFFSET_TO_TEMP,
                        REG_STATUS,
                    ),
                )
            elif line.op in [
                IROperation.PLUS,
                IROperation.MINUS,
                IROperation.TIMES,
                IROperation.DIVIDE,
            ]:
                if not isinstance(line.arg1, int) or not isinstance(line.arg2, int):
                    raise CodeGenerationError("Arg1 or 2 was not an int")
                if not isinstance(line.result, int):
                    raise CodeGenerationError("Result was not an int")
                reg_1 = self._get_register()
                out.append(
                    LdCommand(
                        reg_1,
                        line.arg1 + OFFSET_TO_TEMP,
                        REG_STATUS,
                        "Loading first temp value",
                    ),
                )
                reg_2 = self._get_register()
                out.append(
                    LdCommand(
                        reg_2,
                        line.arg2 + OFFSET_TO_TEMP,
                        REG_STATUS,
                        "Loading second temp value",
                    ),
                )
                command_builder = {
                    IROperation.PLUS: AddCommand,
                    IROperation.MINUS: SubCommand,
                    IROperation.TIMES: MulCommand,
                    IROperation.DIVIDE: DivCommand,
                }[line.op]

                out_reg = self._get_register()
                out.append(
                    command_builder(
                        out_reg,
                        reg_1,
                        reg_2,
                        "Adding the two value and put into return",
                    ),
                )
                out.append(
                    StCommand(
                        out_reg,
                        line.result + OFFSET_TO_TEMP,
                        REG_STATUS,
                        "Putting the result into memory",
                    ),
                )
            elif line.op in [
                IROperation.EQUALS,
                IROperation.LESS_THAN,
            ]:
                if not isinstance(line.arg1, int) or not isinstance(line.arg2, int):
                    raise CodeGenerationError(
                        "Arg1 or Arg2 was not an int",
                    )
                if not isinstance(line.result, int):
                    raise CodeGenerationError("Result was not an int")
                reg_1 = self._get_register()
                reg_2 = self._get_register()
                out_reg = self._get_register()
                out.extend(
                    [
                        LdCommand(
                            reg_1,
                            line.arg1 + OFFSET_TO_TEMP,
                            REG_STATUS,
                            "Loading first temp value",
                        ),
                        LdCommand(
                            reg_2,
                            line.arg2 + OFFSET_TO_TEMP,
                            REG_STATUS,
                            "Loading second temp value",
                        ),
                        SubCommand(
                            reg_1,
                            reg_1,
                            reg_2,
                        ),
                    ],
                )

                if line.op == IROperation.EQUALS:
                    out.append(
                        JeqCommand(
                            reg_1,
                            2,
                            REG_PC,
                        ),
                    )
                elif line.op == IROperation.LESS_THAN:
                    out.append(
                        JltCommand(
                            reg_1,
                            2,
                            REG_PC,
                        ),
                    )
                else:
                    raise CodeGenerationError(
                        "Expected operation to be either equals or less than",
                    )

                out.extend(
                    [
                        LdcCommand(
                            out_reg,
                            0,
                        ),
                        LdaCommand(
                            REG_PC,
                            1,
                            REG_PC,
                        ),
                        LdcCommand(
                            out_reg,
                            1,
                        ),
                    ],
                )

                out.append(
                    StCommand(
                        out_reg,
                        line.result + OFFSET_TO_TEMP,
                        REG_STATUS,
                        "Putting the result into memory",
                    ),
                )

            elif line.op in [
                IROperation.NOT,
                IROperation.UNARY_MINUS,
            ]:
                if not isinstance(line.arg1, int):
                    raise CodeGenerationError(
                        "Arg1 was not an int",
                    )
                if not isinstance(line.result, int):
                    raise CodeGenerationError("Result was not an int")
                reg_1 = self._get_register()
                out.append(
                    LdCommand(
                        reg_1,
                        line.arg1 + OFFSET_TO_TEMP,
                        REG_STATUS,
                        "Loading first temp value",
                    ),
                )
                out_reg = self._get_register()
                negation_code = [
                    LdcCommand(
                        3,
                        2,
                        f"Performing {line.op} operation",
                    ),
                    MulCommand(
                        3,
                        reg_1,
                        3,
                    ),
                    SubCommand(
                        reg_1,
                        reg_1,
                        3,
                    ),
                ]
                if line.op == IROperation.NOT:
                    out.extend(
                        [
                            *negation_code,
                            LdcCommand(
                                3,
                                1,
                            ),
                            AddCommand(
                                out_reg,
                                reg_1,
                                3,
                                "Finished NOT operation",
                            ),
                        ],
                    )
                elif line.op == IROperation.UNARY_MINUS:
                    out.extend(
                        [
                            *negation_code,
                            AddCommand(
                                out_reg,
                                reg_1,
                                0,
                            ),
                        ],
                    )
                else:
                    raise TypeError(
                        "Expected line operation to be either not or unary minus",
                    )

                out.append(
                    StCommand(
                        out_reg,
                        line.result + OFFSET_TO_TEMP,
                        REG_STATUS,
                        "Putting the result into memory",
                    ),
                )
            elif line.op in [IROperation.COPY]:
                if not isinstance(line.arg1, int):
                    raise CodeGenerationError("Arg1 was None")
                if not isinstance(line.result, int):
                    raise CodeGenerationError("Result was not an int")
                reg_1 = self._get_register()
                out.extend(
                    [
                        LdCommand(
                            reg_1,
                            line.arg1 + OFFSET_TO_TEMP,
                            REG_STATUS,
                            "Copy (part 1)",
                        ),
                        StCommand(
                            reg_1,
                            line.result + OFFSET_TO_TEMP,
                            REG_STATUS,
                            "Copy (part 2)",
                        ),
                        AddCommand(
                            REG_RETURN_VALUE,
                            0,
                            reg_1,
                            "Copying also into return reg",
                        ),
                    ],
                )
            elif line.op in [IROperation.LABEL]:
                if not isinstance(line.result, str):
                    raise TypeError("Expected result to be of type string")
                self._goto_mapping[line.result] = TMCommand.current_line_num
            elif line.op in [IROperation.IF_NOT, IROperation.IF]:
                if not isinstance(line.arg1, int):
                    raise TypeError("Expected arg1 to be of type int")
                reg = self._get_register()
                out.append(
                    LdCommand(
                        reg,
                        line.arg1 + OFFSET_TO_TEMP,
                        REG_STATUS,
                        "Loading condition into memeory",
                    ),
                )
                self._jumps_to_complete.append(
                    (line, reg, TMCommand.reserve_line_num()),
                )
            elif line.op in [IROperation.GOTO]:
                self._jumps_to_complete.append(
                    (line, None, TMCommand.reserve_line_num()),
                )
            elif line.op in [IROperation.PARAM]:
                if not isinstance(line.result, int):
                    raise TypeError("Expected param to be an int")
                self._current_params.append(
                    MemoryLocation(
                        "dmem",
                        line.result + OFFSET_TO_TEMP,
                    ),
                )
            elif line.op in [IROperation.CALL]:
                if not isinstance(line.result, int):
                    raise TypeError("Expected call result to be an int")
                if not isinstance(line.arg1, str):
                    raise TypeError("Expected call arg to be a function name")
                if not isinstance(line.arg2, int):
                    raise TypeError("Expected call arg 2 to be number of params")

                params = self._current_params.copy()
                self._current_params.clear()
                out.extend(
                    self._generate_function_call(
                        line.arg1,
                        None,
                        params,
                    ),
                )
                out.append(
                    StCommand(
                        REG_RETURN_VALUE,
                        line.result + OFFSET_TO_TEMP,
                        REG_STATUS,
                    ),
                )

            else:
                raise CodeGenerationError(
                    f"This operation has not been implemented yet: {line.op}",
                )
        return out

    def _resolve_jumps(self) -> list[TMLine]:
        out: list[TMLine] = []
        # Go back through and resolve all the jump since we now know the exact
        # line number to jump to
        for jump in self._jumps_to_complete:
            source_line: int = jump[2]
            condition_reg = jump[1]
            line: IR = jump[0]
            destination = line.result
            if not isinstance(destination, str):
                raise TypeError("Expected destination to be of type string")
            destination_line = self._goto_mapping[destination]

            if line.op == IROperation.GOTO:
                out.append(
                    LdaCommand(
                        REG_PC,
                        destination_line,
                        0,
                        "Unconditional jump",
                        source_line,
                    ),
                )
            elif line.op == IROperation.IF:
                if not isinstance(condition_reg, int):
                    raise TypeError("Expected condition register to be an int")
                if not isinstance(line.arg1, int):
                    raise TypeError("Expected arg1 to be of type int")
                out.append(
                    JneCommand(
                        condition_reg,
                        destination_line,
                        0,
                        "Jump if conditional",
                        source_line,
                    ),
                )
            elif line.op == IROperation.IF_NOT:
                if not isinstance(condition_reg, int):
                    raise TypeError("Expected condition register to be an int")
                if not isinstance(line.arg1, int):
                    raise TypeError("Expected arg1 to be of type int")
                out.append(
                    JeqCommand(
                        condition_reg,
                        destination_line,
                        0,
                        "Jump if not against conditional",
                        source_line,
                    ),
                )
            else:
                raise TypeError("Invalid IROperation in jump map")
        return out

    def _resolve_offsets(self) -> list[TMLine]:
        # Go back through and resolve all of the top offsets, since we know
        # know exactly how many temp variables each function needs.
        out: list[TMLine] = []
        for offset in self._topoffsets_to_complete:
            fn_name = offset[0]
            line_num = offset[1]
            temp_offset = self._topoffsets[fn_name]
            out.append(
                LdaCommand(
                    REG_TOP,
                    temp_offset + 6,
                    REG_STATUS,
                    "Set the new top pointer",
                    line_num,
                ),
            )
        return out

    def generate(self):
        self._code = [
            *self._generate_setup(),
            *self._generate_print_fn(),
        ]

        # We always want the main fn to come first in memory, both for convinence
        # /hardcoding purposes and to match our defined imem spec.
        for definition in self._ast.definition_list:
            if definition.name.value == "main":
                self._code.extend(self._generate_function(definition))

        for definition in self._ast.definition_list:
            if definition.name.value != "main":
                self._code.extend(self._generate_function(definition))

        self._code.extend(self._resolve_jumps())

        self._code.extend(self._resolve_offsets())

        for line in self._code:
            line.print()
