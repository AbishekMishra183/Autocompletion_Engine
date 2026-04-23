
from trie_node import TrieNode


class Trie:
   

    def __init__(self) -> None:
        
        self.root: TrieNode = TrieNode()                                                          
    
    def insert(self, phrase: str) -> None:
        
        node: TrieNode = self.root

        for character in phrase.lower():          
            if character not in node.children:
                node.children[character] = TrieNode()   
            node = node.children[character]       
        node.is_end_of_phrase = True
        node.original_phrase  = phrase                                                  
 

    def search_by_prefix(self, prefix: str) -> list[str]:
        
        node: TrieNode = self.root

        
        for character in prefix.lower():
            if character not in node.children:
                return []           
            node = node.children[character]
        results: list[str] = []
        self._depth_first_collect(node, results)
        return results                                          
    
    def _depth_first_collect(self, node: TrieNode, results: list[str]) -> None:
       
        if node.is_end_of_phrase:
            results.append(node.original_phrase)   

        for child_node in node.children.values():
            self._depth_first_collect(child_node, results)
