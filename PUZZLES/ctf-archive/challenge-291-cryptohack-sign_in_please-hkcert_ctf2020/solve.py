#!/usr/bin/env python3
# Sign in Please (HKCERT CTF 2020) solver.
# Vuln: client `spy` oracle computes sha256(permutate(password+salt, pbox)) for ANY
# pbox with 20 DISTINCT integers -- but Python negative indexing means distinct
# integers need not be distinct POSITIONS, and entry count is unbounded.
# Craft pbox covering only 6 password positions (each via x and x-20) + all 4 salt
# positions (we choose the salt) -> hash commits to only 6 base64 chars -> brute
# force 64^6 offline. 3 spy queries recover all 16 chars, then answer auth.
import sys, os, json, time, base64, hashlib, ast, subprocess, threading

HERE = os.path.dirname(os.path.abspath(__file__))
AL = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
SALT = b"AAAA"
SALT_B64 = base64.b64encode(SALT).decode()
# pbox strings (20 distinct ints; positions chosen via x / x-20 duplicates)
PBOX_A = "[0,1,2,3,4,5,-20,-19,-18,-17,-16,-15,16,17,18,19,-4,-3,-2,-1]"      # pos 0..5 x2
PBOX_B = "[6,7,8,9,10,11,-14,-13,-12,-11,-10,-9,16,17,18,19,-4,-3,-2,-1]"     # pos 6..11 x2
PBOX_C = "[12,13,14,15,0,1,-8,-7,-6,-5,-20,-19,16,17,18,19,-4,-3,-2,-1]"      # pos 12..15 x2 + 0,1 x2

def permutate(payload, pbox): return bytes([payload[x] for x in pbox])

# ---------------- brute force ----------------
def bf6(target_hex, salt=SALT, threads="16"):
    r = subprocess.run([os.path.join(HERE, "bf.exe"), target_hex, salt.hex(), threads],
                       capture_output=True, text=True)
    out = r.stdout.strip()
    if not out.startswith("FOUND"):
        raise RuntimeError("bf6 failed: " + out + r.stderr[:200])
    return out.split()[1]

def bf4(target_hex, known01, salt=SALT):
    # msg = [c12,c13,c14,c15,k0,k1] x2 + salt x2
    k0, k1 = known01
    pre = None
    for i2 in range(64):
        for i3 in range(64):
            for i4 in range(64):
                for i5 in range(64):
                    s = AL[i2]+AL[i3]+AL[i4]+AL[i5]+k0+k1
                    msg = (s+s+salt.decode()*2).encode()
                    if hashlib.sha256(msg).hexdigest() == target_hex:
                        return AL[i2]+AL[i3]+AL[i4]+AL[i5]
    raise RuntimeError("bf4 failed")

# ---------------- transports ----------------
class Remote:
    def __init__(self, host="archive.cryptohack.org", port=1024):
        import socket
        self.s = socket.create_connection((host, port), timeout=60)
        self.buf = b""
    def read_until(self, marker):
        m = marker.encode()
        while m not in self.buf:
            chunk = self.s.recv(4096)
            if not chunk: raise EOFError("connection closed; buf=" + self.buf[-200:].decode(errors="replace"))
            self.buf += chunk
        i = self.buf.index(m) + len(m)
        out, self.buf = self.buf[:i].decode(errors="replace"), self.buf[i:]
        return out
    def send(self, s):
        print("C>", s, flush=True)
        self.s.sendall((s + "\n").encode())
    def spy(self, pbox_str):
        self.read_until("[cmd] ")
        self.send("spy")
        self.read_until("[pbox] "); self.send(pbox_str)
        self.read_until("[salt] "); self.send(SALT_B64)
        h = self.read_until("\n").strip()
        print("S> hash:", h, flush=True)
        assert h.startswith("[hash] "), h
        return h.split()[1]
    def auth(self, password):
        self.read_until("[cmd] ")
        self.send("auth")
        self.read_until("[pbox] ")
        pbox = ast.literal_eval(self.read_until("\n").strip())
        self.read_until("[salt] ")
        salt = base64.b64decode(self.read_until("\n").strip())
        h = hashlib.sha256(permutate(password + salt, pbox)).hexdigest()
        self.send(h)
        resp = self.read_until("\n")
        print("S>", resp.strip(), flush=True)
        return resp

class Local:
    """in-process simulation of chall.py with a planted password"""
    def __init__(self, password):
        sys.path.insert(0, HERE)
        from chall import Server, Client
        self.srv = Server(password); self.cli = Client(password)
    def spy(self, pbox_str):
        pbox = list(map(int, pbox_str[1:-1].split(','))) if pbox_str.startswith('[') else list(map(int, pbox_str.split(',')))
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.cli.spy(pbox, SALT)
        h = buf.getvalue().split()[1]
        print("S> hash:", h, flush=True)
        return h
    def auth(self, password):
        import random
        pbox, salt = self.srv.preauth()
        h = hashlib.sha256(permutate(password + salt, pbox)).hexdigest()
        ok = self.srv.auth(pbox, salt, h)
        return "[flag] planted" if ok else "no way!"

def solve(transport):
    t0 = time.time()
    hA = transport.spy(PBOX_A)
    hB = transport.spy(PBOX_B)
    hC = transport.spy(PBOX_C)
    print("collected 3 hashes at t=%.0fs" % (time.time()-t0), flush=True)
    c05 = bf6(hA); print("chars 0-5:", c05, "t=%.0f" % (time.time()-t0), flush=True)
    c6_11 = bf6(hB); print("chars 6-11:", c6_11, "t=%.0f" % (time.time()-t0), flush=True)
    c12_15 = bf4(hC, (c05[0], c05[1])); print("chars 12-15:", c12_15, "t=%.0f" % (time.time()-t0), flush=True)
    password = (c05 + c6_11 + c12_15).encode()
    assert len(password) == 16
    resp = transport.auth(password)
    return resp

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "remote"
    if mode == "local":
        pw = (sys.argv[2] if len(sys.argv) > 2 else "ABABABABABABABAB").encode()
        r = solve(Local(pw))
        print("LOCAL RESULT:", r)
    else:
        for attempt in range(3):
            try:
                r = solve(Remote())
                if "[flag]" in r:
                    flag = r.split("[flag]")[1].strip()
                    print("FLAG:", flag)
                    open(os.path.join(HERE, "flag_sign_in_please-hkcert_ctf2020.txt"), "w").write(flag + "\n")
                    break
                else:
                    print("auth failed, retrying", flush=True)
            except Exception as e:
                print("attempt %d error: %r" % (attempt, e), flush=True)
                time.sleep(5)
