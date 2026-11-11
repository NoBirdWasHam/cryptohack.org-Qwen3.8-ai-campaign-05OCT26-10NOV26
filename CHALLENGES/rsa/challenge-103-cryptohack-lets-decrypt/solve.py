#!/usr/bin/env python
# lets_decrypt (103): server checks pow(SIGNATURE, e, n) == bytes_to_long(EMSA(msg,256))
#   with n, e chosen BY US (no primality check).  Take e=1, n = SIGNATURE - DL
#   (n > DL, n | (SIG-DL))  =>  pow(SIG,1,n) = SIG % n = DL.  msg must match the regex.
import socket, json, re
from Crypto.Hash import SHA256, SHA1
from Crypto.Util.number import bytes_to_long
def encode(msg, k):
    # server uses SHA-1 (DigestInfo: 30 21 30 09 06 05 2b 0e 03 02 1a 05 00 04 14 <20B>)
    m=msg.encode(); dig=SHA1.new(m).digest()
    di=bytes.fromhex("3021300906052b0e03021a0500")
    em=di + b"\x04\x14" + dig
    ps=k-2-1-len(em)
    assert ps>=8, ps
    return b"\x00\x01"+b"\xff"*ps+b"\x00"+em
pre="I am Mallory"; post=" own CryptoHack.org"
msg=pre+"x"*(256-len(pre)-len(post))+post
assert len(msg)==256 and re.match(r'^I am Mallory.*own CryptoHack.org$', msg)
s=socket.create_connection(("socket.cryptohack.org",13391),timeout=30); s.settimeout(30); s.recv(65536)
buf=b""
def call(opt):
    global buf
    s.sendall((json.dumps(opt)+"\n").encode())
    while True:
        try:
            j=json.loads(buf); buf=b""; return j
        except Exception:
            pass
        d=s.recv(65536)
        if not d: raise EOFError
        buf+=d
SIG=int(call({"option":"get_signature"})["signature"],16)
DL=bytes_to_long(encode(msg,256))
assert DL < SIG, (DL.bit_length(), SIG.bit_length())
n=SIG-DL
assert pow(SIG,1,n)==DL, "mod check failed"
resp=call({"option":"verify","msg":msg,"N":hex(n),"e":"0x1"})
fl=re.search(r'crypto\{[^}]*\}', str(resp))
print("FULL RESP:", resp)
print("FLAG:", fl.group(0) if fl else None)
s.close()
