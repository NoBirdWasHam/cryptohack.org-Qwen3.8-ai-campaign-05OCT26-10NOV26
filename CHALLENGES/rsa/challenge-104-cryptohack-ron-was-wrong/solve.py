#!/usr/bin/env python
# ron_was_wrong (104): 50 OAEP-encrypted keys. Keys 21 & 34 share a 4096-bit factor p.
#   n21 = p*q, n34 = p*r  =>  factor both, decrypt 21.ciphertext (and 34) via OAEP.
import os, math
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Util.number import long_to_bytes
d="extracted/keys_and_messages"
k21=RSA.import_key(open(d+"/21.pem").read())
k34=RSA.import_key(open(d+"/34.pem").read())
g=math.gcd(k21.n,k34.n)
p=g
q21=k21.n//p
r34=k34.n//p
print("p bits",p.bit_length(),"q21 bits",q21.bit_length(),"r34 bits",r34.bit_length())
def oaep_decrypt(n,e,p2,q2,ct_hex):
    # build private key from factors
    import gmpy2
    phi=(p2-1)*(q2-1)
    dval=pow(e,-1,phi)
    key=RSA.construct((n,e,dval,p2,q2))
    return PKCS1_OAEP.new(key).decrypt(bytes.fromhex(ct_hex))
ct21=open(d+"/21.ciphertext").read().strip()
ct34=open(d+"/34.ciphertext").read().strip()
m21=oaep_decrypt(k21.n,65537,p,q21,ct21)
m34=oaep_decrypt(k34.n,17,p,r34,ct34)
print("21 ->", m21)
print("34 ->", m34)
import re
for m in (m21,m34):
    mm=re.search(rb"crypto\{[^}]*\}", m)
    if mm: print("FLAG:", mm.group(0).decode())
