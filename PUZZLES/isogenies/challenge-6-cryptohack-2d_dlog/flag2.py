"""2d_dlog flag step 2: wide AES key search over (iv, ct) with dlog results."""
import re, hashlib, itertools
from Crypto.Cipher import AES

# dlog results (from solve.py run 2026-10-14)
a = 8989068744398147088210219398915291813
b = 6850346275278222392661032070044244531
c = 20317470060808910705949514324772572305
d = 95527147648358416100018697076146379441
M = 1 << 127

text = open(r"~\Practice_runs\cryptohack_org\challenge-209-cryptohack-2d_dlog\output.txt", encoding="utf-8").read()
iv = bytes.fromhex(re.search(r"iv\s*=\s*'([0-9a-f]+)'", text).group(1))
ct = bytes.fromhex(re.search(r"ct\s*=\s*'([0-9a-f]+)'", text).group(1))
print("iv:", iv.hex(), "ct len:", len(ct))

ns = {"a": a, "b": b, "c": c, "d": d}
ncands = []
for name, v in ns.items():
    ncands.append((name + "", v))
    ncands.append((name + "_comp", (M - v) % M))

def keyfamily():
    fam = {}
    s_a, s_b, s_c, s_d = str(a), str(b), str(c), str(d)
    fam["sha256(a,b,c,d csv)"] = hashlib.sha256(f"{a},{b},{c},{d}".encode()).digest()
    fam["sha256(abcdd str concat)"] = hashlib.sha256((s_a+s_b+s_c+s_d).encode()).digest()
    fam["sha256(a b c d sp)"] = hashlib.sha256(f"{a} {b} {c} {d}".encode()).digest()
    fam["sha256(abcd 64B big)"] = hashlib.sha256(a.to_bytes(32,'big')+b.to_bytes(32,'big')+c.to_bytes(32,'big')+d.to_bytes(32,'big')).digest()
    fam["sha256(ab 32B big)"] = hashlib.sha256(a.to_bytes(32,'big')+b.to_bytes(32,'big')).digest()
    fam["sha256(cd 32B big)"] = hashlib.sha256(c.to_bytes(32,'big')+d.to_bytes(32,'big')).digest()
    fam["sha256(ab 16B big)"] = hashlib.sha256(a.to_bytes(16,'big')+b.to_bytes(16,'big')).digest()
    fam["sha256(cd 16B big)"] = hashlib.sha256(c.to_bytes(16,'big')+d.to_bytes(16,'big')).digest()
    fam["sha256(abcd 16B big)"] = hashlib.sha256(a.to_bytes(16,'big')+b.to_bytes(16,'big')+c.to_bytes(16,'big')+d.to_bytes(16,'big')).digest()
    fam["sha512(csv)[:32]"] = hashlib.sha512(f"{a},{b},{c},{d}".encode()).digest()[:32]
    fam["md5(csv)*2"] = hashlib.md5(f"{a},{b},{c},{d}".encode()).digest()*2
    fam["md5(concat)*2"] = hashlib.md5((s_a+s_b+s_c+s_d).encode()).digest()*2
    fam["csv[:16]"] = (f"{a},{b},{c},{d}".encode() + b"\0"*16)[:16]
    fam["concat[:16]"] = ((s_a+s_b+s_c+s_d).encode() + b"\0"*16)[:16]
    fam["concat[:32]"] = ((s_a+s_b+s_c+s_d).encode() + b"\0"*32)[:32]
    fam["ab concat[:16]"] = ((s_a+s_b).encode() + b"\0"*16)[:16]
    fam["cd concat[:16]"] = ((s_c+s_d).encode() + b"\0"*16)[:16]
    for name, v in ns.items():
        for tag, vv in ((name, v), (name+"c", (M-v)%M)):
            fam[f"sha256(str({tag}))"] = hashlib.sha256(str(vv).encode()).digest()
            fam[f"{tag}.to16"] = vv.to_bytes(16, "big")
            fam[f"{tag}.to32"] = vv.to_bytes(32, "big")
            fam[f"{tag}.to32le"] = vv.to_bytes(32, "little")
    return fam

def printable(pt):
    return sum(1 for ch in pt if 32 <= ch < 127) / max(len(pt), 1)

fam = keyfamily()
hits = []
for kname, key in fam.items():
    for ks in (16, 32):
        if len(key) < ks: continue
        k = key[:ks]
        try:
            pt = AES.new(k, AES.MODE_CTR, nonce=iv[:15], initial_value=iv[15:]).encrypt(ct)
            r = printable(pt)
            if r > 0.85:
                hits.append(("CTR", kname, ks, pt))
                print(f"CTR {kname} ks={ks} printable={r:.2f}: {pt!r}")
        except Exception as e:
            pass
        try:
            pt = AES.new(k, AES.MODE_CBC, iv).decrypt(ct)
            r = printable(pt)
            if r > 0.85:
                hits.append(("CBC", kname, ks, pt))
                print(f"CBC {kname} ks={ks} printable={r:.2f}: {pt!r}")
        except Exception as e:
            pass
print("total hits:", len(hits))
for mode, kname, ks, pt in hits:
    print(f"== {mode} {kname} ks={ks} ==")
    print(repr(pt))
