# bad_temper (CryptoHack) — full solver.
# Attack: oracle = CPython Random seeded with 256-bit secret; first_seed = words 0..7
# (temper of A1[0..7] after the seeding twist), get_seed leaks words 8.. onward.
# Collect 155 blocks (words 8..1247) = A1[8..623] + full A2. Untwist A2->A1
# (in-place CPython twist: recovers A1[1..623] + upper bit of A1[0]); the low 31
# bits of A1[0] leak from the SAME twist's last line: A1[623]=A1[396]^f((A0[623]&U)|(A1[0]&L)).
# Then first_seed = temper(A1[0..7]); next block = temper(twist(A2)[0..7]).
import socket, json, struct, sys, time
from mnemonic import Mnemonic
U=0x80000000; L=0x7fffffff; MA=0x9908b0df
def f(y): return (y>>1)^(MA if y&1 else 0)
def inv_f(z):
    b=(z>>31)&1
    return (((z^(MA*b))<<1)|b)&0xffffffff
def ir(y,s):
    x=y;m=s
    while m<32: x^=y>>m; m*=2
    return x&0xffffffff
def il(y,s,mask):
    x=[(y>>i)&1 for i in range(32)]
    for i in range(s,32):
        if (mask>>i)&1: x[i]^=x[i-s]
    return sum(x[i]<<i for i in range(32))&0xffffffff
def untemper(y):
    x=ir(y,18); x=il(x,15,0xefc60000); x=il(x,7,0x9d2c5680); return ir(x,11)
def temper(x):
    x^=x>>11; x^=(x<<7)&0x9d2c5680; x^=(x<<15)&0xefc60000; x^=x>>18
    return x&0xffffffff
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
def words_of(b): return list(struct.unpack('<8I',b))
def pack(ws): return b''.join(struct.pack('<I',w) for w in ws)

def attack(obs_words):
    A2=[untemper(w) for w in obs_words[616:616+624]]
    A1=untwist(A2)
    A1[0]|=inv_f(A1[623]^A1[396])&L
    first_seed=pack([temper(A1[i]) for i in range(8)])
    A3=my_twist(A2)
    next_seed=pack([temper(A3[i]) for i in range(8)])
    return first_seed, next_seed

HOST="socket.cryptohack.org"; PORT=13435
mn=Mnemonic("english")

def attempt():
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
        while len(obs)<1240:
            r=send({"option":"get_seed"})
            if "wallet_seed" not in r: raise RuntimeError(f"unexpected: {r}")
            obs+=words_of(mn.to_entropy(r["wallet_seed"]))
        fs,ns=attack(obs)
        r=send({"option":"first_and_next",
                "first_seed":mn.to_mnemonic(fs),
                "next_seed":mn.to_mnemonic(ns)})
        return r
    finally:
        s.close()

if __name__=="__main__":
    for k in range(5):
        try:
            r=attempt()
            print("RESULT:", r)
            if "flag" in r: sys.exit(0)
            print("no flag, retrying with fresh connection", flush=True)
        except Exception as e:
            print("attempt failed:", repr(e), "retrying", flush=True)
            time.sleep(3)
    sys.exit(1)
