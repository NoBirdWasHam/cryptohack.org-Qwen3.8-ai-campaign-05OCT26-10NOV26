# noleaks: collect many OTP ciphertexts; per position the never-appearing byte = flag byte
import socket, json, base64, collections, sys, time

HOST, PORT = "socket.cryptohack.org", 13370
N = 6000

def recvline(f):
    return json.loads(f.readline())

sock = socket.create_connection((HOST, PORT), timeout=30)
f = sock.makefile("rwb")
banner = f.readline()  # "No leaks\n" (raw line before JSON)
print("banner:", banner[:40], flush=True)

# figure out protocol: first line may be JSON with before_input; try reading one JSON
try:
    first = json.loads(banner)
    print("first json:", str(first)[:100], flush=True)
except Exception:
    pass

req = (json.dumps({"msg": "request"}) + "\n").encode()
cts = []
t0 = time.time()
sock.settimeout(20)
for i in range(N):
    sock.sendall(req)
    line = f.readline()
    if not line:
        print("conn closed at", i, flush=True); break
    try:
        d = json.loads(line)
    except Exception:
        print("bad line", i, line[:80], flush=True); continue
    if "ciphertext" in d:
        cts.append(base64.b64decode(d["ciphertext"]))
    elif "error" in d and "Leaky" in d["error"]:
        continue
    else:
        print("unexpected:", d, flush=True); break
    if i % 500 == 0:
        print(i, "cts", len(cts), f"{time.time()-t0:.0f}s", flush=True)
sock.close()
print("collected", len(cts), "ciphertexts", flush=True)
json.dump([c.hex() for c in cts], open("cts.json", "w"))

# analyze
L = max(len(c) for c in cts)
print("ct length:", set(len(c) for c in cts), flush=True)
flag = bytearray()
for pos in range(L):
    seen = collections.Counter(c[pos] for c in cts if len(c) > pos)
    missing = [b for b in range(256) if b not in seen]
    counts = sorted(seen.values())
    print(pos, "missing:", missing, "min counts:", counts[:3], flush=True)
    if len(missing) == 1:
        flag.append(missing[0])
    else:
        flag.append(ord('?'))
print("FLAG GUESS:", flag.decode(errors="replace"), flush=True)
