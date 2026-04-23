

from __future__ import annotations
from dataclasses import dataclass, field


# ────────────────────────────────────────────────────────────────────────────
# DATA CLASS — PhraseRecord
# ────────────────────────────────────────────────────────────────────────────

@dataclass
class PhraseRecord:
   
    phrase: str
    count:  int = field(default=1)

    def __repr__(self) -> str:
        return f"PhraseRecord(phrase={self.phrase!r}, count={self.count})"


# ────────────────────────────────────────────────────────────────────────────
# CATALOGUE
# ────────────────────────────────────────────────────────────────────────────

class Catalogue:
   

    def __init__(self) -> None:
        
        self._store: dict[str, PhraseRecord] = {}

 
    def add(self, phrase: str, count: int = 1) -> None:
       
        key = phrase.lower().strip()
        self._store[key] = PhraseRecord(phrase=phrase.strip(), count=count)

    # ------------------------------------------------------------------ #
    #  EXISTS                                                              #
    # ------------------------------------------------------------------ #
    def exists(self, phrase: str) -> bool:
       
        return phrase.lower().strip() in self._store

    # ------------------------------------------------------------------ #
    #  GET COUNT                                                           #
    # ------------------------------------------------------------------ #
    def get_count(self, phrase: str) -> int:
       
        record = self._store.get(phrase.lower().strip())
        return record.count if record else 0

    # ------------------------------------------------------------------ #
    #  INCREMENT COUNT  (Rule 3)                                           #
    # ------------------------------------------------------------------ #
    def increment_count(self, phrase: str) -> int:
       
        key = phrase.lower().strip()
        if key in self._store:
            self._store[key].count += 1
            return self._store[key].count
        return 0

    # ------------------------------------------------------------------ #
    #  GET ORIGINAL PHRASE                                                 #
    # ------------------------------------------------------------------ #
    def get_display_phrase(self, phrase: str) -> str:
        
        record = self._store.get(phrase.lower().strip())
        return record.phrase if record else phrase

    # ------------------------------------------------------------------ #
    #  ALL SORTED  (for display / debugging)                              #
    # ------------------------------------------------------------------ #
    def all_phrases_sorted(self) -> list[PhraseRecord]:
        
        return sorted(
            self._store.values(),
            key=lambda record: (-record.count, record.phrase.lower())
        )

    def __len__(self) -> int:
        return len(self._store)

    def __repr__(self) -> str:
        return f"Catalogue(size={len(self._store)})"
