#!/usr/bin/env python3
"""rhetorical_oracle_2 (133, aes, 150pts) — socket.cryptohack.org:13437  (v2)

Server:  P = AES-CBC-decrypt(K, iv=FIXED, submitted_ct); good_pad = unpad OK;
         if good_pad: token = loads(P.decode("unicode_escape"), strict=False);
         flag if token["user_id"] in ADMINS.

Why v1 (subagent's) failed:
  6-block ct = [T1, c1..c5] controls P[0..4] but NOT P[1] = D(c1)^T1, which is
  uncontrolled garbage sitting inside the first JSON string value -> JSON broken
  / user_id never becomes admin. good_pad True, no flag.

v2 attack (7 blocks):
  ct = [T1, c1, c2, c3, c4, c5, c6]
  P[0] = '{"user_id": "h1h2h3'      (forced by T1)
  P[1] = G = D(c1)^T1               (random; MUST contain no 0x22 '"' and no 0x5c '\\')
  P[2..6] = T = '","user_id":"' + ADMIN + '"}' + b'\x01'   (80B, fully controlled)
  => JSON = {"user_id": "h1h2h3<clean-G>","user_id":"ADMIN"}  (strict=False allows
     control chars; unicode_escape is identity when G has no backslash)
  => duplicate key, LAST wins => user_id == ADMIN => flag.

Construction per attempt (one connection; key+T1 are per-connection):
  c6 = random; c5 = D(c6)^P6; c4 = D(c5)^P5; c3 = D(c4)^P4; c2 = D(c3)^P3; c1 = D(c2)^P2
  G = D(c1)^T1  (6th recovery)
  P(G clean) = (254/256)^16 ~= 88% -> expected ~1.1 attempts.
"""
import json
import os
import socket
import sys
import time

HOST, PORT = "socket.cryptohack.org", 13437
if "--local" in sys.argv:
    HOST, PORT = "127.0.0.1", 13937
ADMIN = "0656d38b8cb0b41b82ecc9859cb7c03e53c7c6610bdce9ea14d30d1a33c80204"

T = b'","user_id":"' + ADMIN.encode() + b'"}' + b"\x01"
assert len(T) == 80
NB = 7  # T1 + c1..c6
P = [None] * NB
for i in range(2, NB):
    P[i] = T[(i - 2) * 16:(i - 1) * 16]
assert P[6][-1] == 1


class Conn:
    def __init__(self):
        self.s = socket.create_connection((HOST, PORT), timeout=120)
        self.s.settimeout(120)
        self.buf = b""
        self.n = 0
        o = self._obj()
        self.token = bytes.fromhex(o["token"])
        assert len(self.token) == 80, len(self.token)
        self.T1 = self.token[:16]

    def _fill(self):
        d = self.s.recv(65536)
        if not d:
            raise EOFError
        self.buf += d

    def _obj(self):
        while True:
            i = self.buf.find(b"{")
            if i < 0:
                self._fill()
                continue
            try:
                o, _ = json.JSONDecoder().raw_decode(self.buf[i:].decode("utf-8", "ignore"))
                self.buf = self.buf[:i]
                return o
            except json.JSONDecodeError:
                self._fill()

    def query(self, hexct):
        self.s.sendall(json.dumps({"ciphertext": hexct}).encode() + b"\n")
        self.n += 1
        o = self._obj()
        if "flag" in o:
            return True, o["flag"]
        return bool(o.get("good_pad", False)), None

    def close(self):
        try:
            self.s.close()
        except OSError:
            pass


def recover_D(conn, block):
    res = bytearray(16)
    t0 = time.time()
    for pos in range(16):
        target = pos + 1
        found = None
        for v in range(256):
            cand = bytearray(16)
            cand[15 - pos] = v
            for j in range(pos):
                cand[15 - pos + 1 + j] = res[15 - pos + 1 + j] ^ target
            gp, flag = conn.query((bytes(cand) + block).hex())
            if flag:
                return None, flag
            if gp:
                found = v
                break
        if found is None:
            raise RuntimeError(f"no match pos={pos}")
        res[15 - pos] = target ^ found
    print(f"  D recovered in {time.time()-t0:.0f}s (total {conn.n} q)", flush=True)
    return bytes(res), None


def attempt(attno):
    conn = Conn()
    print(f"attempt {attno}: token ok, T1={conn.T1.hex()}", flush=True)
    c = [None] * NB
    c[6] = os.urandom(16)
    for i in range(6, 1, -1):  # i = 6..2 : build c[i-1] = D(c[i]) ^ P[i]
        Di, flag = recover_D(conn, c[i])
        if flag:
            return flag
        c[i - 1] = bytes(a ^ b for a, b in zip(Di, P[i]))
        print(f"  c[{i-1}] = {c[i-1].hex()}", flush=True)
    D1, flag = recover_D(conn, c[1])
    if flag:
        return flag
    G = bytes(a ^ b for a, b in zip(D1, conn.T1))
    print(f"  G = {G.hex()}", flush=True)
    bad = [b for b in G if b in (0x22, 0x5c)]
    if bad:
        print(f"  G has forbidden bytes {bad!r} -> new connection", flush=True)
        conn.close()
        return None
    ct = conn.T1 + b"".join(c[1:])
    gp, flag = conn.query(ct.hex())
    print(f"  forged ct sent (len {len(ct)}, queries {conn.n}) good_pad={gp}", flush=True)
    conn.close()
    return flag


def main():
    for attno in range(1, 12):
        flag = attempt(attno)
        if flag:
            print("FLAG:", flag, flush=True)
            return flag
        time.sleep(2)
    print("gave up after 10 attempts", flush=True)
    return None


if __name__ == "__main__":
    main()
