"""Collect toomany samples and dump raw data for offline analysis."""
import json
import socket
from collections import Counter

HOST, PORT = "socket.cryptohack.org", 13390
N_CYCLES = 300

s = socket.create_connection((HOST, PORT), timeout=60)
s.settimeout(60)
print("greeting:", s.recv(65536)[:100], flush=True)

buf = b""
dec = json.JSONDecoder()

def recv_obj():
    global buf
    while True:
        i = buf.find(b"{")
        if i >= 0:
            try:
                obj, end = dec.raw_decode(buf[i:].decode("utf-8"))
                buf = buf[i + end:]
                return obj
            except json.JSONDecodeError:
                pass
        d = s.recv(65536)
        if not d:
            raise RuntimeError("EOF")
        buf += d

def send_obj(o):
    s.sendall((json.dumps(o) + "\n").encode())

samples = []
for k in range(N_CYCLES):
    send_obj({"option": "reset"})
    r = recv_obj()
    assert r.get("success"), r
    send_obj({"option": "get_sample"})
    r = recv_obj()
    assert "a" in r and "b" in r, r
    samples.append((r["a"], r["b"]))

with open("samples.jsonl", "w") as f:
    for a, b in samples:
        f.write(json.dumps({"a": a, "b": b}) + "\n")

a_counter = Counter(tuple(a) for a, _ in samples)
b_counter = Counter(b for _, b in samples)
print("top 5 a-counts:", a_counter.most_common(5), flush=True)
print("top 8 b-counts:", b_counter.most_common(8), flush=True)

top_a = [t for t, _ in a_counter.most_common(3)]
for ta in top_a:
    bs = [b for a, b in samples if tuple(a) == ta]
    print(f"a={ta[:8]}... count={len(bs)} b-dist={Counter(bs).most_common(5)}", flush=True)

# also: for the MOST common a, list ALL distinct b values
ta = top_a[0]
bs = [b for a, b in samples if tuple(a) == ta]
print("most-common a: all b values:", sorted(set(bs)), "counts:", Counter(bs), flush=True)
