import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest

base_path = Path(__file__).parent
cache_path = base_path / "cache"
tm_cli_path = base_path / "tm_cli_go"

# Make sure our cache exists
cache_path.mkdir(parents=True, exist_ok=True)


@dataclass
class FileTestParams:
    name: str
    arguments: list[str]
    output: list[str]


def create_and_run_program(
    contents: str,
    arguments: list[str],
    output: list[str],
):
    temp_filename = "temp"
    with open(cache_path / f"{temp_filename}.kln", "w+") as outfile:
        _ = outfile.write(contents)
    obj = FileTestParams(
        temp_filename,
        arguments,
        output,
    )
    run_file(obj, cache_path)


def run_program(obj: FileTestParams):
    programs_path = base_path / "programs"
    run_file(obj, programs_path)


def run_file(obj: FileTestParams, program_path: Path):
    file_path = program_path / obj.name
    kleinc_path = base_path / ".." / "kleinc"

    generated_tm_file = program_path / f"{obj.name}.tm"

    # We never want to be testing 'stale' tm files if things fail to build
    generated_tm_file.unlink(missing_ok=True)

    print(f"Runnign with path: {file_path}...")
    res = subprocess.run(  # noqa: S603
        [kleinc_path, file_path],
        check=False,
        stdout=subprocess.PIPE,
    ).stdout.decode(
        "utf-8",
    )

    if res:
        raise Exception(f"Failed to compile klein program\n{res}")  # noqa: TRY002

    res = subprocess.run(  # noqa: S603
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


def test_print_one():
    run_program(
        FileTestParams(
            "print-one",
            [],
            ["1", "1"],
        ),
    )


def test_divide():
    run_program(
        FileTestParams(
            "divide",
            ["7", "12", "2"],
            ["5", "8", "4"],
        ),
    )
    run_program(
        FileTestParams(
            "divide",
            ["7", "12", "4"],
            ["5", "8", "3", "3", "4"],
        ),
    )


def test_sum_factors():
    run_program(
        FileTestParams(
            "sum-factors",
            ["38"],
            ["1", "2", "19", "16"],
        ),
    )


def test_factors():
    run_program(
        FileTestParams(
            "factors",
            ["18"],
            ["1", "2", "3", "6", "9", "18"],
        ),
    )


def test_euclid():
    run_program(
        FileTestParams(
            "euclid",
            ["138", "624"],
            ["6"],
        ),
    )
    run_program(
        FileTestParams(
            "euclid",
            ["624", "624"],
            ["624"],
        ),
    )


def test_is_excellent():
    run_program(
        FileTestParams(
            "is-excellent",
            [
                "140400",
            ],
            ["1"],
        ),
    )


@pytest.mark.xfail
def test_generate_excellent():
    run_program(
        FileTestParams(
            "generate-excellent",
            ["6"],
            [
                "140400",
                "190476",
                "216513",
                "300625",
                "334668",
                "416768",
                "484848",
                "530901",
            ],
        ),
    )


def test_sieve():
    run_program(
        FileTestParams(
            "sieve",
            ["7"],
            ["2", "3", "0", "5", "0", "7", "1"],
        ),
    )


def test_sieve_no_cli():
    run_program(
        FileTestParams(
            "sieve-no-cli",
            ["7"],
            [
                "2",
                "3",
                "0",
                "5",
                "0",
                "7",
                "0",
                "0",
                "0",
                "11",
                "0",
                "13",
                "0",
                "0",
                "0",
                "17",
                "0",
                "19",
                "0",
                "0",
                "0",
                "23",
                "0",
                "0",
                "0",
                "0",
                "0",
                "29",
                "0",
                "31",
                "0",
                "0",
                "0",
                "0",
                "0",
                "37",
                "0",
                "0",
                "0",
                "1",
            ],
        ),
    )


def test_farey():
    run_program(
        FileTestParams(
            "farey",
            ["127", "1000", "74"],
            ["8", "63"],
        ),
    )
    run_program(
        FileTestParams(
            "farey",
            ["367879", "1000000", "100"],
            ["32", "87"],
        ),
    )


def test_is_special():
    run_program(
        FileTestParams(
            "is-special",
            ["16"],
            ["1"],
        ),
    )
    run_program(
        FileTestParams(
            "is-special",
            ["17"],
            ["0"],
        ),
    )


def test_divisible_by_seven():
    run_program(
        FileTestParams(
            "divisible-by-seven",
            ["42"],
            ["1"],
        ),
    )
    run_program(
        FileTestParams(
            "divisible-by-seven",
            ["45"],
            ["0"],
        ),
    )


def test_is_cantor():
    for cantor_name in [
        "is-cantor-number-bool",
        "is-cantor-number-fast",
        "is-cantor-number-v4",
        "is-cantor-number",
    ]:
        run_program(
            FileTestParams(
                cantor_name,
                ["9081"],
                ["1"],
            ),
        )
        run_program(
            FileTestParams(
                cantor_name,
                ["9083"],
                ["0"],
            ),
        )


def test_horner():
    run_program(
        FileTestParams(
            "horner-hardcoded",
            ["21"],
            ["7548"],
        ),
    )


def test_palindrome():
    run_program(
        FileTestParams(
            "palindrome",
            ["12344321"],
            ["12344321", "12344321", "1"],
        ),
    )
    run_program(
        FileTestParams(
            "palindrome",
            ["1234321"],
            ["1234321", "1234321", "1"],
        ),
    )
    run_program(
        FileTestParams(
            "palindrome",
            ["1234320"],
            ["1234320", "234321", "0"],
        ),
    )


# Is the sqrt function supposed to be this far off (due to integer rounding) or
# is there something else wrong here?
def test_sqrt_newton():
    run_program(
        FileTestParams(
            "sqrt-newton",
            ["100", "10000"],
            ["26"],
        ),
    )


def test_and_shortcircuit():
    crash = """
    function crash(): boolean
        crash()
    """
    create_and_run_program(
        """
    function main(): boolean
        false and crash()
    """
        + crash,
        [],
        ["0"],
    )
    create_and_run_program(
        """
    function main(): boolean
        false and true
    """,
        [],
        ["0"],
    )
    create_and_run_program(
        """
    function main(): boolean
        true and false
    """,
        [],
        ["0"],
    )
    create_and_run_program(
        """
    function main(): boolean
        true and true
    """,
        [],
        ["1"],
    )


def test_or_shortcircuit():
    crash = """
    function crash(): boolean
        crash()
    """
    create_and_run_program(
        """
    function main(): boolean
        false or false
    """,
        [],
        ["0"],
    )
    create_and_run_program(
        """
    function main(): boolean
        false or true
    """,
        [],
        ["1"],
    )
    create_and_run_program(
        """
    function main(): boolean
        true or crash()
    """
        + crash,
        [],
        ["1"],
    )


def test_arg_count():
    opts = [
        ("a", "123"),
        ("b", "345"),
        ("c", "456"),
        ("d", "567"),
        ("e", "678"),
        ("f", "789"),
        ("g", "890"),
    ]
    for i in range(1, len(opts)):
        params = " : integer, ".join(opt[0] for opt in opts[:i]) + ": integer"
        args = [opt[1] for opt in opts[:i]]
        prints = "\n".join(f"print({opt[0]})" for opt in opts[:i])
        create_and_run_program(
            f"""
        function main({params}): boolean
            {prints}
            false
        """,
            args,
            [*args, "0"],
        )


def test_arg_order():
    create_and_run_program(
        """
    function main(a: integer, b: integer, c: integer): boolean
        print(a)
        print(b)
        print(c)
        false
    """,
        ["123", "123456789", "789"],
        ["123", "123456789", "789", "0"],
    )
    create_and_run_program(
        """
    function main(a: integer, b: integer, c: integer): boolean
        out(a, b, c)

    function out(d: integer, e: integer, f: integer): boolean
        print(d)
        print(e)
        print(f)
        false
    """,
        ["123", "123456789", "789"],
        ["123", "123456789", "789", "0"],
    )


def test_recursive():
    create_and_run_program(
        """
    function main(max: integer): integer
        sum_to(max)

    function sum_to(max: integer): integer
        if max < 1 then
            max
        else
            max + sum_to(max - 1)
    """,
        ["10"],
        ["55"],
    )


@dataclass(frozen=True)
class Option:
    arguments: list[str]
    output: list[str]


def test_equality():
    options = [
        Option(
            ["10", "9"],
            ["0"],
        ),
        Option(
            ["10", "10"],
            ["1"],
        ),
        Option(
            ["10", "11"],
            ["0"],
        ),
    ]
    for option in options:
        create_and_run_program(
            """
        function main(a: integer, b: integer): boolean
            a = b
        """,
            option.arguments,
            option.output,
        )


def test_less_than():
    options = [
        Option(
            ["10", "9"],
            ["0"],
        ),
        Option(
            ["10", "10"],
            ["0"],
        ),
        Option(
            ["10", "11"],
            ["1"],
        ),
    ]
    for option in options:
        create_and_run_program(
            """
        function main(a: integer, b: integer): boolean
            a < b
        """,
            option.arguments,
            option.output,
        )


def test_mod():
    create_and_run_program(
        """
    function main( m: integer, n : integer ) : integer
        m - m/n * n
    """,
        ["13", "8"],
        ["5"],
    )
