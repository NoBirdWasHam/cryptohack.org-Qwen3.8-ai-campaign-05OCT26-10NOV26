import socket, json, time, random
from gmpy2 import is_prime, is_probab_prime
HOST, PORT = "socket.cryptohack.org", 13378

def sess(payload):
    s = socket.create_connection((HOST, PORT), timeout=20); s.settimeout(10)
    buf = b""
    try:
        while True:
            d = s.recv(65536)
            if not d: break
            buf += d
            if b"\n" in buf: break
    except Exception:
        pass
    s.sendall((json.dumps(payload) + "\n").encode())
    resp = b""
    try:
        while True:
            d = s.recv(65536)
            if not d: break
            resp += d
            if b"}" in resp: break
    except Exception:
        pass
    s.close()
    return resp.decode(errors="replace").strip()[:140]

small = [n for n in range(3, 1000) if is_prime(n)]

def build(R_bits, S_bits):
    tries = 0
    while True:
        tries += 1
        R = (1 << (R_bits - 1)) | random.getrandbits(R_bits - 1) | 1
        if not is_prime(R):
            continue
        S = 1
        while S.bit_length() < S_bits:
            S *= random.choice(small)
        p = 2 * R * S + 1
        if p.bit_length() < 2048:
            continue
        if is_probab_prime(p, 8):
            if is_prime(p):
                return p, R, S
        if tries % 2000 == 0:
            print(f"  {tries} R-tries so far", flush=True)

for (rb, sb) in [(256, 200), (256, 100), (512, 64)]:
    t0 = time.time()
    p, R, S = build(rb, sb)
    print(f"built R{rb} S{sb}: p {p.bit_length()}b S {S.bit_length()}b in {time.time()-t0:.0f}s", flush=True)
    resp = sess({"p": hex(p), "g": "0x2", "A": "0x4"})
    print("->", resp, flush=True)
    time.sleep(5)
print("PROBE5 DONE", flush=True)
