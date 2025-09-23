import pytest

from compiler.position import Position


@pytest.fixture
def position() -> Position:
    return Position()


class TestPosition:
    def test_init(self, position: Position):
        assert position.get_position() == 0, "Position should start at 0"
        assert position.get_absolute_position() == 0, (
            "Absolute position should start at 0"
        )
        assert position.get_line_number() == 0, "Line number should start at 0"

    def test_increment(self, position: Position):
        position += 1
        assert position.get_position() == 1, "Position should become 1 after increment"
        assert position.get_absolute_position() == 1, (
            "Absolute position should become 1 after increment"
        )
        assert position.get_line_number() == 0, (
            "Line number shouldn't change when incrementing"
        )

        position += 3
        assert position.get_position() == 4, (
            "Position should allow incrementing 3 times"
        )
        assert position.get_absolute_position() == 4, (
            "Absolute position should allow incrementing 3 times"
        )

    def test_add_newline(self, position: Position):
        position.add_newline()
        assert position.get_line_number() == 1, (
            "Line number should increase when adding newline"
        )

        position += 1
        position.add_newline()
        assert position.get_absolute_position() == 1, (
            "Absolute position should not be modified by adding newline"
        )
        assert position.get_position() == 0, (
            "Position should be reset when adding newline"
        )

    def test_equality(self, position: Position):
        alt: Position = Position()
        assert position == alt, "2 empty positions should be equal"
        position += 1
        assert position != alt, (
            "Positions should not be equal when absolute position differ"
        )
        alt += 1
        assert position == alt, "Positions should be equal after both incrementing"
