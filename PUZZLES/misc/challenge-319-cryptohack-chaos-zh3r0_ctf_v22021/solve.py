# chaos-zh3r0_ctf_v22021 solver: collision -> flag (local verify + live)
import sys, socket, re, struct

# ---- exact clone of provided challenge.py hash ----
def ROTL(value, bits, size=32): return ((value % (1 << (size - bits))) << bits) | (value >> (size - bits))
def ROTR(value, bits, size=32): return ((value % (1 << bits)) << (size - bits)) | (value >> bits)
def pad(pt):
    pt += b'\x80'; L = len(pt)
    to_pad = 60-(L%64) if L%64 <= 60 else 124-(L%64)
    return pt + bytearray(to_pad) + int.to_bytes(L-1,4,'big')
def hash(text: bytes):
    text = pad(text)
    text = [int.from_bytes(text[i:i+4],'big') for i in range(0,len(text),4)]
    M = 0xffff
    x,y,z,u = 0x0124fdce, 0x89ab57ea, 0xba89370a, 0xfedc45ef
    A,B,C,D = 0x401ab257, 0xb7cd34e1, 0x76b3a27c, 0xf13c3adf
    RV1,RV2,RV3,RV4 = 0xe12f23cd, 0xc5ab6789, 0xf1234567, 0x9a8bc7ef
    for i in range(0,len(text),4):
        X,Y,Z,U = text[i]^x,text[i+1]^y,text[i+2]^z,text[i+3]^u
        RV1 ^= (x := (X&0xffff)*(M - (Y>>16)) ^ ROTL(Z,1) ^ ROTR(U,1) ^ A)
        RV2 ^= (y := (Y&0xffff)*(M - (Z>>16)) ^ ROTL(U,2) ^ ROTR(X,2) ^ B)
        RV3 ^= (z := (Z&0xffff)*(M - (U>>16)) ^ ROTL(X,3) ^ ROTR(Y,3) ^ C)
        RV4 ^= (u := (U&0xffff)*(M - (X>>16)) ^ ROTL(Y,4) ^ ROTR(Z,4) ^ D)
    for i in range(4):
        RV1 ^= (x := (X&0xffff)*(M - (Y>>16)) ^ ROTL(Z,1) ^ ROTR(U,1) ^ A)
        RV2 ^= (y := (Y&0xffff)*(M - (Z>>16)) ^ ROTL(U,2) ^ ROTR(X,2) ^ B)
        RV3 ^= (z := (Z&0xffff)*(M - (U>>16)) ^ ROTL(X,3) ^ ROTR(Y,3) ^ C)
        RV4 ^= (u := (U&0xffff)*(M - (X>>16)) ^ ROTL(Y,4) ^ ROTR(Z,4) ^ D)
    return int.to_bytes((RV1<<96)|(RV2<<64)|(RV3<<32)|RV4,16,'big')

# collision masked values from lin_collide.py (config A vs B, linearized family)
XA,YA,ZA,UA = 0xffef0000, 0x7fff4001, 0xfffe0000, 0xffef0000
XB,YB,ZB,UB = 0xffef0104, 0x7fff0101, 0xffbf0000, 0xffef0000
x0,y0,z0,u0 = 0x0124fdce, 0x89ab57ea, 0xba89370a, 0xfedc45ef
m1 = struct.pack('>4I', XA^x0, YA^y0, ZA^z0, UA^u0) + bytes(42)  # total 58 bytes
m2 = struct.pack('>4I', XB^x0, YB^y0, ZB^z0, UB^u0) + bytes(42)
assert m1 != m2 and hash(m1) == hash(m2), "local collision FAILED"
print("local collision OK:", hash(m1).hex())

if '--nolive' in sys.argv: sys.exit(0)
h1, h2 = m1.hex(), m2.hex()
s = socket.create_connection(("archive.cryptohack.org", 18948), timeout=30)
s.settimeout(25)
buf = b""
def drain(until_eof=False):
    global buf
    try:
        while True:
            d = s.recv(65536)
            if not d: break
            buf += d
    except socket.timeout:
        pass
drain()
print("greeting:", buf, flush=True)
s.sendall(h1.encode()+b"\n"); drain()
print("after m1:", buf, flush=True)
s.sendall(h2.encode()+b"\n"); drain()
print("after m2:", buf, flush=True)
mm = re.findall(rb'[a-zA-Z0-9_]*\{[^}]*\}', buf)
print("FLAG CANDIDATES:", mm, flush=True)
