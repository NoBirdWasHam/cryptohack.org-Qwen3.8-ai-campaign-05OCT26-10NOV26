#!/usr/bin/env python3
# no_difference: SBOX is NOT injective (rows satisfy S[x]=S[x^0x0F], plus cross-row dups).
# hash: state=INIT; per 4-byte block: xor into state[4:8]; permute; substitute; then 16 rounds.
# permute = bit-transpose (involution). In permuted coords, byte j of t=permute(x):
#   bit i of t_j = bit j of x_i. Message byte k XORs x_{4+k} -> controls bit (4+k) of EVERY t_j,
#   i.e. bit k of the HIGH nibble of every t_j. Low nibbles of t_j are FIXED (= f[j]&0xF).
# Collision: find colliding SBOX pair (u,v) sharing the fixed low nibble of some t_j;
# set t_j = u vs v (adjusting high nibbles via the 4 message bytes). States post-substitute
# coincide -> identical hashes.
import re, ast, socket, json

src = open("13395.py").read()
S = ast.literal_eval(re.search(r"SBOX\s*=\s*(\[[^\]]+\])", src, re.S).group(1))
INIT = [16, 32, 48, 80, 80, 96, 112, 128]

def permute(block):
    r = [0]*8
    for i in range(8):
        x = block[i]
        for j in range(8):
            r[j] |= (x & 1) << i
            x >>= 1
    return r

def hash_local(data):
    state = INIT[:]
    for i in range(0, len(data), 4):
        b = data[i:i+4]
        for j in range(4): state[4+j] ^= b[j]
        state = permute(state)
        state = [S[x] for x in state]
    for _ in range(16):
        state = permute(state)
        state = [S[x] for x in state]
    out = []
    for _ in range(2):
        out += state[4:]
        state = permute(state)
        state = [S[x] for x in state]
    return bytes(out)

f = permute(INIT)  # t when m=0
# colliding pairs sharing low nibble, grouped by low nibble
pairs = {}
for lo in range(16):
    seen = {}
    for x in range(256):
        if (x & 0xF) != lo: continue
        if S[x] in seen:
            pairs.setdefault(lo, []).append((seen[S[x]], x))
        else:
            seen[S[x]] = x
print("pairs by low nibble:", {k: len(v) for k, v in pairs.items()})

cand = None
for j in range(8):
    lo = f[j] & 0xF
    if pairs.get(lo):
        cand = (j,) + pairs[lo][0]
        break
assert cand, "no colliding pair sharing low nibble at any position"
j, u, v = cand
print(f"position j={j}, pair ({u:#04x},{v:#04x}), S equal: {S[u]==S[v]}, low nibble {u&0xF:x}")

def msg_from_t(t):
    x = permute(t)  # involution
    return bytes(x[4+k] ^ INIT[4+k] for k in range(4))

t0 = f[:]; t0[j] = u
t1 = f[:]; t1[j] = v
m0, m1 = msg_from_t(t0), msg_from_t(t1)
assert m0 != m1
h0, h1 = hash_local(m0), hash_local(m1)
print("m0 =", m0.hex(), " m1 =", m1.hex(), " hash match:", h0 == h1)
assert h0 == h1, "local collision failed"

s = socket.create_connection(("socket.cryptohack.org", 13395), timeout=30)
f = s.makefile("rwb")
def send(o):
    f.write((json.dumps(o)+"\n").encode()); f.flush()
    return ast.literal_eval(f.readline().decode())
banner = f.readline()  # quote line only; no JSON prompt on this listener
print("banner:", banner[:200])
resp = send({"a": m0.hex(), "b": m1.hex()})
txt = str(resp)
print("SERVER:", txt[:400])
mm = re.search(r"crypto\{[^}]+\}", txt)
if mm:
    open("flag.txt", "w").write(mm.group(0) + "\n")
    print("FLAG:", mm.group(0))
s.close()
