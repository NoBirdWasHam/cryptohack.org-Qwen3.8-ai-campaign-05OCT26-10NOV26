import subprocess, re, numpy as np
from Crypto.Cipher import AES
M=0xffffffff
def ir(y,s):
    x=y;m=s
    while m<32: x^=y>>m; m*=2
    return x&M
def il(y,s,mask):
    b=[(y>>i)&1 for i in range(32)]
    for i in range(s,32):
        if (mask>>i)&1: b[i]^=b[i-s]
    return sum(b[i]<<i for i in range(32))&M
def untemper(y):
    x=ir(y,18); x=il(x,15,0xefc60000); x=il(x,7,0x9d2c5680); return ir(x,11)
def gen(seed):
    rs=np.random.RandomState(seed); return rs.bytes(16), rs.bytes(16)
def brute(iv):
    X=[untemper(int.from_bytes(iv[i*4:i*4+4],'little')) for i in range(4)]
    r=subprocess.run(['./mtbrute.exe']+[format(x,'x') for x in X]+['0','4294967296'],capture_output=True,text=True)
    m=re.search(r'FOUND (\d+)', r.stdout)
    return int(m.group(1)) if m else None
def unpad(b):
    n=b[-1]; assert 1<=n<=16 and b[-n:]==bytes([n])*n; return b[:-n]

HEX="22781db80eac37953a137fdb48b40bcec0f656a88348086e2b3f169301058cf1366d3a7ba50bb791a20c654d76d5b13df70f54f3009ef4cc77ef254081707c514fa4945173f36110c98ad322e95151258882633d29fae164fbd6a30962e010cf3965cbc8"
data=bytes.fromhex(HEX)
iv2,ct2=data[:16],data[16:]
s2=brute(iv2); print("seed2",s2,flush=True)
iv2b,key2=gen(s2); assert iv2b==iv2
inner=unpad(AES.new(key2,iv=iv2,mode=AES.MODE_CBC).decrypt(ct2))
iv1,ct1=inner[:16],inner[16:]
print("iv1",iv1.hex(),flush=True)
s1=brute(iv1); print("seed1",s1,flush=True)
iv1b,key1=gen(s1); assert iv1b==iv1
flag=unpad(AES.new(key1,iv=iv1,mode=AES.MODE_CBC).decrypt(ct1))
print("FLAG:",flag.decode(errors='replace'),flush=True)
open("flag_import_numpy_as_mt-zh3r0_ctf.txt","w").write(flag.decode(errors='replace').strip())
