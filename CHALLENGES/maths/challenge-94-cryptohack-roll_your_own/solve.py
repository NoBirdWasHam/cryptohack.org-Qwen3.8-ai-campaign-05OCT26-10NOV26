#!/usr/bin/env python
# Roll your Own (roll_your_own, port 13403). We CHOOSE the DLP parameters.
# Server: q (512-bit prime), x=randint(0,q); we send (g,n) s.t. g^q==1 mod n;
# server: h = g^x mod n; we must return x.
# Trick: n = q^2, g = 1+q.  (1+q)^q == 1 mod q^2 (check passes).
#        h = (1+q)^x mod q^2 = 1 + x*q mod q^2  =>  x = (h-1)//q (exact, x<q).
# READ COMPLETE QUOTED HEX (the 1024-bit h splits across TCP reads; must read the
# closing quote, not a partial value).
import socket, json, re
s = socket.create_connection(("socket.cryptohack.org", 13403), timeout=30)
buf = b""
def read_complete_hex():
    global buf
    while True:
        # find a complete "0x...hex" token (opening quote, hex, closing quote)
        m = re.search(rb'"(0x[0-9a-f]+)"', buf)
        if m:
            val = m.group(1).decode()
            # drop everything up to and including this token
            idx = buf.find(m.group(1)) - 1
            buf = buf[idx+len(m.group(1))+2:]
            return int(val, 16)
        d = s.recv(65536)
        if not d:
            raise EOFError("closed")
        buf += d
q = read_complete_hex()
n = q*q; g = 1+q
assert pow(g, q, n) == 1
s.sendall((json.dumps({"g": hex(g), "n": hex(n)}) + "\n").encode())
h = read_complete_hex()
assert h % q == 1, f"h%q={h%q}, not the 1+q lift"
x = (h - 1) // q
s.sendall((json.dumps({"x": hex(x)}) + "\n").encode())
# read answer
out = ""
while True:
    d = s.recv(65536).decode("utf-8","replace")
    if not d: break
    out += d
    for j in re.findall(r'\{[^{}]*\}', out):
        try:
            dd = json.loads(j)
            if "flag" in dd: print("FLAG:", dd["flag"]); s.close(); raise SystemExit(0)
            if "error" in dd: print("ERROR:", dd["error"]); s.close(); raise SystemExit(1)
        except Exception: pass
print("tail:", out[-200:]); s.close()
