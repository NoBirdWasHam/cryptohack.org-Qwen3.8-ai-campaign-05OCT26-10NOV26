#!/usr/bin/env python
"""long_story_short (60 pts) — PBKDF2-HMAC-SHA256 key = the published fingerprint.

Weakness: the passphrase is 128 bytes, i.e. LONGER than the SHA-256 HMAC block
size (64 bytes). Per RFC 2104, an HMAC key longer than the block size is first
replaced by H(key) — here H = SHA-256. So inside every HMAC call the effective
key is SHA-256(passphrase) ... which is EXACTLY the published fingerprint.
Sending passphrase_hex = fingerprint (32 bytes) makes the server derive the same
PBKDF2 key as the true 128-byte passphrase, and the vault opens.

The key can also be computed locally to verify the reasoning before connecting.
"""
import hashlib
import json
import socket
import sys

HOST, PORT = "socket.cryptohack.org", 13434
SALT = b"bluerock-vault-2026"
ITER = 200000


def recv_line(sock):
    buf = b""
    while not buf.endswith(b"\n"):
        c = sock.recv(1)
        if not c:
            raise ConnectionError("closed")
        buf += c
    return buf


def main():
    s = socket.create_connection((HOST, PORT), timeout=60)
    line = recv_line(s).decode().strip()
    print("BEFORE_INPUT:", file=sys.stderr)
    print(line, file=sys.stderr)
    info = json.loads(line)
    fp = info["passphrase_fingerprint"]
    print("fingerprint:", fp, file=sys.stderr)

    # sanity: derive key locally from the fingerprint (the aha of the challenge)
    key_from_fp = hashlib.pbkdf2_hmac("sha256", bytes.fromhex(fp), SALT, ITER, 32)
    print("local key from fingerprint:", key_from_fp.hex(), file=sys.stderr)

    # send the fingerprint as passphrase_hex: len 32 <= 64, so HMAC uses it as-is,
    # zero-padded — identical effective key to SHA256(128-byte passphrase)
    s.sendall((json.dumps({"passphrase_hex": fp}) + "\n").encode())
    resp = recv_line(s).decode().strip()
    print("RESPONSE:", file=sys.stderr)
    print(resp, file=sys.stderr)
    obj = json.loads(resp)
    msg = obj.get("msg", "")
    import re
    m = re.search(r"crypto\{[^}]*\}", msg)
    flag = m.group(0) if m else None
    if flag:
        open("flag.txt", "w").write(flag + "\n")
        print("FLAG:", flag)
    else:
        print("NO FLAG FOUND in response")
    s.close()


if __name__ == "__main__":
    main()
