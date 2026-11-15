# diffecient: murmur3 x86_32 zero-propagation differential over first 8 bytes.
# fwd diff word0=2^18 -> after rotl13*5 = 2^31 -> XOR k2-diff word1=2^31 kills it.
import mmh3, re
M=0xFFFFFFFF
def fwd4(n): n=(n*0xCC9E2D51)&M; n=((n<<15)|(n>>17))&M; return (n*0x1B873593)&M
def inv4(n): n=(n*0x56ED309B)&M; n=((n>>15)|(n<<17))&M; return (n*0xDEE13BB1)&M
DIFF=bytes.fromhex('0000040000000080')  # LE words: 0x00040000, 0x80000000
def collision8(t8):
    f=b''.join(fwd4(int.from_bytes(t8[i:i+4],'little')).to_bytes(4,'little') for i in (0,4))
    d=bytes(a^b for a,b in zip(DIFF,f))
    return b''.join(inv4(int.from_bytes(d[i:i+4],'little')).to_bytes(4,'little') for i in (0,4))
K0=b'A'*28+b'Aa1!'  # 32 bytes: 8 blocks... wait tail: len 32 -> exactly 8 blocks, tail empty
K1=collision8(K0[:8])+K0[8:]
assert len(K1)==32 and K0!=K1
pat=re.compile(rb'(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W)')
assert pat.search(K0) and pat.search(K1)
d0=[mmh3.hash(K0,i)%(2**32-5) for i in range(47)]
d1=[mmh3.hash(K1,i)%(2**32-5) for i in range(47)]
print('digest sets identical:', d0==d1)
print('K0', K0.hex())
print('K1', K1.hex())
