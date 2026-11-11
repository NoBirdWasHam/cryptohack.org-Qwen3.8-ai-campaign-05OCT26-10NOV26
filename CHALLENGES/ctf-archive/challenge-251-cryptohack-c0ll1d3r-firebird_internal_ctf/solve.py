#!/usr/bin/env python3
# C0ll1d3r (Firebird Internal CTF) solver.
# hash(m) = g^int(b'SECUREHASH_'+m) mod p, fresh random 256-bit g and 256-bit prime p
# per connection. Win: send lowercase m != 'pleasegivemetheflag' with same hash.
#
# Step 1 (recover p): exponents e(m) = P*256 + x for 1-char msgs. Pick x so that
#   e_l + e_n = 2*e_m   and   e_l + e_o = e_n + e_m   (108+110=2*109, 108+111=110+109).
# Then p | (h_l*h_n - h_m^2) and p | (h_l*h_o - h_n*h_m) as INTEGERS (both ~2^512),
# and gcd of the two = p (cofactors independent).
# Step 2 (collision): Fermat => m = M mod (p-1) suffices. Find lowercase X of length L
# with int(b'SECUREHASH_'+X) = M mod (p-1): modular knapsack with small digits ->
# CVP in the lattice {v : sum v_i 256^i = 0 mod p-1} (fpylll).
import socket, re, sys, math, time
from gmpy2 import is_prime, invert
from fpylll import IntegerMatrix, LLL, BKZ, CVP

import os
HOST = os.environ.get("CH_HOST", "archive.cryptohack.org")
PORT = int(os.environ.get("CH_PORT", "9391"))
PREF = b'SECUREHASH_'
TARGET = b'pleasegivemetheflag'
P = int.from_bytes(PREF, 'big')
M = int.from_bytes(PREF + TARGET, 'big')

def conn():
    s = socket.create_connection((HOST, PORT), timeout=30)
    s.settimeout(25)
    return s

def readline(s):
    buf = b""
    while b"\n" not in buf:
        d = s.recv(4096)
        if not d:
            break
        buf += d
    return buf

def query(s, msg):
    s.sendall(msg + b"\n")
    line = readline(s)
    m = re.search(rb'([0-9a-f]{64})', line)
    if not m:
        raise RuntimeError("bad response: %r" % line)
    return int(m.group(1), 16)

def exp_of(msg):
    return int.from_bytes(PREF + msg, 'big')

def strip_small(n, lim=100000):
    """remove small prime factors until n is prime"""
    d = 2
    while not is_prime(n):
        f = None
        q = 2
        while q < lim:
            if n % q == 0:
                f = q
                break
            q += 1 if q == 2 else 2
        if f is None:
            return None
        n //= f
    return n

def find_collision(p, L=64, tries=200, bs=40):
    """lowercase X, len L, with int(PREF+X) = M mod (p-1): BKZ + randomized Babai"""
    import random as _random
    N = p - 1
    S = (256**L - 1) // 255
    T = (M - P * 256**L - 109 * S) % N
    A = IntegerMatrix(L, L)
    A[0, 0] = N
    for i in range(1, L):
        A[i, 0] = -(pow(256, i, N))
        A[i, i] = 1
    LLL.reduction(A)
    BKZ.reduction(A, BKZ.Param(bs))
    target = [T] + [0] * (L - 1)
    rows = [[int(A[i, j]) for j in range(L)] for i in range(L)]
    for t in range(tries):
        if t == 0:
            r = [0] * L
        else:  # cheap randomization: shift by one small multiple of a basis vector
            i = _random.randrange(L)
            c = _random.choice([-3, -2, -1, 1, 2, 3])
            r = [c * x for x in rows[i]]
        v = list(CVP.babai(A, [target[j] + r[j] for j in range(L)]))
        d = [target[j] - (v[j] - r[j]) for j in range(L)]
        if all(-12 <= di <= 13 for di in d):
            X = bytes(109 + d[L - 1 - j] for j in range(L))
            m = int.from_bytes(PREF + X, 'big')
            if m % N == M % N and m != M:
                return X
    return None

def attempt():
    s = conn()
    try:
        hl = query(s, b'l')
        hn = query(s, b'n')
        hm = query(s, b'm')
        ho = query(s, b'o')
    except Exception:
        s.close(); raise
    D1 = hl * hn - hm * hm          # e_l+e_n = 2 e_m
    D2 = hl * ho - hn * hm          # e_l+e_o = e_n+e_m
    if D1 == 0 or D2 == 0:
        s.close(); return None, "degenerate D"
    g = math.gcd(abs(D1), abs(D2))
    p = strip_small(g) if not is_prime(g) else g
    if p is None or not (2**250 < p < 2**256) or not is_prime(p):
        s.close(); return None, "p recovery failed (gcd bits=%d)" % g.bit_length()
    # recover g_ (group element) for local verification
    gg = None
    for msg, h in ((b'o', ho), (b'm', hm), (b'n', hn), (b'l', hl)):
        e = exp_of(msg)
        if math.gcd(e, p - 1) == 1:
            cand = pow(h, invert(e, p - 1), p)
            if all(pow(cand, exp_of(mm), p) == hh for mm, hh in ((b'l',hl),(b'n',hn),(b'm',hm),(b'o',ho))):
                gg = cand
                break
    if gg is None:
        s.close(); return None, "g recovery failed"
    if gg % p == 0:
        s.close(); return None, "g=0 degenerate"
    print("  recovered p bits=%d, p%%1e6=%d" % (p.bit_length(), p % 10**6))
    H = pow(gg, M, p)
    for L in (64, 66, 62, 68, 60, 70):
        X = find_collision(p, L)
        if X is None:
            continue
        m = int.from_bytes(PREF + X, 'big')
        if pow(gg, m, p) != H:
            print("  local check failed for L=%d" % L); continue
        # send it (5th query) and read ALL remaining output (flag may come in a
        # second packet after the hash line)
        s.sendall(X + b"\n")
        buf = b""
        t0 = time.time()
        try:
            while time.time() - t0 < 30:
                d = s.recv(4096)
                if not d:
                    break
                buf += d
                if re.search(rb'(firebird|crypto)\{', buf) or buf.count(b"\n") >= 2:
                    break
        except Exception:
            pass
        return buf, None
    s.close(); return None, "no lattice solution"

if __name__ == "__main__":
    for i in range(1, 6):
        print("attempt %d ..." % i)
        try:
            resp, err = attempt()
        except Exception as e:
            print("  error: %r" % e); continue
        if err:
            print("  %s" % err); continue
        print("SERVER: %r" % resp)
        mflag = re.search(rb'(firebird|crypto)\{[^}]*\}', resp or b"")
        if mflag:
            flag = mflag.group(0).decode()
            print("FLAG:", flag)
            open("flag_c0ll1d3r-firebird_internal_ct.txt", "w").write(flag)
            sys.exit(0)
        print("  no flag in response")
    sys.exit(1)
