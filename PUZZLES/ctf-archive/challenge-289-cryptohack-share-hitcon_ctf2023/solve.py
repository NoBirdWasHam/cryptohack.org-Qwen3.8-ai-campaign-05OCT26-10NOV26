#!/usr/bin/env python3
# Share (HITCON CTF 2023) — solver.
# Leak: PyCryptoDome getRandomRange(0,p-1) yields [0,p-2]: coeffs a_1..a_{n-1}
# never equal p-1 mod p. Given candidate r for s mod p, n-1 shares f(1..n-1)
# plus f(0)=r uniquely interpolate the deg n-1 poly. True r => all coeffs in
# [0,p-2]; wrong r survives w.p. ~ (1-1/p)^(n-1). Intersect over rounds, CRT.
import socket, ast, sys, random, math
from math import prod

HOST = "archive.cryptohack.org"
PORT = 12739

def interp_mod_p(xs, ys, r, p):
    """Coeffs (a0..a_{m-1}) of unique poly deg<=m-1 with f(0)=r, f(xs[i])=ys[i], mod p.
    xs are 1..m-1. Return list or None if impossible (won't happen, matrix invertible)."""
    m = len(xs) + 1
    # Build Vandermonde rows for x=1..m-1 with unknowns a1..a_{m-1}; a0=r moved to rhs.
    # Solve (m-1)x(m-1) system mod p.
    k = m - 1
    if k == 0:
        return [r % p]
    A = []
    b = []
    for j, x in enumerate(xs):
        row = []
        xi = 1
        for i in range(1, m):
            xi = xi * x % p
            row.append(xi)
        A.append(row)
        b.append((ys[j] - r) % p)
    # [flag — recorded in FLAGS/post-quantum/challenge-168-cryptohack-lwe-intro/flag.txt] mod p
    nrow = k
    piv_row = 0
    where = []
    for col in range(k):
        piv = None
        for rr in range(piv_row, nrow):
            if A[rr][col] % p:
                piv = rr
                break
        if piv is None:
            return None
        A[piv_row], A[piv] = A[piv], A[piv_row]
        b[piv_row], b[piv] = b[piv], b[piv_row]
        inv = pow(A[piv_row][col], p - 2, p)
        A[piv_row] = [v * inv % p for v in A[piv_row]]
        b[piv_row] = b[piv_row] * inv % p
        for rr in range(nrow):
            if rr != piv_row and A[rr][col]:
                f = A[rr][col]
                A[rr] = [(A[rr][cc] - f * A[piv_row][cc]) % p for cc in range(k)]
                b[rr] = (b[rr] - f * b[piv_row]) % p
        where.append(piv_row)
        piv_row += 1
    sol = [0] * k
    for col in range(k):
        sol[col] = b[where[col]]
    return [r % p] + sol

def survives(ys, r, p):
    n = len(ys) + 1  # shares are f(1..n-1)
    coeffs = interp_mod_p(list(range(1, n)), ys, r, p)
    if coeffs is None:
        return False
    return all(c <= p - 2 for c in coeffs[1:])

def crt(residues, moduli):
    x = 0
    M = 1
    for r, m in zip(residues, moduli):
        # x + M*t ≡ r mod m
        t = (r - x) * pow(M, -1, m) % m
        x += M * t
        M *= m
        x %= M
    return x, M

def small_primes(lo, hi):
    def isp(q):
        if q < 2: return False
        d = 2
        while d * d <= q:
            if q % d == 0: return False
            d += 1
        return True
    return [q for q in range(lo, hi) if isp(q)]

LIST_RE = __import__("re").compile(r"shares = (\[.*?\])")

class Conn:
    def __init__(self, host, port):
        self.s = socket.create_connection((host, port), timeout=25)
        self.f = self.s.makefile("rwb")
    def _readline(self):
        line = self.f.readline()
        if not line:
            raise EOFError("connection closed")
        return line
    def _read_shares(self):
        while True:
            line = self._readline()
            m = LIST_RE.search(line.decode(errors="replace"))
            if m:
                return eval(m.group(1), {"__builtins__": {}}, {})
    def batch(self, p, n, count):
        # Server prompts "p = "/"n = " with NO newline; send all inputs then
        # read lines until each 'shares = [...]' arrives.
        self.f.write((f"{p}\n{n}\n" * count).encode()); self.f.flush()
        return [self._read_shares() for _ in range(count)]
    def finish(self, secret):
        # composite p -> server breaks loop -> "secret = " prompt (no newline)
        self.f.write(b"4\n" + str(secret).encode() + b"\n"); self.f.flush()
        out = b""
        try:
            while True:
                c = self.f.read(1)
                if not c: break
                out += c
                if b"}" in out: break
        except Exception:
            pass
        return out.decode(errors="replace")
    def close(self):
        try: self.s.close()
        except Exception: pass

def solve_prime(conn, p):
    n = p - 1
    cands = set(range(p))
    q = (1 - 1.0 / p) ** (n - 1)
    rounds = max(3, math.ceil(math.log(max(p, 2)) / -math.log(q)) + 2)
    while rounds > 0:
        send = min(rounds, 8)
        rounds -= send
        for ys in conn.batch(p, n, send):
            if len(ys) != n - 1:
                raise AssertionError(f"share count {len(ys)} != {n-1}")
            cands &= {r for r in cands if survives(ys, r, p)}
        if len(cands) == 1:
            return cands.pop()
        if not cands:
            return None
    return None

def run(host, port, target_bits=270):
    primes = [q for q in small_primes(17, 400)]
    random.Random(1337).shuffle(primes)
    attempt = 0
    while attempt < 6:
        attempt += 1
        conn = Conn(host, port)
        try:
            res, mods = [], []
            total = 0.0
            for p in primes:
                r = solve_prime(conn, p)
                if r is None:
                    print(f"  prime {p}: no unique candidate, skipping", flush=True)
                    continue
                res.append(r); mods.append(p)
                total += math.log2(p)
                if total >= target_bits:
                    break
            if total < target_bits:
                print("  not enough primes; reconnecting", flush=True)
                conn.close()
                continue
            x, M = crt(res, mods)
            txt = conn.finish(x)
            print("  server final:", repr(txt[-140:]), flush=True)
            m2 = __import__("re").search(r"(crypto\{[^}]*\}|flag\{[^}]*\})", txt)
            if m2:
                return m2.group(1)
            conn.close()
        except (EOFError, OSError, AssertionError) as e:
            print("  conn lost:", type(e).__name__, e, flush=True)
            try: conn.close()
            except Exception: pass
    return None

if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else HOST
    port = int(sys.argv[2]) if len(sys.argv) > 2 else PORT
    flag = run(host, port)
    print("FLAG:", flag)
