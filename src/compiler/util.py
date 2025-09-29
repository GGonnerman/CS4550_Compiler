import textwrap


def insert_newlines(strs: str, every: int = 80):
    return textwrap.fill(strs, every)
