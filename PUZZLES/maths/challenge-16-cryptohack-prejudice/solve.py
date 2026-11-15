#!/usr/bin/env python3
# prejudice (98): server returns FLAG[:pow(a,p-1,p)] for user-chosen (a,p),
# p prime, 600 < bits(p) <= 900, a < p, MR(basis 64).
# pow(a,p-1,p) = 1 + ((p-1) mod ord_p(a)), so choose p = 1 mod n (n=k+1) and a of
# exact order n  ->  x = k  ->  response = FLAG[:k]. Sweep k=0..40, union prefixes.
import gmpy2, json, socket, sys

def order_ok(a, n, p):
    # ord_p(a) == n  iff  a^n=1 and a^(n/q)!=1 for all prime q | n
    if pow(a, n, p) != 1:
        return False
    m, q = n, 2
    while m > 1:
        if m % q == 0:
            if pow(a, n // q, p) == 1:
                return False
            while m % q == 0:
                m //= q
        q += 1
    return True

def make(k):
    n = k + 1
    while True:
        # p = 1 mod n, ~601 bits
        t = gmpy2.mpz_random(gmpy2.random_state(), 2**600 // n + 1)
        p = t * n + 1
        if p.bit_length() <= 600:
            continue
        if not gmpy2.is_prime(p):
            continue
        for a in range(2, 200):
            if order_ok(a, n, p):
                return p, a
        # rare: no small a works with this p; try another p

def query(p, a):
    s = socket.create_connection(("socket.cryptohack.org", 13385), timeout=30)
    f = s.makefile("rwb")
    hello = f.readline()
    f.write((json.dumps({"prime": int(p), "base": int(a)}) + "\n").encode())
    f.flush()
    resp = json.loads(f.readline().decode())
    f.close(); s.close()
    return resp["Response"]

best = ""
ks = list(range(0, 41)) if len(sys.argv) < 2 else [int(x) for x in sys.argv[1:]]
for k in ks:
    if k == 0:
        p, a = make(0) if False else (None, None)
        # x=0: a=1 -> pow=1? no: pow(1,p-1,p)=1 -> x=1. x=0 needs p|a: p<a fails check.
        # k=0 unreachable; prefixes from k=1 suffice (FLAG[:1] = 'c').
        continue
    p, a = make(k)
    r = query(p, a)
    if "Success" not in r:
        print(k, "FAIL:", r); continue
    pref = r.split("flag: ", 1)[1].strip()
    if len(pref) > len(best):
        best = pref
    print(f"k={k} len={len(pref)} a={a} -> {pref!r}", flush=True)
print("BEST:", best)
