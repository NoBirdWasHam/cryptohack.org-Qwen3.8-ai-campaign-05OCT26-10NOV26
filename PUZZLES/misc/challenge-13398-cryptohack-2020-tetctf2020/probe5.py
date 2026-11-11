# probe5.py 2026-11-01: characterize divergence with data.
# (A) 10 reveal-only sessions (1396/1792) -> fingerprint stats: value range,
#     cross-session duplicates (fixed/weak seed check), per-bit bias.
# (B) generalized 1-bit MT attack for arbitrary target output T:
#       reveals A=T-623 (-> X_{T+1}), B=T-227 (-> X_{T+397});
#       X_{624+T} = X_{T+397} ^ (low31(X_{T+1})>>1) ^ MAGIC*(X_{T+1}&1) ^ msb(X_T)<<30
#     Battery: T in {2018,2019,2020} x msb {0,1} (T=2019 g0/g1 already 0/6).
import socket, time, re, json, os, sys
import solve3

HERE = os.path.dirname(os.path.abspath(__file__))
HOST, PORT = solve3.HOST, solve3.PORT
untemper, temper, MAGIC = solve3.untemper, solve3.temper, solve3.MAGIC

def session(reveals, guess="0", deadline=18):
    ss = socket.create_connection((HOST, PORT), timeout=10)
    ss.settimeout(10)
    ss.sendall(("\n".join(str(x) for x in reveals) + "\n" + str(guess) + "\n").encode())
    buf = b""
    t0 = time.time()
    while time.time() - t0 < deadline:
        try:
            b = ss.recv(65536)
        except socket.timeout:
            break
        if not b:
            break
        buf += b
    ss.close()
    txt = buf.decode(errors="replace")
    L = txt.splitlines()
    nums = [int(l) for l in L if l.strip().isdigit()]
    return L, nums, txt

def gen_attack(oA, oB, T, msb):
    xT1 = untemper(oA)      # output T-623 -> X_{T+1}
    xT397 = untemper(oB)    # output T-227 -> X_{T+397}
    w = xT397 ^ ((xT1 & 0x7fffffff) >> 1) ^ (MAGIC if (xT1 & 1) else 0) ^ (msb << 30)
    return temper(w)

# sanity vs known-good T=2019 spec formula
o = solve3.local_stream(123)
assert gen_attack(o[2019-623], o[2019-227], 2019, 0) == solve3.solve_target(o[1792], o[1396], 0)
assert gen_attack(o[2019-623], o[2019-227], 2019, 1) == solve3.solve_target(o[1792], o[1396], 1)
# and covers for T=2018/2020 on local streams (target = output T)
cov = {}
for T in (2018, 2019):  # T=2020 refuted by line-shape (would print 2021 lines)
    c = 0
    for s in range(120):
        o = solve3.local_stream(s)
        if (gen_attack(o[T-623], o[T-227], T, 0) == o[T] or
                gen_attack(o[T-623], o[T-227], T, 1) == o[T]):
            c += 1
    cov[T] = c
print("local coverage T:", cov)

stats = []
for k in range(10):
    L, nums, txt = session([1396, 1792])
    stats.append({"t": time.time(), "nums": nums, "nlines": len(L),
                  "nnope": sum(1 for l in L if l == "Nope!"),
                  "first": L[0] if L else None})
    time.sleep(0.4)
json.dump(stats, open(os.path.join(HERE, "probe5_stats.json"), "w"), indent=1)
allv = [v for s in stats for v in s["nums"]]
print("stats: n=", len(allv), "max=", max(allv), "min=", min(allv),
      "dups=", len(allv) - len(set(allv)))
for i in range(0, 32, 8):
    print("bit", i, "ones:", sum((v >> i) & 1 for v in allv), "/", len(allv))
print("nlines set:", {s["nlines"] for s in stats}, "nope set:", {s["nnope"] for s in stats})

# weak-seed brute force: seeds from wall-clock or small ints vs session nums
seeded = None
s0 = stats[0]
for seed in set([int(s0["t"]), int(s0["t"]) - 1] + list(range(0, 200))):
    o = solve3.local_stream(seed)
    if o[1396] == s0["nums"][0] or o[1792] == s0["nums"][1]:
        seeded = seed; break
for k in range(1, 10):
    if set(stats[k]["nums"]) & set(stats[0]["nums"]):
        print("CROSS-SESSION DUPLICATE:", k)
print("weak-seed match:", seeded)

results = []
battery = [("T2018msb0", 2018, 0), ("T2018msb1", 2018, 1)]
for name, T, msb in battery:
    A, B = T - 623, T - 227
    L, nums, txt = session([A, B])
    if len(nums) != 2:
        print(name, "BAD nums:", nums); results.append((name, None)); continue
    g = gen_attack(nums[0], nums[1], T, msb)
    L2, _, txt2 = session([A, B], guess=g)
    win = ("crypto{" in txt2) or ("TetCTF{" in txt2)  # 2026-11-05 fix: live flag format is TetCTF{...}
    trace = ("Traceback" in txt2) or ("Error" in txt2)
    print(name, "win=", win, "trace=", trace, "tail=", repr(txt2[len("\n".join(L2)):][:120]) if False else repr(txt2[-0:]))
    results.append((name, win))
    if win:
        m = re.search(r"crypto\{[^}\n]*\}", txt2)
        print("FLAG:", m.group(0))
        open(os.path.join(HERE, "flag_2020-tetctf2020.txt"), "w").write(m.group(0))
        sys.exit(0)
    time.sleep(0.4)
print("battery:", results)
