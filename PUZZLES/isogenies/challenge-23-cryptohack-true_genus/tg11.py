# tg11: SECRET search. 36 bits forced 0; 27 candidate positions free (2^27).
# AES: key = SHA256(int.to_bytes(sec,8))[:32]; check pt[:7] == 'crypto{' via first block only.
import json, hashlib, itertools, sys
from Crypto.Cipher import AES
ls = sorted([l for l in range(3,113) if all(l % d for d in range(2,int(l**.5)+1))] + [139])
p = 2*__import__("math").prod(ls)-1
d = json.load(open("output.txt"))
def q4(z): return pow(z % p, (p-1)//4, p)
def D(a4, a6): return (-16*(4*a4**3 + 27*a6**2)) % p
def coef(v):
    v = list(v); assert all(t == 0 for t in v[1:])
    return int(v[0])
v0 = q4(D(0,1))
insts = d["challenge_data"]
iv = bytes.fromhex(d["iv"]); ct = bytes.fromhex(d["ct"])
cand_pos = []
for j, c in enumerate(insts):
    r = q4(D(coef(c["EC"]["a4"]), coef(c["EC"]["a6"]))) * pow(q4(D(coef(c["EA"]["a4"]), coef(c["EA"]["a6"]))) * q4(D(coef(c["EB"]["a4"]), coef(c["EB"]["a6"]))) % p, p-2, p) % p
    if r == (p - v0) % p:  # Delta even -> possible bit 1
        cand_pos.append(j)
    elif r == v0:
        pass
    else:
        print("ANOMALY", j, r); sys.exit(1)
print("candidate positions:", len(cand_pos), cand_pos, flush=True)
prefix = b"crypto{"
mask_bits = cand_pos
import multiprocessing as mp
CT = ct
def scan(chunk):
    lo, hi = chunk
    out = []
    found_local = []
    for sub in range(lo, hi):
        s = 0
        t = sub
        i = 0
        while t:
            if t & 1: s |= 1 << mask_bits[i]
            t >>= 1; i += 1
        pt0 = AES.new(hashlib.sha256(int.to_bytes(s, 8, 'big')).digest()[:32], AES.MODE_ECB).decrypt(CT[:16])
        if pt0[:7] == prefix:
            full = AES.new(hashlib.sha256(int.to_bytes(s,8,'big')).digest()[:32], AES.MODE_CBC, iv).decrypt(CT)
            k = full[-1]
            if 1 <= k <= 16 and full[-k:] == bytes([k])*k:
                found_local.append((s, full))
    return found_local
if __name__ == "__main__":
    N = 1 << len(mask_bits)
    CH = 1 << 20
    chunks = [(i, min(i+CH, N)) for i in range(0, N, CH)]
    found = []
    with mp.Pool(8) as pool:
        for fl in pool.imap_unordered(scan, chunks):
            found += fl
            print("chunk done, found so far:", len(found), flush=True)
    for s, full in found:
        print("FOUND SECRET", s, "pt:", full, flush=True)
        open("candidate_flag.txt","w").write(full.decode(errors="replace"))
    print("done. found:", len(found), flush=True)
