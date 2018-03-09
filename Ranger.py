import igraph, string, enum
from itertools import combinations

class Ranger(object):
    def __init__(self, nareas, arealabels=None, maxrangesize=None, labelsep=''):
        assert len(arealabels) == nareas
        self.nareas = nareas

        if arealabels is None:
            if nareas <= 26:
                arealabels = tuple(string.ascii_uppercase[:nareas])
            else:
                arealabels = [ 'A{}'.format(i) for i in range(nareas) ]
                labelsep = labelsep or '+'

        self.arealabels = arealabels
        self.areas = enum.IntEnum('areas', arealabels, start=0)
        self.labelsep = labelsep
        self.maxrangesize = maxrangesize
        self.Dg = igraph.Graph()
        self.Dg.add_vertices(nareas)
        self.Dg.vs['name'] = self.arealabels
        self.Qg = igraph.Graph()
