# (c) exhaustive pullback check + honest-prover validation on LocalTest clone (plain pipes, no pwntools)
import itertools, sys, os, subprocess, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hamiltonicity import permute_graph, commit_to_graph, hash_committed_graph, comm_params, get_r_vals
G = [[0,0,1,0,0],[1,0,0,0,0],[0,1,0,0,0],[0,0,0,0,1],[0,0,0,1,0]]
def has_ham(M):
    for p in itertools.permutations(range(5)):
        if all(M[p[k]][p[(k+1)%5]] == 1 for k in range(5)): return p
    return None
hits = [pi for pi in itertools.product(range(-5,5), repeat=5) if has_ham(permute_graph(G,5,list(pi)))]
print("pullbacks (10^5 signed fns) with Ham cycle:", len(hits))

d = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(d,"chal.py")).read().replace('LocalTest = False','LocalTest = True').replace('os.environ["FLAG"]','"localflag{ok}"')
open(os.path.join(d,"chal_local.py"),"w").write(src)

N=5; NUM=128
GC = [[0,1,1,0,1],[1,0,0,0,0],[0,0,0,1,0],[0,1,1,0,0],[1,0,1,1,0]]
CYCLE = [(0,4),(4,2),(2,3),(3,1),(1,0)]
p = subprocess.Popen([sys.executable, "chal_local.py"], cwd=d, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
random.seed(7)
A_vars, open_vars, perm_vars = [], [], []
for i in range(NUM):
    A, openings = commit_to_graph(GC, N)
    perm = list(range(N)); random.shuffle(perm)
    A_vars.append(permute_graph(A,N,perm)); open_vars.append(openings); perm_vars.append(perm)
st=b''
for i in range(NUM): st = hash_committed_graph(A_vars[i], st, comm_params)
bits = bin(int.from_bytes(st,'big'))[-NUM:]
lines=[]
for i in range(NUM):
    openings, perm = open_vars[i], perm_vars[i]
    if int(bits[i]):
        pc=[[perm.index(x[0]), perm.index(x[1])] for x in CYCLE]
        z=[pc, get_r_vals(openings,N,CYCLE)]
    else:
        z=[perm, permute_graph(openings,N,perm)]
    lines.append(json.dumps({"A":A_vars[i],"z":z}))
out, err = p.communicate("\n".join(lines)+"\n", timeout=240)
print("honest LocalTest clone -> localflag:", "localflag{ok}" in out, "| accepted:", out.count("accepted"))
if "localflag{ok}" not in out: print("ERR:", err[-300:], out[-300:])
