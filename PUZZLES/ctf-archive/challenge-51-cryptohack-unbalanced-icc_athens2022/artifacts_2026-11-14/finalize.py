"""Final: real extraction + decrypt + write ch_results_w7c.json."""
import json, pickle, sys
import resultant_extract as RE
from Crypto.Util.number import long_to_bytes

OUT = r"~\AppData\Local\hermes\cache\scratch\ch_results_w7c.json"

d = pickle.load(open("selected.pkl", "rb"))
sel, N, e, c = d["sel"], d["N"], d["e"], d["c"]
p = None
pairs = [(0, 1), (0, 2), (1, 2), (0, 3), (1, 3), (2, 3), (0, 4), (0, 5), (2, 4)]
for i, j in pairs:
    if j >= len(sel):
        continue
    print(f"trying pair ({i},{j})...", flush=True)
    cands = RE.find_p(sel[i], sel[j], N)
    print("cands:", len(cands), flush=True)
    if cands:
        p = cands[0]
        break
if p is None:
    print("FAILED")
    sys.exit(1)

q = N // p
phi = (p - 1) * (q - 1)
assert N == p * q
assert (e * pow(e, -1, phi)) % phi == 1
dd = pow(e, -1, phi)
msg = pow(c, dd, N)
flag = long_to_bytes(msg).decode(errors="replace")
print("p =", p)
print("q =", q)
print("d =", dd)
print("FLAG:", flag)

derivation = (
    "Durfee-Nguyen ASIACRYPT 2000 trivariate Coppersmith (attack on Sun-Yang-Laih AC99 Scheme I, "
    "which this challenge instantiates: p 256-bit, q 768-bit, d 300-bit, e~N, ed=1+k*phi). "
    "Solve 2 + x*(A - y - z) = 0 (mod e), A=N+1, at root (2k, p, q) with yz=N substituted, so "
    "f(root)=2+k*2*phi=2ed=0 mod e. Shift lattice g_{k,i,b}=e^(m-k) x^i y^a z^b f^k (k<m, 1<=i<=m-k, b<2) "
    "and h_{k,j}=e^(m-k) y^(a+j) f^k (k<=m, j<=t) with m=8, t=5, a=1, bounds (2^301, 2^256, 2^768): "
    "rank 126 square lattice, DN determinant condition margin ~+46 bits/dim. LLL (fpylll, delta=0.99) "
    "rows divide column scales exactly; nontrivial short rows vanish over Z at (2k,p,q). Extract p via "
    "paper method: substitute z=N/y, resultant in x of two vanishing polys (fraction-free Bareiss over "
    "Z[y]), integer roots; verify p|N, then d=e^-1 mod (p-1)(q-1), m=c^d mod N."
)
res = {"unbalanced-icc_athens2022": {"flag": flag, "derivation": derivation,
                                     "p": str(p), "q": str(q), "d": str(dd)}}
with open(OUT, "w") as f:
    json.dump(res, f, indent=2)
print("wrote", OUT)
