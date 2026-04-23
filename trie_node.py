


class TrieNode:
    

    __slots__ = ("children", "is_end_of_phrase", "original_phrase")

    def __init__(self) -> None:
        self.children: dict[str, "TrieNode"] = {}
        self.is_end_of_phrase: bool = False
        self.original_phrase: str | None = None

    def __repr__(self) -> str:
        return (
            f"TrieNode("
            f"children={list(self.children.keys())}, "
            f"is_end={self.is_end_of_phrase}, "
            f"phrase={self.original_phrase!r})"
        )
