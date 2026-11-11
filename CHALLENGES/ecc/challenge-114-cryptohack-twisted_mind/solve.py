#!/usr/bin/env python3
"""twisted_mind (114, ecc, 80pts) — socket.cryptohack.org:13416

Attack (small subgroup):
  order = S * Q, S = 102-bit smooth, Q = 91-bit prime.
  Query 1: x0 = x(P_S), P_S order S  -> A1 = x(k*P_S)  -> k mod S via Pohlig-Hellman.
  Query 2: x0 = x(P_Q), P_Q order Q  -> A2 = x(k*P_Q)  -> verifies live curve matches local.
  (Q-part k mod Q = 91-bit ECDLP: the open problem.)
"""
import json
import math
import os
import random
import socket
import sys

HOST, PORT = "socket.cryptohack.org", 13416
if "--local" in sys.argv:
    HOST, PORT = "127.0.0.1", 13416

p = 2**192 - 237
a = -3 % p
b = 1379137549983732744405137513333094987949371790433997718123
order = 6277101735386680763835789423072729104060819681027498877478
Q = 1763644255088983457164385909
S = order // Q
SMOOTH_FACTORS = [2, 11, 269, 2985973, 1631363213, 123462957881]
assert math.prod(SMOOTH_FACTORS) == S

# ---------------- affine EC arithmetic ----------------
def inv(x):
    return pow(x, p - 2, p)

def pt_add(P, Qp):
    if P is None:
        return Qp
    if Qp is None:
        return P
    x1, y1 = P
    x2, y2 = Qp
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        m = (3 * x1 * x1 + a) * inv(2 * y1) % p
    else:
        m = (y2 - y1) * inv(x2 - x1) % p
    x3 = (m * m - x1 - x2) % p
    y3 = (m * (x1 - x3) - y1) % p
    return (x3, y3)

def pt_mul(k, P):
    R = None
    A = P
    while k:
        if k & 1:
            R = pt_add(R, A)
        A = pt_add(A, A)
        k >>= 1
    return R

def rand_point():
    while True:
        x = random.randrange(p)
        rhs = (x**3 + a * x + b) % p
        y = pow(rhs, (p + 1) // 4, p)
        if (y * y) % p == rhs:
            return (x, y)

def lift(x):
    y = pow((x**3 + a * x + b) % p, (p + 1) // 4, p)
    if (y * y) % p == (x**3 + a * x + b) % p:
        return (x, y)
    return None

def find_point_of_order(target, label):
    for _ in range(50):
        # (order//target)*P has order target when P has full order
        cand = pt_mul(order // target, rand_point())
        if cand is None:
            continue
        if pt_mul(target, cand) is not None:
            continue
        ok = True
        for q in prime_factors(target):
            if pt_mul(target // q, cand) is None:
                ok = False
                break
        if ok:
            print(f"found {label} order point (x={cand[0]})")
            return cand
    raise RuntimeError(f"no point of order {target}")

from sympy import factorint
def prime_factors(n):
    return list(factorint(n).keys())

# ---------------- BSGS DLP in prime-order group ----------------
def bsgs(G, T, q):
    """Find e in [0,q) with e*G == T, where ord(G) == q (prime)."""
    if T is None:
        return 0
    m = math.isqrt(q - 1) + 1
    table = {}
    R = None
    for i in range(m):
        table.setdefault(R if R is not None else (0, 0), i)
        R = pt_add(R, G)
    neg_factor = pt_mul(q - m, G)  # -(m*G)
    cur = T
    for j in range(1, m + 2):
        cur = pt_add(cur, neg_factor)
        key = cur if cur is not None else (0, 0)
        if key in table:
            return (j * m + table[key]) % q
    raise RuntimeError("DLP not found")

# ---------------- server I/O ----------------
class Conn:
    def __init__(self):
        self.s = socket.create_connection((HOST, PORT), timeout=110)
        self.buf = b""
    def recv_msg(self):
        while True:
            i = self.buf.find(b"\n")
            if i != -1:
                raw = self.buf[:i].decode()
                self.buf = self.buf[i + 1:]
                try:
                    return json.loads(raw)
                except json.JSONDecodeError:
                    return raw
            self.buf += self.s.recv(65536)
    def recv_obj(self):
        while True:
            msg = self.recv_msg()
            if isinstance(msg, dict):
                return msg
    def send(self, obj):
        self.s.sendall(json.dumps(obj).encode() + b"\n")

# ---------------- main ----------------
def main():
    random.seed()
    print(f"[+] connecting {HOST}:{PORT}")
    c = Conn()
    banner = c.recv_msg()
    print("[+] banner:", json.dumps(banner)[:200])

    print("[+] finding P_S (order S) and P_Q (order Q) ...")
    P_S = find_point_of_order(S, "P_S")
    P_Q = find_point_of_order(Q, "P_Q")

    print("[+] query 1: x(P_S)")
    c.send({"option": "get_pubkey", "x0": P_S[0]})
    resp = c.recv_obj()
    if "pubkey" not in resp:
        raise RuntimeError(f"unexpected response: {resp}")
    A1x = resp["pubkey"]
    print(f"    A1 = {str(A1x)[:40]}...")

    print("[+] query 2: x(P_Q)")
    c.send({"option": "get_pubkey", "x0": P_Q[0]})
    resp = c.recv_obj()
    if "pubkey" not in resp:
        raise RuntimeError(f"unexpected response: {resp}")
    A2x = resp["pubkey"]
    print(f"    A2 = {str(A2x)[:40]}...")

    # ---- curve-consistency verification ----
    print("[+] verifying live curve matches local ...")
    A1 = lift(A1x)
    A2 = lift(A2x)
    print(f"    A1 on local curve: {A1 is not None}")
    print(f"    A2 on local curve: {A2 is not None}")
    if A1:
        print(f"    S*A1 == O (A1 in S-subgroup): {pt_mul(S, A1) is None}")
    if A2:
        print(f"    Q*A2 == O (A2 in Q-subgroup): {pt_mul(Q, A2) is None}")
        print(f"    S*A2 != O (Q-part nonzero) : {pt_mul(S, A2) is not None}")

    # ---- Pohlig-Hellman: k mod S from A1 ----
    # sign ambiguity: point is A1 or -A1
    results = []
    for sign, A1s in [(1, A1), (-1, (A1[0], p - A1[1]) if A1 else None)]:
        if A1s is None:
            continue
        residues = {}
        for q in SMOOTH_FACTORS:
            G = pt_mul(S // q, P_S)
            T = pt_mul(S // q, A1s)
            e = bsgs(G, T, q)
            residues[q] = e
            print(f"    k mod {q} = {e}   (bsgs m={math.isqrt(q-1)+1})")
        # CRT
        r = 0
        m = 1
        for q, e in residues.items():
            # solve r ≡ e (mod q), r ≡ current (mod m)
            mi = pow(m, -1, q)
            r = (r + (e - r) * mi % q * m) % (m * q)
            m *= q
        results.append((sign, r))
        print(f"[+] sign={sign}: k mod S = {r}")

    out = {
        "A1x": A1x,
        "A2x": A2x,
        "P_S_x": P_S[0],
        "P_Q_x": P_Q[0],
        "k_mod_S_candidates": [r for _, r in results],
    }
    with open("live_result.json", "w") as f:
        json.dump(out, f, indent=1)
    print("[+] saved live_result.json")
    print("[+] candidates for privkey mod S:", [str(r) for r in out["k_mod_S_candidates"]])
    c.s.close()

if __name__ == "__main__":
    main()
