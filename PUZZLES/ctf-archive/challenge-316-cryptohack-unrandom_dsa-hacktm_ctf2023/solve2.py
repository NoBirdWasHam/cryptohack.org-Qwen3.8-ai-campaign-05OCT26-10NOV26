#!/usr/bin/env python3
# unrandom DSA (HackTM) — RESUME v2.
# DSA.construct requires: test_probable_prime(p), test_probable_prime(q), (p-1)%q==0,
# 1<g<p, g^q==1 mod p, y=g^x. q needs 30 MR rounds -> cannot pseudoprime by luck.
# INSTEAD: construct q = prod(1 + a_i*L) (Korselt: each a_i | S=sum a_i, a_i odd
# distinct, S=2 mod 4, L=0 mod 2^(t+1)*lcm(a)) => q is Carmichael AND (p_i-1) | (q-1)/2
# => every base is a STRONG LIAR => any 30 MR bases pass. Then keep only q that also
# pass pycryptodome's deterministic lucas_test(U_{q+1}=0). q's factors ~2^31 =>
# Pohlig-Hellman recovers server x in order-q subgroup. Sign and print flag.
import socket, hashlib, math, random, sys, time
import gmpy2
from gmpy2 import is_prime as gprime

PBITS = 1024

def v2(x):
    c = 0
    while x % 2 == 0:
        x //= 2; c += 1
    return c

def find_pattern(npr, cap=4000):
    import itertools
    for S in range(4, cap, 4):
        if S % 8 != 4: continue
        divs = [a for a in range(1, S) if S % a == 0 and a % 4 != 0]
        if len(divs) < npr: continue
        for c in itertools.combinations(divs, npr):
            if sum(c) == S:
                return S, c
    return None

