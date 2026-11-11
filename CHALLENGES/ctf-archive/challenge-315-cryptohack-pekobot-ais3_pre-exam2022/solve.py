# Invalid-curve/ECDH oracle: ask server to compute C1*d = rP, XOR out of quote ciphertext, decrypt flag.
import socket, time

HOST, PORT = "archive.cryptohack.org", 45328
QUOTES = [
    "Konpeko, konpeko, konpeko! Hololive san-kisei no Usada Pekora-peko! domo, domo!",
    "Bun bun cha! Bun bun cha!",
    "kitira!",
    "usopeko deshou",
    "HA\u2191HA\u2191HA\u2193HA\u2193HA\u2193",
    "HA\u2191HA\u2191HA\u2191HA\u2191",
    "it's me pekora!",
    "ok peko",
]

def recv_until(sock, t=5.0):
    sock.settimeout(t)
    buf = b""
    try:
        while True:
            d = sock.recv(4096)
            if not d: break
            buf += d
            if buf.rstrip().endswith(b"> "): break
    except socket.timeout:
        pass
    return buf.decode(errors="replace")

s = socket.create_connection((HOST, PORT), timeout=10)
log = recv_until(s)
print("BANNER:", log.replace("\n", " | "))

def send(msg):
    s.sendall((msg + "\n").encode())
    return recv_until(s)

# Get encrypted flag
out = send("2")
hexes = [l.strip() for l in out.splitlines() if all(c in "0123456789abcdef" for c in l.strip()) and len(l.strip()) >= 64]
assert len(hexes) >= 2, out
C1 = bytes.fromhex(hexes[0]); C2 = bytes.fromhex(hexes[1])
x = int.from_bytes(C1[:32], "big"); y = int.from_bytes(C1[32:], "big")
print("C1 x,y:", x, y)

# Ask server for S = C1 * d = rP, encrypted under a random known quote
out2 = send("1")
out3 = send(str(x))
out4 = send(str(y))
ct_line = [l.strip() for l in out4.splitlines() if len(l.strip()) == 128 and all(c in "0123456789abcdef" for c in l.strip())]
assert ct_line, out2 + out3
ct = bytes.fromhex(ct_line[0])
print("ct ok, try quotes...")

for q in QUOTES:
    qb = q.encode().ljust(64, b"\0")[:64]
    key = bytes(a ^ b for a, b in zip(ct, qb))
    flag = bytes(a ^ b for a, b in zip(C2, key))
    i = flag.find(b"}")
    cand = flag[:i+1] if 4 < i < 40 else None
    if cand and cand.startswith(b"AIS3{") and all(32 <= c < 127 for c in cand):
        print("FLAG:", cand.decode())
        break
else:
    print("no candidate matched")
s.close()
