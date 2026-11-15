#!/usr/bin/env python3
"""
kangaroo_window.py v3 — Bounded multi-herd Pollard kangaroo (van Oorschot-Wiener
parallel collision search w/ distinguished points, classic serial-scheme seeds).

Task: x = dlog_g(y) in [LO,HI], default [2^44, 2^60), both directions
dlog_{h2}(h1) and dlog_{h1}(h2).

Scheme:
- Tame herds start at exponents hi + dT_i (dT_i in [0, 4096), spacing 17):
  they are AHEAD of the wild herds for every x < hi - 4096.
- Wild herds start at y * g^{dW_j}, dW_j in [0, 4096): exponent x + dW_j.
- Jump map shared: f(X) = X * g^{r[X % 32]} mod P, r_k uniform in (0, 2*Sbar),
  mean jump Sbar = sqrt(W)/2 (Pollard optimum; trail-hit density 1/Sbar).
- DP trap: (X mod 2^K) == 0. Persistent table point -> [kind, dist].
  Tame DP dist = true exponent of the point; Wild DP dist = offset from y.
  Cross-kind hit => x = distT - distW (mod q), accepted only after
  pow(g,x,P)==y and lo<=x<=hi verification.
- Same-kind DP re-entry (paths merged): incoming herd hops forward 1..512
  random jumps (vOW trailing-kangaroo re-randomization); bookkeeping stays
  exact because a point's exponent is path-independent.
- Flock cap 8*sqrt(W)+1024 steps per herd (miss ~e^-6) => re-seed: NEW random
  jump table + fresh offsets; DP table KEPT (persistent entries remain valid:
  the meet at a point satisfies the exponent equation regardless of which
  jump map led there).
- Memory O(1) per herd (point, dist, steps); table ~ steps/2^K.
- Self-tests MANDATORY before production (AAR 2026-10-26 lesson: an
  un-self-tested kangaroo's negative result is VOID). --selftest WBITS plants
  a known x in a scaled window; --shadow plants a random x in the FULL
  production window with production parameters.

Lessons baked in (from v1/v2 failures this session):
  * distances MUST accumulate actual jump values rs[j], never step counts;
  * 'no solution' must be the None sentinel, never a truthy segment size;
  * herd step counters must count ALL steps or the flock cap never fires;
  * DP trap interval must be << herd cap or herds re-seed before any DP.
"""
import argparse
import json
import os
import sys
import time
import random
from gmpy2 import mpz, is_prime

P = 0x19dad539e2d348cc3ab07d51f2bb6491d1552aa8cf1db928920fd3d86946aed8805d2e279fa8632dd5fbab8aaf7df1069906b057cc785b7f191ef1b9b5da38cff2e7c64da17bb56a058707d9fd69e546a95e502e556a314c587c7ae36c3d1122e6954f5d81dd9239e02f61b045360187b4caeed271cec1919a0d8a39e855040cf
Q = 0xced6a9cf169a4661d583ea8f95db248e8aa9554678edc944907e9ec34a3576c402e9713cfd43196eafdd5c557bef8834c83582be63c2dbf8c8f78dcdaed1c67f973e326d0bddab502c383ecfeb4f2a354af28172ab518a62c3e3d71b61e8891734aa7aec0eec91cf017b0d8229b00c3da65776938e760c8cd06c51cf42a82067
H1 = 250335104192448110684442096964171969189371208477846978499544515755228857598805930673171509152681305793789903169450438090936970626429806187630240086681623358732517929314870247393468568111513100989768455673769015138136779312483203922847547169463972757664497001482465636402329003817055202840451714256443734563502
H2 = 50837518481371967588098771977165879422445597094015682347125264774697010574110399136037637691883034517374621248070926110725252171239208140392324019115211573768989274797050961703999139947885402838647962534519882622024973824201026885393782961783980351898031905383197219266093119145616328556294476943229578292306

MIDX = 32
U, V = 2, 2          # tame herds, wild herds
SPACING = 17
OFF_MAX = 4096


