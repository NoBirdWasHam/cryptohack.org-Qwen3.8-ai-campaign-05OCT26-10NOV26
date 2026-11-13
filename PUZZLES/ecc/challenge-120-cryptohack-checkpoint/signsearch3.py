# Sign search v3 on RAW per-curve residues (each curve: s = +/-r_i mod m_i).
# Select up to 16 curves (no shared prime >2, prefer large), enumerate signs,
# enforce overlap consistency on shared 2-powers, verify x*G == server_pub.
import json, math, hashlib, re, sys
from Crypto.Cipher import AES
sys.path.insert(0, ".")
from ck_part4 import pmul, P, A, N, O

d = json.load(open("ck_res.json"))
cp = tuple(d["client_pub"]); sp = tuple(d["server_pub"])
ct = bytes.fromhex(d["flag_ct"])
GX = 0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296
GY = 0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5
G = (GX, GY)

def fac_of(m, hint):
    # factor m using the curve's known prime list (hint = fac pairs from curves file)
    return hint

curves = json.load(open("ck_curves.json"))
binfo = {}
for c in curves:
    pp = []
    for l, pe in c["fac"]:
        e = 0; t = pe
        while t % l == 0: t //= l; e += 1
        pp.append((l, e))
    binfo[c["b"]] = pp

raw = d["raw"]
print("raw residues:", len(raw))
cinfo = []
for row in raw:
    b, m, r = row["b"], row["m"], row["r"]
    pp = binfo.get(b)
    if pp is None: continue
    # verify product of prime powers == m
    prod = 1
    for l, e in pp: prod *= l ** e
    if prod % m != 0: continue
    cinfo.append((m, r, [(l, e, r % (l ** e)) for l, e in pp]))
cinfo.sort(key=lambda t: -t[0].bit_length())

sel = []
big_used = set()
for m, r, pp in cinfo:
    bigs = {l for l, e, rr in pp if l > 2}
    if bigs & big_used: continue
    sel.append((m, r, pp))
    big_used |= bigs
    if len(sel) >= 16: break
mbits = sum(e * math.log2(l) for m, r, pp in sel for l, e, rr in pp)
print("selected:", len(sel), "distinct-prime-power bits:", round(mbits))

k = len(sel)
pmax = {}   # l -> (e, rr, owner)
for i, (m, r, pp) in enumerate(sel):
    for l, e, rr in pp:
        if l not in pmax or pmax[l][0] < e:
            pmax[l] = (e, rr, i)
pmax = [(l, e, rr, o) for l, (e, rr, o) in pmax.items()]
overlaps = []
for i in range(k):
    for j in range(i + 1, k):
        pi = {l: (e, rr) for l, e, rr in sel[i][2]}
        pj = {l: (e, rr) for l, e, rr in sel[j][2]}
        for l in pi.keys() & pj.keys():
            e = min(pi[l][0], pj[l][0])
            overlaps.append((i, j, l, e, pi[l][1], pj[l][1]))
print("overlap constraints:", len(overlaps))

def crt_pair(x1, m1, x2, m2):
    return (x1 + m1 * (((x2 - x1) * pow(m1, -1, m2)) % m2)) % (m1 * m2), m1 * m2

hits = []
for mask in range(1 << k):
    good = True
    for i, j, l, e, ri, rj in overlaps:
        me = l ** e
        si = ri if not (mask >> i) & 1 else (-ri) % me
        sj = rj if not (mask >> j) & 1 else (-rj) % me
        if si != sj: good = False; break
    if not good: continue
    x, M = 0, 1
    for l, e, rr, owner in pmax:
        sgn = 1 if not (mask >> owner) & 1 else -1
        me = l ** e
        x, M = crt_pair(x, M, (sgn * rr) % me, me)
    if pmul(x, G) == sp:
        hits.append((x, mask))
        print("HIT mask=", bin(mask), "x bits=", x.bit_length(), flush=True)
print("total hits:", len(hits))
for x, mask in hits[:2]:
    shared = pmul(x, cp)
    key = hashlib.sha256(str(shared[0]).encode()).digest()[:16]
    pt = AES.new(key, AES.MODE_CBC, ct[:16]).decrypt(ct[16:])
    print("plaintext:", pt[:80])
    mm = re.search(rb"crypto\{[^}]+\}", pt)
    if mm:
        open("flag.txt", "w").write(mm.group(0).decode() + "\n")
        print("FLAG SAVED:", mm.group(0).decode())
        break
