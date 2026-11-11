# probe11: (A) JSON-dict-as-graph: does a 5x5 dict pass check_graph/open_graph/permute_graph
# while hashing differently from the equivalent list? (FS-input malleability -> fixed-point MITM)
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hamiltonicity import hash_committed_graph, comm_params, check_graph, open_graph, permute_graph
from hamiltonicity import commit_to_graph

N = 5
G = [[0,0,1,0,0],[1,0,0,0,0],[0,1,0,0,0],[0,0,0,0,1],[0,0,0,1,0]]
Adict = {str(i): {str(j): v for j, v in enumerate(row)} for i, row in enumerate(G)}
print("A) check_graph(dict):")
try:
    print("   ", check_graph(Adict, N))
except Exception as e:
    print("    EXC:", type(e).__name__, e)
print("A) open_graph-like index: Adict[0][2] ->", end=" ")
try:
    print(Adict[0][2])
except Exception as e:
    print("EXC:", type(e).__name__, e)
# openings must stay LIST for m,r = openings[i][j]; test G_permuted == G_test where
# G_permuted is a list -> list == G_test(list) fine. Also permute_graph(G, perm) is a list.
# hash of dict matrix:
Alist = [[1,2,3,4,5] for _ in range(5)]
h1 = hash_committed_graph(Alist, b"", comm_params)
h2 = hash_committed_graph(Adict, b"", comm_params)
print("A) hash(list)=%s\n   hash(dict)=%s  differ: %s" % (h1[:6].hex(), h2[:6].hex(), h1 != h2))
# str of a single-integer dict row vs int:
r = {str(j): v for j, v in enumerate([1,0,1,0,0])}
print("A) row str repr:", str(r))
