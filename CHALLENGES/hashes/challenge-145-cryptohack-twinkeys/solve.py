#!/usr/bin/env python3
"""twinkeys exploit: send the textcoll MD5 collision pair to socket.cryptohack.org:13397.

msg1 must start with b"CryptoHack Secure Safe" (byte21='e'); msg2 differs at byte21 ('i').
Usage: python solve.py [msg1.bin msg2.bin]   (defaults: assembled from textcoll outputs)
"""
import json
import socket
import sys
import hashlib
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BT = os.path.join(HERE, "build_textcoll")
KEY_START = b"CryptoHack Secure Safe"


def assemble():
    b1a = open(os.path.join(BT, "textcoll1_block1_0.txt"), "rb").read()
    b1b = open(os.path.join(BT, "textcoll2_block1_0.txt"), "rb").read()
    cands = []
    for n2 in ("textcoll1_block2_0.txt", "textcoll2_block2_0.txt"):
        p = os.path.join(BT, n2)
        if os.path.exists(p):
            b2 = open(p, "rb").read()
            cands.append((b1a + b2, b1b + b2))
            cands.append((b1a + b2, b1b + b2))
    # also same-block2 combos
    p1 = os.path.join(BT, "textcoll1_block2_0.txt")
    p2 = os.path.join(BT, "textcoll2_block2_0.txt")
    if os.path.exists(p1) and os.path.exists(p2):
        cands.append((b1a + open(p1, "rb").read(), b1b + open(p2, "rb").read()))
    return cands


def main():
    if len(sys.argv) >= 3:
        msgs = [(open(sys.argv[1], "rb").read(), open(sys.argv[2], "rb").read())]
    else:
        msgs = assemble()

    m1 = m2 = None
    for a, b in msgs:
        if hashlib.md5(a).hexdigest() == hashlib.md5(b).hexdigest() and a != b:
            if a.startswith(KEY_START) and not b.startswith(KEY_START):
                m1, m2 = a, b
                break
            if b.startswith(KEY_START) and not a.startswith(KEY_START):
                m1, m2 = b, a
                break
    if m1 is None:
        print("No valid collision pair found locally. Aborting.")
        for a, b in msgs:
            print(" md5 equal:", hashlib.md5(a).hexdigest() == hashlib.md5(b).hexdigest(),
                  "a prefix:", a.startswith(KEY_START), "b prefix:", b.startswith(KEY_START),
                  "len", len(a), len(b))
        sys.exit(1)
    print("local md5:", hashlib.md5(m1).hexdigest(), "len", len(m1))

    s = socket.create_connection(("socket.cryptohack.org", 13397), timeout=30)
    f = s.makefile("rw", newline="\n")

    def recvline():
        line = f.readline()
        if not line:
            raise EOFError("connection closed")
        print("<", line.strip())
        try:
            return json.loads(line)
        except Exception:
            return {"raw": line}

    def sendline(obj):
        data = json.dumps(obj) + "\n"
        print(">", data.strip())
        f.write(data)
        f.flush()

    recvline()  # greeting
    sendline({"option": "insert_key", "key": m1.hex()})
    recvline()
    sendline({"option": "insert_key", "key": m2.hex()})
    recvline()
    sendline({"option": "unlock"})
    r = recvline()
    print("RESULT:", r)


if __name__ == "__main__":
    main()
