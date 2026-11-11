# Hyper512 (HITCON CTF 2024) solver.
# keystream bit k_n = f(x_n,y_n,z_n,w_n) with
#   x_n = b1[3n]^b1[3n+1]^b1[3n+2], y_n = b2[n], z_n = b3[4n..4n+3], w_n = b4[2n]^b4[2n+1]
#   f = y^z^xz^w*(xy^xz^yz)  (ANF of the sha256 lookup table)
# Each b_r sequence = Fibonacci LFSR (taps = MASK bits); first 128 outputs = state bits.
# Encode in CryptoMiniSat (native XOR clauses) -> recover 4x128-bit states -> decrypt.
import sys, time
import pycryptosat

gift_hex, ct_hex = open('output.txt').read().split()
gift = bytes.fromhex(gift_hex); ct = bytes.fromhex(ct_hex)
from hashlib import sha256
T = [sha256(str(v).encode()).digest()[0] & 1 for v in range(3142, 3153)]
def fval(x,y,z,w): return T[3*x+y+4*z+2*w]

MASKS = [0x6D6AC812F52A212D5A0B9F3117801FD5, 0xD736F40E0DED96B603F62CBE394FEF3D,
         0xA55746EF3955B07595ABC13B9EBEED6B, 0xD670201BAC7515352A273372B2A95B23]
TAPS = [[i for i in range(128) if m >> i & 1] for m in MASKS]

N = int(sys.argv[1]) if len(sys.argv) > 1 else 1024   # keystream bits to use
TMAX = [max(3*N+5,130), max(N+5,130), max(4*N+5,130), max(2*N+5,130)]

nxt = [0]
def V(name):
    nxt[0] += 1; return nxt[0]

bv = [[V(('b',r,t)) for t in range(TMAX[r])] for r in range(4)]

s = pycryptosat.Solver()
for r in range(4):
    taps = TAPS[r]
    for t in range(TMAX[r]-128):
        s.add_xor_clause([bv[r][t+128]] + [bv[r][t+i] for i in taps], rhs=False)

for n in range(N):
    kb = (gift[n//8] >> (7-(n%8))) & 1  # n-th keystream bit, MSB-first
    x = V('x'); y = bv[1][n]
    s.add_xor_clause([x] + [bv[0][3*n+i] for i in range(3)], rhs=False)
    z = V('z')
    s.add_xor_clause([z] + [bv[2][4*n+i] for i in range(4)], rhs=False)
    w = V('w')
    s.add_xor_clause([w] + [bv[3][2*n], bv[3][2*n+1]], rhs=False)
    p1, p2, p3 = V('p1'), V('p2'), V('p3')   # xy, xz, yz
    for a,b_,c in ((x,y,p1),(x,z,p2),(y,z,p3)):
        s.add_clauses([[-a,-b_,c],[-a,b_,-c],[a,-b_,-c],[-c,a],[-c,b_]])
    sm = V('s')  # p1^p2^p3
    s.add_xor_clause([sm, p1, p2, p3], rhs=False)
    u = V('u')   # w & s
    for cl in ([[-w,-sm,u],[-w,sm,-u],[w,-sm,-u],[-u,w],[-u,sm]]):
        s.add_clause(cl)
    s.add_xor_clause([y, z, p2, u], rhs=bool(kb))

print(f'vars={nxt[0]} solving N={N} ...', flush=True)
t0=time.time()
res = s.solve()
print('sat:', res[0], f'{time.time()-t0:.1f}s', flush=True)
if not res[0]:
    sys.exit(1)
model = res[1]
def val(v): return model[v] if v>0 else not model[-v]

states = []
for r in range(4):
    st = 0
    for i in range(128):
        if val(bv[r][i]): st |= 1 << i
    states.append(st)
key = states[0] | (states[1]<<128) | (states[2]<<256) | (states[3]<<384)
print('key =', hex(key))

# ---- validate: reproduce keystream with recovered key, using chall.py logic ----
class LFSR:
    def __init__(self, n, key, mask):
        self.n=n; self.state=key & ((1<<n)-1); self.mask=mask
    def __call__(self):
        b=self.state&1
        self.state=(self.state>>1) | (((self.state&self.mask).bit_count()&1)<<(self.n-1))
        return b
class Cipher:
    def __init__(self, key):
        self.lfsr1=LFSR(128,key,MASKS[0]); key>>=128
        self.lfsr2=LFSR(128,key,MASKS[1]); key>>=128
        self.lfsr3=LFSR(128,key,MASKS[2]); key>>=128
        self.lfsr4=LFSR(128,key,MASKS[3])
    def bit(self):
        x=self.lfsr1()^self.lfsr1()^self.lfsr1()
        y=self.lfsr2()
        z=self.lfsr3()^self.lfsr3()^self.lfsr3()^self.lfsr3()
        w=self.lfsr4()^self.lfsr4()
        return sha256(str(3*x+y+4*z+2*w+3142).encode()).digest()[0]&1
    def stream(self):
        while True:
            b=0
            for i in reversed(range(8)): b |= self.bit()<<i
            yield b
    def encrypt(self, pt): return bytes([x^y for x,y in zip(pt,self.stream())])

c = Cipher(key)
ks = c.encrypt(b'\x00'*len(gift))
assert ks == gift, 'gift mismatch!'
flag = c.encrypt(ct)
print('gift verified OK; flag =', flag.decode(errors='replace'))
open('flag_hyper512-hitcon_ctf2024.txt','w').write(flag.decode().strip())
