# probe10: (1) can a mid-chained sha256 state be recovered (backward induction)?
# (2) can a chained digest be forced = chosen target 0x00..00 (length-extension)?
# (3) does the no-separator concat allow SAME-graph digit-shifts (True<->1, 1->10|0->"0")?
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hamiltonicity import hash_committed_graph, comm_params, commit_to_graph, permute_graph, open_graph

# (3) same-graph digit-shift demo: two openings of the SAME commitment matrix
# whose hash strings differ but opened graphs are identical.
G = [[0,0,1,0,0],[1,0,0,0,0],[0,1,0,0,0],[0,0,0,0,1],[0,0,0,1,0]]
A, openings = commit_to_graph(G, 5)
op2 = [[list(c) for c in row] for row in openings]
op2[0][0][0] = True          # opens same 0-commitment (True==0)
op2[0][1][0] = False         # opens same 1... wait True==1 False==0
# messages: G[0][1]=0 -> False ; G[0][0]=0 -> True? G[0][0]=0 so True WRONG there; use demo on real 1s:
op2[0][0][0] = False         # entry (0,0) is 0 -> False ok
op2[0][2][0] = True          # entry (0,2) is 1 -> True ok
M = open_graph(A,5,op2)
print("(3) opened graph identical with bool messages:", M == G)
# digit-shift pair on string vs int entry (int part opens, str part shifts next entry):
s1 = "".join(str(x) for xs in [[1,1],[0]] for x in xs)
s2 = "".join(str(x) for xs in [["10",0],["0"]] for x in xs)
# (10|0|0) vs ("10"|"0|0") both -> "1000"
print("(3) digit concat collision demo:", s1, s2, s1 == s2)

# (1) midstate recovery: can we find state S such that a chain of 64 arbitrary
# msgs yields digest with low64==T? (grind ~2^64 -> infeasible; just measure hash rate)
import time, hashlib
t0=time.time(); c=0
for i in range(300000):
    hashlib.sha256(b"a%dsalt"%i).digest(); c+=1
print("rate %.0f sha256/s -> 2^64 = %.1f years" % (c/(time.time()-t0), 2**64/(c/(time.time()-t0)/3.15e7)))

# (2) length-extension chain: h_i = sha256(params||h_{i-1}||msg). h_{i-1} is in the
# MIDDLE of the hash input (padded tail), so sha256.length-extension cannot
# append msgs. Confirm input layout:
params = str(comm_params).encode()
print("(2) prefix len", len(params), "-> state at byte", len(params), "of 64-byte block => mid-block, no extension")
