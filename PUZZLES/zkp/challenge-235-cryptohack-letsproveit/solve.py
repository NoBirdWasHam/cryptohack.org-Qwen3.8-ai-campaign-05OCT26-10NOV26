#!/usr/bin/env python3
"""Solve letsproveit (socket.cryptohack.org:13430).

Attack: the server's prime p is drawn from random.Random(nonce + seed) and we
control `seed` via the refresh option -> we can recompute p locally.
Proof: r = (v - c*FLAG) mod (p-1) with c = sha3_256(t^y^g)^2 (~2^512),
FLAG ~ 2^310, v < 2^512, c*FLAG < p-1  =>  r = p-1 + v - c*FLAG exactly.
So c*FLAG = (p-1-r) + v with v in [0, 2^512) => FLAG in {(p-1-r)//c + d},
d in 0..~5 (width 2^512/c <= 4). Verify candidate with pow(2, S, p) == y.
"""
import json, socket, hashlib, random, sys, string
from Crypto.Util.number import bytes_to_long, long_to_bytes, isPrime

BITS = 2 << 9   # 1024
G = 2
HOST, PORT = "socket.cryptohack.org", 13430

def local_p(nonce: bytes, seed: bytes, N=BITS):
    """Replicate server getPrime() from Random(nonce+seed)."""
    R = random.Random(nonce + seed)
    while True:
        number = R.getrandbits(N) | 1
        if isPrime(number, randfunc=lambda x: long_to_bytes(R.getrandbits(x))):
            return number

def decode_flag(S):
    # S = bytes_to_long of 39 bytes: first7 + (middle31 XOR nonce) + last1.
    X = long_to_bytes(S).rjust(39, b"\x00")
    mid = bytes(a ^ b for a, b in zip(X[7:38], NONCE))
    bs = X[:7] + mid + X[38:]
    for i in range(39):
        cand = bs[:i] + bs[i+1:]
        if (cand.startswith(b"crypto{") and cand.endswith(b"}")
                and all(32 <= c < 127 for c in cand)):
            return cand.decode()
    return None

def attack(send):
    """send(dict)->dict. Returns flag string or None."""
    send({"option": "get_proof"})                       # turn 1, unlocks refresh
    seed = bytes(8)
    m = send({"option": "refresh", "seed": seed.hex()})
    assert "msg" in m, m
    resp = send({"option": "get_proof"})                # p now from OUR seed
    t, r, y = resp["t"], resp["r"], resp["y"]
    p = local_p(NONCE, seed)
    c = bytes_to_long(hashlib.sha3_256(long_to_bytes(t ^ y ^ G)).digest()) ** 2
    # c*FLAG = (p-1) + v - r  with v in [0, 2^512)  =>  FLAG in [(p-1-r)/c, (p-1-r+2^512)/c)
    base = p - 1 - r
    q = base // c
    width = (1 << 512) // c + 4
    for d in range(0, width):
        S = q + d
        if pow(G, S, p) == y:
            fl = decode_flag(S)
            if fl:
                return fl
    return None

# ---------------- offline harness ----------------
def make_offline():
    src = open("13430.py").read()
    src = src.replace("from utils import listener", "")
    src = src.replace("listener.start_server(port=13430)", "")
    src = src.replace('FLAG = b"crypto{?????????????????????????????}"',
                      'FLAG = b"crypto{" + b"ZkPr00fM4th3m4t1c5R0ck5!"[:30].ljust(30, b"X") + b"}"')
    ns = {"__name__": "srv"}
    exec(compile(src, "13430.py", "exec"), ns)
    ch = ns["Challenge"]()
    global NONCE
    NONCE = bytes.fromhex(ch.before_input.split(": ")[1].strip())
    return ch.challenge

# ---------------- live socket ----------------
def connect():
    s = socket.create_connection((HOST, PORT), timeout=60)
    f = s.makefile("rwb")
    lines = []
    while True:
        ln = f.readline()
        if not ln:
            break
        lines.append(ln.decode())
        if "nonce" in lines[-1]:
            break
    global NONCE
    NONCE = bytes.fromhex(lines[-1].split(":")[1].strip())
    def send(d):
        f.write((json.dumps(d) + "\n").encode())
        f.flush()
        return json.loads(f.readline().decode())
    return s, send

if __name__ == "__main__":
    if "--local" in sys.argv:
        send = make_offline()
        print("local flag recovered:", attack(send))
    else:
        s, send = connect()
        flag = attack(send)
        print("FLAG:", flag)
        if flag:
            open(f"flag_letsproveit.txt", "w").write(flag)
        s.close()
