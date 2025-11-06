from typing import ClassVar

from compiler.ast_nodes import Program
from compiler.symbol_table import SymbolTable


class CodeGenerator:
    def __init__(self, ast: Program, symbol_table: SymbolTable):
        self._ast: Program = ast
        self._symbol_table: SymbolTable = symbol_table
        self._code: list[TMCommand] = []

    def generate(self):
        self._code = [
            InCommand(0, 1, "in command"),
            OutCommand(1, 1, "out command"),
            AddCommand(2, 1, 1, 2, "add command"),
            SubCommand(3, 1, 1, 2, "sub command"),
            MulCommand(4, 1, 1, 2, "mul command"),
            DivCommand(5, 1, 1, 2, "div command"),
            HaltCommand(6, "halt command"),
            LdcCommand(7, 1, 2, "load command"),
            LdaCommand(8, 1, 2, 3, "load addr command"),
            LdCommand(9, 1, 2, 3, "load data command"),
            StCommand(10, 1, 2, 3, "st command"),
            JeqCommand(11, 1, 2, 3, "jump equal"),
            JneCommand(12, 1, 2, 3, "jump not equal"),
            JltCommand(13, 1, 2, 3, "jump less than"),
            JleCommand(14, 1, 2, 3, "jump less or equal"),
            JgtCommand(15, 1, 2, 3, "jump greater than"),
            JgeCommand(16, 1, 2, 3, "jump greater or equal"),
        ]
        for line in self._code:
            line.print()


class TMCommand:
    max_line_size: ClassVar[int] = 0
    max_command_size: ClassVar[int] = 0
    max_register_section: ClassVar[int] = 0
    seen_line_nums: ClassVar[set[int]] = set()

    def __init__(
        self,
        line_num: int,
        command: str,
        register_section: str,
        comment: str | None,
    ):
        if line_num in TMCommand.seen_line_nums:
            raise IndexError(f"Duplicated line number {line_num}")
        self.line_num: int = line_num
        self.command: str = command
        self.register_section: str = register_section
        self.comment: str | None = comment

        TMCommand.max_line_size = max(TMCommand.max_line_size, len(str(self.line_num)))
        TMCommand.max_command_size = max(TMCommand.max_command_size, len(self.command))
        TMCommand.max_register_section = max(
            TMCommand.max_register_section,
            len(self.register_section),
        )

    def print(
        self,
    ):
        line_num_formatted = str(self.line_num).rjust(TMCommand.max_line_size)
        command_formatted = str(self.command).ljust(TMCommand.max_command_size)
        register_section_formatted = str(self.register_section).ljust(
            TMCommand.max_register_section,
        )
        comment_formatted = f" ; {self.comment}" if self.comment else ""
        print(
            f"{line_num_formatted}: {command_formatted} {register_section_formatted}{comment_formatted}",
        )


class ROCommand(TMCommand):
    def __init__(
        self,
        line_num: int,
        command: str,
        r1: int,
        r2: int,
        r3: int,
        comment: str | None = None,
    ):
        super().__init__(
            line_num,
            command,
            f"{r1},{r2},{r3}",
            comment,
        )


class InCommand(ROCommand):
    def __init__(
        self,
        line_num: int,
        write_to_register: int,
        comment: str | None = None,
    ):
        super().__init__(line_num, "IN", write_to_register, 0, 0, comment)


class OutCommand(ROCommand):
    def __init__(
        self,
        line_num: int,
        read_from_register: int,
        comment: str | None = None,
    ):
        super().__init__(line_num, "OUT", read_from_register, 0, 0, comment)


class AddCommand(ROCommand):
    def __init__(
        self,
        line_num: int,
        destination_register: int,
        left_side_register: int,
        right_side_register: int,
        comment: str | None = None,
    ):
        super().__init__(
            line_num,
            "ADD",
            destination_register,
            left_side_register,
            right_side_register,
            comment,
        )


class SubCommand(ROCommand):
    def __init__(
        self,
        line_num: int,
        destination_register: int,
        left_side_register: int,
        right_side_register: int,
        comment: str | None = None,
    ):
        super().__init__(
            line_num,
            "SUB",
            destination_register,
            left_side_register,
            right_side_register,
            comment,
        )


