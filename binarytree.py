class Node(object):
    def __init__(self, key, value, left=None, right=None, parent=None):
        self.left = left
        self.right = right
        self.key = key
        self.value = value
        self.parent = parent

    def __iter__(self):
        return (i for i in self.iterkeys())

    def iterkeys(self):
        return (i.key for i in self.iteritems())

    def iteritems(self):
        if self:
            if self.has_left_child():
                for node in self.left:
                    yield node

            yield self

            if self.has_right_child():
                for node in self.right:
                    yield node

    def has_left_child(self):
        return self.left

    def has_right_child(self):
        return self.right

    def is_left_child(self):
        return self.parent and self.parent.left == self

    def is_right_child(self):
        return self.parent and self.parent.right == self

    def is_leaf(self):
        return not (self.left or self.right)

    def has_any_children(self):
        return self.left or self.right

    def has_both_children(self):
        return self.left and self.right

    def find_replacement(self):
        replacement = None
        if self.has_right_child():
            replacement = self.right.find_min()

        return replacement

    def find_min(self):
        current = self.left
        while current.has_left_child():
            current = current.left
        return current

    def splice_out(self):
        if self.is_leaf():
            if self.is_left_child():
                self.parent.left = None
            else:
                self.parent.right = None

        elif self.has_any_children():

            if self.has_left_child():
                self.left.parent = self.parent
                if self.is_left_child():
                    self.parent.left = self.left
                else:
                    self.parent.right = self.left

            else:
                self.right.parent = self.parent
                if self.is_left_child():
                    self.parent.left = self.right
                else:
                    self.parent.right = self.right


class BinarySearchTree(object):
    def __init__(self):
        self.root = None
        self.size = 0

    def __setitem__(self, key, value):
        self.set(key, value)

    def __getitem__(self, key):
        return self.get(key)

    def __contains__(self, key):
        return True if self._get(key, self.root) else False

    def __delitem__(self, key):
        self.delete(key)

    def __iter__(self):
        if not self.root:
            return

        for x in self.root:
            yield x

    def set(self, key, value):
        if self.root:
            self.size += self._set(key, value, self.root)
        else:
            self.root = Node(key, value)
            self.size = 1

    def _set(self, key, value, current_node):
        """
        Recursive function to set a value in the tree by updating or creating a node.
        :param key:
        :param value:
        :param current_node:
        :return: The old value, None if one had not been set
        """
        if key == current_node.key:
            current_node.value = value
            return 0

        elif key > current_node.key:
            if current_node.has_right_child():
                return self._set(key, value, self.root.right)
            else:
                current_node.right = Node(key, value)
                return 1

        elif key < current_node.key:
            if current_node.has_left_child():
                return self._set(key, value, current_node.left)
            else:
                current_node.left = Node(key, value)
                return 1

    def get(self, key, default=None):
        if self.root:
            ret = self._get(key, self.root, default)
            return ret.value if ret != default else default
        else:
            return default

    def _get(self, key, current_node, default=None):
        if not current_node:
            return default
        elif key == current_node.key:
            return current_node
        elif key > current_node.key:
            return self._get(key, current_node.right, default)
        else:
            return self._get(key, current_node.left, default)

    def delete(self, key):
        if self.size > 1:
            node_to_delete = self._get(key, self.root)
            if node_to_delete:
                self.remove(node_to_delete)
                self.size -= 1
            else:
                raise KeyError('Key not found!')
        elif self.size == 1 and self.root.key == key:
            self.root = None
            self.size = 0
        else:
            raise KeyError('Key not found!')

    def remove(self, current_node):
        if current_node.is_leaf():
            if current_node.is_left_child():
                current_node.parent.left = None
            elif current_node.is_right_child():
                current_node.parent.right = None
        elif current_node.has_both_children():
            repl = current_node.find_replacement()
            repl.splice_out()
            current_node.key = repl.key
            current_node.value = repl.value
        else:
            if current_node.has_left_child():
                if current_node.is_left_child():
                    current_node.parent.left = current_node.left
                    current_node.left.parent = current_node.parent
                elif current_node.is_right_child():
                    current_node.parent.right = current_node.left
                    current_node.left.parent = current_node.parent
                else:
                    self.root = current_node.left
                    self.root.parent = None
            else:
                if current_node.is_left_child():
                    current_node.parent.left = current_node.right
                    current_node.left.parent = current_node.parent
                elif current_node.is_right_child():
                    current_node.parent.right = current_node.right
                    current_node.left.parent = current_node.parent
                else:
                    self.root = current_node.right
                    self.root.parent = None
