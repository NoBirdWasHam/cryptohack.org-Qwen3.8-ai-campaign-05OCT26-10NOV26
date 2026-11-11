# clean semantics probe on live server (60s alarm budget)
import sys, time
from sbase import S

def main():
 t0 = time.time()
s = S()
print("pow %.1fs" % s.pow_t, flush=True)
def spy(tag, pbox, salt="QUFB"):
    o = s.spy(pbox, salt)
    print(tag, repr(o[:70]), "t=%.0f" % (time.time()-t0), flush=True)
spy("id21   ", list(range(21)))
spy("id21dup", list(range(21)))
spy("set20  ", list(range(20)) + [16])
spy("neg    ", list(range(-21, 0)))
spy("mixneg ", list(range(16)) + [-5,-4,-3,-2,-1,16,17,18])
spy("dup42  ", list(range(21)) + list(range(21)))
spy("rep0x21+", list(range(21)) + [5]*100)
s.send("\U0001f5a5\ufe0f")
pbox, salt = s.auth_begin()
print("auth pbox", pbox, "salt", salt.hex(), "t=%.0f" % (time.time()-t0), flush=True)
print("auth garb:", repr(s.auth_answer("0"*64)), flush=True)
o = s.spy(pbox, __import__("base64").b64encode(salt).decode())
print("spy with round pbox/salt:", repr(o[:70]), flush=True)
s.close() if hasattr(s, "close") else s.s.close()
