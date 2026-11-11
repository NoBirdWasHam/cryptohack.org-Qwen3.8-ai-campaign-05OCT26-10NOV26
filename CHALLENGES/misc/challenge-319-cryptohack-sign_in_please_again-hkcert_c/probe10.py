# probe10: guard semantics with issued salt + password persistence across connections
import sys, time, base64
from sbase import S
ID21 = list(range(21))
B  = list(range(20)) + [-21]                                  # no pepper, 21 distinct
C  = ID21 + ID21                                              # dup42
D  = list(range(-21, 0))                                      # all neg
E  = [0,1,2,3,4,5,-21,-20,-19,-18,-17,-16,16,17,18,19,-5,-4,-3,-2,-1]  # 6 chars+pepper+salt x2
G  = [0,1,2,3,4,5,-21,-20,-19,-18,-17,-16,6,16,17,18,19,-5,-4,-3,-2]   # 7 chars, salt x2, no pepper
T  = list(range(16)) + [-21,-20,-19,-18,-17]  # pw bytes only: 21 distinct, no salt/pepper -> persistence test

def battery(tag, pbox, salt):
    s = S()
    s.send("\U0001f5a5\ufe0f")
    P, Sl = s.auth_begin()
    print(tag, "issued salt", Sl.hex(), flush=True)
    print("R ans:", repr(s.auth_answer("0"*64)), flush=True)
    sb = base64.b64encode(salt(Sl)).decode() if callable(salt) else base64.b64encode(Sl).decode()
    out = {}
    for name, pb in [("id21",ID21),("B",B),("C",C),("D",D),("E",E),("G",G),
                     ("never",ID21), ("never",ID21)]:
        if name == "never":
            o = s.spy(pb, "AUEC")
        else:
            o = s.spy(pb, sb)
        out[name] = o[:50] if name != "never" else o[:20]
        print(name, repr(out[name]), flush=True)
    s.s.close()
    return out

def main():
    a = battery("CONN1", None, None)
    b = battery("CONN2", None, None)
    print("T same across conns (pw persistence):", a.get("T") == b.get("T"), flush=True)
    print("aG,bG:", a.get("G"), b.get("G"), flush=True)

if __name__ == "__main__":
    main()
