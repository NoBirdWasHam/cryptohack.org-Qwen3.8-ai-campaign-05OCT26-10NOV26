#!/usr/bin/env python3
# OFFICIAL-method cross-check: the author's exploit.py algorithm (cscbe/CSCBE-2024-WRITE-UPS
# Crypto/Additional Problems/Resources/exploit.py), ported to my buffer-safe client, run against
# the instrumented clone (plog.txt records the server's TRUE p per connection).
# Steps identical to the author's: zero-byte message, add+decrypt until first nonzero byte x,
# residue p = -x mod N; N in 128..159; CRT; flag = chr((c % p) % 2**7).
import sys
sys.path.insert(0, ".")
from solver_oracle2 import Client, handshake, crt   # reuse verified client + CRT

HOST, PORT = "archive.cryptohack.org", 21970

c = Client(HOST, PORT)
cts = handshake(c)
print("flag ciphertexts:", len(cts), flush=True)

mods = {}
for N in range(128, 160):
    if N == 128:
        c.until(b"Choose N: ")
    else:
        c.line("1")
        c.until(b"Choose N: ")
    c.line(str(N))
    c.until(b"Message to encode")
    c.line("00")                       # single ZERO byte, exactly like the official script
    c.until(b"What do you want to do?")
    while True:
        c.line("3")                    # decrypt
        c.until(b"Decrypted message: ")
        seg = c.until(b"What do you want to do?")
        d = seg.split(b"\n")[0].strip()[:2]
        if d != b"00":
            break
        c.line("2")                    # add another zero encryption
        c.until(b"Message to encode")
        c.line("00")
        c.until(b"What do you want to do?")
    mods[N] = N - int(d, 16)           # author's line: p mod N == N - x
print("residues collected:", len(mods), flush=True)

p, mod = crt([(val, N) for N, val in sorted(mods.items())])
print("official-method p =", p, flush=True)

true = int(open("plog.txt").read().splitlines()[-1])
flag = "".join(chr((x % p) % 2**7) for x in cts)
print("server's TRUE p   =", true, flush=True)
print("MATCH:", p == true, "| modulus bits:", mod.bit_length(), flush=True)
print("recovered plaintext:", flag, flush=True)   # planted placeholder string, verification only
