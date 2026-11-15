# Solve cryptohack "invariant": invariant-subspace preimage of a DM-style hash.
#
# V = {states whose 16 nibbles all lie in {6,7}} is invariant under MyCipher for
# ANY key: subkey XOR flips only the low bit (6<->7), SB has the 2-cycle (6 7),
# and the linear layer XORs each nibble with its column parity (XOR of four
# {6,7} values = parity bit in {0,1}), which keeps nibbles in {6,7}.
#
# Hash: h0=0; h_i = E_K(h_{i-1} ^ m_i) ^ m_i, K = sha512(full message).
# Pick m1 in V  ->  h1 = E_K(m1)^m1 has all nibbles in {0,1}.
# Pick m2 in V  ->  x = h1^m2 in V  ->  E_K(x) in V; want E_K(x) == m2 so h2 = 0.
# K depends on m2, so brute force all 2^16 m2 in V (recomputing K each time);
# expected ~1 hit per 2^16 trials; rotate m1 if unlucky.
import itertools, socket, json, sys
from hashlib import sha512

NR = 31
SB = [13, 14, 0, 1, 5, 10, 7, 6, 11, 3, 9, 12, 15, 8, 2, 4]
SR = [0, 5, 10, 15, 4, 9, 14, 3, 8, 13, 2, 7, 12, 1, 6, 11]

def make_encrypt(RK):
    subkeys = [[(RK >> (16 * j + i)) & 1 for i in range(16)] for j in range(NR + 1)]
    def encrypt(S):  # S = list of 16 nibbles
        for r in range(NR):
            k = subkeys[r]
            S = [S[i] ^ k[i] for i in range(16)]
            S = [SB[S[SR[i]]] for i in range(16)]
            X = [S[0]^S[1]^S[2]^S[3], S[4]^S[5]^S[6]^S[7],
                 S[8]^S[9]^S[10]^S[11], S[12]^S[13]^S[14]^S[15]]
            S = [S[j] ^ X[j >> 2] for j in range(16)]
        k = subkeys[NR]
        return [S[i] ^ k[i] for i in range(16)]
    return encrypt

def nibs(b): return [int(_, 16) for _ in b.hex()]
def byts(S): return bytes.fromhex("".join("{:x}".format(v) for v in S))

def xor(a, b): return bytes(x ^ y for x, y in zip(a, b))

def find_preimage():
    import random
    rnd = random.Random(0xC0FFEE)
    for attempt in range(20):
        # random m1 in V
        m1 = bytes((6 | rnd.getrandbits(1)) << 4 | (6 | rnd.getrandbits(1)) for _ in range(8))
        m1n = nibs(m1)
        # enumerate m2 in V via 16-bit mask
        for mask in range(1 << 16):
            m2 = bytes((6 | (mask >> (2 * j + 1)) & 1) << 4 | (6 | (mask >> (2 * j)) & 1)
                       for j in range(8))
            data = m1 + m2
            enc = make_encrypt(int(sha512(data).digest().hex(), 16))
            h1 = xor(byts(enc(m1n)), m1)          # nibbles in {0,1}
            x = nibs(xor(h1, m2))                  # in V
            if enc(x) == nibs(m2):
                return data
        print(f"attempt {attempt}: no hit for m1={m1.hex()}", flush=True)
    raise RuntimeError("no preimage found")

def local_verify(data):
    enc = make_encrypt(int(sha512(data).digest().hex(), 16))
    h = [0] * 16
    for i in range(0, len(data), 8):
        blk = nibs(data[i:i + 8])
        h = enc([a ^ b for a, b in zip(h, blk)])
        h = [a ^ b for a, b in zip(h, blk)]
    return byts(h)

if __name__ == "__main__":
    data = find_preimage()
    d = local_verify(data)
    assert d == b"\x00" * 8, d.hex()
    print("LOCAL OK  data =", data.hex())
    open("preimage.txt", "w").write(data.hex())

    if "--offline" in sys.argv:
        sys.exit(0)
    s = socket.create_connection(("socket.cryptohack.org", 13393), timeout=30)
    f = s.makefile("rwb")
    pre = f.readline()
    print("server:", pre)
    f.write((json.dumps({"option": "hash", "data": data.hex()}) + "\n").encode())
    f.flush()
    resp = f.readline()
    print("resp:", resp)
    j = json.loads(resp)
    if "flag" in j:
        print("FLAG:", j["flag"])
        open("flag_invariant.txt", "w").write(j["flag"])
    else:
        print("no flag in response:", j)
    s.close()
