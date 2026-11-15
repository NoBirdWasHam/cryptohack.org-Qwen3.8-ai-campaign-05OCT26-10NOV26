# Prefix-FS attack: grind each A_i (via +kP seams / fresh r) until
# LSB(state_i) matches strategy type (real G -> want 0, fake cycle -> want 1).
# If live derives e_i from running state (not final), all 128 accept -> flag.
import json, random, socket, time, sys
from hamiltonicity import pedersen_commit, permute_graph, commit_to_graph
from hamiltonicity import hash_committed_graph, comm_params

N, NR = 5, 128
G = [[0,0,1,0,0],[1,0,0,0,0],[0,1,0,0,0],[0,0,0,0,1],[0,0,0,1,0]]
CYCLE = [(0,1),(1,2),(2,3),(3,4),(4,0)]

def fake_graph_commit():
    F = [[0]*N for _ in range(N)]; op = [[None]*N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            v = 1 if (i,j) in CYCLE else 0
            c, r = pedersen_commit(v)
            F[i][j] = c; op[i][j] = [v, r]
    return F

def grind(state, want):
    # returns (A, state) with LSB(int(state')) == want
    tries = 0
    while True:
        tries += 1
        if want == 0:
            A, openings = commit_to_graph(G, N)
            perm = list(range(N)); random.shuffle(perm)
            A = permute_graph(A, N, perm)
            z = [perm, permute_graph(openings, N, perm)]
        else:
            F = fake_graph_commit()
            A = F
            z = [list(map(list, CYCLE)), [op_r for (_, op_r) in
                 [(0, [0]*N)] for _ in range(0)]]  # placeholder replaced below
            # openings for cycle entries in node order: r of A[i][j] where (i,j)=CYCLE[k]
            # fake graph was permuted? No: we use identity layout, cycle = CYCLE as-is.
            # need r values: recompute deterministically by recommitting? store them:
        # simpler: recompute with stored r
        st = hash_committed_graph(A, state, comm_params)
        if int.from_bytes(st, "big") & 1 == want:
            return A, z, st, tries

# rewrite cleanly with stored openings
def grind2(state, want):
    tries = 0
    while True:
        tries += 1
        if want == 0:
            A, openings = commit_to_graph(G, N)
            perm = list(range(N)); random.shuffle(perm)
            A = permute_graph(A, N, perm)
            z = [perm, permute_graph(openings, N, perm)]
        else:
            A = [[0]*N for _ in range(N)]; rmap = {}
            for i in range(N):
                for j in range(N):
                    v = 1 if (i,j) in CYCLE else 0
                    c, r = pedersen_commit(v)
                    A[i][j] = c; rmap[(i,j)] = r
            z = [list(map(list, CYCLE)), [rmap[e] for e in CYCLE]]
        st = hash_committed_graph(A, state, comm_params)
        if int.from_bytes(st, "big") & 1 == want:
            return A, z, st, tries

proofs = []
state = b""
tot = 0
for i in range(NR):
    A, z, state, t = grind2(state, i % 2)  # alternate strategies
    tot += t
    proofs.append(json.dumps({"A": A, "z": z}))
print("grind total attempts:", tot, flush=True)

s = socket.create_connection(("archive.cryptohack.org", 34597), timeout=20)
buf = b""
def pump(t):
    global buf
    end = time.time()+t
    while time.time() < end:
        s.settimeout(max(0.1, end-time.time()))
        try: d = s.recv(65536)
        except Exception: return
        if not d: return
        buf += d
PROMPT = b"send fiat shamir proof"
pump(10)
for i in range(NR):
    s.sendall(proofs[i].encode()+b"\n")
    end = time.time()+8
    while time.time() < end and buf.count(PROMPT) < i+2 and b"computing" not in buf:
        s.settimeout(max(0.1, end-time.time()))
        try: d = s.recv(65536)
        except Exception: break
        if not d: break
        buf += d
end = time.time()+25
while time.time() < end and b"crypto{" not in buf and b"Traceback" not in buf and b"didn't verify" not in buf:
    s.settimeout(max(0.1, end-time.time()))
    try: d = s.recv(65536)
    except Exception: break
    if not d: break
    buf += d
open("_local/attack1.log","wb").write(buf)
txt = buf.decode(errors="replace")
print("ACCEPT COUNT:", txt.count("accepted"))
print("TAIL:", txt[-800:])
import re
m = re.search(r"crypto\{[^}]*\}", txt)
print("FLAG:", m.group(0) if m else None)
