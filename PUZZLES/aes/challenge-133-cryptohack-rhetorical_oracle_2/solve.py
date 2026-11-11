#!/usr/bin/env python3
"""rhetorical_oracle_2 (133, aes, 150pts) — socket.cryptohack.org:13437

Server:  P = AES-CBC-decrypt(K, iv=FIXED self.iv, submitted_ciphertext)
         good_pad = unpad check; if good: loads(plaintext.decode("unicode_escape"))
         flag if token["user_id"] in ADMINS.  No query limit (max_payload 4096).

Attack (two-stage, duplicate JSON keys):
  Stage 1: use the server's own token first block T1 as our block 0.
           P[0] = D_K(T1) ^ self.iv = P_T1 = b'{"user_id": "UUU'  (16 bytes: 13-char
           JSON prefix + 3 hex chars of our random user_id — unknown to us, but any
           3 printable chars are fine).
  Stage 2: Beaulieu-Desmedt construction of blocks 1..5 (D_K oracle via the padding
           oracle on 2-block submissions; the fixed self.iv only touches block 0 which
           is never padding-checked).  Target plaintext (95B JSON + 0x01 pad = 96B):

           b'{"user_id": "UUU'  (forced by T1, UUU unknown)
           b'","user_id":"0656d38b8cb0b41b82ecc9859cb7c03e53c7c6610bdce9ea14d30d1a33c80204"}'
           + b'\x01'

         => JSON with DUPLICATE user_id keys; json.loads keeps the LAST one = admin.
         Pure ASCII => unicode_escape decode is identity.
"""
import socket, json, os, sys, time

HOST, PORT = "socket.cryptohack.org", 13437
if "--local" in sys.argv:
    HOST, PORT = "127.0.0.1", 13937
ADMIN = "0656d38b8cb0b41b82ecc9859cb7c03e53c7c6610bdce9ea14d30d1a33c80204"
# Token plaintext = b'{"user_id": "USER64"}' = 78B + 0x02 0x02 = 80B = 5 blocks.
# P_T[0] = b'{"user_id": "UUU' (13-byte prefix + 3 hex chars of our random user_id,
# unknown but irrelevant).  Forged JSON = P_T[0] (16B) + TAIL[0:79] (79B) = 95B
#   = b'{"user_id": "UUU' + b'","user_id":"ADMIN64"}'  (duplicate user_id, last wins)
# + 0x01 pad (1B) = 96B = 6 blocks.
TAIL = b'","user_id":"' + ADMIN.encode() + b'"}' + b"\x01"  # 80 bytes
assert len(TAIL) == 80, len(TAIL)
NB = 6                                     # total blocks in forged ct
P = [None] * NB
for i in range(1, NB):
    P[i] = TAIL[(i-1)*16 : i*16]
assert P[5][-1] == 1 and len(P[5]) == 16


class Conn:
    def __init__(self):
        self.s = socket.create_connection((HOST, PORT), timeout=60)
        self.s.settimeout(60)
        self.buf = b""
        self.n = 0
        o = self._obj()  # greeting {"token": ...}
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
                self._fill(); continue
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


def recover_D(conn, block):
    """Recover D_K(block) via the oracle: submit [cand, block];
    last decrypted block = D_K(block) ^ cand (self.iv only affects block 0)."""
    res = bytearray(16)
    t0 = time.time()
    for pos in range(16):
        target = pos + 1
        found = None
        for v in range(256):
            cand = bytearray(16)
            cand[15 - pos] = v
            for j in range(pos):
                idx = 15 - pos + 1 + j
                cand[idx] = res[idx] ^ target
            gp, flag = conn.query((bytes(cand) + block).hex())
            if flag:
                return None, flag
            if gp:
                found = v
                break
        if found is None:
            raise RuntimeError(f"no match pos={pos}")
        res[15 - pos] = target ^ found
    print(f"  D recovered in {time.time()-t0:.1f}s (total {conn.n} q)", flush=True)
    return bytes(res), None


def main():
    conn = Conn()
    print(f"token ok, T1={conn.T1.hex()}", flush=True)
    c = [None] * NB
    c[NB - 1] = os.urandom(16)
    for i in range(NB - 1, 1, -1):   # i = 5..2 : build c[i-1]
        Di, flag = recover_D(conn, c[i])
        if flag:
            print("FLAG:", flag); return flag
        c[i - 1] = bytes(a ^ b for a, b in zip(Di, P[i]))
        print(f"  c[{i-1}] = {c[i-1].hex()}", flush=True)
    ct = conn.T1 + b"".join(c[1:])
    print("forged ct len", len(ct), "queries", conn.n, flush=True)
    gp, flag = conn.query(ct.hex())
    print("RESULT good_pad", gp, flush=True)
    if flag:
        print("FLAG:", flag)
    return flag


if __name__ == "__main__":
    main()
