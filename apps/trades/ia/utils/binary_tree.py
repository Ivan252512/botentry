class Node:
    def __init__(self, _key, _info):
        self.left = None
        self.right = None
        self.val = int(_key)
        self.info = _info
        
        
class BinaryTree:
    def __init__(self, _key, _info):
        self.root = Node(_key, _info)
        self.size = 1
        
    def _r_insert(self, root, _key, _info):
        if root is None:
            self.size += 1
            return Node(_key, _info)
        else:
            if root.val == _key:
                return root
            elif root.val < _key:
                root.right = self._r_insert(root.right, _key, _info)
            else:
                root.left = self._r_insert(root.left, _key, _info)
        return root
    
    def insert(self, _key, _info):
        self._r_insert(self.root, int(_key), _info)
            
    def _search_in_node(self, _node, _key):
        if _node is None:
            return False, None
        if _key == _node.val:
            return _node.val, _node.info
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
            
    def search(self, _key):
        return self._search_in_node(self.root, int(_key))