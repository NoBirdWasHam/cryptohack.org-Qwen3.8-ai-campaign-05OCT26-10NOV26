import os, sys
sys.path.insert(0, '.')
from aes import AES

no_op = lambda *x: None

def enc_stage(option, key, msg):
    cipher = AES(key)
    if option=='ark': cipher._add_round_key = no_op; off=0
    elif option=='sb': cipher._sub_bytes = no_op; off=16
    elif option=='sr': cipher._shift_rows = no_op; off=32
    else: cipher._mix_columns = no_op; off=48
    secret = b''.join(key[i:i+1]*4 for i in range(16))
    if msg is None:
        m = secret[off:off+16]
    else:
        m = msg
    return cipher.encrypt(m)

k1 = os.urandom(16)
print("k1:", k1.hex())

# 1. ark keyless?
k2 = os.urandom(16)
a1 = enc_stage('ark', k1, b'\x00'*16); a2 = enc_stage('ark', k2, b'\x00'*16)
print("ark keyless:", a1==a2)

# 2. sb affine: E(x)^E(y)^E(x^y) == 0 for random x,y (same key)
import random
ok=True
for _ in range(5):
    x=bytes(random.randrange(256) for _ in range(16)); y=bytes(random.randrange(256) for _ in range(16))
    if bytes(p^q^r for p,q,r in zip(enc_stage('sb',k1,x),enc_stage('sb',k1,y),enc_stage('sb',k1,bytes(a^b for a,b in zip(x,y))))) != b'\x00'*16: ok=False
print("sb affine:", ok)
# affine constant key-dependence: E(0) under k1 vs k2 (same w0w1? no) — just show differs
print("sb E(0) diff across keys:", enc_stage('sb',k1,b'\x00'*16)!=enc_stage('sb',k2,b'\x00'*16))

# 3. mc-stage secret ciphertext dependence on w2 (bytes 8..11), w3 fixed; vary w2
kA = k1; kB = bytearray(k1); kB[8]^=1; kB=bytes(kB)
print("mc-secret depends on w2:", enc_stage('mc',kA,None)!=enc_stage('mc',kB,None))
kC = bytearray(k1); kC[3]^=1; kC=bytes(kC)   # change w0 byte3
print("mc-secret depends on w0:", enc_stage('mc',kA,None)!=enc_stage('mc',kC,None))
kD = bytearray(k1); kD[12]^=1; kD=bytes(kD)
print("mc-secret depends on w3:", enc_stage('mc',kA,None)!=enc_stage('mc',kD,None))
# which of the 16 output bytes change under w2 byte j change?
kBase=k1
changed=[]
for byteidx in [8,9,10,11,12,13,14,15]:
    kk=bytearray(kBase); kk[byteidx]^=1; kk=bytes(kk)
    d=[i for i,(p,q) in enumerate(zip(enc_stage('mc',kBase,None),enc_stage('mc',kk,None))) if p!=q]
    changed.append((byteidx,d))
print("mc changed-bytes per key-byte:", changed)
# sr stage dependencies
changed=[]
for byteidx in [8,9,10,11,12,13,14,15]:
    kk=bytearray(kBase); kk[byteidx]^=1; kk=bytes(kk)
    d=[i for i,(p,q) in enumerate(zip(enc_stage('sr',kBase,None),enc_stage('sr',kk,None))) if p!=q]
    changed.append((byteidx,d))
print("sr changed-bytes per key-byte:", changed)
