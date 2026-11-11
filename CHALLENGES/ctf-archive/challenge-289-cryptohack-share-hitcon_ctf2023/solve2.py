#!/usr/bin/env python3
# Share (HITCON CTF 2023) — fast solver v2.
# Flaw: PyCryptodome getRandomRange(0, p-1) returns [0, p-2], so the random
# coefficients a_1..a_{n-1} of the Shamir polynomial are NEVER p-1 mod p.
# With n = p-1 we get shares f(1)..f(p-2); for a candidate r = f(0), the
# degree p-2 interpolant of points {(0,r),(1,y1),...,(p-2,y_{p-2})} is
#   f = r*L_0 + sum_j y_j*L_j   (Lagrange basis over nodes 0..p-2, fixed per p).
# So a_i(r) = r*L0_i + S_i with S = sum y_j L_j. Wrong r survives a round iff
# a_i(r) != p-1 for all i=1..p-2  <=>  r not in K, K = {(p-1-S_i)/L0_i}.
# NOTE: L_0(x) = (x^{p-1}-1)/(x+1)/c = alternating +-1 coeffs -> all nonzero.
# Per round: O(p^2) once (vs O(p^4) in v1). Intersect kill-sets over rounds,
# one prime = s mod p, CRT over ~270 bits of primes, submit.
import sys, os, math, re, socket, time

FOLDER = os.path.dirname(os.path.abspath(__file__))

def small_prime_list(lo, hi):
    def isp(q):
        if q < 2: return False
        d = 2
        while d * d <= q:
            if q % d == 0: return False
            d += 1
        return True
    return [q for q in range(lo, hi + 1) if isp(q)]

def prep(p):
    """Lagrange basis helpers for nodes 0..p-2 mod p.
    Returns (cols, L0inv): cols[i-1][k] = coeff of x^i in L_{k+1};
    L0inv[i-1] = inverse of coeff of x^i in L_0 (i=1..p-2)."""
    Wc = [1]                      # W(x) = prod_{a=0}^{p-2} (x-a)
    for a in range(p - 1):
        new = [(-a * Wc[0]) % p]
        for i in range(1, len(Wc)):
            new.append((Wc[i - 1] - a * Wc[i]) % p)
        new.append(Wc[-1])
        Wc = new
    L = len(Wc)                   # degree p-1
    def basis(j):                 # L_j(x) = (W/(x-j)) / W'(j)
        Q = [0] * (L - 1)
        carry = Wc[-1]
        for i in range(L - 2, -1, -1):
            Q[i] = carry
            carry = (Wc[i] + carry * j) % p   # final carry = W(j) = 0
        d = 0                     # W'(j) = Q(j) via Horner
        for v in reversed(Q):
            d = (d * j + v) % p
        inv = pow(d, p - 2, p)
        return [(v * inv) % p for v in Q]
    L0 = basis(0)
    rows = [basis(j) for j in range(1, p - 1)]
    cols = [[rows[k][i] for k in range(p - 2)] for i in range(1, p - 1)]
    L0inv = [pow(L0[i], p - 2, p) for i in range(1, p - 1)]
    return cols, L0inv

def killset(cols, L0inv, ys, p):
    K = set()
    for col, inv0 in zip(cols, L0inv):
        s = 0
        for a, b in zip(ys, col):
            s += a * b
        K.add(((p - 1 - s) % p) * inv0 % p)
    return K

def solve_prime(p, feeds):
    """feeds: iterable of share lists f(1..p-2). Returns set of surviving r."""
    cols, L0inv = prep(p)
    cands = set(range(p))
    for ys in feeds:
        assert len(ys) == p - 2, f"share count {len(ys)} != {p-2}"
        cands -= killset(cols, L0inv, ys, p)
        if len(cands) <= 1:
            break
    return cands

def crt(residues, moduli):
    x, M = 0, 1
    for r, m in zip(residues, moduli):
        t = (r - x) * pow(M, -1, m) % m
        x += M * t
        M *= m
        x %= M
    return x, M

def plan(margin=8.0):
    primes = small_prime_list(17, 257)
    rounds = [max(3, math.ceil((math.log(p) + margin) * p / (p - 2))) for p in primes]
    return primes, rounds

