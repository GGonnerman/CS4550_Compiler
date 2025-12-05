import subprocess
from dataclasses import dataclass
from pathlib import Path

base_path = Path(__file__).parent
tm_cli_path = base_path / "tm-cli-go"
programs_path = base_path / "programs"

# *   $ klein divide 7 12 2                                         *
# *   5                                                             *
# *   8                                                             *
# *   4                                                             *


@dataclass
class FileTestParams:
    name: str
    arguments: list[str]
    output: list[str]


def run_file(obj: FileTestParams):
    file_path = programs_path / obj.name
    kleinc_path = base_path / ".." / "kleinc"

    res = subprocess.run(
        [kleinc_path, file_path],
        check=False,
        stdout=subprocess.PIPE,
    ).stdout.decode(
        "utf-8",
    )

    res = subprocess.run(
        [tm_cli_path, file_path, *obj.arguments],
        check=False,
        stdout=subprocess.PIPE,
    ).stdout.decode(
        "utf-8",
    )

    expected_result = [f"OUT instruction prints: {v}" for v in obj.output]
    expected_result.append(
        "HALT: 0,0,0",
    )
    assert res.splitlines()[:-1] == expected_result, (
        f"Results for {obj.name} should match"
    )


def test_divide():
    run_file(
        FileTestParams(
            "divide",
            ["7", "12", "2"],
            ["5", "8", "4"],
        ),
    )
    run_file(
        FileTestParams(
            "divide",
            ["7", "12", "4"],
            ["5", "8", "3", "3", "4"],
        ),
    )


def test_sum_factors():
    run_file(
        FileTestParams(
            "sum-factors",
            ["38"],
            ["1", "2", "19", "16"],
        ),
    )


def test_sieve():
    run_file(
        FileTestParams(
            "sieve",
            ["7"],
            ["2", "3", "0", "5", "0", "7"],
        ),
    )
