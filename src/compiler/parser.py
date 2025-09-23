from compiler.scanner import Scanner


class Parser:
    def __init__(self, scanner: Scanner):
        self._scanner: Scanner = scanner

    def parse(self) -> bool:
        return False
