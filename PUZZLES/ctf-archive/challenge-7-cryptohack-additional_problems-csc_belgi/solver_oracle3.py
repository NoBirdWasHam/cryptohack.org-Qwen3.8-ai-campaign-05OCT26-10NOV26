#!/usr/bin/env python3
# CSC Belgium "Additional Problems" — solver v3 (official-method-based, hardened).
#
# Core (author-verified) principle: with a ZERO-byte message, decrypt prints (sum(noise) - w*p) mod N.
# Noise per add = N*r_j < 2**126 < p/2, so at most ONE new wrap can occur between two decryptions:
# at the FIRST decryption where a byte is nonzero, that byte's coordinate has wrapped EXACTLY once
# => x = (-p) mod N  => p mod N = N - x.  All nonzero bytes at that first nonzero decryption must
# agree — up to L independent votes per N.
# One N alone is never enough (p is 128-bit); collect for N = 128..255 and CRT (lcm >> 2**128).
# Then plaintext byte = (c_flag mod p) mod 128 (flag-block noise provably unwrapped).
# No flag value lives in this file; only self-derived/service-printed plaintext is printed.
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
    """Token reader preserving bytes past the token (menu prompts are never lost)."""

    def __init__(self, host, port):
        self.s = socket.create_connection((host, port), timeout=90)
        self.fr = self.s.makefile("rb")
        self.fw = self.s.makefile("wb")
        self.buf = b""

    def until(self, tag):
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


def dec_bytes(c):
    c.line("3")
    c.until(DEC)
    seg = c.until(MENU)
    hx = seg.split(b"\n")[0]
    return bytes.fromhex(hx.decode().strip().replace(" ", ""))


def residue(c, N, L=24, max_steps=40, first=False):
    """p mod N via first-nonzero unanimous vote; None if no wrap within budget."""
    if first:
        c.until(CHOOSE)
    else:
        c.line("1")
        c.until(CHOOSE)
    c.line(str(N))
    c.until(MSG)
    zero = "00" * L
    c.line(zero)
    c.until(MENU)
    v = dec_bytes(c)
    if any(v):
        print(f"  N={N}: baseline nonzero {v[:4].hex()} -- assumption broke", flush=True)
        return None
    for step in range(1, max_steps + 1):
        c.line("2")
        c.until(MSG)
        c.line(zero)
        c.until(MENU)
        v = dec_bytes(c)
        nz = {j: x for j, x in enumerate(v) if x}
        if nz:
            res = {(N - x) % N for x in nz.values()}
            if len(res) != 1:
                print(f"  N={N}: vote split {sorted(res)} ({len(nz)} bytes) -- DISCARD", flush=True)
                return None
            return res.pop(), len(nz), step
    return None


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
    if not pairs:
        return None
    try:
        cand, mod = crt(pairs)
    except ValueError as e:
        print("  CRT inconsistent:", e, "(resuming from last clean residue)", flush=True)
        return ("inconsistent", mod)
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

    pairs, first = [], True
    for N in range(128, 256):
        try:
            r = residue(c, N, first=first)
            first = False
        except (EOFError, TimeoutError, OSError) as e:
            print(f"N={N}: link error ({type(e).__name__}) -- new session, p resets, restarting", flush=True)
            c = Client(HOST, PORT)
            cts = handshake(c)
            pairs, first = [], True
            continue
        if r is None:
            continue
        res, votes, step = r
        pairs.append((res, N))
        print(f"N={N}: p = {res} (mod {N})   [{votes}-byte unanimous, wrapped at step {step}, pairs={len(pairs)}]", flush=True)
        done = try_finish(pairs, cts)
        if done and done[0] != "inconsistent":
            p, flag = done
            print(f"p = {p}", flush=True)
            print("FLAG:", flag, flush=True)
            return

    done = try_finish(pairs, cts)
    if done and done[0] != "inconsistent":
        print("FINAL:", done[1], flush=True)
    else:
        _, mod = crt(pairs) if pairs else (0, 1)
        print(f"ended with {len(pairs)} residues, modulus {mod.bit_length()} bits -- short", flush=True)


if __name__ == "__main__":
    main()
