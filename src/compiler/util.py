import textwrap


def insert_newlines(strs: str, every: int = 80):
    # Code Borrowed from: https://stackoverflow.com/a/26538082
    return "\n".join(
        [
            "\n".join(
                textwrap.wrap(
                    line,
                    every,
                    break_long_words=False,
                    replace_whitespace=False,
                ),
            )
            for line in strs.splitlines()
            if line.strip() != ""
        ],
    )
