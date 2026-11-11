# Probe live build: does it check each round immediately (old) or after 128 (new)?
import json, random, socket, sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hamiltonicity import commit_to_graph, permute_graph

HOST, PORT = "archive.cryptohack.org", 34597
N = 5
G = [[0,0,1,0,0],[1,0,0,0,0],[0,1,0,0,0],[0,0,0,0,1],[0,0,0,1,0]]

s = socket.create_connection((HOST, PORT), timeout=8)
f = s.makefile("rwb")
def recv_till(timeout=6):
    s.settimeout(timeout)
    data = b""
    try:
        while True:
            c = f.read(1)
            if not c: break
            data += c
    except Exception:
        pass
    return data

print("GREETING:", recv_till().decode(errors="replace"))
perm = list(range(N)); random.shuffle(perm)
Gp = permute_graph(G, N, perm)
A, openings = commit_to_graph(Gp, N)
z = [perm, openings]
t0 = time.time()
f.write((json.dumps({"A": A, "z": z}) + "\n").encode()); f.flush()
resp = recv_till(6)
print("AFTER-ROUND1 (%.1fs):" % (time.time()-t0), repr(resp.decode(errors="replace")))
s.close()
