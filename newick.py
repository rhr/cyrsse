import string, sys, re, shlex
import pyparsing
from pyparsing import Word, QuotedString, OneOrMore, Group, Suppress
from io import StringIO
from tree import Node

pyparsing.ParserElement.enablePackrat()

LABELCHARS = '-.|/?#&'
META = re.compile(r'([^,=\s]+)\s*=\s*(\{[^=}]*\}|"[^"]*"|[^,]+)?')

def add_label_chars(chars):
    global LABELCHARS
    LABELCHARS += chars

class Tokenizer(shlex.shlex):
    """Provides tokens for parsing newick strings."""
    def __init__(self, infile):
        global LABELCHARS
        shlex.shlex.__init__(self, infile, posix=False)
        self.commenters = ''
        self.wordchars = self.wordchars+LABELCHARS
        self.quotes = "'"

    def parse_embedded_comment(self):
        ws = self.whitespace
        self.whitespace = ""
        v = []
        while 1:
            token = self.get_token()
            if token == '':
                sys.stdout.write('EOF encountered mid-comment!\n')
                break
            elif token == ']':
                break
            elif token == '[':
                self.parse_embedded_comment()
            else:
                v.append(token)
        self.whitespace = ws
        return "".join(v)

    def parse_ampersand_comment(s):
        word = Word(string.letters+string.digits+"%_")
        key = word.setResultsName("key") + Suppress("=")
        single_value = (Word(string.letters+string.digits+"-.") |
                        QuotedString("'") |
                        QuotedString('"'))
        range_value = Group(Suppress("{") +
                            single_value.setResultsName("min") +
                            Suppress(",") +
                            single_value.setResultsName("max") +
                            Suppress("}"))
        pair = (key + (single_value | range_value).setResultsName("value"))
        g = OneOrMore(pair)
        d = []
        for x in g.searchString(s):
            v = x.value
            if type(v) == str:
                try:
                    v = float(v)
                except ValueError:
                    pass
            else:
                try:
                    v = map(float, v.asList())
                except ValueError:
                    pass
            d.append((x.key, v))
        return d

def parse(data, ttable=None, treename=None):
    """
    Parse a newick string.

    *data* is any file-like object that can be coerced into shlex, or
    a string (converted to StringIO)

    *ttable* is a dictionary mapping node labels in the newick string
     to other values.

    Returns: the root node.
    """
    if isinstance(data, str):
        data = StringIO(data)

    tokens = Tokenizer(data)

    node = None
    lp = 0
    rp = 0
    previous = None
    ni = 0  # node id counter (preorder) - zero-based indexing

    while 1:
        token = tokens.get_token()
        if token == ';' or token == tokens.eof:
            assert lp == rp, "unbalanced parentheses in tree description: (%s, %s)" % (lp, rp)
            break

        # internal node
        elif token == '(':
            lp = lp+1
            newnode = Node()
            newnode.ni = ni
            ni += 1
            ## newnode.treename = treename
            if node:
                node.add_child(newnode)
            else:
                node = newnode
            node = newnode

        elif token == ')':
            rp = rp+1
            node = node.parent

        elif token == ',':
            node = node.parent

        # branch length
        elif token == ':':
            token = tokens.get_token()
            if token == '[':
                node.length_comment = tokens.parse_embedded_comment()
                token = tokens.get_token()

            if not (token == ''):
                try:
                    brlen = float(token)
                except ValueError:
                    raise ValueError("invalid literal for branch length, '%s'" % token)
            else:
                raise ValueError('unexpected end-of-file (expecting branch length)')

            node.length = brlen
        # comment
        elif token == '[':
            node.comment = tokens.parse_embedded_comment()
            if node.comment[0] == '&':
                # metadata
                meta = META.findall(node.comment[1:])
                if meta:
                    node.meta = {}
                    for k, v in meta:
                        v = eval(v.replace('{','(').replace('}',')'))
                        node.meta[k] = v

        # leaf node or internal node label
        else:
            if previous != ')':  # leaf node
                if ttable:
                    try:
                        ttoken = (ttable.get(int(token)) or
                                  ttable.get(token))
                    except ValueError:
                        ttoken = ttable.get(token)
                    if ttoken:
                        token = ttoken
                newnode = Node()
                newnode.ni = ni
                ni += 1
                newnode.label = "_".join(token.split()).replace("'", "")
                node.add_child(newnode)
                node = newnode
            else:  # label
                if ttable:
                    node.label = ttable.get(token, token)
                else:
                    node.label = token

        previous = token
    return node
