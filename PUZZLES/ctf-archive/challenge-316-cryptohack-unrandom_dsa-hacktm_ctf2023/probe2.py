#!/usr/bin/env python3
# Probe 2: valid (1024,160) params; observe full deployed flow.
import socket, random
from sympy import isprime

rng = random.Random(42)
q = None
while q is None or not isprime(q):
    q = rng.randrange(1 << 159, 1 << 160) | 1
# p = k*q+1 prime, 1024 bits
k = None
while True:
    k = rng.randrange(1 << 863, 1 << 864)
    p = k * q + 1
    if p.bit_length() == 1024 and isprime(p):
        break
g = None
for h in range(2, 100):
    gg = pow(h, k, p)
    if gg != 1:
        g = gg; break

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

print(repr(ask("q = "))); send(str(q))
print(repr(ask("p = "))); send(str(p))
print(repr(ask("g = "))); send(str(g))
print(repr(ask("hex"))); send("1337")
data = ""
import time
s.settimeout(20)
try:
    while True:
        ch = f.read(1)
        if not ch: break
        data += ch
except Exception as e:
    data += f"<<{type(e).__name__}>>"
print("AFTER SEED:", repr(data))
# if it waits at sign = , send garbage and see error
if "sign = " in data:
    send("00" * 40)
    s.settimeout(20)
    rest = ""
    try:
        rest = f.read()
    except Exception as e:
        rest = f"<<{type(e).__name__}>>"
    print("AFTER GARBAGE SIGN:", repr(rest))
s.close()
