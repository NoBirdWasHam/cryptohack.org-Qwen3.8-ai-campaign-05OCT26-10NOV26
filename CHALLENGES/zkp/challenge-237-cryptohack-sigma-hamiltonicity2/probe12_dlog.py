# probe12: BSGS dlog_{h2}(h1) up to m=2^22 (and inverse direction). If a small relation
# exists between h1,h2 the Pedersen commitments are fully malleable -> challenge breaks.
import gmpy2, time, sys
sys.path.insert(0, r"~/Practice_runs/cryptohack_org/challenge-237-cryptohack-sigma-hamiltonicity2")
from hamiltonicity import P, q, h1, h2
m = 1 << 22
t0 = time.time()
tbl = {}
x = gmpy2.mpz(1)
hm = pow(h2, m, P)
for j in range(m):
    k = int(x)
    if k not in tbl: tbl[k] = j
    x = x * hm % P
print("table built %.0fs, %d entries" % (time.time()-t0, len(tbl)))
target = gmpy2.mpz(h1)
inv_h2 = pow(gmpy2.mpz(h2), -1, P)
for i in range(m):
    k = int(target)
    if k in tbl and tbl[k] > 0:
        d = i * m + tbl[k]
        if pow(h2, d, P) == h1:
            print("FOUND dlog_{h2}(h1) =", d)
            sys.exit(0)
    target = target * inv_h2 % P
    if i % (1 << 18) == 0:
        print("i=%d  %.0fs" % (i, time.time()-t0), flush=True)
print("no dlog < 2^22 (%.0fs)" % (time.time()-t0))
