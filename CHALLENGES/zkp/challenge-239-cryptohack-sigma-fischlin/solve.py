# sigma-fischlin / Fischlin's Transformation (archive.cryptohack.org:3583)
# Attack: the Fischlin loop searches loop-counter e for RO<2^506 varying ONLY the
# real branch (e_b=e^e_sim, z_b=r+e_b*w_b); the simulated branch is frozen.
# Given the leaked witness w of branch L, reconstruct the trajectory the prover
# WOULD have taken had L been real: r = z_L - e_L*w, z_L' = r + (e'^e_O)*w.
# If branch L is real -> no hit for e'<e (always). If simulated -> hits w.p.
# 1-(1-2^-6)^e. So a trajectory hit before e proves b != L. Retry attempts
# (16/round) until a hit; else guess L.
import sys, json, subprocess, os
from hashlib import sha512
from Crypto.Util.number import bytes_to_long
from params import p, q, g

B = 6
LIMIT = 2 ** (512 - B)

def RO(a0, a1, e, e0, e1, z0, z1):
    h = sha512(b'my')
    for x in (a0, a1, e, e0, e1, z0, z1):
        h.update(b'very' if x is a1 else b'cool' if x is e else b'random' if x is e0
                 else b'oracle' if x is e1 else b'for' if x is z0 else b'fischlin' if x is z1 else b'my')
        h.update(str(x).encode())
    return bytes_to_long(h.digest())

def RO(a0, a1, e, e0, e1, z0, z1):
    h = sha512(b'my'); h.update(str(a0).encode()); h.update(b'very')
    h.update(str(a1).encode()); h.update(b'cool'); h.update(str(e).encode())
    h.update(b'random'); h.update(str(e0).encode()); h.update(b'oracle')
    h.update(str(e1).encode()); h.update(b'for'); h.update(str(z0).encode())
    h.update(b'fischlin'); h.update(str(z1).encode())
    return bytes_to_long(h.digest())

def check_branch(L, w, y, pr):
    """Return True if trajectory check passes (consistent with L being real)."""
    a0, a1, e = pr["a0"], pr["a1"], pr["e"]
    e0, e1, z0, z1 = pr["e0"], pr["e1"], pr["z0"], pr["z1"]
    aL, eL, zL = (a0, e0, z0) if L == 0 else (a1, e1, z1)
    eO = e1 if L == 0 else e0
    if pow(g, (zL - eL * w) % q, p) != aL:
        return False  # inconsistent even as a valid transcript
    r = (zL - eL * w) % q
    for ep in range(e):
        eLp = ep ^ eO
        zLp = (r + eLp * w) % q
        if L == 0:
            hit = RO(aL, a1, ep, eLp, e1, zLp, z1)
        else:
            hit = RO(a0, aL, ep, e0, eLp, z0, zLp)
        if hit < LIMIT:
            return False  # prover would have broken earlier -> L was simulated
    return True

PROMPTS = [b"which witness do you want to see?",
           b"do you think you can guess my witness? (y,n)",
           b"which witness did the prover use?"]

class IO:
    def __init__(self):
        self.buf = b""
    def send(self, s):
        raise NotImplementedError
    def read_until_prompt(self):
        raise NotImplementedError

class SockIO(IO):
    def __init__(self, host, port):
        import socket
        super().__init__()
        self.s = socket.create_connection((host, port), timeout=60)
    def send(self, s):
        self.s.sendall((s + "\n").encode())
    def read_until_prompt(self):
        while True:
            for pr in PROMPTS:
                if self.buf.rstrip().endswith(pr):
                    out = self.buf
                    self.buf = b""
                    return out.decode(errors="replace")
            d = self.s.recv(65536)
            if not d:
                raise EOFError("connection closed: " + self.buf.decode(errors="replace"))
            self.buf += d

class ProcIO(IO):
    def __init__(self, python, script, flag):
        super().__init__()
        env = dict(os.environ, FLAG=flag)
        self.proc = subprocess.Popen([python, script], stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     env=env, bufsize=0)
    def send(self, s):
        self.proc.stdin.write((s + "\n").encode())
        self.proc.stdin.flush()
    def read_until_prompt(self):
        while True:
            for pr in PROMPTS:
                if self.buf.rstrip().endswith(pr):
                    out = self.buf; self.buf = b""
                    return out.decode(errors="replace")
            d = self.proc.stdout.read(1)
            if not d:
                raise EOFError("proc closed: " + self.buf.decode(errors="replace"))
            self.buf += d

def parse(block):
    y0 = y1 = w = None
    proof = None
    for line in block.splitlines():
        line = line.strip()
        if line.startswith("y0 = "): y0 = int(line[5:])
        elif line.startswith("y1 = "): y1 = int(line[5:])
        elif line.startswith("w0 = "): w = int(line[5:]); L = 0
        elif line.startswith("w1 = "): w = int(line[5:]); L = 1
        elif line.startswith("{"): proof = json.loads(line)
    return y0, y1, L, w, proof

def play_round(io, round_idx, leak_branch=0, verbose=True):
    # returns True if round won
    last = None
    for att in range(16):
        block = io.read_until_prompt()
        y0, y1, L, w, proof = parse(block)
        io.send(str(leak_branch))
        block = io.read_until_prompt()
        y0, y1, L, w, proof = parse(block)
        ok = check_branch(L, w, y0 if L == 0 else y1, proof)
        if verbose:
            print(f"r{round_idx} a{att}: e={proof['e']} leak={L} traj_ok={ok}", flush=True)
        if ok:
            io.send("y")
            io.read_until_prompt()
            guess = str(L)
            io.send(guess)
        else:
            if att < 15:
                io.send("n")
            else:
                io.send("y")
                io.read_until_prompt()
                io.send(str(1 - L))
        res = io.read_until_prompt() if round_idx < 63 else None
        if round_idx == 63:
            # after last correct guess the flag is printed; read rest
            try:
                rest = io.rest() if hasattr(io, "rest") else ""
            except Exception:
                rest = ""
            return ("flag", res)
        txt = res.decode(errors="replace") if isinstance(res, bytes) else (res or "")
        if "wow you distinguished" in txt:
            return True
        if "didn't guess" in txt:
            print("LOST ROUND:", txt, flush=True)
            return False
        # maybe flag printed early?
        if "crypto{" in txt:
            return ("flag", txt)
        return ("unknown", txt)

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "remote"
    if mode == "local":
        io = ProcIO(sys.executable, "chal.py", "crypto{test_flag}")
        leak = 0
        for r in range(64):
            out = play_round(io, r, leak)
            if isinstance(out, tuple) and out[0] == "flag":
                print("FLAG BLOCK:", out[1]); return
            if out is not True:
                print("fail at round", r, out); return
        print(io.proc.stdout.read().decode())
    else:
        io = SockIO("archive.cryptohack.org", 3583)
        leak = 0
        for r in range(64):
            out = play_round(io, r, leak)
            if isinstance(out, tuple) and out[0] == "flag":
                print("FLAG BLOCK:", out[1]); return
            if out is not True:
                print("fail at round", r, out); return
        print("done?")

if __name__ == "__main__":
    main()
