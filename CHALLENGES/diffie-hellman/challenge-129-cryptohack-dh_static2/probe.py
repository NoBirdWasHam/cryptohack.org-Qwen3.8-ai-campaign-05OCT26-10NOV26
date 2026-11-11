#!/usr/bin/env python
# dh_static2 probe: what does Bob validate?
import socket, json, sys

def session(payload):
    s = socket.create_connection(("socket.cryptohack.org", 13378), timeout=15)
    s.settimeout(12)
    buf = b""
    def readline():
        nonlocal buf
        try:
            while b"\n" not in buf:
                d = s.recv(65536)
                if not d: return None
                buf += d
        except Exception:
            if buf.strip():
                line, buf = buf.split(b"\n", 1) if b"\n" in buf else (buf, b"")
                return line.decode().strip()
            return None
        line, buf = buf.split(b"\n", 1)
        return line.decode().strip()
    got = []
    for _ in range(4):
        l = readline()
        if l is None: break
        got.append(l)
    s.sendall((json.dumps(payload) + "\n").encode())
    try:
        resp = readline()
    except Exception as e:
        resp = f"<timeout {e}>"
    s.close()
    return got, resp

P0 = 0xffffffffffffffffc90fdaa22168c234c4c6628b80dc1cd129024e088a67cc74020bbea63b139b22514a08798e3404ddef9519b3cd3a431b302b0a6df25f14374fe1356d6d51c245e485b576625e7ec6f44c42e9a637ed6b0bff5cb6f406b7edee386bfb5a899fa5ae9f24117c4b1fe649286651ece45b3dc2007cb8a163bf0598da48361c55d39a69163fa8fd24cf5f83655d23dca3ad961c62f356208552bb9ed529077096966d670c354e4abc9804f1746c08ca237327ffffffffffffffff

tests = {
  "A=1 (old trick)":      {"p": hex(P0), "g": "0x2", "A": "0x1"},
  "g=A (dh_static fix)":  None,  # filled below using intercepted A
  "composite p":          {"p": hex(1000003*1000033), "g": "0x2", "A": "0x1234"},
  "small p":              {"p": hex(1000003), "g": "0x2", "A": "0x1234"},
}

# first grab a fresh A for the g=A test
got, _ = session({})
alice = json.loads(got[0].split(":",1)[1].strip()) if got and got[0].startswith("{") else None
import re
for l in got:
    if l.startswith("{") and '"A"' in l:
        alice = json.loads(l)
if alice:
    tests["g=A (dh_static fix)"] = {"p": alice["p"], "g": alice["g"], "A": alice["A"], "B2": alice["A"]}
    tests["g=A real"] = {"p": alice["p"], "g": alice["A"], "A": alice["A"]}

for name, pl in tests.items():
    if pl is None: continue
    try:
        got, resp = session(pl)
        print(f"== {name}: {str(resp)[:160]}")
    except Exception as ex:
        print(f"== {name}: ERR {ex}")
