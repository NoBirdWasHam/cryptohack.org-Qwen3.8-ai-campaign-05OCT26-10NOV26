#!/usr/bin/env python
# signing_server (101): blind RSA-signature oracle.
#   get_secret -> C = secret^E mod N   (encrypted secret)
#   sign(m)    -> m^D mod N            (private-exponent oracle)
# Blind: pick r; b = C * r^E mod N; sig = b^D = secret * r mod N; secret = sig * r^-1.
import socket, json
s=socket.create_connection(("socket.cryptohack.org",13374),timeout=30); s.settimeout(30)
s.recv(65536)  # welcome
buf=b""
def call(opt):
    global buf
    s.sendall((json.dumps(opt)+"\n").encode())
    while b'}' not in buf:
        d=s.recv(65536)
        if not d: raise EOFError
        buf+=d
    j=json.loads(buf[:buf.index(b'}')+1]); buf=buf[buf.index(b'}')+1:]
    return j
pk=call({"option":"get_pubkey"})
N=int(pk["N"],16); E=int(pk["e"],16)
sec=call({"option":"get_secret"})
C=int(sec["secret"],16)
r=pow(2,1024,N-1)   # random r, coprime to N
blind=(C*pow(r,E,N))%N
sig=call({"option":"sign","msg":hex(blind)})
sigv=int(sig["signature"],16)
secret=(sigv*pow(r,-1,N))%N
msg=secret.to_bytes((secret.bit_length()+7)//8,"big")
print("SECRET:", msg)
m2=msg
import re
mm=re.search(rb"crypto\{[^}]*\}", m2)
print("FLAG:", mm.group(0).decode() if mm else "(flag in secret above)")
s.close()
