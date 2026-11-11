#!/usr/bin/env python3
"""Collider (CryptoHack #13389, 50 pts) — MD5 collision exploit.

The service keys stored documents by MD5 hash. A fresh Challenge instance is
created per CONNECTION (verified by live probing: a doc added on conn 1 is
gone on conn 2), but the connection stays open and processes MULTIPLE JSON
lines per session. So:

  conn: send A -> "added to system"
        send B -> md5(B) == md5(A), B != A -> "Document system crash,
                  leaking flag: crypto{...}"

(A, B) is a generic MD5 collision pair generated with md5fastcoll (Marc
Stevens' hashclash core, built from source; no second preimage needed —
2^123, infeasible). This pair: md5 = 3778dd67655b79828307612d215f560a,
128 bytes each.

Note: the two pre-stored docs in the source (508dcc.../cb07ff...) have keys
that match their content exactly, so colliding with them would require a
second preimage — the in-connection trick above is the actual path.
"""
import hashlib
import json
import socket
import sys

HOST, PORT = "socket.cryptohack.org", 13389
MSG1 = r"~\AppData\Local\hermes\cache\scratch\hashclash_src\msg1.bin"
MSG2 = r"~\AppData\Local\hermes\cache\scratch\hashclash_src\msg2.bin"


def main():
    a = open(MSG1, "rb").read()
    b = open(MSG2, "rb").read()
    ha, hb = hashlib.md5(a).hexdigest(), hashlib.md5(b).hexdigest()
    assert ha == hb, f"local collision check failed: {ha} != {hb}"
    assert a != b, "documents must differ"
    print(f"collision pair: md5={ha}")

    s = socket.create_connection((HOST, PORT), timeout=30)
    s.settimeout(15)
    try:
        buf = b""
        while b"\n" not in buf:  # prompt line (plain text)
            buf += s.recv(4096)
        print(f"prompt: {buf.split(b'\n')[0]!r}")

        s.sendall((json.dumps({"document": a.hex()}) + "\n").encode())
        buf = b""
        while b"\n" not in buf:
            buf += s.recv(4096)
        r1 = json.loads(buf.split(b"\n")[0])
        print(f"send A: {r1}")

        s.sendall((json.dumps({"document": b.hex()}) + "\n").encode())
        buf = b""
        while b"\n" not in buf:
            buf += s.recv(4096)
        r2 = json.loads(buf.split(b"\n")[0])
        print(f"send B: {r2}")
        msg = json.dumps(r2)
        if "crypto{" in msg:
            flag = msg[msg.index("crypto{"): msg.index("}") + 1]
            print("FLAG:", flag)
            return 0
    finally:
        s.close()
    print("no flag in response")
    return 1


if __name__ == "__main__":
    sys.exit(main())
