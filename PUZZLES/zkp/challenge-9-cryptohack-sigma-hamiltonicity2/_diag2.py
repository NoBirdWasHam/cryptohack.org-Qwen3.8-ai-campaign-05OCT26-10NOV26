# Diagnose: first cross, full bookkeeping vs planted x.
import sys
sys.path.insert(0, ".")
import time
import kangaroo_window as KW

g = KW.H2
lo = 1 << 20
hi = 1 << 21
x_true = lo + lo // 3 + 17
y = pow(g, x_true, KW.P)
d = KW.Dlog(g, y, lo, hi, 10, seed=123)
print("residues mod 12 tame:", [(int(d.hi) + i * KW.V) % 12 for i in range(KW.U)],
      "wild:", [(j * KW.U) % 12 for j in range(KW.V)],
      "x%12:", x_true % 12, "hi%12:", int(d.hi) % 12)
print("sbar", d.sbar, "cap", d.cap_per_herd)

orig_dp = d._dp


def spy(h):
    k = int(h[1])
    ent = d.dps.get(k)
    if ent is not None and ent[0] != h[0]:
        x = (h[2] - ent[1]) if h[0] == "T" else (ent[1] - h[2])
        ok = (lo <= (x % int(KW.Q)) <= hi) and pow(g, x % int(KW.Q), KW.P) == y
        print(f"CROSS incoming {h[0]} dist={h[2]} stored {ent[0]} dist={ent[1]} "
              f"-> x={x} ok={ok} planted={x_true}")
        if not ok:
            e_stored = ent[1] if ent[0] == "T" else x_true + ent[1]
            e_incoming = h[2] if h[0] == "T" else x_true + h[2]
            print("  true point exp: stored-side", e_stored, " incoming-side", e_incoming)
            print("  diff", e_incoming - e_stored)
            sys.exit(1)
    return orig_dp(h)


d._dp = spy
t0 = time.time()
seg = 2048
while time.time() - t0 < 180:
    for h in d.herds:
        if h[3] > d.cap_per_herd:
            d.reseed()
            break
        r = d.step(h, seg)
        if r is not None:
            print("FOUND OK:", r, "== planted", x_true)
            sys.exit(0)
print("no find; rounds", d.rounds, "cross", d.cross)
