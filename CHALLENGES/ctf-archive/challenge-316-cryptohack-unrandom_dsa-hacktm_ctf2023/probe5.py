#!/usr/bin/env python3
# Determinism fingerprint (fast I/O like probe2): same params+seed twice, then diff seed.
import socket, random
from sympy import isprime

rng = random.Random(7)
q = None
while q is None or not isprime(q):
    q = rng.randrange(1 << 159, 1 << 160) | 1
while True:
    k = rng.getrandbits(864)
    p = k * q + 1
    if p.bit_length() == 1024 and isprime(p):
        break
h = 2
while pow(h, (p - 1) // 2, p) == 1:
    h += 1
g = pow(h, k, p)
print("params ready")

def get_y(seed):
    s = socket.create_connection(("archive.cryptohack.org", 2783), timeout=30)
    f = s.makefile("rw", encoding="utf-8", errors="replace")
    def ask(sub):
        data = ""
        while sub not in data:
            ch = f.read(1)
            if not ch:
                return data + "<<EOF>>"
            data += ch
        return data
    def send(line):
        f.write(line + "\n"); f.flush()
    ask("q = "); send(str(q))
    ask("p = "); send(str(p))
    ask("g = "); send(str(g))
    ask("hex"); send(hex(seed)[2:])
    data = ""
    s.settimeout(25)
    try:
        while "sign = " not in data:
            ch = f.read(1)
            if not ch: break
            data += ch
    except Exception as e:
        data += f"<<{type(e).__name__}>>"
    s.close()
    return data

outs = [get_y(0x1337), get_y(0x1337), get_y(0x42)]
for o in outs:
    print(o[:100])
print("same seed twice equal:", outs[0] == outs[1])
print("diff seed differs:", outs[0] != outs[2])