# ---------------- offline selftest (in-process server replica) -------------
def selftest(margin=8.0, target=262):
    sys.path.insert(0, FOLDER)
    from server import SecretSharing
    from Crypto.Util.number import bytes_to_long
    import os as _os
    secret = bytes_to_long(_os.urandom(32))
    primes, rounds = plan(margin)
    res, mods, bits = [], [], 0.0
    t0 = time.time()
    for p, R in zip(primes, rounds):
        feeds = []
        for _ in range(R):
            feeds.append(SecretSharing(p, p - 1, secret).get_shares()[:-1])
        cands = solve_prime(p, feeds)
        if len(cands) != 1:
            print(f"  p={p}: AMBIGUOUS ({len(cands)} cands)")
            return False
        res.append(cands.pop()); mods.append(p); bits += math.log2(p)
        if bits >= target:
            break
    x, M = crt(res, mods)
    ok = (x == secret)
    print(f"selftest: primes={len(res)} bits={bits:.0f} rounds<= {sum(rounds)} "
          f"time={time.time()-t0:.1f}s  recovered==secret: {ok}")
    return ok

# ---------------- live socket ------------------------------------------------
LIST_RE = re.compile(r"shares = (\[.*?\])")

class Conn:
    def __init__(self, host, port, timeout=35):
        self.s = socket.create_connection((host, port), timeout=timeout)
        self.f = self.s.makefile("rwb")
    def read_until_shares(self):
        while True:
            line = self.f.readline()
            if not line:
                raise EOFError("connection closed")
            m = LIST_RE.search(line.decode(errors="replace"))
            if m:
                return eval(m.group(1), {"__builtins__": {}}, {})
    def finish(self, secret):
        # server reads p AND n before testing primality -> send two throwaway
        # lines (4, 4) so p=4 triggers break, THEN the real secret.
        self.f.write(b"4\n4\n" + str(secret).encode() + b"\n")
        self.f.flush()
        out = b""
        try:
            while True:
                c = self.f.read(1)
                if not c:
                    break
                out += c
                if b"}" in out:
                    break
        except Exception:
            pass
        return out.decode(errors="replace")
    def close(self):
        try: self.s.close()
        except Exception: pass

def run(host, port, margin=10.0, attempts=5):
    primes, rounds = plan(margin)
    for att in range(1, attempts + 1):
        print(f"attempt {att}: connect {host}:{port} margin={margin}", flush=True)
        t0 = time.time()
        conn = None
        try:
            conn = Conn(host, port)
            res, mods, bits = [], [], 0.0
            for p, R in zip(primes, rounds):
                # stream per-prime: no unconsumed backlog before the 30s alarm
                conn.f.write(b"".join(f"{p}\n{p-1}\n".encode() for _ in range(R)))
                conn.f.flush()
                feeds = [conn.read_until_shares() for _ in range(R)]
                cands = solve_prime(p, feeds)
                if len(cands) != 1:
                    raise RuntimeError(f"p={p} ambiguous ({len(cands)} cands)")
                res.append(cands.pop()); mods.append(p); bits += math.log2(p)
                print(f"  [{time.time()-t0:.1f}s] p={p:4d} s mod p = {res[-1]} "
                      f"(bits={bits:.0f})", flush=True)
                if bits >= 290:
                    break
            x, M = crt(res, mods)
            if x >= (1 << 256):
                # a prime resolved wrong (CRT result escaped the 256-bit range)
                raise RuntimeError(f"CRT out of range ({bits:.0f} bits) -> wrong residue, retry")
            txt = conn.finish(x)
            print("  final:", repr(txt[-160:]), flush=True)
            m = re.search(r"(hitcon\{[^}]*\}|crypto\{[^}]*\}|flag\{[^}]*\})", txt)
            if m:
                return m.group(1)
        except (EOFError, OSError, RuntimeError) as e:
            print(f"  attempt {att} failed: {type(e).__name__}: {e}", flush=True)
        finally:
            if conn:
                conn.close()
    return None

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "live"
    if mode == "selftest":
        sys.exit(0 if selftest() else 1)
    else:
        host = sys.argv[2] if len(sys.argv) > 2 else "archive.cryptohack.org"
        port = int(sys.argv[3]) if len(sys.argv) > 3 else 12739
        flag = run(host, port)
        print("FLAG:", flag)
        sys.exit(0 if flag else 1)
