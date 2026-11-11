# jeff self-test: local stream, run the same core attack, print diagnostics.
import random, types

class LFSR:
    def __init__(self, key, taps):
        d = max(taps); self._s = key; self._t = [d-t for t in taps]
    def bit(self):
        b = self._s[0]
        self._s = self._s[1:] + [self._sum(self._s[p] for p in self._t)]
        return b
    def _sum(self, L):
        s = 0
        for x in L: s ^= x
        return s
class Jeff:
    def __init__(self, key):
        key = [int(i) for i in list("{:069b}".format(key))]
        self.LFSR = [LFSR(key[:19],[19,18,17,14]), LFSR(key[19:46],[27,26,25,22]), LFSR(key[46:],[23,22,20,18])]
    def bit(self):
        b = [l.bit() for l in self.LFSR]
        return b[1] if b[0] else b[2]

random.seed(42)
KEY = random.getrandbits(69)
J = Jeff(KEY)
stream = [J.bit() for _ in range(256)]
print("key", KEY, "guess", KEY >> 50)

# --- solver core (copied from solve.py) ---
N = 256
def rows_for(taps, n):
    d = max(taps); t = [d - x for x in taps]
    out_rows = [0]*n
    for j in range(d):
        s = [0]*d; s[j] = 1
        for i in range(n):
            b = s[0]
            nb = 0
            for p in t: nb ^= s[p]
            s = s[1:] + [nb]
            if b: out_rows[i] |= (1 << j)
    return out_rows, d

def sim(taps, state_bits, n):
    d = max(taps); t = [d - x for x in taps]
    s = list(state_bits); out = []
    for _ in range(n):
        b = s[0]
        nb = 0
        for p in t: nb ^= s[p]
        s = s[1:] + [nb]
        out.append(b)
    return out

def gf2_solve(eqs, d):
    piv = {}
    for mask, rhs in eqs:
        m, r = mask, rhs
        while m:
            j = m.bit_length() - 1
            if j in piv:
                pm, pr = piv[j]
                m ^= pm; r ^= pr
            else:
                piv[j] = (m, r); break
        else:
            if r: return []
    if len(piv) < d: return None
    x = 0
    for j in sorted(piv):
        pm, pr = piv[j]
        v = pr ^ (bin(pm & ~(1<<j) & x).count("1") & 1)
        if v: x |= 1 << j
    return [x]

r0, d0 = rows_for([19,18,17,14], N)
r1, d1 = rows_for([27,26,25,22], N)
r2, d2 = rows_for([23,22,20,18], N)

# sanity: rows reproduce stream for true state
kbits = [(KEY >> (68-j)) & 1 for j in range(69)]
b0 = sim([19,18,17,14], kbits[:19], N)
b1 = sim([27,26,25,22], kbits[19:46], N)
b2 = sim([23,22,20,18], kbits[46:], N)
assert all((b1[i] if b0[i] else b2[i]) == stream[i] for i in range(N)), "sim mismatch"
print("sim OK")

# rows linear check: <r1[i], s1bits> == b1[i]
s1mask = 0
for j, bit in enumerate(kbits[19:46]):
    if bit: s1mask |= 1 << j
for i in range(N):
    assert (bin(r1[i] & s1mask).count("1") & 1) == b1[i], f"row mismatch at {i}"
print("rows OK")

# run guess loop (self-test: only true guess + 500 random wrong ones)
d0bits = 19
found = None
cand = [KEY >> 50] + [random.randrange(1 << d0bits) for _ in range(500)]
for guess in cand:
    s0 = [(guess >> (d0bits-1-j)) & 1 for j in range(d0bits)]
    bb0 = sim([19,18,17,14], s0, N)
    eqs1 = [(r1[i], stream[i]) for i in range(N) if bb0[i]]
    eqs2 = [(r2[i], stream[i]) for i in range(N) if not bb0[i]]
    if len(eqs1) < d1 or len(eqs2) < d2: continue
    s1s = gf2_solve(eqs1, d1)
    if not s1s: continue
    s2s = gf2_solve(eqs2, d2)
    if not s2s: continue
    for s1 in s1s:
        bb1 = sim([27,26,25,22], [(s1 >> j) & 1 for j in range(d1)], N)
        for s2 in s2s:
            bb2 = sim([23,22,20,18], [(s2 >> j) & 1 for j in range(d2)], N)
            if all((bb1[i] if bb0[i] else bb2[i]) == stream[i] for i in range(N)):
                found = guess
                break
    if found: break
print("found guess:", found, "expected:", KEY >> 50)
