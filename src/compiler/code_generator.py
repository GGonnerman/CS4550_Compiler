from collections import defaultdict
from math import ceil

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
    Register,
    StCommand,
    SubCommand,
    TMCommand,
    TMLine,
)

REG_ZERO = Register(0)
REG_GPS = [Register(1), Register(2), Register(3)]
# REG_RETURN_VALUE = 4  # noqa: ERA001
REG_STATUS = Register(5)
REG_TOP = Register(6)
REG_PC = Register(7)

OFFSET_TO_TEMP = 7


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
        self._jumps_to_complete: list[tuple[IR, Register | None, int]] = []
        self._current_params: list[int] = []

        self._topoffsets_to_complete: list[tuple[str, int]] = []
        self._topoffsets: dict[str, int] = {}

        self._current_fn_context: dict[str, int] = {}

        self._register_map: dict[Register, list[int]] = defaultdict(list)

    # TODO: Test this function
    # Returns: tuple representing register id to use and whether that vlaue is EVER used again
    def get_furthest_register(self, upcoming_ir: list[IR]) -> tuple[Register, bool]:  # noqa: C901
        # Determine distance to next use of value in each register
        distance_to_registers: dict[Register, int] = dict[Register, int]()
        for distance, ir in enumerate(upcoming_ir):
            for reg_id, reg_values in self._register_map.items():
                if (
                    isinstance(ir.result, int)
                    and ir.result in reg_values
                    and reg_id not in distance_to_registers
                ):
                    distance_to_registers[reg_id] = distance
                if (
                    isinstance(ir.arg1, int)
                    and ir.arg1 in reg_values
                    and reg_id not in distance_to_registers
                ):
                    distance_to_registers[reg_id] = distance
                if (
                    isinstance(ir.arg2, int)
                    and ir.arg2 in reg_values
                    and reg_id not in distance_to_registers
                ):
                    distance_to_registers[reg_id] = distance
            if len(distance_to_registers) == len(REG_GPS):
                break

        # If any register is NEVER used again, return that reg
        for reg in REG_GPS:
            if reg not in distance_to_registers:
                return (reg, False)

        # Otherwise, return the reg with the longest until used next
        furthest_distance = max(distance_to_registers.values())
        for reg_id, distance in distance_to_registers.items():
            if distance == furthest_distance:
                return (reg_id, True)

        raise ValueError("Unable to find a furthest register")

    def get_register(
        self,
        value: int,
        upcoming_ir: list[IR],
    ) -> tuple[Register, list[TMLine]]:
        commands: list[TMLine] = []
        # If already in a register, return that
        for reg_id, reg_values in self._register_map.items():
            if value in reg_values:
                commands.append(
                    Comment(f"Found {value} already in a register, using that"),
                )
                # It would already be in register map, so no need to add it
                return (reg_id, commands)

        best_register, commands = self.get_new_register(value, upcoming_ir)

        commands.append(
            LdCommand(
                best_register,
                value + OFFSET_TO_TEMP,
                REG_STATUS,
            ),
        )

        self._register_map[best_register] = [value]

        return (best_register, commands)

    def get_new_register(
        self,
        value: int | None,
        upcoming_ir: list[IR],
    ) -> tuple[Register, list[TMLine]]:
        commands: list[TMLine] = []
        commands.append(Comment("Was forced to get a new register..."))
        # If theres an empty register, return that
        for reg_id in REG_GPS:
            reg_values = self._register_map[reg_id]
            if len(reg_values) == 0:
                if value is None:
                    self._register_map[reg_id] = []
                else:
                    self._register_map[reg_id] = [value]
                commands.append(
                    Comment(
                        f"Found reg {reg_id} which was already empty! Using that...",
                    ),
                )
                return (
                    reg_id,
                    commands,
                )

        # Value was in nothing AND none were empty, so we need to find the furthest-away register
        # and use that
        furthest_away_reg, need_stored = self.get_furthest_register(upcoming_ir)
        if need_stored:
            for temp_position in self._register_map[furthest_away_reg]:
                # We don't store into parms (negative offsets)
                if temp_position < 0:
                    continue

                commands.append(
                    Comment(
                        f"Using furthest away reg {furthest_away_reg}, which needs saved...",
                    ),
                )
                commands.append(
                    StCommand(
                        furthest_away_reg,
                        temp_position + OFFSET_TO_TEMP,
                        REG_STATUS,
                        "Storing the most-unused reg into memory",
                    ),
                )
        else:
            # for reg_idx, reg_val in self._register_map.items():
            commands.append(
                Comment(
                    f"{furthest_away_reg}: {', '.join(map(str, self._register_map[furthest_away_reg]))}",
                ),
            )

            commands.extend(
                Comment(
                    f"IR Upcoming: {line}",
                )
                for line in upcoming_ir
            )

            commands.append(
                Comment(
                    f"Using furthest away reg {furthest_away_reg}, which is never touched again!",
                ),
            )

        if value is None:
            self._register_map[furthest_away_reg] = []
        else:
            self._register_map[furthest_away_reg] = [value]

        return (furthest_away_reg, commands)

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

    def _get_label(self) -> str:
        return self._label_maker.get_label()

    def _generate_setup(self) -> list[TMLine]:
        param_count: int = self._get_parameter_count("main")

        imem_offset_for_params = 0
        if param_count > 0:
            imem_offset_for_params += 2
        if param_count > 1:
            imem_offset_for_params += 4 * ceil((param_count - 2) / 2)
        main_location_imem = 22 + imem_offset_for_params

        top_offset_from_top: int = param_count + REG_TOP
        return_addr_offset_from_top: int = 1 + param_count
        code: list[TMLine] = [
            LdcCommand(REG_TOP, 1),
            StCommand(REG_TOP, top_offset_from_top, REG_TOP, "Store current top"),
        ]
        # Move all arguments down 1 slot in DMEM
        # and reverse the order (so actually move it down via #params - 1)
        if param_count >= 1:
            selected_reg = Register(1)
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
            swap_reg_1 = Register(1)
            swap_reg_2 = Register(2)
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

        out_register = Register(1)
        code.extend(
            [
                LdcCommand(REG_PC, main_location_imem, "Jump to main"),
                LdCommand(
                    out_register,
                    0,
                    REG_TOP,
                    "Save the return value from main into a register for printing",
                ),  # Copy return value into main and then print it
                OutCommand(out_register, "Printing main return value"),
                HaltCommand(),
            ],
        )
        return code

    def _calling_sequence_calling_fn(
        self,
        function_name: str,
        destination_addr: int | None,
        params: list[int],
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

        for i, param in enumerate(reversed(params)):
            # TODO: Technically, I should find a way to get upcoming IR here...
            reg, commands = self.get_register(param, [])
            code.append(Comment("Register map for context:"))
            for reg_idx, reg_val in self._register_map.items():
                code.append(Comment(f"{reg_idx}: {', '.join(map(str, reg_val))}"))
            code.append(
                Comment(f"Planning to copy value:{param} from {reg} into arg slot"),
            )
            code.extend(commands)

            param_offset_in_dmem = i + 1
            code.append(
                StCommand(
                    reg,
                    param_offset_in_dmem,
                    REG_TOP,
                    "Load param from register into arg slot",
                ),
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
                StCommand(REG_TOP, 0, REG_STATUS, "Store return address"),
            ],
        )

        self._topoffsets_to_complete.append(
            (
                function_name,
                TMCommand.reserve_line_num(),
            ),
        )

        if isinstance(destination_addr, int):
            code.append(
                LdcCommand(REG_PC, destination_addr),
            )
        else:
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
        for reg_num in REG_GPS:  # Just save the three "general purpose registers"
            commands.append(StCommand(reg_num, reg_num, REG_STATUS))  # noqa: PERF401
        return commands

    def _restore_gp_registers(self) -> list[TMLine]:
        commands: list[TMLine] = []
        for reg_num in REG_GPS:  # Just save the three "general purpose registers"
            commands.append(LdCommand(reg_num, reg_num, REG_STATUS))  # noqa: PERF401
        return commands

    def _generate_print_fn(self) -> list[TMLine]:
        param_count = self._get_parameter_count("print")
        # TODO: Make sure clearing register_map at right places
        # Can hard code since nothing else happens in this function context
        selected_reg = Register(1)
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
        params: list[int],
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
        print_location_imem = 11 + 2 * main_param_count
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
            self._register_map.clear()
            ir = []
            self._generate_ir(print_expr.argument_list.arguments[0].value, ir)
            argument_code: list[TMLine] = self._parse_ir(ir)
            temp_spots_required = max(temp_spots_required, self._tmp_count)

            code.extend(argument_code)

            code.extend(
                self._generate_function_call(
                    "print",
                    print_location_imem,
                    [print_expr.argument_list.arguments[0].value.place],
                ),
            )
        # Every time we reset temps, we also should clear the register map
        # TODO: Technically, here we could find a way to leave references to
        # negative values in the register map since those correspond to arguments
        # which span the enitre fn body, and only clear the *entire* map when
        # leaving a function context...
        self._reset_temps()
        self._register_map.clear()
        ir = []
        self._generate_ir(body.body, ir)
        code.extend(self._parse_ir(ir))
        temp_spots_required = max(temp_spots_required, self._tmp_count)
        self._topoffsets[definition.name.value] = temp_spots_required + 1
        # +1 is required here because we don't use offset 0
        chosen_reg, commands = self.get_register(body.body.place, [])
        code.extend(commands)
        code.append(
            Comment(
                f"Finished body. Gonna store {body.body.place} place now from {chosen_reg}. Reg Map:",
            ),
        )
        for reg_idx, reg_val in self._register_map.items():
            code.append(Comment(f"{reg_idx}: {', '.join(map(str, reg_val))}"))
        code.append(
            StCommand(
                chosen_reg,
                -1 - len(definition.parameters.parameters),
                REG_STATUS,
                "Store result into return addr (Check this)",  # FIXME: Verify this
            ),
        )
        code.extend(self._return_sequence_called_fn(param_count))
        # Clear the register map since we're leaving the context of this method
        # TODO: I don't think this is needed here since it should mirror temp lifetimes
        self._register_map.clear()

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
            print(f"* {line}")
        print()
        for idx, line in enumerate(ir):
            out.append(Comment(f"Running {line.op} operation..."))
            upcoming_ir = ir[idx:]
            if line.op == IROperation.SET_LITERAL:
                if not isinstance(line.arg1, int):
                    raise CodeGenerationError("Arg1 was None")
                if not isinstance(line.result, int):
                    raise CodeGenerationError("Result was not an int")

                register, commands = self.get_new_register(line.result, upcoming_ir)
                out.append(Comment("Register map"))
                for reg_idx, reg_val in self._register_map.items():
                    out.append(Comment(f"{reg_idx}: {', '.join(map(str, reg_val))}"))
                out.extend(commands)
                out.append(
                    LdcCommand(register, line.arg1, "Loading literal"),
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
                reg_1, commands = self.get_register(line.arg1, upcoming_ir)
                out.extend(commands)
                reg_2, commands = self.get_register(line.arg2, upcoming_ir)
                out.extend(commands)
                command_builder = {
                    IROperation.PLUS: AddCommand,
                    IROperation.MINUS: SubCommand,
                    IROperation.TIMES: MulCommand,
                    IROperation.DIVIDE: DivCommand,
                }[line.op]

                out_reg, commands = self.get_new_register(line.result, upcoming_ir)
                out.extend(commands)
                out.append(
                    command_builder(
                        out_reg,
                        reg_1,
                        reg_2,
                        "Adding the two value and put into return",
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
                reg_1, commands = self.get_register(line.arg1, upcoming_ir)
                out.extend(commands)
                reg_2, commands = self.get_register(line.arg2, upcoming_ir)
                out.extend(commands)
                out_reg, commands = self.get_new_register(line.result, upcoming_ir)
                out.extend(commands)
                out.extend(
                    [
                        SubCommand(
                            out_reg,
                            reg_1,
                            reg_2,
                        ),
                    ],
                )

                if line.op == IROperation.EQUALS:
                    out.append(
                        JeqCommand(
                            out_reg,
                            2,
                            REG_PC,
                        ),
                    )
                elif line.op == IROperation.LESS_THAN:
                    out.append(
                        JltCommand(
                            out_reg,
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
                reg_1, commands = self.get_register(line.arg1, upcoming_ir)
                out.extend(commands)
                out_reg, commands = self.get_new_register(line.result, upcoming_ir)
                out.extend(commands)
                utility_reg, commands = self.get_new_register(
                    None,
                    upcoming_ir,
                )
                out.extend(commands)
                negation_code = [
                    LdcCommand(
                        utility_reg,
                        2,
                        f"Performing {line.op} operation",
                    ),
                    MulCommand(
                        utility_reg,
                        reg_1,
                        utility_reg,
                    ),
                    SubCommand(
                        reg_1,
                        reg_1,
                        utility_reg,
                    ),
                ]
                if line.op == IROperation.NOT:
                    out.extend(
                        [
                            *negation_code,
                            LdcCommand(
                                utility_reg,
                                1,
                            ),
                            AddCommand(
                                out_reg,
                                reg_1,
                                utility_reg,
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
                                REG_ZERO,
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
                reg_1, commands = self.get_register(line.arg1, upcoming_ir)
                out.extend(commands)
                # FIXME: This code is really bad, and indicates underlying issues!!
                # FIXME: Very unsure abt this code working
                self._register_map[reg_1].append(line.result)
            elif line.op in [IROperation.LABEL]:
                if not isinstance(line.result, str):
                    raise TypeError("Expected result to be of type string")
                self._goto_mapping[line.result] = TMCommand.current_line_num
            elif line.op in [IROperation.IF_NOT, IROperation.IF]:
                if not isinstance(line.arg1, int):
                    raise TypeError("Expected arg1 to be of type int")
                reg, commands = self.get_register(line.arg1, upcoming_ir)
                out.extend(commands)
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
                out.append(Comment(f"Adding {line.result} into params"))
                self._current_params.append(line.result)
            elif line.op in [IROperation.CALL]:
                if not isinstance(line.result, int):
                    raise TypeError("Expected call result to be an int")
                if not isinstance(line.arg1, str):
                    raise TypeError("Expected call arg to be a function name")
                if not isinstance(line.arg2, int):
                    raise TypeError("Expected call arg 2 to be number of params")

                out.append(Comment("Early grab register for fn return value"))
                out_reg, commands = self.get_new_register(line.result, upcoming_ir)
                out.extend(commands)

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
                    LdCommand(
                        out_reg,
                        0,
                        REG_TOP,
                        "Pulling the return value into the right register",
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
                        REG_ZERO,
                        "Unconditional jump",
                        source_line,
                    ),
                )
            elif line.op == IROperation.IF:
                if not isinstance(condition_reg, Register):
                    raise TypeError("Expected condition register to be an int")
                if not isinstance(line.arg1, int):
                    raise TypeError("Expected arg1 to be of type int")
                out.append(
                    JneCommand(
                        condition_reg,
                        destination_line,
                        REG_ZERO,
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
                        REG_ZERO,
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
