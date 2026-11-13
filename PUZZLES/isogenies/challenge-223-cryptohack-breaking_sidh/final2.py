"""Chunked FINAL for breaking_sidh: find last-3 digits t in ranges, then shared secret."""
import json, re, sys
import run_attack as ra

skB, alt = ra.load_state()
assert len(skB) == 70, f"need 70 digits, have {len(skB)}"
skB_str = str(skB)

def block(tlo, thi):
    return f'''
skB = {skB_str}
key = sum(skB[k]*3^k for k in range(len(skB)))
jEB = EB.j_invariant()
for t in range({tlo}, {thi}):
    cand = key + t*3^(b-3)
    C, _ = Pushing3Chain(E0, P3 + cand*Q3, b)
    if C.j_invariant() == jEB:
        print("TFOUND", t, flush=True)
        sB = cand
        ch, _ = Pushing3Chain(EA, phiA_P3 + sB*phiA_Q3, b)
        J = ch.j_invariant()
        print("SHARED_J_STR:", str(J), flush=True)
        print("SHARED_J_CONJ_STR:", str(J^p), flush=True)
        break
else:
    print("TNONE", flush=True)
'''

if __name__ == "__main__":
    tlo, thi = int(sys.argv[1]), int(sys.argv[2])
    out, en, ev = ra.call(ra.SETUP + block(tlo, thi), timeout=90, tries=2)
    print(out)
    print("EN:", en, "EV:", str(ev)[:200])
