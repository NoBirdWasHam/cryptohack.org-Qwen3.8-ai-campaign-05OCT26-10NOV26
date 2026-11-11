#!/usr/bin/env python3
# CSC Belgium "Additional Problems" (CryptoHack ctf-archive, port 21970) — DECRYPT-ORACLE SOLVER.
# Key facts: p fixed per connection; N selectable via menu 'new'; decrypt prints (c mod p) mod N per byte.
# Accumulate known message M: decrypted value = (N*R + M - w*p) mod N, w = #wraps of the sum past multiples of p.
# For small per-step w-ranges, each observation constrains p mod N; intersect over coords/steps; do for all
# N in [128,255]; CRT(lcm 2^7, 3^5, 5^3, 7^2, 11^2, 13^2, all primes<=255...) > 2^128 => exact p. Flag = (c_i mod p) mod 128.
import socket, re, sys, math
from functools import reduce

HOST, PORT = "127.0.0.1", 13337
if len(sys.argv) >= 3:
    HOST, PORT = sys.argv[1], int(sys.argv[2])

class Client:
    def __init__(self, host, port):
        self.s = socket.create_connection((host, port), timeout=30)
        self.f = self.s.makefile("rwb")
        self.buf = b""
    def until(self, tag):
        while tag not in self.buf:
            c = self.f.read(1)
            if not c: raise EOFError(self.buf[-200:])
            self.buf += c
        i = self.buf.rindex(tag)
        out = self.buf; self.buf = b""
        return out
    def line(self, s):
        self.f.write(s.encode() + b"\n"); self.f.flush()

def parse_dec(seg):
    m = re.search(rb"Decrypted message: ([0-9a-f ]+)", seg)
    return bytes.fromhex(m.group(1).replace(b" ", b"").decode())

def pmodN(csock, N, L=8, T=12, first=False):
    """constrain p mod N: fresh 'new' (keeps same p), accumulate L-byte constant message, decrypt after each add."""
    if first:
        csock.until(b"Choose N: ")           # very first menu item after the ciphertext block
    else:
        csock.line("1")                      # new encryption (p unchanged); menu prompt already consumed
        csock.until(b"Choose N: ")
    csock.line(str(N))
    csock.until(b"Message to encode")
    msg = b"A" * L                      # byte 65 < 128 <= N OK
    csock.line(msg.hex())
    csock.until(b"What do you want to do?")
    def dec_once():
        csock.line("3")
        csock.until(b"Decrypted message: ")
        seg = csock.until(b"What do you want to do?")
        hx = seg.split(b"\n")[0]
        return bytes.fromhex(hx.decode().strip().replace(" ", ""))
    v0 = dec_once()
    cands = None
    Kmax = 0
    for t in range(T):
        csock.line("2")                  # add
        csock.until(b"Message to encode")
        csock.line(msg.hex())
        v = dec_once()
        Kmax += (2 * L) // 8 + 2        # upper bound on wraps this step (avg noise 2^125 / p>=2^127 -> ~L/8)
        newc = None
        for c in range(N):
            ok = True
            for j in range(L):
                d = (v[j] - v0[j] - 65 * (t + 1)) % N   # remove known accumulated plaintext; d = -k*p mod N
                found = False
                acc = 0
                for k in range(Kmax + 1):
                    if acc == d: found = True; break
                    acc = (acc + c) % N
                if not found: ok = False; break
            if ok:
                newc = newc | {c} if newc is not None else {c}
        cands = newc
        if cands is None or len(cands) == 0:
            return None
        if len(cands) == 1:
            return cands.pop()
    return sorted(cands) if cands else None

def crt(pairs):
    # pairwise CRT over possibly non-coprime moduli (consistent)
    r, m = 0, 1
    for a, n in pairs:
        # solve r + m*t = a mod n
        from math import gcd
        g = math.gcd(m, n)
        if (a - r) % g: raise ValueError("inconsistent CRT")
        # t = ((a-r)/g) * inv(m/g, n/g) mod n/g
        mm, nn = m // g, n // g
        t = ((a - r) // g * pow(mm, -1, nn)) % nn
        r = r + m * t
        m = m * nn
    return r % m, m

def main():
    global sock
    sock = Client(HOST, PORT)
    head = sock.until(b"We've even encrypted our secret flag with it:")
    # ciphertext block until blank/menu
    seg = sock.until(b"Now you get to encrypt")
    cts = [int(x) for x in re.findall(rb"\b(\d{200,})\b", seg)]
    print("flag ciphertexts:", len(cts))
    pairs = []
    for N in range(128, 256):
        r = pmodN(sock, N, first=(N == 128))
        if r is None:
            print(f"N={N}: FAILED (empty candidate set)"); continue
        if isinstance(r, list):
            print(f"N={N}: ambiguous {r[:5]}... len={len(r)} — skip")
            continue
        pairs.append((r, N))
        print(f"N={N}: p mod N = {r}  (pairs={len(pairs)})", flush=True)
        if len(pairs) >= 4:
            try:
                cand, mod = crt(pairs)
                if cand.bit_length() > 128:  # lcm grew past p range? keep collecting
                    pass
            except ValueError as e:
                print("CRT inconsistent at", N, e)
        # early exit once modulus covers p and cand is a verified prime decrypting flag block
        try:
            cand, mod = crt(pairs)
            if mod >= 2**128:
                p = cand % mod
                if p < 2**127: p += 0
                # try p candidates p, p+? within [2^127,2^128)
                ok = True
                for c in cts[:8]:
                    m = (c % p) % 128
                    if not (32 <= m < 127): ok = False; break
                if ok and (p % 2 == 1):
                    flag = "".join(chr((c % p) % 128) for c in cts)
                    if len(flag) >= 8:
                        print("p recovered (modulus covered):", p)
                        print("FLAG:", flag)
                        return
        except Exception as e:
            print("crt early err", e)
    cand, mod = crt(pairs)
    p = cand % mod
    while p < 2**127: p += mod
    print("final p:", p, "modulus bits:", mod.bit_length())
    flag = "".join(chr((c % p) % 128) for c in cts)
    print("FLAG:", flag)

if __name__ == "__main__":
    main()
