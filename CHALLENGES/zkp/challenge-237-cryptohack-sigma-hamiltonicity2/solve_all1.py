# all-bit-1 attack: honest chained commitment to a TRUE directed 5-cycle every round.
# Wins iff verifier branches on string truthiness (bool("0")==True).
# usage: python solve_all1.py local <chalfile>   |   python solve_all1.py live
import json, random, socket, sys, os, time, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hamiltonicity import pedersen_commit, hash_committed_graph, comm_params

N = 5
NUM = 128
CYCLE = [[0,4],[4,2],[2,3],[3,1],[1,0]]

random.seed()

def build_round():
    A = [[0 for _ in range(N)] for _ in range(N)]
    rmap = {}
    for s, d in CYCLE:
        comm, r = pedersen_commit(1)
        A[s][d] = comm
        rmap[(s, d)] = r
    openings = [rmap[(s, d)] for s, d in CYCLE]
    return {"A": A, "z": [CYCLE, openings]}, A

proofs, A_vars = [], []
for i in range(NUM):
    p, A = build_round()
    proofs.append(json.dumps(p))
    A_vars.append(A)

st = b''
for i in range(NUM):
    st = hash_committed_graph(A_vars[i], st, comm_params)
bits = bin(int.from_bytes(st, 'big'))[-NUM:]
print(f"local predicted bits: ones={bits.count('1')} zeros={bits.count('0')}")
print(f"bits[:24]: {bits[:24]}")

mode = sys.argv[1]
if mode == "local":
    chalfile = sys.argv[2]
    proc = subprocess.Popen(
        [sys.executable, chalfile],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        cwd=os.path.dirname(os.path.abspath(__file__)))
    out, err = proc.communicate(("\n".join(proofs) + "\n").encode(), timeout=300)
    txt = out.decode(errors="replace")
    print("accepted:", txt.count("accepted"))
    print("flag line:", "localflag{ok}" in txt)
    if "localflag{ok}" not in txt:
        tail = (txt + err.decode(errors="replace"))[-500:]
        print("TAIL:", tail)
    print("VERDICT(all-1 attack wins):", "localflag{ok}" in txt)
else:
    HOST, PORT = "archive.cryptohack.org", 34597
    s = socket.create_connection((HOST, PORT), timeout=15); s.settimeout(60)
    time.sleep(0.5)
    greet = s.recv(65536)
    print("greeting:", greet[:80])
    for p in proofs:
        s.sendall((p + "\n").encode()); time.sleep(0.01)
    out = b""; t0 = time.time()
    while time.time() - t0 < 120:
        try:
            d = s.recv(65536)
        except socket.timeout:
            continue
        except Exception:
            break
        if not d:
            break
        out += d
    txt = out.decode(errors="replace")
    print("accepted:", txt.count("accepted"))
    print("computing line present:", "computing fiat shamir challenge" in txt)
    print("flag present:", "flag" in txt.lower() and "convicted" not in txt and "convinced" in txt)
    if "flag" in txt.lower():
        for line in txt.splitlines():
            if "flag" in line.lower() or "convinced" in line:
                print("OUTLINE:", line)
    print("live bits seen:", "".join(__import__("re").findall(r"challenge bit is (\d)", txt))[:64])
    print("TAIL:", txt[-600:])
    s.close()
