#!/usr/bin/env python
"""Seventy-Two (50 pts, hashes/key-derivation): bcrypt 72-byte truncation.

material = f"{TENANT}|{username}|{password}" is hashed with bcrypt, which silently
uses only the first 72 bytes. For username k.barrymore@corp.bluerock.example the
prefix "TENANT|username|" is 71 bytes, so ONLY the first byte of the 32-char random
password affects the stored hash -> at most 62 login guesses.
"""
import json, socket, string, sys

HOST, PORT = "socket.cryptohack.org", 13433
TARGET = "k.barrymore@corp.bluerock.example"
CHARSET = string.ascii_letters + string.digits  # server's PASSWORD_CHARSET

def try_login(password, verbose=True):
    s = socket.create_connection((HOST, PORT), timeout=30)
    f = s.makefile("r", encoding="utf-8", errors="replace")
    before = f.readline()
    if verbose:
        print("BEFORE:", before.strip()[:200])
    s.sendall((json.dumps({"username": TARGET, "password": password}) + "\n").encode())
    resp = f.readline()
    s.close()
    try:
        d = json.loads(resp)
    except Exception:
        d = {"raw": resp.strip()[:200]}
    return d

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "probe":
        print(json.dumps(try_login("a")))
        sys.exit(0)
    for i, c in enumerate(CHARSET, 1):
        d = try_login(c, verbose=False)
        msg = d.get("msg", "")
        if "Flag:" in msg:
            print(f"GOT IT at guess {i}/{len(CHARSET)}: pw[0] = {c!r}")
            print("RESPONSE:", json.dumps(d))
            flag = msg.split("Flag: ", 1)[1].strip()
            open("seventy_two_flag.txt", "w").write(flag + "\n")
            sys.exit(0)
        if verbose := (i % 10 == 0):
            print(f"guess {i}: {msg or d}")
    print("ALL 62 GUESSES FAILED")
