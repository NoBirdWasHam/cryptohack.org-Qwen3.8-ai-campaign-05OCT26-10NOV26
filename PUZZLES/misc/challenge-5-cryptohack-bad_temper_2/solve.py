# bad_temper_2 (CryptoHack, 150 pts, misc) — full solver.
#
# Server: Random() seeded with a 32-byte secret; "get_seed" leaks randbytes(32)
# = 8 tempered MT19937 words per call; "secret" option gives the flag iff you
# submit the original 32-byte seed.
#
# Attack:
#  1. Collect 78 get_seed responses = 624 consecutive tempered outputs
#     = temper(twist(S0)) where S0 = state right after seeding (left==0 forces
#     a twist before the very first output).
#  2. Untwist (part-1 technique) -> S0 (word 0 is the constant 0x80000000, so
#     the usual low-31-bits-of-word-0 ambiguity is irrelevant).
#  3. Invert CPython's init_by_array analytically:
#       loop1: mt[i] = (mt[i] ^ ((mt[i-1]^(mt[i-1]>>30))*1664525)) + key[j] + j
#       loop2: mt[i] = (mt[i] ^ ((mt[i-1]^(mt[i-1]>>30))*1566083941)) - i
#       mt[0] = 0x80000000
#     loop2 touches each index 1..623 once (increasing order) and only mixes
#     with the *new* mt[i-1] -> undo i=623..2 with final state, then i=1 using
#     mt0_after_loop1 == L1[623] (set by loop1's wrap).
#     loop1 first pass: index i (2..623) is written once, from old S0[i] and
#     new mt[i-1] -> K[(i-1)%keylen] = L1[i] - T1(L1[i-1]) - ((i-1)%keylen).
#  4. NOTE Lib/random.py Random.seed(bytes) first maps
#       X = int.from_bytes(secret + sha512(secret).digest(), 'big')
#     then splits X into 24 little-endian 32-bit words = init_by_array key.
#     So K[23..16] (big-endian) == secret, K[15..0] == sha512 tail -> free
#     integrity check.  Verify against a further get_seed, then submit.
import socket, json, struct, sys, time, hashlib

U=0x80000000; L=0x7fffffff; MA=0x9908b0df
MASK=0xffffffff
M1=1664525; M2=1566083941

# ---------- MT19937 untwist (from part 1) ----------
def f(y): return (y>>1)^(MA if y&1 else 0)
def inv_f(z):
    b=(z>>31)&1
    return (((z^(MA*b))<<1)|b)&MASK
def ir(y,s):
    x=y;m=s
    while m<32: x^=y>>m; m*=2
    return x&MASK
def il(y,s,mask):
    x=[(y>>i)&1 for i in range(32)]
    for i in range(s,32):
        if (mask>>i)&1: x[i]^=x[i-s]
    return sum(x[i]<<i for i in range(32))&MASK
def untemper(y):
    x=ir(y,18); x=il(x,15,0xefc60000); x=il(x,7,0x9d2c5680); return ir(x,11)
def temper(x):
    x^=x>>11; x^=(x<<7)&0x9d2c5680; x^=(x<<15)&0xefc60000; x^=x>>18
    return x&MASK
def my_twist(O):
    mt=list(O)
    for i in range(624):
        y=(mt[i]&U)|(mt[(i+1)%624]&L)
        mt[i]=mt[(i+397)%624]^f(y)
    return mt
def untwist(N):
    O=[0]*624
    for i in range(227,624):
        y=inv_f(N[i]^N[i-227]) if i<623 else inv_f(N[623]^N[396])
        O[i]|=y&U
        if i<623: O[i+1]|=y&L
    for i in range(0,227):
        y=inv_f(N[i]^O[i+397])
        O[i]|=y&U
        O[i+1]|=y&L
    return O

# ---------- CPython seeding model + inverse ----------
def init_genrand(s):
    st=[0]*624; st[0]=s
    for i in range(1,624):
        st[i]=(1812433253*(st[i-1]^(st[i-1]>>30))+i)&MASK
    return st
def T1(x): return ((x^(x>>30))*M1)&MASK
def T2(x): return ((x^(x>>30))*M2)&MASK

def seed_model(argbuf):
    st=init_genrand(19650218)
    keylen=len(argbuf); i=1; j=0
    for k in range(max(keylen,624),0,-1):
        st[i]=(st[i]^T1(st[i-1]))+argbuf[j]+j
        st[i]&=MASK
        i+=1; j+=1
        if i==624: st[0]=st[623]; i=1
        if j==keylen: j=0
    for k in range(623,0,-1):
        st[i]=(st[i]^T2(st[i-1]))-i
        st[i]&=MASK
        i+=1
        if i==624: st[0]=st[623]; i=1
    st[0]=0x80000000
    return st

