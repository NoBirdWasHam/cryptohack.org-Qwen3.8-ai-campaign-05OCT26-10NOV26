#!/usr/bin/env python
# sigma-intro (225, zkp, 20pts): Schnorr proof of DLOG knowledge.
# Source gives p,q,g,w,y directly -> play the protocol for real.
import socket, json, secrets
p=0x1ed344181da88cae8dc37a08feae447ba3da7f788d271953299e5f093df7aaca987c9f653ed7e43bad576cc5d22290f61f32680736be4144642f8bea6f5bf55ef
q=0xf69a20c0ed4465746e1bd047f57223dd1ed3fbc46938ca994cf2f849efbd5654c3e4fb29f6bf21dd6abb662e911487b0f9934039b5f20a23217c5f537adfaaf7
g=2
w=0x5a0f15a6a725003c3f65238d5f8ae4641f6bf07ebf349705b7f1feda2c2b051475e33f6747f4c8dc13cd63b9dd9f0d0dd87e27307ef262ba68d21a238be00e83
y=0x514c8f56336411e75d5fa8c5d30efccb825ada9f5bf3f6eb64b5045bacf6b8969690077c84bea95aab74c24131f900f83adf2bfe59b80c5a0d77e8a9601454e5
assert pow(g,w,p)==y%p
s=socket.create_connection(("socket.cryptohack.org",13425),timeout=30); s.settimeout(10)
import time
s.recv(65536)  # greeting
buf=b""
def recv_json():
    global buf
    for _ in range(200):
        try:
            obj,idx=json.JSONDecoder().raw_decode(buf.decode("utf-8","replace"))
            buf=buf[idx:]; return obj
        except json.JSONDecodeError:
            try: d=s.recv(65536)
            except socket.timeout: continue
            if not d:  # connection closed; parse whatever arrived
                obj,idx=json.JSONDecoder().raw_decode(buf.decode("utf-8","replace"))
                buf=buf[idx:]; return obj
            buf+=d
    raise RuntimeError("no json in buffer")
r=secrets.randbelow(q-1)+1
a=pow(g,r,p)
s.sendall((json.dumps({"a":a})+"\n").encode())
ch=recv_json()
e=ch["e"]
z=(r+e*w)%q
s.sendall((json.dumps({"z":z})+"\n").encode())
res=recv_json()
print("RESULT:", json.dumps(res))
s.close()
