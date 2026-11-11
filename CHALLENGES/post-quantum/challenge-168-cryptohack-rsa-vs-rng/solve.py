# rsa-vs-rng: LCG mod 2^512 (A,B known). P and Q are LCG states g steps apart.
# Q = A^g P + B*(A^g-1)/(A-1) mod 2^512.  P*Q = N -> quadratic in P mod 2^512.
# Hensel-lift roots bit by bit for each gap g; test N % P == 0.
import json
from Crypto.Util.number import long_to_bytes

d = json.load(open("flag_9713440954a452ff8c5e5b05247f19fe.enc"))
N, E, ct = int(d["N"]), int(d["E"]), bytes.fromhex(d["ciphertext"])
MOD = 2**512
A = 2287734286973265697461282233387562018856392913150345266314910637176078653625724467256102550998312362508228015051719939419898647553300561119192412962471189
B = 4179258870716283142348328372614541634061596292364078137966699610370755625435095397634562220121158928642693078147104418972353427207082297056885055545010537
Am1_inv = None
Sg = 0  # (A^g - 1)/(A-1) computed iteratively: S = S*A + 1

def roots_mod_2k(alpha, beta, N, kmax=512):
    # solve alpha*x^2 + beta*x - N = 0 mod 2^kmax by lifting
    cands = [x for x in (0, 1) if (alpha*x*x + beta*x - N) % 2 == 0]
    mod = 2
    for k in range(1, kmax):
        nxt = []
        for x in cands:
            for bit in (0, 1):
                y = x + bit * mod
                if (alpha*y*y + beta*y - N) % (mod*2) == 0:
                    nxt.append(y)
        cands = nxt
        mod *= 2
        if not cands or len(cands) > 64: break
    return cands

alpha = 1
Sg = 0
for g in range(1, 4000):
    alpha = alpha * A % MOD                      # A^g
    Sg = (Sg * A + 1) % MOD                      # 1 + A + ... + A^(g-1)
    beta = B * Sg % MOD
    for P in roots_mod_2k(alpha, beta, N):
        if P > 2 and N % P == 0:
            Q = N // P
            phi = (P-1)*(Q-1)
            pt = pow(int.from_bytes(ct, "big"), pow(E, -1, phi), N)
            flag = long_to_bytes(pt)
            print("gap", g, "FLAG:", flag.decode(errors="replace"))
            open("flag_rsa_vs_rng.txt", "w").write(flag.decode())
            raise SystemExit
    if g % 500 == 0:
        print("g", g, "no hit yet", flush=True)
print("no factor found in g range")
