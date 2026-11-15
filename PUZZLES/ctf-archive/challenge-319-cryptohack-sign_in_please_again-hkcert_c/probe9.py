# probe9: pin down remote spy rule after a preauth round
import sys, time, base64
from sbase import S

def main():
    t0 = time.time()
    s = S()
    print("pow %.1fs" % s.pow_t, flush=True)
    def spy(tag, pbox, salt="QUFB"):
        o = s.spy(pbox, salt)
        print(tag, repr(o[:50]), "t=%.0f" % (time.time()-t0), flush=True)
    s.send("\U0001f5a5\ufe0f")
    P1, S1 = s.auth_begin()
    print("R1", P1, S1.hex(), "t=%.0f" % (time.time()-t0), flush=True)
    print("R1 ans:", repr(s.auth_answer("0"*64)), flush=True)
    q = base64.b64encode(S1).decode()
    spy("id21+lastsalt ", list(range(21)), q)
    spy("lastpbox+QUFB ", P1, "QUFB")
    spy("lastpbox+lasts", P1, q)
    spy("shuf21+lastsal", sorted(P1, key=lambda x: x*7 % 23), q)
    s.send("\U0001f5a5\ufe0f")
    P2, S2 = s.auth_begin()
    print("R2", P2, S2.hex(), "same_pbox=", P2 == P1, flush=True)
    print("R2 ans:", repr(s.auth_answer("0"*64)), flush=True)
    spy("P1+S1 stale   ", P1, base64.b64encode(S1).decode())
    spy("P2+S2 fresh   ", P2, base64.b64encode(S2).decode())
    s.s.close()

if __name__ == "__main__":
    main()
