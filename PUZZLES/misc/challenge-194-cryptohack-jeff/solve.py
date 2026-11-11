# jeff: 3 LFSRs (19/27/23 bits) muxed: out = b1 if b0 else b2. 256 known keystream bits.
# Brute force 19-bit LFSR0; the b0=1 positions give linear eqs on LFSR1 state, b0=0 on LFSR2.
# GF(2) solve (rows precomputed), verify, then sha1(str(key)) -> AES-CBC decrypt.
import hashlib, json, ast
from Crypto.Cipher import AES

stream = None
data = None
for line in open("output_d5e714c9cb62f14696f21db9c5a4a2e5.txt"):
    line = line.strip()
    if line.startswith("["):
        stream = json.loads(line)
    elif line.startswith("{"):
        data = ast.literal_eval(line)
assert stream and data, "parse"
N = len(stream)

def rows_for(taps, n):
    d = max(taps)
    t = [d - x for x in taps]
    out_rows = [0]*n  # mask per time i over d basis bits
    for j in range(d):
        s = [0]*d; s[j] = 1
        for i in range(n):
            b = s[0]
            nb = 0
            for p in t: nb ^= s[p]
            s = s[1:] + [nb]
            if b: out_rows[i] |= (1 << j)
    return out_rows, d

r0, d0 = rows_for([19,18,17,14], N)
r1, d1 = rows_for([27,26,25,22], N)
r2, d2 = rows_for([23,22,20,18], N)

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
    # eqs: list of (mask, rhs); returns list of full solutions (<=8) or []
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
            if r: return []   # 0 = 1 contradiction
    if len(piv) < d:
        free = [j for j in range(d) if j not in piv]
        if len(free) > 3: return []
        sols = []
        for combo in range(1 << len(free)):
            x = 0
            for k, j in enumerate(free):
                if combo >> k & 1: x |= 1 << j
            for j in sorted(piv):
                pm, pr = piv[j]
                v = pr
                m = pm & ~(1 << j)
                v ^= bin(m & x).count("1") & 1
                if v: x |= 1 << j
                else: x &= ~(1 << j)
            sols.append(x)
        return sols
    x = 0
    for j in sorted(piv):
        pm, pr = piv[j]
        v = pr ^ (bin(pm & ~(1<<j) & x).count("1") & 1)
        if v: x |= 1 << j
    return [x]

iv = bytes.fromhex(data["iv"])
ct = bytes.fromhex(data["encrypted_flag"])

# precompute LFSR0 guesses as bit sequences
d0bits = 19
found = None
for guess in range(1 << d0bits):
    s0 = [(guess >> (d0bits-1-j)) & 1 for j in range(d0bits)]
    b0 = sim([19,18,17,14], s0, N)
    eqs1 = [(r1[i], stream[i]) for i in range(N) if b0[i]]
    eqs2 = [(r2[i], stream[i]) for i in range(N) if not b0[i]]
    if len(eqs1) < d1 or len(eqs2) < d2: continue
    s1s = gf2_solve(eqs1, d1)
    if not s1s: continue
    s2s = gf2_solve(eqs2, d2)
    if not s2s: continue
    for s1 in s1s:
        b1 = sim([27,26,25,22], [(s1 >> j) & 1 for j in range(d1)], N)
        for s2 in s2s:
            b2 = sim([23,22,20,18], [(s2 >> j) & 1 for j in range(d2)], N)
            if all((b1[i] if b0[i] else b2[i]) == stream[i] for i in range(N)):
                bits = "".join(str((guess >> (d0bits-1-j)) & 1) for j in range(d0bits))
                bits += "".join(str((s1 >> j) & 1) for j in range(d1))
                bits += "".join(str((s2 >> j) & 1) for j in range(d2))
                key = int(bits, 2)
                aes_key = hashlib.sha1(str(key).encode()).digest()[:16]
                pt = AES.new(aes_key, AES.MODE_CBC, iv).decrypt(ct)
                if b"crypto" in pt:
                    print("KEY:", key, "FLAG:", pt.rstrip(b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'))
                    open("flag_jeff.txt","w").write(pt.decode(errors="replace"))
                    found = True
                    break
        if found: break
    if found: break
if not found: print("no solution")
