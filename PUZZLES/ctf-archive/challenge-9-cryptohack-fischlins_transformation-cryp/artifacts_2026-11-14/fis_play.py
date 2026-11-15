#!/usr/bin/env python3
# Fischlin WI game client. Usage: python fis_play.py [host] [port] [logfile]
import socket, re, json, sys, time, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fis_dist import replay_b0

HOST = sys.argv[1] if len(sys.argv) > 1 else "archive.cryptohack.org"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 3583
LOGF = sys.argv[3] if len(sys.argv) > 3 else "fis_play.log"
LOG = open(LOGF, "a", buffering=1)
def log(*a):
    m = " ".join(str(x) for x in a)
    print(m, flush=True); LOG.write(m + "\n")

# thresholds by attempts-remaining n (from DP in fis_dp_check.py)
THR = {2:70,3:102,4:129,5:153,6:175,7:195,8:216,9:235,10:255,11:274,12:293,13:311,14:330,15:349,16:367}

MARK = ["which witness do you want to see?",
        "do you think you can guess",
        "which witness did the prover use?",
        "skill issue", "well done"]

def read_until(s, buf, markers, timeout=120.0):
    t0 = time.time()
    s.settimeout(2.0)
    while time.time() - t0 < timeout:
        for m in markers:
            if m in buf:
                i = max(buf.find(m) + len(m) for m in markers if m in buf)
                return buf[:i], buf[i:]
        try:
            d = s.recv(65536)
        except socket.timeout:
            continue
        except Exception as e:
            log("RECV EXC", repr(e)); return buf, ""
        if not d:
            log("EOF. tail:", repr(buf[-200:])); return buf, ""
        buf += d.decode("utf8", "replace")
    return buf, ""

def main():
    s = socket.create_connection((HOST, PORT), timeout=30)
    log("=== connected", HOST, PORT, time.strftime("%H:%M:%S"))
    buf = ""
    rounds_won = 0
    try:
        for rnd in range(64):
            buf, rest = read_until(s, buf, ["which witness do you want to see?", "round:"])
            # consume up to prompt
            if "round:" in buf:
                log("HDR:", [l for l in buf.splitlines() if l.startswith("round:")][:1])
            buf = rest
            for att in range(16):
                s.sendall(b"0\n")
                buf, rest = read_until(s, buf, ["do you think you can guess"])
                mw = re.search(r"w0 = (\d+)", buf)
                if not mw:
                    log("W0 PARSE FAIL:", repr(buf[-300:])); return False, rounds_won
                w0 = int(mw.group(1))
                mp = None
                for line in buf.splitlines():
                    ls = line.strip()
                    if ls.startswith("{") and ls.endswith("}"):
                        mp = ls
                if mp is None:
                    log("PROOF PARSE FAIL:", repr(buf[-300:])); return False, rounds_won
                proof = {k: int(v) for k, v in json.loads(mp).items()}
                e = proof["e"]
                assert proof["e0"] ^ proof["e1"] == e
                hit, fok = replay_b0(proof, w0)
                nrem = 16 - att - 1
                consistent_b0 = (hit is None) and fok
                if not consistent_b0:
                    ans, conf = 1, True      # replay contradicts b=0 => definitely b=1
                elif nrem == 0:
                    ans, conf = 0, True      # forced final attempt
                elif e >= THR[nrem + 1]:
                    ans, conf = 0, True      # soft evidence, DP threshold
                else:
                    ans, conf = 0, False
                log(f"[r{rnd} a{att}] e={e} hit={hit} fok={fok} -> {'STOP ans='+str(ans) if conf else 'continue'}")
                buf = rest
                if conf:
                    s.sendall(b"y\n")
                    buf, rest = read_until(s, buf, ["which witness did the prover use?"])
                    buf = rest
                    s.sendall(f"{ans}\n".encode())
                    break
                else:
                    s.sendall(b"n\n")
                    buf, rest = read_until(s, buf, ["which witness do you want to see?"])
                    buf = rest
            buf, rest = read_until(s, buf, ["skill issue", "round:", "well done"])
            if "crypto{" in buf or "well done" in buf:
                time.sleep(1.0)
                s.settimeout(5)
                try:
                    tail = s.recv(65536).decode("utf8", "replace")
                except Exception:
                    tail = ""
                full = buf + rest + tail
                log("WIN:", repr(full[-300:]))
                mf = re.search(r"crypto\{[^}]*\}", full)
                return (True, rounds_won + 1, mf.group(0) if mf else None)
            if "skill issue" in buf:
                log("FAILED at round", rnd, "| tail:", repr(buf[-200:]))
                return False, rounds_won
            if "wow you distinguished" in buf or "more for flag" in buf:
                rounds_won += 1
                buf = rest
                continue
            log("UNEXPECTED verdict:", repr(buf[-300:])); return False, rounds_won
        return False, rounds_won
    finally:
        try: s.close()
        except Exception: pass
        log("rounds_won:", rounds_won, time.strftime("%H:%M:%S"))

if __name__ == "__main__":
    r = main()
    print("RESULT:", r)
