import math

class Terminal(object):

    def __init__(self, label, token, index):
        """
        Parameters
        ----------
        label: str
        token: str
        index: int
        """
        self.label = label
        self.token = token
        self.index = index

        self.index_span = (index, index)
        self.head_token_index = index
        self.head_child_index = index

        self.depth = None
        self.height = None

        self.with_nonterminal_labels = True
        self.with_terminal_labels = True

    ###########
    def __str__(self):
        return "( %s %s )" % (self.label, self.token)

    def tolist(self):
        """
        Returns
        -------
        list[str]
        """
        return [self.label, self.token]

    def leaves(self):
        """
        Returns
        -------
        list[str]
        """
        return [self.token]

    def labelleaves(self):
        """
        Returns
        -------
        list[str]
        """
        return [self.label]

    ###########
    def is_terminal(self):
        """
        Returns
        -------
        bool
        """
        return True

    ###########
    def calc_spans(self):
        """
        Returns
        -------
        (int, int)
        """
        return self.index_span

    def calc_heads(self, func_head_child_rule):
        """
        Parameters
        ----------
        func_head_child_rule: function: NonTerminal -> int

        Returns
        -------
        int
        """
        return self.head_token_index

    ###########
    def set_depth(self, depth=0):
        """
        Parameters
        ----------
        depth: int

        Returns
        -------
        int
        """
        self.depth = depth
        return self.depth

    def set_height(self):
        """
        Returns
        -------
        int
        """
        self.height = 0
        return self.height


class NonTerminal(object):

    def __init__(self, label):
        """
        Parameters
        ----------
        label: str
        """
        self.label = label
        self.children = []

        self.index_span = (None, None)
        self.head_token_index = None
        self.head_child_index = None

        self.depth = None
        self.height = None

        self.with_nonterminal_labels = True
        self.with_terminal_labels = True

    def add_child(self, node):
        """
        Parameters
        ----------
        node: NonTerminal or Terminal
        """
        self.children.append(node)

    ###########
    def __str__(self):
        inner = " ".join([c.__str__() for c in self.children])
        return "( %s %s )" % (self.label, inner)

    def tolist(self):
        """
        Returns
        -------
        list[T]
            T -> str or list[T]
        """
        inner = [self.label] + [c.tolist() for c in self.children]
        return inner

    def leaves(self):
        """
        Returns
        -------
        list[str]
        """
        leaves = []
        for c in self.children:
            leaves.extend(c.leaves())
        return leaves

    def labelleaves(self):
        """
        Returns
        -------
        list[str]
        """
        leaves = []
        for c in self.children:
            leaves.extend(c.labelleaves())
        return leaves

    ###########
    def is_terminal(self):
        """
        Returns
        -------
        bool
        """
        return False

    ###########
    def calc_spans(self):
        """
        Returns
        -------
        (int, int)
        """
        min_index = math.inf
        max_index = -math.inf
        for c_i in range(len(self.children)):
            i, j = self.children[c_i].calc_spans()
            if i < min_index:
                min_index = i
            if max_index < j:
                max_index = j
        self.index_span = (min_index, max_index)
        return min_index, max_index

    def calc_heads(self, func_head_child_rule):
        """
        Parameters
        ----------
        func_head_child_rule: function: NonTerminal -> int

        Returns
        -------
        int
        """
        head_token_indices = []
        for c_i in range(len(self.children)):
            head_token_index = self.children[c_i].calc_heads(func_head_child_rule)
            head_token_indices.append(head_token_index)

        self.head_child_index = func_head_child_rule(self)
        self.head_token_index = head_token_indices[self.head_child_index]
        return self.head_token_index

    ###########
    def set_depth(self, depth=0):
        """
        Parameters
        ----------
        depth: int

        Returns
        -------
        int
        """
        self.depth = depth
        max_cdepth = -1
        for c_i in range(len(self.children)):
            cdepth = self.children[c_i].set_depth(depth=depth+1)
            if cdepth > max_cdepth:
                max_cdepth = cdepth
        return max_cdepth

    def set_height(self):
        """
        Returns
        -------
        int
        """
        max_height = -1
        for c_i in range(len(self.children)):
            cheight = self.children[c_i].set_height()
            if cheight > max_height:
                max_height = cheight
        self.height = max_height + 1
        return self.height


def sexp2tree(sexp, LPAREN, RPAREN):
    """
    Parameters
    ----------
    sexp: list[str]
    LPAREN: str
    RPAREN: str

    Returns
    -------
    NonTerminal

    Examples
    --------
    >> sexp = "( S ( NP ( DT a ) ( NN cat ) ) ( VP ( VBZ bites ) ( NP ( DT a ) ( NN mouse ) ) ) )".split()
    """
    tokens = sexp
    n_tokens = len(tokens)
    i = 0
    pos_count = 0
    ROOT = NonTerminal("ROOT")
    stack = [ROOT]
    while i < n_tokens:
        if tokens[i] == LPAREN:
            assert tokens[i+1] not in [LPAREN, RPAREN]
            node = NonTerminal(label=tokens[i+1])
            stack.append(node)
            i += 2
        elif tokens[i] == RPAREN:
            node = stack.pop()
            stack[-1].add_child(node)
            i += 1
        else:
            node = stack.pop()
            node = Terminal(label=node.label, token=tokens[i], index=pos_count)
            pos_count += 1
            stack.append(node)
            i += 1
    assert len(stack) == 1
    ROOT = stack.pop()
    assert len(ROOT.children) == 1
    return ROOT.children[0]


