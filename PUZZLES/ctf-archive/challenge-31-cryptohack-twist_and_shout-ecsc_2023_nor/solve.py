"""Invalid-curve solver for twist_and_shout-ecsc_2023_nor.
Twist order is squarefree: 3*79*644899*1283505703*19385376821*89480282251.
Model twist subgroup as E(F_{q^2}) points with x in F_q, y = c*w, w^2=xi.
BSGS per factor -> e = +/-d mod l; CRT over 2^6 sign choices; ASCII check.
"""
import math, itertools, sys
from sympy import sqrt_mod
from sympy.ntheory.modular import crt

q = 2**128 - 159
a, b = 1, 1494
NT = 340282366920938463461745030229583898519
FACTORS = [3, 79, 644899, 1283505703, 19385376821, 89480282251]

xi = 2
while pow(xi, (q - 1) // 2, q) != q - 1:
    xi += 1
INV_XI = pow(xi, -1, q)

def is_qr(t):
    return t != 0 and pow(t, (q - 1) // 2, q) == 1

# twist-form point: None (infinity) or (x:int, c:int) meaning (x, c*w)
def padd(P, Q):
    if P is None: return Q
    if Q is None: return P
    x1, c1 = P; x2, c2 = Q
    if x1 == x2:
        if (c1 + c2) % q == 0: return None
        m = (3 * x1 * x1 + a) * pow(xi * 2 * c1 % q, -1, q) % q
    else:
        m = (c2 - c1) * pow(x2 - x1, -1, q) % q
    x3 = (xi * m * m - x1 - x2) % q
    c3 = (m * (x1 - x3) - c1) % q
    return (x3, c3)

def smul(P, m):
    R = None
    while m > 0:
        if m & 1: R = padd(R, P)
        P = padd(P, P)
        m >>= 1
    return R

def fnegc(P): return None if P is None else (P[0], (-P[1]) % q)

def find_gen(l):
    """twist x-coordinate + generator of order l subgroup."""
    x = 1
    while True:
        f = (x**3 + a * x + b) % q
        if f != 0 and not is_qr(f):
            c = sqrt_mod(f * INV_XI % q, q)
            P = (x, c)
            Q = smul(P, NT // l)
            if Q is not None and smul(Q, l) is None:
                return Q[0], Q
        x += 1

class Table:
    def __init__(self, l, Q):
        self.l, self.Q = l, Q
        self.B = math.isqrt(l) + 1
        self.tab = {None: 0}
        cur = None
        for j in range(1, self.B + 1):
            cur = padd(cur, Q)
            if cur not in self.tab:
                self.tab[cur] = j
        self.step = fnegc(smul(Q, self.B))
    def dlog_sign(self, T):
        """return e with T = [e]Q or T=[-e]Q ... e = +/-d mod l either way."""
        cur = T
        for i in range(self.B + 2):
            j = self.tab.get(cur)
            if j is not None:
                return (i * self.B + j) % self.l
            cur = padd(cur, self.step)
        raise RuntimeError("no match")

def build_tables():
    ctxs = []
    for l in FACTORS:
        x, Q = find_gen(l)
        ctxs.append((l, x, Table(l, Q)))
        print(f"factor {l}: x={x} B={math.isqrt(l)+1}", flush=True)
    return ctxs

def target_from_x(xd):
    f = (xd**3 + a * xd + b) % q
    if f == 0 or is_qr(f):
        return None
    return (xd % q, sqrt_mod(f * INV_XI % q, q))

def recover_d(residue_pairs):
    """residue_pairs: list of (l, [r1, r2]) -> list of ASCII candidates."""
    out = []
    for combo in itertools.product(*[p for _, p in residue_pairs]):
        res = crt(FACTORS, list(combo))
        if res is None: continue
        d0, M = res  # sympy returns (solution, modulus)
        if d0 is None or d0 == 0: continue
        L = (d0.bit_length() + 7) // 8
        try:
            bs = d0.to_bytes(L, "big")
        except OverflowError:
            continue
        if all(32 <= ch < 127 for ch in bs):
            out.append((d0, bs.decode()))
    return out

def solve_with_oracle(ctxs, oracle):
    rps = []
    for l, x, tbl in ctxs:
        try:
            xd = oracle(x)
        except ValueError:
            xd = None  # [d]Q = O -> pow(0,-1) -> d = 0 mod l
        if xd is None:  # service died on pow(0,-1) -> d = 0 mod l
            rps.append((l, [0]))
            continue
        T = target_from_x(xd)
        if T is None:
            raise RuntimeError(f"unexpected residue status for l={l}")
        e = tbl.dlog_sign(T)
        rps.append((l, sorted({e % l, (-e) % l})))
    return recover_d(rps)

if __name__ == "__main__":
    import time
    mode = sys.argv[1] if len(sys.argv) > 1 else "test"
    t0 = time.time()
    ctxs = build_tables()
    print(f"tables built in {time.time()-t0:.1f}s", flush=True)
    if mode == "test":
        import importlib.util
        spec = importlib.util.spec_from_file_location("ts", "twist_and_shout.py")
        ts = importlib.util.module_from_spec(spec); spec.loader.exec_module(ts)
        ok = 0
        for i in range(20):
            body = "fk" + "abcdefghijklmnop"[:3 + i % 8] + str(i)  # keep d < 2^128
            flag = "ECSC{" + body + "}"
            d = ts.gen_secret(flag)
            try:
                oracle = lambda xv: ts.shout(xv, d)
                cands = solve_with_oracle(ctxs, oracle)
            except ValueError:
                ok += 0; print("skip (d=0 mod l case)", flag); continue
            hit = any(c[0] == d for c in cands)
            ok += hit
            if not hit: print("FAIL", flag, cands[:3])
        print(f"local round-trip: {ok}/20 in {time.time()-t0:.1f}s")
    elif mode == "live":
        import socket
        buf = b""
        def connect():
            global buf
            s = socket.create_connection(("archive.cryptohack.org", 11718), timeout=60)
            b2 = b""
            while b"x-coordinate: " not in b2:
                c = s.recv(4096)
                if not c: raise RuntimeError("closed")
                b2 += c
            buf = b2[b2.index(b"x-coordinate: ")+14:]
            return s
        s = connect()
        def read_until(tag):
            global buf, s
            while tag.encode() not in buf:
                chunk = s.recv(4096)
                if not chunk: raise RuntimeError("conn closed")
                buf += chunk
            i = buf.index(tag.encode()); out, buf = buf[:i], buf[i+len(tag):]
            return out
        def oracle(xv):
            global s
            for _ in range(2):
                try:
                    s.sendall((str(xv) + "\n").encode())
                    return int(read_until(b"x-coordinate: ").decode().strip())
                except Exception:
                    s = connect()
            return None
        cands = solve_with_oracle(ctxs, oracle)
        print(cands)
