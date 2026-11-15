# tg12: SECRET search. Fix tg11 bug: CBC first block = ECB_Dec(C0) XOR IV (tg11 omitted IV).
# Constraint: 63 instances => ZZ.bits() length 63 => bit 62 == 1 => 2^26 space.
import json, hashlib, sys
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

ls = sorted([l for l in range(3,113) if all(l % d for d in range(2,int(l**.5)+1))] + [139])
p = 2*__import__("math").prod(ls)-1
def q4(z): return pow(z % p, (p-1)//4, p)
def D(a4, a6): return (-16*(4*a4**3 + 27*a6**2)) % p
def coef(v):
    v = list(v); assert all(t == 0 for t in v[1:])
    return int(v[0])

def cand_positions(challenge_data):
    v0 = q4(D(0,1))
    cand = []
    for j, c in enumerate(challenge_data):
        r = q4(D(coef(c["EC"]["a4"]), coef(c["EC"]["a6"]))) * pow(
            q4(D(coef(c["EA"]["a4"]), coef(c["EA"]["a6"]))) * q4(D(coef(c["EB"]["a4"]), coef(c["EB"]["a6"]))) % p,
            p-2, p) % p
        if r == (p - v0) % p:
            cand.append(j)
        elif r != v0:
            raise SystemExit(f"ANOMALY {j} {r}")
    return cand

PREFIX = b"crypto{"
def scan(chunk, IV, CT, mask_bits):
    """chunk = (lo,hi) over 26-bit sub-masks; bit 62 always set."""
    lo, hi = chunk
    X = IV[:16]
    C0 = CT[:16]
    out = []
    for sub in range(lo, hi):
        s = 1 << 62
        t = sub
        i = 0
        while t:
            if t & 1: s |= 1 << mask_bits[i]
            t >>= 1; i += 1
        key = hashlib.sha256(int.to_bytes(s, 8, 'big')).digest()
        pt0 = bytes(a ^ b for a, b in zip(AES.new(key, AES.MODE_ECB).decrypt(C0), X))
        if pt0[:7] == PREFIX:
            full = AES.new(key, AES.MODE_CBC, IV).decrypt(CT)
            k = full[-1]
            if 1 <= k <= 16 and full[-k:] == bytes([k])*k and full[:7] == PREFIX:
                out.append((s, full))
    return out

# ---------- synthetic unit test of the FULL pipeline (key deriv + IV + bit layout) ----------
def selftest():
    import random
    mask = [0, 2, 4, 6, 7, 9, 11, 12, 15, 19, 24, 26, 27, 29, 30, 31, 36, 37, 40, 44, 45, 48, 49, 52, 58, 60]
    for trial in range(3):
        s0 = (1 << 62)
        for b in random.sample(mask, 2): s0 |= 1 << b
        flag = pad(b"crypto{synthetic_test_flag_" + str(trial).zfill(3).encode() + b"}", 16)
        iv0 = bytes(random.getrandbits(8) for _ in range(16))
        key0 = hashlib.sha256(int.to_bytes(s0, 8, 'big')).digest()
        ct0 = AES.new(key0, AES.MODE_CBC, iv0).encrypt(flag)
        # scan 25% chunk containing s0's sub-mask
        sub0 = 0
        for i, bp in enumerate(mask):
            if s0 >> bp & 1: sub0 |= 1 << i
        sub0 &= ~(1 << 26)
        res = scan((sub0, sub0+1), iv0, ct0, mask)
        assert res and res[0][0] == s0 and res[0][1] == flag, f"selftest FAIL {trial} {res}"
    print("selftest OK (3/3 synthetic secrets recovered incl IV XOR fix)", flush=True)

if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    d = json.load(open("output.txt"))
    IV = bytes.fromhex(d["iv"]); CT = bytes.fromhex(d["ct"])
    mask_all = cand_positions(d["challenge_data"])
    assert 62 in mask_all, "bit62 must be a candidate position"
    mask = [b for b in mask_all if b != 62]
    assert len(mask) == 26, (len(mask), mask)
    print("free positions:", len(mask), mask, "space:", 2**len(mask), flush=True)
    N = 1 << len(mask); CH = 1 << 19
    chunks = [(i, min(i+CH, N)) for i in range(0, N, CH)]
    import multiprocessing as mp, functools
    worker = functools.partial(scan, IV=IV, CT=CT, mask_bits=mask)
    found = []
    with mp.Pool(8) as pool:
        for fl in pool.imap_unordered(worker, chunks, chunksize=1):
            for f in fl: found.append(f); print("PARTIAL HIT", hex(f[0]), f[1], flush=True)
    print("done. found:", len(found), flush=True)
    for s, full in found:
        print("FOUND SECRET", s, "pt:", full, flush=True)
        open("candidate_flag.txt","w").write(full.decode(errors="replace"))
