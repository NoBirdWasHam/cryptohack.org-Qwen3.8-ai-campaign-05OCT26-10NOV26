#!/usr/bin/env python
# Common Ground (challenge-90). Identity: gcd(N^a-1, N^b-1) = N^gcd(a,b)-1.
# So the "enormous" numbers reduce to N^g - 1 where g = gcd(a,b) (tiny).
import math, hashlib, json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

lines=[l.strip() for l in open("output_provided.txt")]
N=int(lines[0].split("=")[1].strip())
a=int(lines[1].split("=")[1].strip())
b=int(lines[2].split("=")[1].strip())
g=math.gcd(a,b)                       # <-- the whole trick
gval=pow(N,g)-1
key=hashlib.sha256(gval.to_bytes((gval.bit_length()+7)//8,"big")).digest()[:16]
j=json.loads(lines[3])
iv=bytes.fromhex(j["iv"]); ct=bytes.fromhex(j["ct"])
pt=unpad(AES.new(key,AES.MODE_CBC,iv=iv).decrypt(ct),16)
print("g =", g)
print("PT:", pt.decode())
