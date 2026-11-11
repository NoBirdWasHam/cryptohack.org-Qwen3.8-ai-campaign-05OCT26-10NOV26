import socket, json
from Crypto.Cipher import AES
def bxor(a,b): return bytes(x^y for x,y in zip(a,b))
HOST="socket.cryptohack.org"; PORT=13388
s=socket.create_connection((HOST,PORT),timeout=60); s.settimeout(40)
buf=b''
def fill():
    global buf
    d=s.recv(65536)
    if d: buf+=d
def obj():
    global buf
    while True:
        i=buf.find(b'{')
        if i<0: fill(); continue
        try:
            o,_=json.JSONDecoder().raw_decode(buf[i:].decode('utf-8','ignore')); buf=buf[:i]; return o
        except json.JSONDecodeError: fill()
def send(o):
    s.sendall(json.dumps(o).encode()+b"\n"); return obj()
# msg1 = 15 bytes (no admin)
msg1=b'a'*15
r=send({"option":"sign","message":msg1.hex()})
sig1=bytes.fromhex(r["signature"])
print("sig1:",sig1.hex())
# block2 = pad("admin=True"+5 bytes, 16)
admin=b"admin=True"+b"a"*5   # 15 bytes
block2=admin+b"\x01"        # 16 bytes
forged=bxor(AES.new(block2,AES.MODE_ECB).encrypt(sig1),sig1)
print("forged:",forged.hex())
# message2 = msg1 || 0x01 || admin  (server pads the whole thing)
msg2=msg1+b"\x01"+admin
r=send({"option":"get_flag","signature":forged.hex(),"message":msg2.hex()})
print("RESULT:",r)
s.close()