def build_q(pattern, t=11, r_span=0.25):
    """Find L=2^(t+1)*lcm(a)*r such that all a_i*L+1 prime and q 160-bit. Sieve over r."""
    S, a = pattern
    M0 = (1 << (t + 1))
    for x in a:
        M0 = M0 * x // math.gcd(M0, x)
    prod_a = math.prod(a)
    L0 = round((2 ** 159.5) / prod_a ** (1.0 / len(a)))
    r0 = max(2, L0 // M0)
    r_hi = int(r0 * (1 + r_span))
    # wheel primes
    wp = [7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
    CH = 2_000_000
    found = []
    r = r0
    while r < r_hi and len(found) < 3:
        ch_hi = min(r_hi, r + CH)
        n = ch_hi - r
        ok = bytearray(b'\x01') * n
        for l in wp:
            if M0 % l == 0: continue  # a_i*M0*r+1 never 0 mod l handled below per a_i
            for ai in a:
                if (ai * M0) % l == 0: continue
                bad = (-pow(ai * M0, -1, l)) % l  # r = bad mod l kills factor ai*L+1
                first = bad - r % l
                if first < 0: first += l
                ok[first::l] = b'\x00' * len(ok[first::l])
        for j in range(n):
            if not ok[j]: continue
            rr = r + j
            L = M0 * rr
            facs = [ai * L + 1 for ai in a]
            if all(gprime(f) for f in facs):
                q = math.prod(facs)
                if q.bit_length() == 160 and q % 2:
                    found.append((q, facs, L))
        r = ch_hi
    return found

def make_p(q, rng):
    while True:
        # want p = q*sq + 1 with sq prime (so p-1 fully factored -> primitive root)
        sq = rng.getrandbits(PBITS - 1 - q.bit_length()) | 1
        p = sq * q + 1
        if p.bit_length() == PBITS and gprime(p) and gprime(sq):
            facset = make_p.facs + [sq]
            for h in range(2, 10_000):
                if all(pow(h, (p - 1) // f, p) != 1 for f in facset):
                    g = pow(h, sq, p)  # order exactly q
                    assert pow(g, q, p) == 1 and g != 1
                    return p, g
    make_p.facs = facs

def bsgs_small(gi, yi, p, n):
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

def pohlig_hellman(g, y, p, q, facs):
    x, M = 0, 1
    for l in set(facs):
        e = (p - 1) // l
        xi = bsgs_small(pow(g, e, p), pow(y, e, p), p, l)
        t = ((xi - x) * pow(M, -1, l)) % l
        x += M * t
        M *= l
        x %= M
    assert 0 < x < q and pow(g, x, p) == y, "PH failed"
    return x

def sign(x, q, p, g, rng, msg=b"sign me!"):
    ob = (q.bit_length() + 7) // 8
    z = int.from_bytes(hashlib.sha256(msg).digest()[:ob], "big")
    while True:
        k = rng.randrange(1, q)
        r = pow(g, k, p) % q
        if r == 0 or math.gcd(k, q) != 1: continue
        s_ = (pow(k, -1, q) * (z + x * r)) % q
        if s_ == 0 or math.gcd(s_, q) != 1: continue
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
        if not ch: break
        data += ch if isinstance(ch, str) else ch.decode()
    return data

def build_all():
    import itertools
    from Crypto.Math.Primality import test_probable_prime, PROBABLY_PRIME
    rng = random.Random()
    pats = [(12, (1, 2, 3, 6))]
    pat = find_pattern(6)
    if pat: pats.append(pat)
    for S, a in pats:
        print(f"[+] pattern S={S} a={a}", flush=True)
        for (q, facs, L) in build_q((S, a)):
            from Crypto.Math.Primality import lucas_test, PROBABLY_PRIME as PP
            from Crypto.Math.Numbers import Integer
            t0 = time.time()
            # verify construction: Korselt + v2 + all-base strong liar spot-check
            assert all((q - 1) % (f - 1) == 0 for f in set(facs))
            assert all(v2(f - 1) < v2(q - 1) for f in set(facs))
            if test_probable_prime(q) != PROBABLY_PRIME:
                print(f"    q (L={L}) FAILS test_probable_prime, next", flush=True); continue
            if lucas_test(Integer(q)) != PP:
                print(f"    q (L={L}) fails lucas, next", flush=True); continue
            print(f"[+] q ok ({time.time()-t0:.1f}s) q={q}", flush=True)
            make_p.facs = list(set(facs))
            p, g = make_p(q, rng)
            print(f"[+] p={p}\n[+] g={g}", flush=True)
            return q, p, g, list(set(facs))

def main():
    t0 = time.time()
    q, p, g, facs = build_all()
    print(f"[+] built in {time.time()-t0:.1f}s", flush=True)
    if "--local" in sys.argv:
        import subprocess, os
        env = dict(os.environ, FLAG="FAKEFLAG{local_test_ok}")
        proc = subprocess.Popen([sys.executable, "-u", "server_local.py"],
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=env)
        ask = lambda sub: ask_until(proc.stdout, sub)
        send = lambda line: (proc.stdin.write((line + "\n").encode()), proc.stdin.flush())
        ask("q = "); send(str(q))
        ask("p = "); send(str(p))
        ask("g = "); send(str(g))
        ask("hex"); send("1337")
        y = int(read_to_nl(proc.stdout, ask("y = ")).split("y = ")[1].split()[0])
        x = pohlig_hellman(g, y, p, q, facs)
        print("[*] x =", x, flush=True)
        send(sign(x, q, p, g))
        print("SERVER SAYS:", proc.stdout.read().decode())
        proc.wait()
    else:
        s = socket.create_connection(("archive.cryptohack.org", 2783), timeout=60)
        f = s.makefile("rw", encoding="utf-8", errors="replace")
        def send(line):
            f.write(line + "\n"); f.flush()
        ask_until(f, "q = "); send(str(q))
        ask_until(f, "p = "); send(str(p))
        ask_until(f, "g = "); send(str(g))
        ask_until(f, "hex"); send("1337")
        out = read_to_nl(f, ask_until(f, "y = "))
        y = int(out.split("y = ")[1].split()[0])
        print("[*] y =", y, flush=True)
        x = pohlig_hellman(g, y, p, q, facs)
        print("[*] x =", x, flush=True)
        send(sign(x, q, p, g))
        s.settimeout(60)
        rest = f.read()
        print("SERVER SAYS:", rest, flush=True)
        s.close()

if __name__ == "__main__":
    main()
