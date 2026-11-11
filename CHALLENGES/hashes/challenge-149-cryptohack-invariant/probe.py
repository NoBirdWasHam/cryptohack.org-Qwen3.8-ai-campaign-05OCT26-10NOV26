# Probe the cipher: cycle structure of SB and invariance of V = {nibbles in {6,7}}
import itertools, random
from hashlib import sha512

NR = 31
SB = [13, 14, 0, 1, 5, 10, 7, 6, 11, 3, 9, 12, 15, 8, 2, 4]
SR = [0, 5, 10, 15, 4, 9, 14, 3, 8, 13, 2, 7, 12, 1, 6, 11]

# cycle structure of SB
seen = set(); cycles = []
for s in range(16):
    if s in seen: continue
    cyc = []; x = s
    while x not in seen:
        seen.add(x); cyc.append(x); x = SB[x]
    cycles.append(cyc)
print("SB cycles:", cycles)

class MyCipher:
    __NR = 31
    __SB = SB
    __SR = SR
    def __init__(self, key):
        self.__RK = int(key.hex(), 16)
        self.__subkeys = [[(self.__RK >> (16 * j + i)) & 1 for i in range(16)]
                          for j in range(self.__NR + 1)]
    def __xorAll(self, v):
        res = 0
        for x in v: res ^= x
        return res
    def encrypt(self, plaintext):
        assert len(plaintext) == 8
        S = [int(_, 16) for _ in list(plaintext.hex())]
        for r in range(self.__NR):
            S = [S[i] ^ self.__subkeys[r][i] for i in range(16)]
            S = [self.__SB[S[self.__SR[i]]] for i in range(16)]
            X = [self.__xorAll(S[i:i + 4]) for i in range(0, 16, 4)]
            S = [X[c] ^ S[4 * c + r]
                 for c, r in itertools.product(range(4), range(4))]
        S = [S[i] ^ self.__subkeys[self.__NR][i] for i in range(16)]
        return bytes.fromhex("".join("{:x}".format(_) for _ in S))

# empirical test: V invariant under encryption for random keys
def rand_V():
    return bytes((6 if random.random() < .5 else 7) * 1 + (0 if False else 0) for _ in range(0)) or \
           bytes([ (6 if random.getrandbits(1)==0 else 7) << 4 | (6 if random.getrandbits(1)==0 else 7) for _ in range(8)])

ok = True
for t in range(200):
    key = sha512(str(t).encode()).digest()
    c = MyCipher(key)
    x = rand_V()
    out = c.encrypt(x)
    nib = [int(h,16) for h in out.hex()]
    if not all(n in (6,7) for n in nib):
        ok = False; print("VIOLATION", x.hex(), out.hex()); break
print("V invariant under full encryption (200 random keys):", ok)

# also check {0,1} closure of XOR of two V states is trivially true; check round-level invariance explicitly
# round: subkey-bit XOR keeps {6,7}; SB: 6->7,7->6; linear: col XOR of four {6,7} = parity in {0,1}
print("SB(6)=", SB[6], "SB(7)=", SB[7])
