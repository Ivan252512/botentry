class Node:
    def __init__(self, _key):
        self.left = None
        self.right = None
        self.val = int(_key)
        
        
class BinaryTree:
    def __init__(self, _key):
        self.root = Node(_key)
        
    def _r_insert(self, root, _key):
        if root is None:
            return Node(_key)
        else:
            if root.val == _key:
                return root
            elif root.val < _key:
                root.right = self._r_insert(root.right, _key)
            else:
                root.left = self._r_insert(root.left, _key)
        return root
    
    def insert(self, _key):
        self._r_insert(self.root, int(_key))
            
    def _search_in_node(self, _node, _key):
        if _node is None:
            return False
        if _key == _node.val:
            return True
        if _key < _node.val:
            return self._search_in_node(_node.left, _key)
        if _key > _node.val:
            return self._search_in_node(_node.right, _key)
            
    def to_list(self, _node):
        if _node is not None:
            return [_node.val] + self.to_list(_node.left) + self.to_list(_node.right)
        return []
            
    def get_list(self):
        return str(self.to_list(self.root))
        
    def print_tree(self, _node, _level):
        if _node is not None:
            self.print_tree(_node.left, _level + 1)
            print(' ' * 4 * _level + '->', _node.val)
            self.print_tree(_node.right, _level + 1)
            
    def format_print(self):
        self.print_tree(self.root, 0)
            
    def search(self, _key):
        return self._search_in_node(self.root, int(_key))