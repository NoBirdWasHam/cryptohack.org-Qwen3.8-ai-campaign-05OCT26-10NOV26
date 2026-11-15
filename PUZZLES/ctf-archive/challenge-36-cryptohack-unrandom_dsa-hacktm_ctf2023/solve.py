#!/usr/bin/env python3
# unrandom DSA (HackTM CTF) — CryptoHack archive, archive.cryptohack.org:2783
#
# Server: we supply (q,p,g); x = SystemRandom().randint(1,q-1) (truly random:
# SystemRandom.urandom is bound at import time, before the os.urandom patch);
# it prints y=g^x mod p and verifies OUR signature on b"sign me!".
# DSS.new enforces FIPS (L,N) pairs, so q must be 160/224/256 bits.
#
# Attack: choose q a real 160-bit prime and p = q*s + 1 a 1024-bit prime with
# s squarefree and (p-1)/q-smooth, s > q. Then 0 < x < q < s, so x is fully
# determined by x mod s, and Pohlig-Hellman over the prime factors of s
# (each ~2^24, plain BSGS) recovers x mod s = x. The seeded-MT / patched
# os.urandom is a decoy: no RNG is consumed after random.seed().
import socket, hashlib, math, random, sys
from sympy import isprime

QBITS, PBITS = 160, 1024
FACTOR_LO, FACTOR_HI = 1 << 23, 1 << 25

def build(seed):
    rng = random.Random(seed)
    q = None
    while q is None or not isprime(q):
        q = rng.randrange(1 << (QBITS - 1), 1 << QBITS) | 1
    lo, hi = 1 << (PBITS - 1 - QBITS), 1 << (PBITS - QBITS)
    tries = 0
    while True:
        tries += 1
        s, facs = 2, [2]   # p-1 = q*s must be even (p odd prime)
        while s < (lo >> 25):
            f = rng.randrange(FACTOR_LO, FACTOR_HI) | 1
            if isprime(f) and f != q:
                s *= f; facs.append(f)
        # final factor chosen to land s inside [lo, hi)
        f_lo, f_hi = (lo + s - 1) // s, (hi - 1) // s
        f = None
        for _ in range(300):
            c = rng.randrange(f_lo, f_hi + 1) | 1
            if isprime(c) and c not in facs:
                f = c; break
        if f is None:
            continue
        s *= f; facs.append(f)
        if not (lo <= s < hi and s > q):
            continue
        p = q * s + 1
        if p.bit_length() == PBITS and isprime(p):
            # g must be a PRIMITIVE ROOT mod p (order p-1 = q*s), NOT an
            # order-q element: y=g^x lives in <g>, and only ord(g) divisible
            # by each l|s lets y^((p-1)/l) expose x mod l. DSA.construct /
            # DSS.verify impose no g^q==1 check; the verify identity holds
            # for any g with y=g^x.
            for h in range(2, 1000):
                if all(pow(h, (p - 1) // f, p) != 1 for f in facs + [q]):
                    g = h
                    assert math.prod(facs) == s and pow(g, p - 1, p) == 1
                    return q, p, g, facs, tries

def bsgs_small(gi, yi, p, n):
    """DLOG: gi^x = yi mod p, 0 <= x < n, n ~ 2^24."""
    m = math.isqrt(n) + 1
    table = {}
    cur = 1
    for j in range(m):
        table.setdefault(cur, j)
        cur = cur * gi % p
    factor = pow(gi, -m, p)
    gamma = yi
    for i in range(m + 1):
        if gamma in table:
            x = i * m + table[gamma]
            if x < n and pow(gi, x, p) == yi:
                return x
        gamma = gamma * factor % p
    raise ValueError("dlog failed")

def pohlig_hellman(g, y, p, q, s_factors):
    """Recover x (0<x<q<s) from y=g^x mod p using smooth s | p-1, x < s."""
    x, M = 0, 1
    for l in s_factors:
        gi = pow(g, (p - 1) // l, p)
        yi = pow(y, (p - 1) // l, p)
        xi = bsgs_small(gi, yi, p, l)
        t = ((xi - x) * pow(M, -1, l)) % l
        x += M * t
        M *= l
        x %= M
    assert 0 < x < q and pow(g, x, p) == y, "PH failed"
    return x

def sign(x, q, p, g, msg=b"sign me!"):
    ob = (q.bit_length() + 7) // 8
    z = int.from_bytes(hashlib.sha256(msg).digest()[:ob], "big")
    rng = random.SystemRandom()
    while True:
        k = rng.randrange(1, q)
        r = pow(g, k, p) % q
        if r == 0: continue
        s_ = (pow(k, -1, q) * (z + x * r)) % q
        if s_ == 0: continue
        return (r.to_bytes(ob, "big") + s_.to_bytes(ob, "big")).hex()

def ask_until(f, sub):
    data = ""
    while sub not in data:
        ch = f.read(1)
        if not ch:
            raise EOFError("closed: " + repr(data))
        data += ch if isinstance(ch, str) else ch.decode()
    return data

def read_to_nl(f, data):
    while not data.endswith("\n"):
        ch = f.read(1)
        if not ch:
            break
        data += ch if isinstance(ch, str) else ch.decode()
    return data

def run(host, port, q, p, g, facs):
    s = socket.create_connection((host, port), timeout=60)
    f = s.makefile("rw", encoding="utf-8", errors="replace")
    def ask(sub):
        return ask_until(f, sub)
    def send(line):
        f.write(line + "\n"); f.flush()
    ask("q = "); send(str(q))
    ask("p = "); send(str(p))
    ask("g = "); send(str(g))
    ask("hex"); send("1337")
    out = read_to_nl(f, ask("y = "))
    y = int(out.split("y = ")[1].split()[0])
    print("[*] y =", y, flush=True)
    x = pohlig_hellman(g, y, p, q, facs)
    print("[*] x =", x, flush=True)
    send(sign(x, q, p, g))
    rest = f.read().decode(errors="replace")
    s.close()
    return rest

if __name__ == "__main__":
    q, p, g, facs, tries = build(0xC0FFEE)
    s = math.prod(facs)
    print(f"[+] q={q}\n[+] p={p}\n[+] g={g}\n[+] s={s} bits={s.bit_length()} factors={len(facs)} tries={tries}", flush=True)
    if "--local" in sys.argv:
        import subprocess, os
        env = dict(os.environ, FLAG="FAKEFLAG{local_test_ok}")
        proc = subprocess.Popen([sys.executable, "-u", "server_local.py"],
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=env)
        def ask(sub):
            return ask_until(proc.stdout, sub)
        def send(line):
            proc.stdin.write((line + "\n").encode()); proc.stdin.flush()
        ask("q = "); send(str(q))
        ask("p = "); send(str(p))
        ask("g = "); send(str(g))
        ask("hex"); send("1337")
        y = int(read_to_nl(proc.stdout, ask("y = ")).split("y = ")[1].split()[0])
        x = pohlig_hellman(g, y, p, q, facs)
        send(sign(x, q, p, g))
        print("SERVER SAYS:", proc.stdout.read().decode())
        proc.wait()
    else:
        print("SERVER SAYS:", run("archive.cryptohack.org", 2783, q, p, g, facs))
