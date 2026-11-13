# Mini end-to-end: full challenge structure at small scale, tests digit-sum J, P/Q, GP-BM, AES.
import json, math, hashlib, subprocess, random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# ---- mini field & recurrences (mirroring functional.sage exactly) ----
MP = 10**15 + 37  # "p"
LEN = 8
random.seed(7)
COEFFS = [random.randrange(MP) for _ in range(LEN)]
cg = [int(10000*math.log10(2+i)) % MP for i in range(6)]
ch = [int(10000*math.log10(1337+i)) % MP for i in range(4)]
ci = [int(10000*math.log10(31337+i)) % MP for i in range(5)]
G = {n: int(10000*math.sin(LEN+n)) % MP for n in range(6)}
H = {n: int(10000*math.sin(LEN+6+n)) % MP for n in range(3)}
I = {n: int(10000*math.sin(LEN+9+n)) % MP for n in range(3)}
for n in range(3, 200000):
    I[n] = (ci[0]*I[n-2] + ci[1]*G[n-3] + ci[2]*H[n-3] + ci[3]*H[n-1] + ci[4]*I[n-1] + 1) % MP
    H[n] = (ch[0]*H[n-3] + ch[1]*I[n-1] + ch[2]*G[n-2] + ch[3]*H[n-1] + n) % MP
    if n >= 6:
        G[n] = (cg[0]*G[n-6] + cg[1]*H[n-2] + cg[2]*I[n-3] + cg[3]*G[n-3] + cg[4]*H[n-4] + cg[5]*I[n] + 2*n**3 + 42) % MP

# mini j: threshold B0=40, taps n-30-i (i 0..9), weights b_i; digit base 7 (<40 => 2 digits)
B0, T0, W, BASE = 40, 30, 10, 7
b = [int(10000*math.log(31337+i)) % MP for i in range(W)]
S3 = [I[n + 0] for n in range(BASE)]  # placeholder digits source: i(k)
S3 = [I[9973 + k] for k in range(BASE)]  # arbitrary 7 values standing in for S3[d]
def jseq(NMAX):
    Js = {}
    for n in range(B0):
        ds = []
        m = n
        while m: ds.append(m % BASE); m //= BASE
        if not ds: ds = [0]
        Js[n] = sum(S3[d] for d in ds) % MP
    for n in range(B0, NMAX):
        Js[n] = sum(b[i]*Js[n-T0-i] for i in range(W)) % MP
    return Js
Jt = jseq(B0 + 60000)
IT = B0 + 51234
print("true j(IT) =", Jt[IT])

# ---- pipeline (mirror of my solver): J init with digits INCLUDING n=0 -> [0] ----
J = []
for n in range(B0):
    d0 = n % BASE; d1 = n // BASE
    J.append((S3[d0] + (S3[d1] if d1 else 0)) % MP)  # NOTE digits(0)=[] ; d1=0 only when n<BASE
# digits: n<BASE -> [d0]; n in [BASE,40) -> [d0, d1]
J = []
for n in range(B0):
    if n == 0: J.append(0)
    elif n < BASE: J.append(S3[n % BASE] % MP)
    else: J.append((S3[n % BASE] + S3[n // BASE]) % MP)
Q = [0]*(T0+W); Q[0] = 1
for i in range(W): Q[T0+i] = (-b[i]) % MP
P = J[:]
for k in range(T0, B0):
    P[k] = (J[k] - sum(b[i]*J[k-T0-i] for i in range(0, k-T0+1))) % MP
# BM (python, same as GP semantics)
def bm_coeff(Pp, Qq, n, mod):
    Pp = Pp[:]; Qq = Qq[:]
    while n:
        Qm = [(c if e % 2 == 0 else (-c) % mod) for e, c in enumerate(Qq)]
        d = len(Pp) + len(Qq) - 1
        S = [0]*d
        for e2, c2 in enumerate(Qm):
            if c2:
                for j, c in enumerate(Pp):
                    if c: S[j+e2] = (S[j+e2] + c*c2) % mod
        st = 0 if n % 2 == 0 else 1
        Pp = S[st::2]
        S2 = [0]*(len(Qq)*2)
        for e1, c1 in enumerate(Qq):
            if c1:
                for e2, c2 in enumerate(Qm):
                    if c2 and (e1+e2) % 2 == 0:
                        S2[(e1+e2)//2] = (S2[(e1+e2)//2] + c1*c2) % mod
        # trim
        while len(S2) > 1 and S2[-1] == 0: S2.pop()
        Qq = S2
        n >>= 1
    return Pp[0] * pow(Qq[0], -1, mod) % mod
got = bm_coeff(P, Q, IT, MP)
print("pipeline j(IT) =", got, "MATCH:", got == Jt[IT])
# AES sanity
flag = b"CH{mini_flag_check}"
key = hashlib.sha256(str(Jt[IT]).encode()).digest()
ct = AES.new(key, AES.MODE_ECB).encrypt(pad(flag, 16))
pt = AES.new(hashlib.sha256(str(got).encode()).digest(), AES.MODE_ECB).decrypt(ct)
print("decrypted:", pt)
