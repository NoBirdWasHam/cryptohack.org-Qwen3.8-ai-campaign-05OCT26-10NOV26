# Live model test: in-place vs out-of-place twist on the real server.
# Collect 155 get_seed blocks (words 8..1247). For i in 227..623 the two twist
# models predict A2[i] differently: IP uses A2[i-227], OP uses A1[i-227].
import socket, json, struct, sys
from mnemonic import Mnemonic
U=0x80000000; L=0x7fffffff; MA=0x9908b0df
def f(y): return (y>>1)^(MA if y&1 else 0)
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
def words_of(b): return list(struct.unpack('<8I',b))

HOST="socket.cryptohack.org"; PORT=13435
mn=Mnemonic("english")
s=socket.create_connection((HOST,PORT),timeout=60); s.settimeout(40)
buf=b''
def fill():
    global buf
    d=s.recv(65536)
    if not d: raise EOFError("server closed")
    buf+=d
def obj():
    global buf
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

obs=[]
for i in range(155):
    r=send({"option":"get_seed"})
    if "wallet_seed" not in r: print("ERR", r); sys.exit(1)
    obs+=words_of(mn.to_entropy(r["wallet_seed"]))
    if i%25==0: print("got",i,flush=True)
print("total words:", len(obs))
A1=[None]*624
for p in range(8,624): A1[p]=untemper(obs[p-8])
A2=[untemper(w) for w in obs[616:616+624]]
ip_ok=op_ok=0
for i in range(235,623):   # A1[i-227] must be known (>=8) for OP model; avoid i=623 special case
    y=(A1[i]&U)|(A1[i+1]&L)
    src_ip = A2[i-227]
    src_op = A1[i-227]
    if (src_ip^f(y))&0xffffffff==A2[i]: ip_ok+=1
    if (src_op^f(y))&0xffffffff==A2[i]: op_ok+=1
print(f"in-place model matches: {ip_ok}/388")
print(f"out-of-place model matches: {op_ok}/388")
s.close()