class Dlog:
    def __init__(self, g, y, lo, hi, K, seed=0xC0FFEE):
        self.g, self.y = mpz(g), mpz(y)
        self.lo, self.hi = mpz(lo), mpz(hi)
        self.W = int(self.hi - self.lo)
        self.sqrtW = self.W ** 0.5
        self.sbar = self.sqrtW / 2.0
        self.K = K
        self.trapmask = mpz((1 << K) - 1)
        self.rng = random.Random(seed)
        self.dps = {}
        self.herds = []
        self.steps = 0
        self.dp_count = 0
        self.cross = 0
        self.rounds = 0
        self.cap_per_herd = int(8 * self.sqrtW) + 1024
        self.reseed()

    def _build_jumps(self):
        rmax = max(2, int(self.sbar))
        self.rs = [self.rng.randrange(1, 2 * rmax + 1) for _ in range(MIDX)]
        self.jumps = [pow(self.g, r, P) for r in self.rs]

    def reseed(self):
        if self.herds:
            self.steps += sum(h[3] for h in self.herds)
        self.rounds += 1
        self._build_jumps()
        self.herds = []
        for i in range(U):
            e = int(self.hi) + self.rng.randrange(0, OFF_MAX) + i * SPACING
            self.herds.append(self.new("T", e))
        for j in range(V):
            e = self.rng.randrange(0, OFF_MAX) + j * SPACING
            self.herds.append(self.new("W", e))

    def new(self, kind, e):
        pt = pow(self.g, e, P) if kind == "T" else self.y * pow(self.g, e, P) % P
        return [kind, pt, e, 0]  # kind, point, dist, steps in flock

    def _dp(self, h):
        self.dp_count += 1
        k = int(h[1])
        ent = self.dps.get(k)
        if ent is None:
            self.dps[k] = [h[0], h[2]]
            return None
        if ent[0] == h[0]:
            # merged trails: hop the incoming (trailing) herd forward
            tab, rs = self.jumps, self.rs
            pt, dist = h[1], h[2]
            for _ in range(self.rng.randrange(1, 513)):
                j = pt % MIDX
                pt = pt * tab[j] % P
                dist += rs[j]
            h[1], h[2] = pt, dist
            return None
        self.cross += 1
        x = (h[2] - ent[1]) if h[0] == "T" else (ent[1] - h[2])
        x %= int(Q)
        if self.lo <= x <= self.hi and pow(self.g, x, P) == self.y:
            return x
        return None

    def step(self, h, cap):
        jumps, rs, trapmask = self.jumps, self.rs, self.trapmask
        pt, dist = h[1], h[2]
        n = 0
        for n in range(1, cap + 1):
            j = pt % MIDX
            pt = pt * jumps[j] % P
            dist += rs[j]
            if not (pt & trapmask):
                h[1], h[2] = pt, dist
                h[3] += n
                r = self._dp(h)
                if r is not None:
                    return r
                pt, dist = h[1], h[2]
                n = 0
        h[1], h[2] = pt, dist
        h[3] += n
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", choices=["h2h1", "h1h2"], required=True)
    ap.add_argument("--lo", type=int, default=1 << 44)
    ap.add_argument("--hi", type=int, default=1 << 60)
    ap.add_argument("--K", type=int, default=20)
    ap.add_argument("--max-hours", type=float, default=10.0)
    ap.add_argument("--selftest", type=int, default=0, metavar="WBITS")
    ap.add_argument("--shadow", action="store_true")
    ap.add_argument("--seed", type=int, default=0xC0FFEE)
    ap.add_argument("--ckpt", default="")
    ap.add_argument("--stats-every", type=float, default=60.0)
    args = ap.parse_args()

    g, y = (H2, H1) if args.dir == "h2h1" else (H1, H2)
    assert is_prime(P) and is_prime(Q), "params corrupt"
    shadow_x = None
    if args.shadow:
        rr = random.Random(args.seed ^ 0xBAD)
        shadow_x = args.lo + rr.randrange(args.hi - args.lo)
        y = pow(g, shadow_x, P)
        print(f"[shadow {args.dir}] planted x0={shadow_x}", flush=True)

    if args.selftest:
        lo = 1 << args.selftest
        hi = 2 * lo
        x_true = lo + (lo // 3) + 17
        y = pow(g, x_true, P)
        K = max(10, args.selftest // 2 - 3)
        print(f"[selftest {args.dir}] W=2^{args.selftest} K={K} plant={x_true}", flush=True)
        d = Dlog(g, y, lo, hi, K, seed=args.seed)
        ckpt_path = f"_selftest_{args.dir}_{args.selftest}.json"
        mode = "selftest"
        deadline = time.time() + 1800
    else:
        d = Dlog(g, y, args.lo, args.hi, args.K, seed=args.seed)
        ckpt_path = args.ckpt or f"kangaroo_{args.dir}.ckpt.json"
        mode = "shadow" if args.shadow else "production"
        deadline = time.time() + args.max_hours * 3600

    t0 = time.time()
    last = t0
    seg = 4096
    found = None

    def write_ckpt():
        data = {"mode": mode, "dir": args.dir,
                "found": None if found is None else int(found),
                "steps_total": d.steps + sum(h[3] for h in d.herds),
                "rounds": d.rounds, "dps": d.dp_count, "cross": d.cross,
                "table": len(d.dps),
                "herds": [[h[0], h[3]] for h in d.herds],
                "t": round(time.time() - t0, 1)}
        tmp = ckpt_path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(data, f)
        os.replace(tmp, ckpt_path)

    while time.time() < deadline and found is None:
        for h in d.herds:
            if h[3] > d.cap_per_herd:
                d.reseed()
                break
            r = d.step(h, seg)
            if r is not None:
                found = r
                break
        now = time.time()
        if now - last >= args.stats_every:
            write_ckpt()
            st = d.steps + sum(h[3] for h in d.herds)
            print(json.dumps({"dir": args.dir, "t": round(now - t0, 1),
                              "steps_total": st, "rounds": d.rounds,
                              "dps": d.dp_count, "cross": d.cross,
                              "rate": round(st / max(1e-9, now - t0))}), flush=True)
            last = now

    write_ckpt()
    steps_total = d.steps + sum(h[3] for h in d.herds)
    print(json.dumps({"event": "done", "dir": args.dir,
                      "found": None if found is None else int(found),
                      "status": "found" if found is not None else "budget-exhausted",
                      "steps": steps_total, "rounds": d.rounds, "cross": d.cross,
                      "hours": round((time.time() - t0) / 3600, 3)}), flush=True)

    if args.selftest:
        ok = found is not None and int(found) == x_true
        print(f"[selftest {args.dir}] -> {'PASS' if ok else 'FAIL'}", flush=True)
        sys.exit(0 if ok else 2)
    if args.shadow:
        ok = found is not None and int(found) == shadow_x
        print(f"[shadow {args.dir}] found={None if found is None else int(found)} "
              f"expect={shadow_x} -> {'PASS' if ok else 'FAIL'}", flush=True)
        sys.exit(0 if ok else 2)
    if found is not None:
        with open(f"SOLUTION_{args.dir}.txt", "w") as f:
            f.write(str(int(found)) + "\n")


if __name__ == "__main__":
    main()
