# tenet_the_plagarism-hkcert_ct: derive the effective keystream space and bound the attack.
# challenge.py builds each of the 16 AES-128-CTR ciphers with key = key[i:i+1] + b'\0'*15
# and Counter.new(128, initial_value=0) -> identical key FORMAT and identical counter stream.
# So the whole cipher is a pure XOR of 16 keystreams, each chosen from ONE 256-entry table,
# and applying the same key twice cancels. Effective space = even-cardinality multisets over
# 256 entries of total weight <= 16 = subsets S with |S| <= 16, |S| even => C(256,16) ~ 2^74.
# Known plaintext "Congratulations! hkcert21{" + "}" gives 27 known bytes = 216 bits of the
# keystream XOR, which should pin the subset uniquely.
# This script: validate the model, enumerate the reduced (6-byte-alphabet) version with an
# exact 8+8 MITM to prove the recovery machinery, and measure the full-scale cost honestly.
from Crypto.Util import Counter
from Crypto.Cipher import AES
import itertools, math, os

BLK = 4  # 62-byte message -> counter blocks 0..3
def keystream_tables(nblk=BLK):
    tabs = []
    for i in range(16):
        t = {}
        for b in range(256):
            k = bytes([b]) + b"\0"*15
            a = AES.new(key=k, mode=AES.MODE_CTR,
                        counter=Counter.new(128, initial_value=0))
            t[b] = a.encrypt(b"\0"*(16*nblk))
        tabs.append(t)
    return tabs

def tenet_encrypt(msg, key):
    out = msg
    for i in range(16):
        a = AES.new(key=key[i:i+1] + b"\0"*15, mode=AES.MODE_CTR,
                    counter=Counter.new(128, initial_value=0))
        out = a.encrypt(out)
    return out

def x(*bs):
    r = bs[0]
    for y in bs[1:]:
        r = bytes(p ^ q for p, q in zip(r, y))
    return r

if __name__ == "__main__":
    # ---- 1. do the 16 slots share one table?
    t0, t1 = keystream_tables(1)[0], keystream_tables(1)[1]
    print("slot0 table == slot1 table:", all(t0[b] == t1[b] for b in range(256)))

    # ---- 2. model validation on self-generated ciphertexts
    tab = keystream_tables()[0]
    ok = True
    for _ in range(5):
        key = os.urandom(16)
        m = b"Congratulations! hkcert21{" + b"Q"*35 + b"}"
        c = tenet_encrypt(m, key)
        est = x(b"\0"*(16*BLK), *[tab[b] for b in key])
        ok &= (est[:len(m)] == x(c, m))
    print("model (XOR of 16 keystreams, dup bytes cancel) ok:", ok)

    # ---- 3. reduced parity-subset MITM (correct algorithm: duplicates cancel, so the
    #         keystream depends only on the parity subset S of the alphabet; MITM splits S
    #         into (low-half subsets) x (high-half subsets) and matches on the known keystream).
    A = 16                                   # reduced alphabet size
    tabA = {b: tab[b] for b in range(A)}
    key = bytes(b % A for b in os.urandom(16))
    m = b"Congratulations! hkcert21{" + b"Q"*35 + b"}"
    D = x(tenet_encrypt(m, key), m)[:32]     # 256 bits known here (more than real 216)
    true_S = frozenset(b for b in set(key) if key.count(b) % 2 == 1)
    lo, hi = range(A//2), range(A//2, A)
    L = {}
    for r in range(len(hi)//2 + 1):
        pass
    # enumerate all subsets of hi-half (2^8=256) -> dict; stream lo-half (2^8)
    H = {}
    for mask in range(1 << (A//2)):
        s = [b for j, b in enumerate(hi) if mask >> j & 1]
        H[x(b"\0"*32, *[tabA[b] for b in s])] = mask
    cands = []
    for mask in range(1 << (A//2)):
        s = [b for j, b in enumerate(lo) if mask >> j & 1]
        need = x(D, *[tabA[b] for b in s])
        if need in H:
            m2 = H[need]
            S = frozenset([b for j, b in enumerate(lo) if mask >> j & 1] +
                          [b for j, b in enumerate(hi) if m2 >> j & 1])
            cands.append(S)
    print("parity-subset MITM: candidates=%d, true S found:" % len(cands), true_S in cands)

    # ---- 4. cost estimate for full scale (alphabet 256, |S| <= 16 even, 216 bits of D)
    print("parity-subset MITM one side: C(256,8) = 2^%.1f entries; all even S: 2^%.1f"
          % (len(bin(math.comb(256, 8)))-1, math.log2(2**255)))
