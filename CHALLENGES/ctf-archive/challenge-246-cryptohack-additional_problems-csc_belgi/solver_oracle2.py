#!/usr/bin/env python3
# CSC Belgium "Additional Problems" (CryptoHack ctf-archive, port 21970) -- DECRYPT-ORACLE SOLVER.
#
# Server facts (from deployed server.py, byte-exact repro on this host):
#   p = getPrime(128) is generated ONCE PER CONNECTION (the 'new' menu item resets only N + accumulator).
#   Flag block: c = p*q + 128*r + m per byte, q = getrandbits(1024), r in [0, 2**119).
#   'new' picks any N in [128,255]; 'add' adds one encryption per byte; 'decrypt' prints (acc mod p) mod N per byte.
#
# Attack: right after 'new' the accumulator is [0]*l, so the baseline decrypt is all zeros.
# After t adds, accumulator per byte = sum(noise_j) + 65*t with each noise_j = N*r_j + 65 < 2**126 + 65, so
#   v_t[j] = (R - w*p) mod N  with  0 <= w <= Kmax(t) ~= t/2 + 2      (because p >= 2**127)
# => d_j := v_t[j] - v0[j] - 65*t (mod N) must equal (-k*c) mod N for some 0 <= k <= Kmax, where c = p mod N.
# Intersect those sets over bytes and steps -> c exactly. Collect c for enough N, CRT (lcm > 2**128) -> p.
# Then plaintext byte = (c_i mod p) mod 128. No flag value lives in this file.
import socket, re, sys
from math import gcd

HOST, PORT = "127.0.0.1", 13337
if len(sys.argv) >= 3:
    HOST, PORT = sys.argv[1], int(sys.argv[2])

MENU = b"What do you want to do?"
CHOOSE = b"Choose N: "
MSG = b"Message to encode"
DEC = b"Decrypted message: "


class Client:
    """Token reader that PRESERVES bytes read past the token, so menu prompts are never lost."""

    def __init__(self, host, port):
        self.s = socket.create_connection((host, port), timeout=90)
        self.fr = self.s.makefile("rb")
        self.fw = self.s.makefile("wb")
        self.buf = b""

    def until(self, tag):
        """Return everything up to AND INCLUDING tag; anything further stays in self.buf."""
        while tag not in self.buf:
            c = self.fr.read(1)
            if not c:
                raise EOFError("closed; tail=" + repr(self.buf[-300:]))
            self.buf += c
        i = self.buf.index(tag) + len(tag)
        out, self.buf = self.buf[:i], self.buf[i:]
        return out

    def line(self, s):
        self.fw.write(s.encode() + b"\n")
        self.fw.flush()


def handshake(c):
    c.until(b"We've even encrypted our secret flag with it:")
    seg = c.until(b"Now you get to encrypt")
    return [int(x) for x in re.findall(rb"\b(\d{200,})\b", seg)]


def dec_once(c):
    """Menu is the live prompt. Send '3'; consume hex payload; leave following menu text buffered."""
    c.line("3")
    c.until(DEC)
    seg = c.until(MENU)
    hx = seg.split(b"\n")[0]
    return bytes.fromhex(hx.decode().strip().replace(" ", ""))


def feasible(ds, Kmax, N):
    """{c in Z_N : for every d in ds there is 0<=k<=Kmax with d == (-k*c) mod N}"""
    out = None
    for d in ds:
        d %= N
        s = set()
        if d == 0:
            s.update(range(N))                     # k = 0 satisfies this byte for every c
        for k in range(1, Kmax + 1):
            g = gcd(k, N)
            if d % g:
                continue
            mm, nn, dd = k // g, N // g, d // g
            base = (-dd * pow(mm, -1, nn)) % nn     # c == base (mod nn)
            for t in range(g):
                s.add(base + t * nn)
        out = s if out is None else (out & s)
        if not out:
            return set()
    return out


def pmodN(c, N, L=24, T=16, first=False):
    """Unique value of p mod N, a candidate list, or None."""
    if first:
        c.until(CHOOSE)                             # first prompt after the flag block
    else:
        c.line("1")                                 # 'new' -- same p, fresh accumulator
        c.until(CHOOSE)
    c.line(str(N))
    c.until(MSG)
    msg = b"A" * L                                  # byte 65 < N always (N >= 128)
    c.line(msg.hex())
    c.until(MENU)

    v0 = dec_once(c)                                 # 'new' does ONE encryption -> w=0 -> v0 == msg
    if list(v0) != [65] * L:
        print(f"  N={N}: baseline decrypt != message echo ({v0[:6].hex()}) -- skipping", flush=True)
        return None

    cands = set(range(N))
    for t in range(1, T + 1):
        c.line("2")                                 # add the same known message
        c.until(MSG)
        c.line(msg.hex())
        v = dec_once(c)
        n_enc = 1 + t                               # 'new' seeded one encryption
        Kmax = (n_enc * (2**126 + 256)) // (2**127) + 2   # per-byte wrap bound (p >= 2**127)
        ds = [(v[j] - v0[j] - 65 * t) % N for j in range(L)]   # v0[j]=65, so = v[j]-65*(1+t)
        cands &= feasible(ds, Kmax, N)
        if not cands:
            print(f"  N={N}: candidates died at step {t} -- skipping", flush=True)
            return None
        if len(cands) == 1:
            return cands.pop()
    return sorted(cands) if cands else None


def crt(pairs):
    r, m = 0, 1
    for a, n in pairs:
        g = gcd(m, n)
        if (a - r) % g:
            raise ValueError(f"inconsistent: {r} mod {m} vs {a} mod {n}")
        mm, nn = m // g, n // g
        t = ((a - r) // g * pow(mm, -1, nn)) % nn
        r, m = r + m * t, m * nn
    return r % m, m


def try_finish(pairs, cts):
    if len(pairs) < 3:
        return None
    try:
        cand, mod = crt(pairs)
    except ValueError as e:
        print("  CRT inconsistent:", e, flush=True)
        return None
    if mod < 2**128 or not (2**127 <= cand < 2**128) or cand % 2 == 0:
        return None
    probe = [chr((x % cand) % 128) for x in cts]
    if len(probe) >= 8 and all(32 <= ord(ch) < 127 for ch in probe):
        return cand, "".join(probe)
    return None


def main():
    c = Client(HOST, PORT)
    cts = handshake(c)
    print("flag ciphertexts:", len(cts), flush=True)

    pairs = []
    for N in range(128, 256):
        try:
            r = pmodN(c, N, first=(N == 128))
        except (EOFError, TimeoutError, OSError) as e:
            print(f"N={N}: link error ({type(e).__name__}) -- reconnecting, p changes, restarting", flush=True)
            c = Client(HOST, PORT)
            cts = handshake(c)
            pairs = []
            continue
        if r is None:
            print(f"N={N}: skipped", flush=True)
            continue
        if isinstance(r, list):
            print(f"N={N}: ambiguous, {len(r)} candidates -- skip", flush=True)
            continue
        pairs.append((r, N))
        print(f"N={N}: p == {r} (mod {N})  [pairs={len(pairs)}]", flush=True)
        done = try_finish(pairs, cts)
        if done:
            p, flag = done
            print("p recovered after N=%d: %d" % (N, p), flush=True)
            print("FLAG:", flag, flush=True)
            return

    done = try_finish(pairs, cts)
    if done:
        print("FINAL:", done[1], flush=True)
    else:
        print(f"collected {len(pairs)} residues; modulus insufficient or verification failed", flush=True)


if __name__ == "__main__":
    main()
