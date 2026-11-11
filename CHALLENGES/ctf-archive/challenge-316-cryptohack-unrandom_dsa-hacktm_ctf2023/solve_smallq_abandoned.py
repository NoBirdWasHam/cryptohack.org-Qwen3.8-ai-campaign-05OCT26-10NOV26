#!/usr/bin/env python3
# unrandom DSA (HackTM CTF) — we choose (q,p,g); pick a 32-bit subgroup so x
# (uniform in [1,q-1]) is recoverable from y=g^x mod p by BSGS, then forge the
# signature on b"sign me!" ourselves. The os.urandom/seed patch is a decoy:
# SystemRandom.urandom is bound at import time, and the server never signs.
import socket, hashlib, math, random, sys

def find_params(bits=32):
    from sympy import isprime
    rng = random.Random(0)
    while True:
        q = rng.randrange(1 << (bits - 1), 1 << bits) | 1
        if not isprime(q):
            continue
        p = 2 * q + 1
        if not isprime(p):
            continue
        for h in range(2, 100):
            g = pow(h, (p - 1) // q, p)
            if g != 1:
                return q, p, g

def bsgs(g, y, p, q):
    m = math.isqrt(q) + 1
    table = {}
    cur = 1
    for j in range(m):
        table.setdefault(cur, j)
        cur = cur * g % p
    factor = pow(g, -m, p)
    gamma = y
    for i in range(m + 1):
        if gamma in table:
            x = i * m + table[gamma]
            if 1 <= x < q and pow(g, x, p) == y:
                return x
        gamma = gamma * factor % p
    raise ValueError("no x found")

def solve(host, port, q, p, g, msg=b"sign me!"):
    s = socket.create_connection((host, port), timeout=30)
    f = s.makefile("rwb")
    def ask(prompt=None, expect=None):
        data = b""
        while True:
            line = f.readline()
            if not line:
                raise EOFError("closed: " + repr(data))
            data += line
            txt = data.decode(errors="replace")
            if expect and expect in txt:
                return txt
            if not expect and (prompt in txt):
                return txt
    def send(line):
        f.write((line + "\n").encode()); f.flush()
    ask("q = "); send(str(q))
    ask("p = "); send(str(p))
    ask("g = "); send(str(g))
    ask("hex"); send("1337")
    out = ask(expect="y = ")
    y = int(out.split("y = ")[1].split()[0])
    x = bsgs(g, y, p, q)
    ob = (q.bit_length() + 7) // 8
    z = int.from_bytes(hashlib.sha256(msg).digest()[:ob], "big")
    rng = random.SystemRandom()
    while True:
        k = rng.randrange(1, q)
        r = pow(g, k, p) % q
        if r == 0: continue
        s_ = (pow(k, -1, q) * (z + x * r)) % q
        if s_ == 0: continue
        break
    sign = r.to_bytes(ob, "big") + s_.to_bytes(ob, "big")
    ask("sign = "); send(sign.hex())
    rest = f.read().decode(errors="replace")
    s.close()
    return x, rest

if __name__ == "__main__":
    q, p, g = find_params()
    print("params q=%d p=%d g=%d" % (q, p, g))
    if "--local" in sys.argv:
        import subprocess, os, threading, time
        env = dict(os.environ, FLAG="FAKEFLAG{local_test_ok}")
        proc = subprocess.Popen([sys.executable, "-u", "server_local.py"],
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=env)
        # emulate via socket: simpler to just run the attack logic inline
        # (server_local.py reads from stdin; use a pipe-based shim)
        class Shim:
            def __init__(self, proc): self.proc = proc
        # Instead: drive directly with a socket-less variant
        def ask_local(prompt=None, expect=None):
            data = b""
            while True:
                line = proc.stdout.readline()
                if not line: raise EOFError(repr(data))
                data += line
                txt = data.decode()
                if expect and expect in txt: return txt
                if not expect and prompt in txt: return txt
        def send_local(line):
            proc.stdin.write((line + "\n").encode()); proc.stdin.flush()
        ask_local("q = "); send_local(str(q))
        ask_local("p = "); send_local(str(p))
        ask_local("g = "); send_local(str(g))
        ask_local("hex"); send_local("1337")
        out = ask_local(expect="y = ")
        y = int(out.split("y = ")[1].split()[0])
        x = bsgs(g, y, p, q)
        ob = (q.bit_length() + 7) // 8
        z = int.from_bytes(hashlib.sha256(b"sign me!").digest()[:ob], "big")
        k = random.SystemRandom().randrange(1, q)
        r = pow(g, k, p) % q
        s_ = (pow(k, -1, q) * (z + x * r)) % q
        sign = r.to_bytes(ob, "big") + s_.to_bytes(ob, "big")
        ask_local("sign = "); send_local(sign.hex())
        print("SERVER SAYS:", proc.stdout.read().decode())
        proc.wait()
    else:
        x, rest = solve("archive.cryptohack.org", 2783, q, p, g)
        print("x =", x)
        print("SERVER SAYS:", rest)
