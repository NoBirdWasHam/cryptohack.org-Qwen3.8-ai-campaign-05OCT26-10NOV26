import socket, json, secrets
from Crypto.Util.number import long_to_bytes, bytes_to_long
ADMIN=b"admin=True"; V=bytes_to_long(ADMIN)
class Conn:
    def __init__(s,host,port):
        s.sock=socket.create_connection((host,port),timeout=60); s.sock.settimeout(30); s.buf=b""
    def send(s,obj): s.sock.sendall((json.dumps(obj)+"\n").encode())
    def recv(s):
        dec=json.JSONDecoder()
        while True:
            t=s.buf.lstrip()
            if t:
                try:
                    obj,idx=dec.raw_decode(t.decode())
                    s.buf=s.buf[len(s.buf)-len(t)+idx:]
                    return obj
                except json.JSONDecodeError: pass
            d=s.sock.recv(65536)
            if not d: raise EOFError
            s.buf+=d
s=Conn("socket.cryptohack.org",13376); s.sock.recv(65536)
s.send({"option":"get_pubkey"}); pk=s.recv()
N=int(pk["N"],16); E=int(pk["e"],16)
flag=None
for _ in range(20):
    r=secrets.randbelow(N-2)+1
    msgp=(V*pow(r,E,N))%N
    mb=msgp.to_bytes((msgp.bit_length()+7)//8,'big')
    if ADMIN in mb: continue
    s.send({"option":"sign","msg":mb.hex()}); resp=s.recv()
    sigp=int(resp["signature"],16); sig=(sigp*pow(r,-1,N))%N
    s.send({"option":"verify","msg":long_to_bytes(V).hex(),"signature":hex(sig)}); vr=s.recv()
    if "response" in vr and vr["response"].startswith("crypto{"):
        flag=vr["response"]; break
s.sock.close()
open("flag.txt","w").write(flag)
print("FLAG_WRITTEN", flag)
