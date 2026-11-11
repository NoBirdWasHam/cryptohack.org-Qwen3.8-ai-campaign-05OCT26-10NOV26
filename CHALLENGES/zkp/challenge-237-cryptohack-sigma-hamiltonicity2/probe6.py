# Local: (1) float fake-open feasibility; (2) pullback Hamiltonian-cycle exhaustive check
import json, itertools, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hamiltonicity import pedersen_open, comm_params, permute_graph
from math import nextafter
P,q,h1,h2 = comm_params
G = [[0,0,1,0,0],[1,0,0,0,0],[0,1,0,0,0],[0,0,0,0,1],[0,0,0,1,0]]

# (1) float opening to 1 with r=0: need fl(f*I1)==1.0, I1=pow(h1,-1,P)
I1 = pow(h1,-1,P)
f = 1.0/float(I1)
found = None
for cand in [f, nextafter(f,0), nextafter(f,2), nextafter(nextafter(f,0),0), nextafter(nextafter(f,2),2)]:
    ok = pedersen_open(cand, 1, 0)
    print("cand", repr(cand), "->", ok)
    if ok and found is None: found = cand
print("f1 =", repr(found))
print("json roundtrip ok:", json.loads(json.dumps(found)) == found)
print("open(1.0,0,0):", pedersen_open(1.0, 0, 0))
print("open(1,0,0) real:", pedersen_open(1, 0, 0))
# also opening to 0 with r=0 via float
print("open(1.0,0,0) again:", pedersen_open(1.0,0,0))

# (2) exhaustive: any function pi:5->5 (incl negative wrap) whose pullback has directed Ham cycle?
def has_ham_cycle(M):
    nodes = range(5)
    for perm in itertools.permutations(range(5)):
        ok = True
        for k in range(5):
            if M[perm[k]][perm[(k+1)%5]] != 1: ok = False; break
        if ok: return perm
    return None
hits = 0
for pi in itertools.product(range(-5,5), repeat=5):
    M = permute_graph(G, 5, list(pi))
    if has_ham_cycle(M): hits += 1
print("pullbacks with Ham cycle:", hits, "of", 10**5)
