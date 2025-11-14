from abc import ABC, abstractmethod
from typing import ClassVar


class TMLine(ABC):
    @abstractmethod
    def print(self):
        raise NotImplementedError("Printing must be implemented by subclass")


class Comment(TMLine):
    def __init__(self, comment: str):
        self._comment: str = comment

    def print(self):
        print(f"* {self._comment}")


class TMCommand(TMLine):
    max_line_size: ClassVar[int] = 0
    max_command_size: ClassVar[int] = 0
    max_register_section: ClassVar[int] = 0
    seen_line_nums: ClassVar[set[int]] = set()
    current_line_num: int = 0

    def __init__(
        self,
        command: str,
        register_section: str,
        comment: str | None = None,
        line_num: int | None = None,
    ):
        if line_num in TMCommand.seen_line_nums:
            raise IndexError(f"Duplicated line number {line_num}")
        self.line_num: int = line_num or TMCommand.current_line_num
        self.command: str = command
        self.register_section: str = register_section
        self.comment: str | None = comment

        TMCommand.current_line_num += 1
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
    def __init__(  # noqa: PLR0913
        self,
        command: str,
        r1: int,
        r2: int,
        r3: int,
        comment: str | None = None,
        line_num: int | None = None,
    ):
        super().__init__(
            command,
            f"{r1},{r2},{r3}",
            comment,
            line_num,
        )


class InCommand(ROCommand):
    def __init__(
        self,
        write_to_register: int,
        comment: str | None = None,
        line_num: int | None = None,
    ):
        super().__init__("IN", write_to_register, 0, 0, comment, line_num)


class OutCommand(ROCommand):
    def __init__(
        self,
        read_from_register: int,
        comment: str | None = None,
        line_num: int | None = None,
    ):
        super().__init__("OUT", read_from_register, 0, 0, comment, line_num)


class AddCommand(ROCommand):
    def __init__(
        self,
        destination_register: int,
        left_side_register: int,
        right_side_register: int,
        comment: str | None = None,
        line_num: int | None = None,
    ):
        super().__init__(
            "ADD",
            destination_register,
            left_side_register,
            right_side_register,
            comment,
            line_num,
        )


class SubCommand(ROCommand):
    def __init__(
        self,
        destination_register: int,
        left_side_register: int,
        right_side_register: int,
        comment: str | None = None,
        line_num: int | None = None,
    ):
        super().__init__(
            "SUB",
            destination_register,
            left_side_register,
            right_side_register,
            comment,
            line_num,
        )


class MulCommand(ROCommand):
    def __init__(
        self,
        destination_register: int,
        left_side_register: int,
        right_side_register: int,
        comment: str | None = None,
        line_num: int | None = None,
    ):
        super().__init__(
            "MUL",
            destination_register,
            left_side_register,
            right_side_register,
            comment,
            line_num,
        )


class DivCommand(ROCommand):
    def __init__(
        self,
        destination_register: int,
        left_side_register: int,
        right_side_register: int,
        comment: str | None = None,
        line_num: int | None = None,
    ):
        super().__init__(
            "DIV",
            destination_register,
            left_side_register,
            right_side_register,
            comment,
            line_num,
        )


class HaltCommand(ROCommand):
    def __init__(self, comment: str | None = None, line_num: int | None = None):
        super().__init__("HALT", 0, 0, 0, comment, line_num)


class RMCommand(TMCommand):
    def __init__(  # noqa: PLR0913
        self,
        command: str,
        r1: int,
        offset: int,
        r2: int,
        comment: str | None = None,
        line_num: int | None = None,
    ):
        super().__init__(
            command,
            f"{r1},{offset}({r2})",
            comment,
            line_num,
        )


class LdcCommand(RMCommand):
    def __init__(
        self,
        load_into: int,
        constant_value: int,
        comment: str | None = None,
        line_num: int | None = None,
    ):
        super().__init__(
            "LDC",
            load_into,
            constant_value,
            0,
            comment,
            line_num,
        )


class LdaCommand(RMCommand):
    def __init__(
        self,
        load_into: int,
        offset: int,
        address: int,
        comment: str | None = None,
        line_num: int | None = None,
    ):
        super().__init__(
            "LDA",
            load_into,
            offset,
            address,
            comment,
            line_num,
        )


class LdCommand(RMCommand):
    def __init__(
        self,
        load_into: int,
        offset: int,
        address: int,
        comment: str | None = None,
        line_num: int | None = None,
    ):
        super().__init__(
            "LD",
            load_into,
            offset,
            address,
            comment,
            line_num,
        )


class StCommand(RMCommand):
    def __init__(
        self,
        load_from: int,
        offset: int,
        into_address: int,
        comment: str | None = None,
        line_num: int | None = None,
    ):
        super().__init__(
            "ST",
            load_from,
            offset,
            into_address,
            comment,
            line_num,
        )


class JeqCommand(RMCommand):
    def __init__(
        self,
        test: int,
        offset: int,
        goto_address: int,
        comment: str | None = None,
        line_num: int | None = None,
    ):
        super().__init__(
            "JEQ",
            test,
            offset,
            goto_address,
            comment,
            line_num,
        )


class JneCommand(RMCommand):
    def __init__(
        self,
        test: int,
        offset: int,
        goto_address: int,
        comment: str | None = None,
        line_num: int | None = None,
    ):
        super().__init__(
            "JNE",
            test,
            offset,
            goto_address,
            comment,
            line_num,
        )


class JltCommand(RMCommand):
    def __init__(
        self,
        test: int,
        offset: int,
        goto_address: int,
        comment: str | None = None,
        line_num: int | None = None,
    ):
        super().__init__(
            "JLT",
            test,
            offset,
            goto_address,
            comment,
            line_num,
        )


class JleCommand(RMCommand):
    def __init__(
        self,
        test: int,
        offset: int,
        goto_address: int,
        comment: str | None = None,
        line_num: int | None = None,
    ):
        super().__init__(
            "JLE",
            test,
            offset,
            goto_address,
            comment,
            line_num,
        )


class JgtCommand(RMCommand):
    def __init__(
        self,
        test: int,
        offset: int,
        goto_address: int,
        comment: str | None = None,
        line_num: int | None = None,
    ):
        super().__init__(
            "JGT",
            test,
            offset,
            goto_address,
            comment,
            line_num,
        )


class JgeCommand(RMCommand):
    def __init__(
        self,
        test: int,
        offset: int,
        goto_address: int,
        comment: str | None = None,
        line_num: int | None = None,
    ):
        super().__init__(
            "JGE",
            test,
            offset,
            goto_address,
            comment,
            line_num,
        )