class MulCommand(ROCommand):
    def __init__(
        self,
        line_num: int,
        destination_register: int,
        left_side_register: int,
        right_side_register: int,
        comment: str | None = None,
    ):
        super().__init__(
            line_num,
            "MUL",
            destination_register,
            left_side_register,
            right_side_register,
            comment,
        )


class DivCommand(ROCommand):
    def __init__(
        self,
        line_num: int,
        destination_register: int,
        left_side_register: int,
        right_side_register: int,
        comment: str | None = None,
    ):
        super().__init__(
            line_num,
            "DIV",
            destination_register,
            left_side_register,
            right_side_register,
            comment,
        )


class HaltCommand(ROCommand):
    def __init__(self, line_num: int, comment: str | None = None):
        super().__init__(line_num, "HALT", 0, 0, 0, comment)


class RMCommand(TMCommand):
    def __init__(
        self,
        line_num: int,
        command: str,
        r1: int,
        offset: int,
        r2: int,
        comment: str | None = None,
    ):
        super().__init__(
            line_num,
            command,
            f"{r1},{offset}({r2})",
            comment,
        )


class LdcCommand(RMCommand):
    def __init__(
        self,
        line_num: int,
        load_into: int,
        constant_value: int,
        comment: str | None = None,
    ):
        super().__init__(
            line_num,
            "LDC",
            load_into,
            constant_value,
            0,
            comment,
        )


class LdaCommand(RMCommand):
    def __init__(
        self,
        line_num: int,
        load_into: int,
        offset: int,
        address: int,
        comment: str | None = None,
    ):
        super().__init__(
            line_num,
            "LDA",
            load_into,
            offset,
            address,
            comment,
        )


class LdCommand(RMCommand):
    def __init__(
        self,
        line_num: int,
        load_into: int,
        offset: int,
        address: int,
        comment: str | None = None,
    ):
        super().__init__(
            line_num,
            "LD",
            load_into,
            offset,
            address,
            comment,
        )


class StCommand(RMCommand):
    def __init__(
        self,
        line_num: int,
        load_from: int,
        offset: int,
        into_address: int,
        comment: str | None = None,
    ):
        super().__init__(
            line_num,
            "ST",
            load_from,
            offset,
            into_address,
            comment,
        )


class JeqCommand(RMCommand):
    def __init__(
        self,
        line_num: int,
        test: int,
        offset: int,
        goto_address: int,
        comment: str | None = None,
    ):
        super().__init__(
            line_num,
            "JEQ",
            test,
            offset,
            goto_address,
            comment,
        )


class JneCommand(RMCommand):
    def __init__(
        self,
        line_num: int,
        test: int,
        offset: int,
        goto_address: int,
        comment: str | None = None,
    ):
        super().__init__(
            line_num,
            "JNE",
            test,
            offset,
            goto_address,
            comment,
        )


class JltCommand(RMCommand):
    def __init__(
        self,
        line_num: int,
        test: int,
        offset: int,
        goto_address: int,
        comment: str | None = None,
    ):
        super().__init__(
            line_num,
            "JLT",
            test,
            offset,
            goto_address,
            comment,
        )


class JleCommand(RMCommand):
    def __init__(
        self,
        line_num: int,
        test: int,
        offset: int,
        goto_address: int,
        comment: str | None = None,
    ):
        super().__init__(
            line_num,
            "JLE",
            test,
            offset,
            goto_address,
            comment,
        )


class JgtCommand(RMCommand):
    def __init__(
        self,
        line_num: int,
        test: int,
        offset: int,
        goto_address: int,
        comment: str | None = None,
    ):
        super().__init__(
            line_num,
            "JGT",
            test,
            offset,
            goto_address,
            comment,
        )


class JgeCommand(RMCommand):
    def __init__(
        self,
        line_num: int,
        test: int,
        offset: int,
        goto_address: int,
        comment: str | None = None,
    ):
        super().__init__(
            line_num,
            "JGE",
            test,
            offset,
            goto_address,
            comment,
        )
