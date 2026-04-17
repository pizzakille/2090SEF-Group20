class TrieNode:
    def __init__(self):
        self.children = {} # Store the child node
        self.is_end_of_word = False #Indicate whether this is the end of a word.
        self.patient_ids = [] # Store information which related to patient's id.

class Trie:
    def __init__(self):
        self.root = TrieNode()

    #Insert patient's name.
    def insert(self, name: str, patient_id: int) -> None: 
        if not isinstance(name, str):
            return
        name = name.strip().lower()  # Pre-processing.
        if not name:
            return
        
        node = self.root # Initialize node.
        for char in name: 
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        if patient_id not in node.patient_ids: # Avoid repeated adding.
            node.patient_ids.append(patient_id)

    def find_node(self, word: str) -> TrieNode:
        node = self.root
        for char in word:
            if char not in node.children:
                return None
            node = node.children[char]
        return node if node.is_end_of_word else None

    # Delete patient's name if the patient is cured.
    def delete(self, name: str, patient_id: int) -> bool:
        word = name.strip().lower()
        def delete_helper(node, word, depth):
            if not node:
                return False, False
            
            if depth == len(word):
                if node.is_end_of_word and patient_id in node.patient_ids:
                    node.patient_ids.remove(patient_id)

                    # If the node has no connection to other ID.
                    if not node.patient_ids:
                        node.is_end_of_word = False

                        if not node.children:
                            return True, True # Find and delete node.
                        return True, False # Find node but no need to delete.
                    return True, False # Find node but node has other patient's ID.
                return False, False # Not found.
            
            char = word[depth]
            if char not in node.children:
                return False, False
            found, should_delete_child = delete_helper(node.children[char], word, depth+1)
        
            if should_delete_child:
                del node.children[char] # Delete child node.
                # Delete current node which is not the end of the node and has no any other child node. 
                if not node.is_end_of_word and not node.children:
                    return found, True
            return found, True
        
        found, _ = delete_helper(self.root, word, 0)
        
        return found
              
    # Search all prefix name and corresponding case ID.
    def search_prefix(self, prefix: str) -> list: 
        prefix = prefix.strip().lower()
        node = self.root  
        #Locate the last character node of the prefix.
        for char in prefix:
            if char not in node.children: # If the prefix not exist.
                return []
            node = node.children[char]

        results = []
        self.collect_words(node, prefix, results)
        return results
    
    def collect_words(self, node: TrieNode, prefix: str, results: list):
        if node.is_end_of_word:
            results.append((prefix, node.patient_ids.copy()))
        for char, child_node in node.children.items():
            self.collect_words(child_node, prefix + char, results)

        
    
    def _dfs_collect_ids(self, node) -> list: # Collect all patient's id.
        ids = set(node.patient_ids)        
        for child in node.children.values():
            ids.update(self._dfs_collect_ids(child))
        return ids


# Sort the case based on their id (use LSD, or Least Significant Digit first).
class RadixSort: 
    @staticmethod
    def sort_objects(obj_list:list, key_func) -> list:
        if not obj_list:
            return obj_list.copy()
        
        # Extract key value and get maximum value.
        keys = [key_func(obj) for obj in obj_list]
        max_key = max(keys)
        if max_key < 0 :
            raise ValueError("RadixSort only supports non-negative integer keys.")
        if max_key == 0:
            return obj_list.copy()
        
        max_digits = len(str(max_key))
        # Sort the object and their values.
        paired = list(zip(keys, obj_list))
        
        for digit in range(max_digits):
            buckets = [[] for _ in range(10)]
            divisor = 10 ** digit
            for key, obj in paired:
                current_digit = (key//divisor) % 10
                buckets[current_digit].append((key, obj))
            # Flatten them.
            paired = [item for bucket in buckets for item in bucket]

        # Return the sorted list for the object.
        return [obj for _, obj in paired]
        
    @staticmethod
    def sort(arr: list) -> list:
        if not arr:
            return arr.copy()

        # Solve the situation which the largest number is 0.
        max_num = max(arr)
        if max_num == 0:
            return arr.copy()
        
        max_digits = len(str(max_num))

        for digit in range(max_digits):
            buckets = [[] for _ in range(10)]
            divisor = 10 ** digit
            for num in arr:
                #Get the current number. 
                current_digit = (num//divisor)%10
                buckets[current_digit].append(num)
            # Update array.
            arr = [num for bucket in buckets for num in bucket]

        return arr