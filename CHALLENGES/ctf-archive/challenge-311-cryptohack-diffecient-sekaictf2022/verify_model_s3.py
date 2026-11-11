
# independent verification of diffecient model facts (local mmh3, no live)
import mmh3, math, random
# 1) mmh3.hash == reference murmur3 x86_32 (pure python impl)
def fmix(h):
    m=0xFFFFFFFF
    h^=h>>16; h=(h*0x85ebca6b)&m; h^=h>>13; h=(h*0xc2b2ae35)&m; h^=h>>16; return h
m=0xFFFFFFFF
def rotl(v,r): return ((v<<r)|(v>>(32-r)))&m
def mm(k):
    m=0xFFFFFFFF
    k=(k*0xcc9e2d51)&m; k=rotl(k,15); k=(k*0x1b873593)&m; return k
def murmur(data, seed):
    m=0xFFFFFFFF
    h=seed
    for i in range(0,len(data)//4*4,4):
        blk=int.from_bytes(data[i:i+4],'little')
        h^=mm(blk); h=rotl(h,13); h=(h*5+0xe6546b64)&m
    r=len(data)%4; tail=data[len(data)//4*4:]; k=0
    if r:
        for j in range(r-1,-1,-1): k=(k<<8)|tail[j]
        # switch order: k^= tail[0] | tail[1]<<8 | tail[2]<<16
        k=0
        for j in range(r): k|= tail[j]<<(8*j)
        h^=mm(k)
    h^=len(data); h=fmix(h)
    return h if h < 2**31 else h-2**31
random.seed(7)
ok = True
for _ in range(200):
    bb = bytes(random.randrange(256) for _ in range(random.randrange(0, 40)))
    for s in (0, 1, 23, 46, 100):
        if murmur(bb, s) != mmh3.hash(bb, s):
            ok = False
print("murmur3 model == mmh3:", ok)
# 2) bijection claim: fixed key -> digests across seeds distinct
K=bytes(random.randrange(256) for _ in range(64))
d=[mmh3.hash(K,i)%(2**32-5) for i in range(47)]
print("47 seed-digests distinct:", len(set(d))==47)
# 3) 1-byte XOR structure: dig_i(b) == fmix(i ^ mix32(b) ^ 1)?
b=bytes([random.randrange(256)])
c=mm(b[0])^1
print("1-byte xor-const:", all(fmix((i^c)&0xFFFFFFFF)==(mmh3.hash(b,i)%(2**32-5)) for i in range(47)))
# 4) density and brute force cost
m=2**32-5; i=1102; k=47
fp=pow(1-pow(math.e,-k*i/m),k)
print("security bits at i=1102:", int(1/fp).bit_length(), " i=1101:", int(1/pow(1-pow(math.e,-k*1101/m),k)).bit_length())
rho=51793/m
print("rho^47 bits:", -math.log2(rho**47))
