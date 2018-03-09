import newick
import pandas as pd

root = newick.parse(open('psychotria.newick').read())

cdef enum Area:
    K, O, M, H, nareas

cdef enum Range:
    K, KO, O, OM, M, MH, H, nstates

cdef enum Rate:
    lam, mu, q

v = [ (lam, i, i, i) for i in range(nareas) ]
v.extend([ (lam, i, i-1, i+1) for i in KO, OM, MH ])
v.extend([ (lam, i, i-1, i) for i in KO, OM, MH ])

pframe = pd.DataFrame.from_records
