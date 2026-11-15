# probe13: fresh LIVE re-verification of (a) bit derivation, (b) live G == provided G.
# Strategy: all 128 rounds commit to permuted provided-G (type-0), send honest z.
# Server prints actual challenge bits; dies at first bit=1 (int not subscriptable).
# => live printed bits must match local chain; bit=0 rounds must ACCEPT
#    (acceptance in bit=0 round proves opened matrix == permute(liveG,perm) => liveG == provided G).
import json, random, socket, sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hamiltonicity import commit_to_graph, permute_graph, hash_committed_graph, comm_params

HOST, PORT = "archive.cryptohack.org", 34597
N = 5
G = [[0,0,1,0,0],[1,0,0,0,0],[0,1,0,0,0],[0,0,0,0,1],[0,0,0,1,0]]
NUM = 128

s = socket.create_connection((HOST, PORT), timeout=15); s.settimeout(60)
time.sleep(0.5)
greet = s.recv(65536)
print("greeting:", greet[:80])
random.seed()
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
print("local bits[:16]:", bits[:16], "first-1 at:", bits.find('1'))
proofs = []
for i in range(NUM):
    z = [perm_vars[i], permute_graph(open_vars[i], N, perm_vars[i])]  # always type-0 answer
    proofs.append(json.dumps({"A": A_vars[i], "z": z}))
for p in proofs:
    s.sendall((p + "\n").encode()); time.sleep(0.01)
out = b""; t0 = time.time()
while time.time()-t0 < 90:
    try: d = s.recv(65536)
    except socket.timeout: continue
    except Exception: break
    if not d: break
    out += d
txt = out.decode(errors="replace")
import re
live_bits = "".join(re.findall(r"challenge bit is (\d)", txt))
n0 = bits.find('1')
# expected live behavior: rounds 0..n0-1 accepted (bit 0), round n0 prints bit 1 then traceback
print("accepted:", txt.count("accepted"), "| expected bit0 prefix len:", n0)
print("live bits[:%d]: %s" % (len(live_bits), live_bits))
print("BITS MATCH prefix:", live_bits == bits[:len(live_bits)])
tail = txt[-400:]
print("TAIL:", tail)
print("VERDICT: liveG==providedG & bit-derivation-match:",
      (txt.count("accepted") == n0 and live_bits == bits[:n0+1] and n0 >= 1) or (n0==0 and "Traceback" in tail and len(live_bits)==1))
s.close()
