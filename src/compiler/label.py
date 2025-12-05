from random import choice


class Label:
    # Require set for alphabet to avoid duplicate elements
    def __init__(self, alphabet: set[str] | None = None, length: int = 3):
        self._generated_labels: set[str] = set()
        self._length: int = length
        self._alphabet: list[str] = (
            list[str](alphabet)
            if alphabet
            else [
                "alfa",
                "bravo",
                "charlie",
                "delta",
                "echo",
                "foxtrot",
                "golf",
                "hotel",
                "india",
                "juliett",
                "kilo",
                "lima",
                "mike",
                "november",
                "oscar",
                "papa",
                "quebec",
                "romeo",
                "sierra",
                "tango",
                "uniform",
                "victor",
                "whiskey",
                "xray",
                "yankee",
                "zulu",
            ]
        )

    def _get_label(self) -> str:
        return "-".join([choice(self._alphabet) for _ in range(self._length)])  # noqa: S311

    def get_label(self) -> str:
        while True:
            if self._generated_labels == len(self._alphabet) ** self._length:
                raise Exception("All possible labels have been generated")  # noqa: TRY002
            label = self._get_label()
            if label not in self._generated_labels:
                self._generated_labels.add(label)
                return label
