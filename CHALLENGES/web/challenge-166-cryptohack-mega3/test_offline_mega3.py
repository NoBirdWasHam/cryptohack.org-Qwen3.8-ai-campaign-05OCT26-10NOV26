# Offline test of mega3 attack against local 13410.py instance.
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "challenge-165-cryptohack-mega2"))
from harness import load_challenge
import solve_mega3 as sm

class LocalS:
    def __init__(self, ch):
        mats = []
        for line in ch.before_input.split("\n"):
            line = line.strip()
            if line.startswith("{"):
                try: mats.append(json.loads(line))
                except Exception: pass
        self.ch = ch
        self.mat, self.filemat, self.rec = mats
        self.n, self.e = self.mat["share_key_pub"]
        self.ske = bytes.fromhex(self.mat["share_key_enc"])
        self.mke = self.mat["master_key_enc"]
        self.node_key_enc = bytes.fromhex(self.filemat["node_key_enc"])
        self.file_enc = bytes.fromhex(self.filemat["file_enc"])
        self.p_given = self.rec["share_key"][2]
    def act(self, msg):
        self.ch.exit = False
        return self.ch.challenge(msg)

if __name__ == "__main__":
    ok = 0
    for trial in range(2):
        ch = load_challenge(os.path.join(HERE, "13410.py"))
        s = LocalS(ch)
        nk = sm.attack(s)
        if nk:
            txt = sm.finish(s, nk)
            print(f"trial {trial}: FILE: {txt}", flush=True)
            ok += 1
        else:
            print(f"trial {trial}: FAILED", flush=True)
    print("ok", ok, "/2")
