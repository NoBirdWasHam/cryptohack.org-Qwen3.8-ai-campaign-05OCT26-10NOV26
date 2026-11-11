# Attack test: answer bit=1 rounds with permuted-G's OWN edge list (works iff live
# testcycle lacks the chaining assert). bit=0 rounds answered honestly.
import json, random, socket, sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hamiltonicity import commit_to_graph, permute_graph, hash_committed_graph, comm_params

HOST, PORT = "archive.cryptohack.org", 34597
N = 5
G = [[0,0,1,0,0],[1,0,0,0,0],[0,1,0,0,0],[0,0,0,0,1],[0,0,0,1,0]]
EDGES = [(0,2),(1,0),(2,1),(3,4),(4,3)]
NUM = 128

s = socket.create_connection((HOST, PORT), timeout=10); s.settimeout(5)
time.sleep(0.5); s.recv(65536)
A_vars, open_vars, perm_vars = [], [], []
for i in range(NUM):
    A, openings = commit_to_graph(G, N)
    perm = list(range(N)); random.shuffle(perm)
    A_vars.append(permute_graph(A, N, perm))
    open_vars.append(openings); perm_vars.append(perm)
st = b''
for i in range(NUM):
    st = hash_committed_graph(A_vars[i], st, comm_params)
bits = bin(int.from_bytes(st, 'big'))[-NUM:]
print("local bits:", bits)
proofs = []
for i in range(NUM):
    openings, perm = open_vars[i], perm_vars[i]
    if int(bits[i]):
        nodes = [[perm[a], perm[b]] for (a,b) in EDGES]
        rvals = [openings[a][b][1] for (a,b) in EDGES]
        z = [nodes, rvals]
    else:
        z = [perm, permute_graph(openings, N, perm)]
    proofs.append(json.dumps({"A": A_vars[i], "z": z}))
for p in proofs:
    s.sendall((p + "\n").encode()); time.sleep(0.01)
out = b""; t0 = time.time()
while time.time()-t0 < 30:
    try: d = s.recv(65536)
    except socket.timeout: continue
    except Exception: break
    if not d: out += b"<EOF>"; break
    out += d
txt = out.decode(errors="replace")
print("accepted count:", txt.count("accepted"), "flag:", "crypto{" in txt)
print("TAIL:", txt[-500:])
if "crypto{" in txt:
    import re
    m = re.search(r"crypto\{[^}]*\}", txt)
    print("FLAG:", m.group(0))
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "flag_sigma-hamiltonicity2.txt"), "w").write(m.group(0)+"\n")
s.close()
