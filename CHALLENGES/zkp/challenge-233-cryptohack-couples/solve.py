# CryptoHack "couples" (zkp, port 13415)
# Attack: set_internal_z with z = p-5. Then poly(z,x) = x^(z+7) - x^3 = x^(p+2)-x^3
# = x^3*(x^(p-1)-1) = 0 mod p (Fermat, x != 0). inverse(0,p) returns 0, so the
# server sets self.z = 0 (the "Wtf?" guard checks x*z==1 mod p, and 0 != 1).
# With z=0: xzH and xzG are both the point at infinity, so
#   l = pairing(inf, G1) = 1  and  r = pairing(received_H, inf) = 1  -> equal.
# Any on-curve G and any hsh then yields the flag.
import socket, json

PORT = 13415
p = 21888242871839275222246405745257275088696311157297823662689037894645226208583

s = socket.create_connection(("socket.cryptohack.org", PORT), timeout=30)
s.settimeout(25)

def read_until_obj(buf):
    while True:
        bpos = buf.find(b"{")
        if bpos >= 0:
            try:
                obj, i = json.JSONDecoder().raw_decode(buf[bpos:].decode())
                return obj, buf[bpos + i:]
            except json.JSONDecodeError:
                pass
        d = s.recv(65536)
        if not d:
            raise RuntimeError("connection closed")
        buf += d

buf = b""  # plain-text greeting is skipped by read_until_obj (no '{' in it)

def send(obj):
    s.sendall((json.dumps(obj) + "\n").encode())

# 1) zero out internal z
send({"option": "set_internal_z", "z": hex(p - 5)})
msg, buf = read_until_obj(buf)
print("set_internal_z ->", msg)
assert "msg" in msg and "changed" in msg["msg"], msg

# 2) trivial proof: G = G1 generator (1,2,1), arbitrary hsh
send({"option": "do_proof", "G": "(1,2,1)", "hsh": "1"})
msg, buf = read_until_obj(buf)
print("do_proof ->", msg)
if "msg" in msg and msg["msg"].startswith("crypto{"):
    print("FLAG:", msg["msg"])
else:
    raise SystemExit("no flag: %r" % (msg,))
