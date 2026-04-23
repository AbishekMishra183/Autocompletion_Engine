
from __future__ import annotations

import heapq
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from trie      import Trie
from catalogue import Catalogue, PhraseRecord

PRELOADED_PHRASES: list[tuple[str, int]] = [
    # Phrase                                  Count
    ("artificial intelligence trends",          980),
    ("artificial neural networks",              420),
    ("algorithm time complexity",               310),
    ("apple macbook pro review",                275),
    ("autocomplete engine design",              190),
    ("best python libraries 2024",              870),
    ("binary search tree tutorial",             340),
    ("blockchain technology overview",          290),
    ("best machine learning courses",           760),
    ("cloud computing services",                650),
    ("css grid layout tutorial",                480),
    ("competitive programming tips",            220),
    ("data structures and algorithms",         1200),
    ("deep learning with tensorflow",           540),
    ("docker container tutorial",               410),
    ("dynamic programming problems",            330),
    ("git branching strategies",                560),
    ("graph traversal algorithms",              300),
    ("how to learn javascript",                 730),
    ("hash map vs hash set",                    195),
    ("javascript async await",                  690),
    ("java spring boot tutorial",               385),
    ("kubernetes deployment guide",             450),
    ("linear regression explained",             260),
    ("machine learning roadmap",                810),
    ("microservices architecture",              500),
    ("natural language processing",             620),
    ("nodejs express rest api",                 470),
    ("object oriented programming",             380),
    ("open source contribution guide",          215),
    ("python list comprehension",               710),
    ("prefix tree trie implementation",         175),
    ("react hooks tutorial",                    660),
    ("redis caching strategies",                290),
    ("sql joins explained",                     590),
    ("system design interview",                 920),
    ("sorting algorithms comparison",           340),
    ("typescript generics guide",               255),
    ("trie vs hash map performance",            140),
    ("vector databases explained",              310),
]

TOP_N = 5   


class AutocompleteEngine:
    

    def __init__(self) -> None:
        self._trie      = Trie()
        self._catalogue = Catalogue()
        self._load_initial_phrases()


    def _load_initial_phrases(self) -> None:
     
        for phrase, count in PRELOADED_PHRASES:
            self._catalogue.add(phrase, count)
            self._trie.insert(phrase)

    # ------------------------------------------------------------------ #
    #  RULE 1 + 2: GET SUGGESTIONS  (the core algorithm)                  #
    # ------------------------------------------------------------------ #
    def get_suggestions(self, prefix: str) -> list[tuple[str, int]]:
       
        prefix = prefix.strip()
        if not prefix:
            return []

        # ── Phase 1: Trie lookup ──────────────────────────────────────
        raw_matches: list[str] = self._trie.search_by_prefix(prefix)
       

        if not raw_matches:
            return []

        

        min_heap: list[tuple[int, str, str]] = []

        for phrase in raw_matches:
            count         = self._catalogue.get_count(phrase)
            display       = self._catalogue.get_display_phrase(phrase)
            heap_item     = (-count, phrase.lower(), display)

            if len(min_heap) < TOP_N:
                heapq.heappush(min_heap, heap_item)
            else:
                
                if heap_item < min_heap[0]:
                    heapq.heapreplace(min_heap, heap_item)
               
        results = sorted(
            min_heap,
            key=lambda item: (item[0], item[1])  
        )
        

        return [(item[2], -item[0]) for item in results]
      

    # ------------------------------------------------------------------ #
    #  RULE 3: SELECT SUGGESTION → INCREMENT COUNT                         #
    # ------------------------------------------------------------------ #
    def select_suggestion(self, phrase: str) -> int:
        
        return self._catalogue.increment_count(phrase)

    # ------------------------------------------------------------------ #
    #  RULE 4: SUBMIT UNKNOWN PHRASE → ADD WITH COUNT = 1                  #
    # ------------------------------------------------------------------ #
    def submit_phrase(self, phrase: str) -> tuple[str, int]:
       
        phrase = phrase.strip()

        if not self._catalogue.exists(phrase):
           
            self._catalogue.add(phrase, count=1)  # O(1)
            self._trie.insert(phrase)              # O(m)
            return ("added", 1)
        else:
           
            new_count = self._catalogue.increment_count(phrase)  # O(1)
            return ("incremented", new_count)

    # ------------------------------------------------------------------ #
    #  UTILITY: TOP PHRASES (for catalogue display)                        #
    # ------------------------------------------------------------------ #
    def get_top_phrases(self, n: int = 10) -> list[PhraseRecord]:
       
        return self._catalogue.all_phrases_sorted()[:n]

    @property
    def catalogue_size(self) -> int:
        """Total number of phrases currently in the catalogue."""
        return len(self._catalogue)