def unseed(S, keylen=24):
    """S = state right after Random().seed(<bytes hashing to keylen words>).
    Return the keylen key words."""
    # loop2 order is i=2..623 then i=1 (i is NOT reset after loop1):
    #   F[i] = (L1[i] ^ T2(F[i-1])) - i   for i=3..623
    #   F[2] = (L1[2] ^ T2(L1[1])) - 2    (mt[1] still old at step 2)
    #   F[1] = (L1[1] ^ T2(F[623])) - 1   (mt[0] = mt[623] set at wrap)
    L1=[0]*624
    for i in range(623,2,-1):
        L1[i]=((S[i]+i)&MASK)^(T2(S[i-1]))
    L1[1]=((S[1]+1)&MASK)^(T2(S[623]))
    L1[2]=((S[2]+2)&MASK)^(T2(L1[1]))
    # undo loop1 first pass: L1[i] = (S0[i] ^ T1(L1[i-1])) + K[(i-1)%keylen] + ((i-1)%keylen)
    S0=init_genrand(19650218)
    K={}
    for i in range(3,624):
        j=(i-1)%keylen
        k=((L1[i]-(S0[i]^T1(L1[i-1]))-j)&MASK)
        K.setdefault(j,set()).add(k)
    words=[0]*keylen
    for j in range(keylen):
        if len(K[j])!=1:
            raise RuntimeError(f"key word {j} inconsistent: {K[j]}")
        words[j]=K[j].pop()
    return words

def secret_from_key(K):
    """K = 24 LE words of int.from_bytes(secret+sha512(secret),'big')."""
    secret=b''.join(struct.pack('>I',K[w]) for w in range(23,15,-1))
    assert hashlib.sha512(secret).digest()==b''.join(struct.pack('>I',K[w]) for w in range(15,-1,-1)), "sha512 self-check failed"
    return secret

def attack(obs_words):
    """obs_words: >=624 consecutive tempered words from a freshly seeded oracle."""
    N=[untemper(w) for w in obs_words[:624]]
    S0=untwist(N)
    assert S0[0]==0x80000000, hex(S0[0])
    K=unseed(S0)
    assert seed_model(K)==S0, "model state mismatch"
    return secret_from_key(K)

def predict_next(secret, nwords, after_words):
    """Given secret and total observed word count, predict next nwords."""
    from random import Random
    r=Random(); r.seed(secret)
    for _ in range(after_words//8):
        r.randbytes(32)
    return r.randbytes(32)

HOST="socket.cryptohack.org"; PORT=13438

def attempt():
    from mnemonic import Mnemonic
    mn=Mnemonic("english")
    s=socket.create_connection((HOST,PORT),timeout=60); s.settimeout(40)
    buf=b''
    def fill():
        nonlocal buf
        d=s.recv(65536)
        if not d: raise EOFError("server closed")
        buf+=d
    def obj():
        nonlocal buf
        while True:
            i=buf.find(b'{')
            if i<0: fill(); continue
            try:
                o,idx=json.JSONDecoder().raw_decode(buf[i:].decode('utf-8','ignore'))
                buf=buf[i+idx:]
                return o
            except json.JSONDecodeError: fill()
    def send(o):
        s.sendall(json.dumps(o).encode()+b"\n"); return obj()
    try:
        obs=[]
        while len(obs)<624:
            r=send({"option":"get_seed"})
            if "wallet_seed" not in r: raise RuntimeError(f"unexpected: {r}")
            obs+=list(struct.unpack('<8I', mn.to_entropy(r["wallet_seed"])))
        N=[untemper(w) for w in obs[:624]]
        S0=untwist(N)
        secret=attack(obs)
        # local sanity: model reproduces observed words
        tw=my_twist(S0)
        assert [temper(tw[i]) for i in range(624)]==obs[:624]
        # extra check against server: one more get_seed must match our model
        r=send({"option":"get_seed"})
        nxt=list(struct.unpack('<8I', mn.to_entropy(r["wallet_seed"])))
        tw2=my_twist(tw)
        assert [temper(tw2[i]) for i in range(8)]==nxt, "server desync!"
        r=send({"option":"secret","secret":secret.hex()})
        return r, secret
    finally:
        s.close()

if __name__=="__main__":
    for k in range(5):
        try:
            r,secret=attempt()
            print("RESULT:", r)
            print("secret:", secret.hex())
            if "flag" in r:
                open("flag_bad_temper_2.txt","w").write(r["flag"])
                sys.exit(0)
            print("no flag, retrying", flush=True)
        except Exception as e:
            print("attempt failed:", repr(e), "retrying", flush=True)
            time.sleep(3)
    sys.exit(1)
