# sigma-fischlin / Fischlin's Transformation (archive.cryptohack.org:3583)
# Attack: the Fischlin loop searches loop-counter e for RO<2^506 varying ONLY the
# real branch (e_b=e^e_sim, z_b=r+e_b*w_b); the simulated branch is frozen.
# Given leaked witness w of branch L, replay the trajectory the prover WOULD have
# taken had L been real: r = z_L - e_L*w, z_L' = r + (e'^e_O)*w.
# Real branch -> no RO hit for e'<e (always). Simulated -> hit w.p. 1-(63/64)^e.
# A hit before e proves b != L. Say "n" (retry, fresh proof) until a hit; else
# guess L on the last attempt.
import sys, json, subprocess, os, socket, re
from hashlib import sha512
from Crypto.Util.number import bytes_to_long
from params import p, q, g

LIMIT = 2 ** (512 - 6)

def RO(a0, a1, e, e0, e1, z0, z1):
    h = sha512(b'my'); h.update(str(a0).encode()); h.update(b'very')
    h.update(str(a1).encode()); h.update(b'cool'); h.update(str(e).encode())
    h.update(b'random'); h.update(str(e0).encode()); h.update(b'oracle')
    h.update(str(e1).encode()); h.update(b'for'); h.update(str(z0).encode())
    h.update(b'fischlin'); h.update(str(z1).encode())
    return bytes_to_long(h.digest())

def check_branch(L, w, pr):
    """True = trajectory consistent with branch L being the real one."""
    a0, a1, e = pr["a0"], pr["a1"], pr["e"]
    e0, e1, z0, z1 = pr["e0"], pr["e1"], pr["z0"], pr["z1"]
    aL, eL, zL = (a0, e0, z0) if L == 0 else (a1, e1, z1)
    eO = e1 if L == 0 else e0
    r = (zL - eL * w) % q
    if pow(g, r, p) != aL:
        return False
    for ep in range(e):
        eLp = ep ^ eO
        zLp = (r + eLp * w) % q
        if L == 0:
            hit = RO(aL, a1, ep, eLp, e1, zLp, z1)
        else:
            hit = RO(a0, aL, ep, e0, eLp, z0, zLp)
        if hit < LIMIT:
            return False
    return True

PROMPTS = [b"which witness do you want to see?",
           b"do you think you can guess my witness? (y,n)",
           b"which witness did the prover use?"]

class SockIO:
    def __init__(self, host, port):
        self.s = socket.create_connection((host, port), timeout=120)
        self.buf = b""
    def send(self, s):
        self.s.sendall((s + "\n").encode())
    def read_until_prompt(self):
        while True:
            for pr in PROMPTS:
                if self.buf.rstrip().endswith(pr):
                    out = self.buf; self.buf = b""
                    return out.decode(errors="replace")
            d = self.s.recv(65536)
            if not d:
                out = self.buf; self.buf = b""
                raise EOFError(out.decode(errors="replace"))
            self.buf += d

class ProcIO(SockIO):
    def __init__(self, python, script, flag):
        env = dict(os.environ, FLAG=flag)
        self.proc = subprocess.Popen([python, script], stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     env=env, bufsize=0)
        self.buf = b""
    def send(self, s):
        self.proc.stdin.write((s + "\n").encode()); self.proc.stdin.flush()
    def read_until_prompt(self):
        while True:
            for pr in PROMPTS:
                if self.buf.rstrip().endswith(pr):
                    out = self.buf; self.buf = b""
                    return out.decode(errors="replace")
            d = self.proc.stdout.read(1)
            if not d:
                out = self.buf; self.buf = b""
                raise EOFError(out.decode(errors="replace"))
            self.buf += d

def parse(block):
    y0 = y1 = w = None; L = None; proof = None
    for line in block.splitlines():
        line = line.strip()
        if line.startswith("y0 = "): y0 = int(line[5:])
        elif line.startswith("y1 = "): y1 = int(line[5:])
        elif line.startswith("w0 = "): w = int(line[5:]); L = 0
        elif line.startswith("w1 = "): w = int(line[5:]); L = 1
        elif line.startswith("{"): proof = json.loads(line)
    return y0, y1, L, w, proof

def play_round(io, round_idx, pending, leak_branch=0, verbose=True):
    """pending: block already read (result of previous guess + this round header).
    Returns (won, next_pending_block_or_flagtext)."""
    block = pending; pending = None
    for att in range(16):
        if block is None:
            block = io.read_until_prompt()
        y0, y1, L, w, proof = parse(block)
        io.send(str(leak_branch))
        block = io.read_until_prompt()
        y0, y1, L, w, proof = parse(block)
        ok = check_branch(L, w, proof)
        if verbose:
            print(f"r{round_idx} a{att}: e={proof['e']} leak={L} traj_ok={ok}", flush=True)
        if (not ok) or att == 15:
            # FAIL => certain b=1-L; PASS => only weak posterior, so retry with "n"
            io.send("y")
            block = io.read_until_prompt()   # result + next round header + P1
            guess = str(L if ok else 1 - L)
            io.send(guess)
            try:
                block = io.read_until_prompt()
            except EOFError as ex:
                return ("flag", str(ex))
            txt = block
            if "wow you distinguished" in txt:
                return (True, txt)
            if "didn't guess" in txt:
                print("LOST:", txt[:200], flush=True)
                return (False, txt)
            if "crypto{" in txt:
                return ("flag", txt)
            return ("unknown", txt)
        else:
            io.send("n")
            block = None  # next attempt header arrives on next read
    return ("impossible", "")

def run_connection():
    io = SockIO("archive.cryptohack.org", 3583)
    pending = None
    for r in range(64):
        won, pend = play_round(io, r, pending, verbose=(r % 8 == 0))
        if won is True:
            pending = pend
            continue
        if won == "flag":
            return pend
        return None
    return None

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "remote"
    if mode == "local":
        io = ProcIO(sys.executable, "chal.py", "crypto{test_flag}")
        pending = None
        for r in range(64):
            won, pend = play_round(io, r, pending)
            if won is True:
                pending = pend; continue
            print("FLAGTEXT:", pend)
            m = re.search(r"crypto\{[^}]*\}", pend)
            print("FLAG:", m.group(0) if m else "??")
            return
        return
    import time
    for conn in range(12):
        try:
            txt = run_connection()
        except Exception as ex:
            print(f"conn {conn}: exception {ex}", flush=True)
            txt = None
        if txt:
            print("FLAGTEXT:", txt, flush=True)
            m = re.search(r"crypto\{[^}]*\}", txt)
            print("FLAG:", m.group(0) if m else "??", flush=True)
            if m:
                return
        print(f"conn {conn} failed, reconnecting", flush=True)
        time.sleep(3)
    print("no flag captured", flush=True)

if __name__ == "__main__":
    main()
