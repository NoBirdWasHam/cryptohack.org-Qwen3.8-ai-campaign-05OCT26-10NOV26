import ast, itertools

groups = [ast.literal_eval(l) for l in open("output.txt") if l.strip()]
m = 15725
def par(a):
    v = 0
    for j, x in enumerate(bytes(a)):
        v |= (x & 1) << j
    return bin(v & m).count("1") & 1

# bit = 0 if group all-match (likely real), 1 otherwise (definitely fake)
dec_bits = []
amb = []  # groups classified 0 (could be accidental fake=1)
for gi, g in enumerate(groups):
    am = all(par(a) == (b & 1) for a, b in g)
    dec_bits.append(0 if am else 1)
    amb.append(am)

out = bytearray()
for i in range(0, len(dec_bits), 8):
    byte = 0
    for k, bit in enumerate(dec_bits[i:i+8]):
        byte |= bit << k
    out.append(byte)
s = out.decode("latin1")
print("len bytes:", len(out), "allmatch groups:", sum(amb))
print("decode:", s)

allowed = set(b"crypto{}" + b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_!?.-")
bad = [i for i, c in enumerate(out) if c not in allowed]
print("bad:", [(i, hex(out[i])) for i in bad])

def fixes(pos):
    byte = out[pos]
    res = []
    zeros = [k for k in range(8) if not (byte >> k) & 1]
    for r in range(0, len(zeros) + 1):
        for combo in itertools.combinations(zeros, r):
            nb = byte
            for k in combo:
                nb |= 1 << k
            if nb in allowed:
                res.append((r, nb))
    res.sort()
    return res[:4]

for p in bad:
    print(p, "->", [(r, chr(v)) for r, v in fixes(p)])
