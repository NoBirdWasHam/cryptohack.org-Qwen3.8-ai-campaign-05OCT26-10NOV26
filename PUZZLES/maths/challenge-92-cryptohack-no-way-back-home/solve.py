# No Way Back Home (#92): the "quantum-safe" KX leaks v (the key seed).
# v = p*r (multiple of p, r in [1,n)); vka=p*r*kA, vkb=p*r*kB, vkakb=p*r*kA*kB are all
# multiples of p, so r mod q is recoverable: r = a*b*(ab)^-1 mod q where
# a=vka//p mod q, b=vkb//p mod q, ab=vkakb//p mod q. Then v=p*r, key=sha256(long_to_bytes(v)).
import re
from Crypto.Cipher import AES
from Crypto.Util.number import long_to_bytes, inverse
from Crypto.Util.Padding import unpad
from hashlib import sha256
txt=open("out_provided.txt").read()
p=int(re.search(r'p, q = \((\d+), (\d+)\)',txt).group(1)); q=int(re.search(r'p, q = \((\d+), (\d+)\)',txt).group(2))
n=p*q
vka=int(re.search(r'vka = (\d+)',txt).group(1)); vkb=int(re.search(r'vkb = (\d+)',txt).group(1))
vka_kb=int(re.search(r'vkakb = (\d+)',txt).group(1)); c=re.search(r"c = '([0-9a-f]+)'",txt).group(1)
a=(vka//p)%q; b=(vkb//p)%q; ab=(vka_kb//p)%q
r=(a*b*inverse(ab,q))%q; v=p*r
key=sha256(long_to_bytes(v)).digest()
print("PT:", unpad(AES.new(key,AES.MODE_ECB).decrypt(bytes.fromhex(c)),16).decode())
