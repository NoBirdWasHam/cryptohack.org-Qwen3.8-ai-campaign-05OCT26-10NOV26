# Local end-to-end test of c_from_pair + decrypt_full
import sys, random, itertools
sys.path.insert(0, ".")
import server
from solve_live import c_from_pair, decrypt_full

random.seed(42)
pub, priv = server.genkey(512)
n, c = pub.n, pub.c
flag = b"crypto{local_test_flag_123}"
while len(flag) < 60: flag += b"\xab"
m = int.from_bytes(flag, "big")
encf = server.encrypt(m, pub)

def q(r, s, t):
    try:
        mm = server.decrypt(server.Enc(r, s, t), pub, priv)
        return server.encrypt(mm, pub).r
    except Exception:
        return None

pairs = []
tries = 0
while len(pairs) < 8 and tries < 200:
    tries += 1
    r = random.randrange(2**500, 2**510)
    rp = q(r, 1, 1)
    if rp is None or rp == r: continue
    pairs.append((r, rp))
facs = {}
for (i,a),(j,b) in itertools.combinations(enumerate(pairs),2):
    g = __import__("math").gcd(abs(a[1]-a[0]), abs(b[1]-b[0]))
    if g > 2**300: facs.setdefault(g, []).append((i,j))
cl = sorted(facs.items(), key=lambda kv: -len(kv[1]))
p = cl[0][0]; qz = n // p
assert p * qz == n and p in (priv.p, priv.q), "factor fail"
print("factors ok")

cp = cq = None
tries = 0
while (cp is None or cq is None) and tries < 60:
    tries += 1
    r = random.randrange(2**500, 2**510)
    r0, r1 = q(r, 1, 0), q(r, 1, 1)
    if r0 is None or r1 is None or r0 == r1: continue
    fp = c_from_pair(r, r0, r1, p); fq = c_from_pair(r, r0, r1, qz)
    for cand, prime, name, cur in ((fp, p, "cp", cp), (fq, qz, "cq", cq)):
        if cand is not None:
            true_c = c % prime
            ok = cand == true_c
            print(name, "query", tries, "correct?", ok)
            if name == "cp" and ok: cp = cand
            if name == "cq" and ok: cq = cand
mf = decrypt_full(encf.r, encf.s, encf.t, __import__("server").__dict__ and ( (cq*p*(pow(p,-1,qz)) + cp*qz*(pow(qz,-1,p))) % n ), priv.p, priv.q)
print("LOCAL FLAG:", mf.to_bytes(96, "big")[:40])
print("MATCH:", mf == m)
