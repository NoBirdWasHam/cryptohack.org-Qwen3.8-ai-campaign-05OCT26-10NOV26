import os, re, socket, subprocess, sys, time
from mt_lib import build_and_solve, make_predictor

PROBE = 936          # probe rounds (y=0)
_RAW = None
SOLVE_LO, SOLVE_HI = 312, 905   # r_ idx of equation rounds
HOLD_LO, HOLD_HI = 906, 935
NEED_HARVEST = 977

def parse_frac(tok):
    if "/" in tok:
        n, d = tok.split("/")
        return int(d) * 2**53 // int(n)
    return None  # capped 1024 branch

class Conn:
    def __init__(self, proc=None, hostport=None):
        if hostport:
            self.s = socket.create_connection(hostport, timeout=30)
            self.f = self.s.makefile("rwb")
        else:
            self.f = proc.stdout
        self.p = proc
    def _readline(self):
        line = self.f.readline()
        if not line:
            raise EOFError
        s = line.decode(errors="replace").strip()
        if _RAW:
            _RAW.write(repr(s) + "\n")
        return s
    def round(self, guess):
        # send, then read: leftover prompt ignored; stop after 'total score'
        # but read ONE more line because a win prints the flag line right after
        # the score (and its text may not contain the word 'flag').
        self._send(guess)
        score_line = None
        while True:
            line = self._readline()
            low = line.lower()
            m = re.search(r"[A-Za-z0-9_\-]*\{[^}]*\}", line)
            if m:
                return "FLAG", line
            if score_line is None:
                if "total score" in line:
                    score_line = line
                    continue
                if "Error" in line or "Maybe better luck" in line:
                    return None, line
                continue
            # after score line: normal case is next prompt; win case flag (above)
            if "enter your guess" in low or "Error" in line or "Maybe better luck" in line:
                break
        tok = re.search(r"round score: (\S+)", score_line).group(1)
        u = None if tok == "1024" else parse_frac(tok)
        return u, score_line
    def _send(self, guess):
        if self.p:
            self.p.stdin.write((guess + "\n").encode()); self.p.stdin.flush()
        else:
            self.s.sendall((guess + "\n").encode())

class MissingWindow(Exception):
    pass

def run(conn):
    global _RAW
    _RAW = open("raw_log.txt", "w", buffering=1)
    lg = open("round_log.txt", "w", buffering=1)
    us = {}
    for r_ in range(PROBE):
        u, out = conn.round("0")
        lg.write("P%d resp=%r\n" % (r_, out))
        if u == "FLAG":
            print("EARLY FLAG:", out); return out
        if "flag" in out.lower():
            print("EARLY FLAG:", out); return out
        if "Error" in out or "Maybe better luck" in out:
            print("server bailed:", out); return None
        us[r_] = u
    miss_win = [k for k in range(312) if us.get(k) is None]
    if miss_win:
        raise MissingWindow("missing rounds in param window: %s" % miss_win)
    print("probe done, missing(outside window):", sum(1 for v in us.values() if v is None))
    t0 = time.time()
    st1 = build_and_solve(us, SOLVE_LO, SOLVE_HI, HOLD_LO, HOLD_HI)
    print("state recovered + holdout verified in %.1fs" % (time.time() - t0))
    nxt = make_predictor(st1)
    for k in range(312, PROBE):
        u = nxt()
        if us[k] is not None:
            assert u == us[k], "predictor desync at %d" % k
    wins = 0
    t0h = time.time()
    for r_ in range(PROBE, PROBE + 1100):
        u = nxt()
        y = "%.17g" % (u / 2**53)
        uu, out = conn.round(y)
        lg.write("H%d y=%s t=%.2f resp=%r\n" % (r_, y, time.time() - t0h, out))
        if uu == "FLAG":
            print("FLAG LINE:", out, flush=True)
            return out
        if "flag" in out.lower():
            print("FLAG LINE:", out)
            m = re.search(r"crypto\S*\{[^}]*\}", out)
            return m.group(0) if m else out
        if "Error" in out or "Maybe better luck" in out:
            print("server bailed:", out); return None
        if "round score: 1024" not in out:
            print("prediction miss at r_=%d: %s" % (r_, out), flush=True)
        else:
            wins += 1
    print("no flag after", wins, "harvest rounds")
    return None

if __name__ == "__main__":
    local = bool(sys.argv[1:]) and sys.argv[1] == "--local"
    for attempt in range(8):
        proc = None
        try:
            if local:
                env = dict(os.environ, FLAG=os.environ.get("LOCAL_FLAG", "crypto{local_test_flag}"), PYTHONUNBUFFERED="1")
                proc = subprocess.Popen([sys.executable, "-u", "challenge.py"],
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=env)
                c = Conn(proc=proc)
            else:
                host = os.environ.get("CH_HOST", "archive.cryptohack.org")
                port = int(os.environ.get("CH_PORT", "1337"))
                c = Conn(hostport=(host, port))
            res = run(c)
            print("RESULT:", res)
            break
        except MissingWindow as e:
            print("attempt %d: %s -> retrying" % (attempt, e))
            if proc:
                proc.kill()
            time.sleep(1)
