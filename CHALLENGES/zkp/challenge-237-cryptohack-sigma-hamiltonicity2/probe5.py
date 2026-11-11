# Probe5: is live G the LocalTest graph (has a cycle)? Honest prover vs both candidate graphs.
import json, random, socket, sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hamiltonicity import commit_to_graph, permute_graph, hash_committed_graph, comm_params, get_r_vals

HOST, PORT = "archive.cryptohack.org", 34597
N = 5
G_CYCLE = [[0,1,1,0,1],[1,0,0,0,0],[0,0,0,1,0],[0,1,1,0,0],[1,0,1,1,0]]
CYCLE = [(0,4),(4,2),(2,3),(3,1),(1,0)]
NUM = 128

def run(G, cycle):
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
    proofs = []
    for i in range(NUM):
        A, openings, perm = A_vars[i], open_vars[i], perm_vars[i]
        if int(bits[i]):
            pc = [[perm.index(x[0]), perm.index(x[1])] for x in cycle]
            z = [pc, get_r_vals(openings, N, cycle)]
        else:
            z = [perm, permute_graph(openings, N, perm)]
        proofs.append(json.dumps({"A": A, "z": z}))
    for p in proofs:
        s.sendall((p + "\n").encode()); time.sleep(0.01)
    out = b""; t0 = time.time()
    while time.time()-t0 < 25:
        try: d = s.recv(65536)
        except socket.timeout: continue
        except Exception: break
        if not d: out += b"<EOF>"; break
        out += d
    txt = out.decode(errors="replace")
    print("nbits1:", bits.count("1"), "accepted:", txt.count("accepted"), "flag:", "crypto{" in txt)
    print("TAIL:", txt[-400:])
    s.close()
    return txt

run(G_CYCLE, CYCLE)
