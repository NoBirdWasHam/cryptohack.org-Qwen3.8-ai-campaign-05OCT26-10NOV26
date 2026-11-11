#!/usr/bin/env python3
"""Live oracle probe: confirm keystream echo, measure latency + parallel throughput."""
import requests, time, random, sys
from concurrent.futures import ThreadPoolExecutor

BASE = "https://aes.cryptohack.org/oh_snap/send_cmd/{ct}/{nonce}/"
H = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) probe/1.0"}

def get_ks(s, nonce_hex, m=64):
    url = BASE.format(ct="00"*m, nonce=nonce_hex)
    r = s.get(url, headers=H, timeout=30)
    d = r.json()
    if "error" in d and d["error"].startswith("Unknown command:"):
        return bytes.fromhex(d["error"].split(":",1)[1].strip())
    raise RuntimeError(d)

s = requests.Session()
# correctness: same nonce twice -> same keystream
n1 = "41"*8
k1 = get_ks(s, n1); k2 = get_ks(s, n1)
print("deterministic:", k1 == k2, "ks[:8]:", k1[:8].hex())
# latency
t0=time.time()
for _ in range(10):
    get_ks(s, "%016x" % random.randrange(1<<64))
lat = (time.time()-t0)/10
print(f"serial latency/query: {lat:.3f}s")

# parallel throughput
def one(_):
    ss = requests.Session()
    for _ in range(5):
        get_ks(ss, "%016x" % random.randrange(1<<64))
    return 5
for workers in (4, 8, 16):
    t0=time.time()
    with ThreadPoolExecutor(workers) as ex:
        got = sum(ex.map(one, range(workers)))
    dt = time.time()-t0
    print(f"workers={workers}: {got} queries in {dt:.1f}s -> {got/dt:.1f} q/s")
    time.sleep(2)
