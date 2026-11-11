#!/usr/bin/env python3
"""Solve letsproveitagain (socket.cryptohack.org:13431).

Differences from part 1: v is drawn ONCE in __init__ and reused in every proof;
the Fiat-Shamir challenge c = sha3_256(t^y^g^salt) with salt = R.randint(2,1024)
(only ~1023 possibilities, unknown to us); max_turns = 4.

Attack: choose our own seed via refresh so two proofs share the same prime p
(and the same v). For each proof r = (v - c*FLAG) mod (p-1); since c*FLAG < p-1
and v < p-1, this is exact: r = p-1 + v - c*FLAG. Subtracting the two proofs:
    r_a - r_b = (c_b - c_a) * FLAG
Brute-force salt_a, salt_b in [2,1024] until (r_a-r_b)/(c_b-c_a) is an integer
that decodes to a valid flag. No knowledge of p or v required.

Turn sequence (4 get_proofs max): P1, refresh(seed), P2 (our p), P3,
refresh(seed), P4 (our p again). P2 & P4 are the pair used.
"""
import json, socket, hashlib, sys

BITS = 2 << 9
G = 2
HOST, PORT = "socket.cryptohack.org", 13431
NONCE = None

def decode_flag(S):
    if S <= 0 or S.bit_length() > 320:
        return None
    X = S.to_bytes(39, "big")
    mid = bytes(a ^ b for a, b in zip(X[7:38], NONCE))
    bs = X[:7] + mid + X[38:]
    for i in range(39):
        cand = bs[:i] + bs[i+1:]
        if (cand.startswith(b"crypto{") and cand.endswith(b"}")
                and all(32 <= c < 127 for c in cand)):
            return cand.decode()
    return None

def csalts(t, y):
    return [bytes_to_long_sha3(t ^ y ^ G ^ salt) for salt in range(2, BITS + 1)]

def bytes_to_long_sha3(b):
    from Crypto.Util.number import bytes_to_long, long_to_bytes
    return bytes_to_long(hashlib.sha3_256(long_to_bytes(b)).digest())

def attack(send):
    send({"option": "get_proof"})                     # P1 (turn1, unlocks refresh)
    seed = bytes(8)
    m = send({"option": "refresh", "seed": seed.hex()})
    assert "msg" in m, m
    a = send({"option": "get_proof"})                 # P2: p from OUR seed
    send({"option": "get_proof"})                     # P3 (burn, unlocks refresh)
    m = send({"option": "refresh", "seed": seed.hex()})
    assert "msg" in m, m
    b = send({"option": "get_proof"})                 # P4: same p, same v
    assert a["y"] == b["y"], "proofs must share p (same y)"
    num = a["r"] - b["r"]
    ca = csalts(a["t"], a["y"])
    cb = csalts(b["t"], b["y"])
    for c2 in ca:
        for c4 in cb:
            den = c4 - c2
            if den and num % den == 0:
                fl = decode_flag(num // den)
                if fl:
                    return fl
    return None

# ---------------- offline harness ----------------
def make_offline():
    src = open("13431.py").read()
    src = src.replace("from utils import listener", "")
    src = src.replace("listener.start_server(port=13431)", "")
    src = src.replace('FLAG = b"crypto{?????????????????????????????}"',
                      'FLAG = b"crypto{" + b"Ag41n_Zk_S1gm4_Pr070c41!"[:30].ljust(30, b"Q") + b"}"')
    ns = {"__name__": "srv"}
    exec(compile(src, "13431.py", "exec"), ns)
    ch = ns["Challenge"]()
    global NONCE
    NONCE = bytes.fromhex(ch.before_input.split(": ")[1].strip())
    return ch.challenge

# ---------------- live socket ----------------
def connect():
    s = socket.create_connection((HOST, PORT), timeout=120)
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
            open("flag_letsproveitagain.txt", "w").write(flag)
        s.close()
