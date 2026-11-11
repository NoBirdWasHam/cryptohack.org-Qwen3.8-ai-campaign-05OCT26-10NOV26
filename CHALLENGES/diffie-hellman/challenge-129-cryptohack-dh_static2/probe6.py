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

small = [n for n in range(3, 2000) if is_prime(n)]

def build(R_bits, target_bits=2048):
    # p = 2*R*S + 1 EXACTLY target_bits; R prime R_bits; S smooth filling the rest
    S_bits = target_bits - R_bits - 2
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
        if p.bit_length() != target_bits:
            continue
        if is_probab_prime(p, 12):
            return p, R, S
        if tries % 5000 == 0:
            print(f"  {tries} R-tries", flush=True)

for rb in (256, 512, 224):
    t0 = time.time()
    p, R, S = build(rb)
    print(f"built R{rb}: p {p.bit_length()}b S {S.bit_length()}b in {time.time()-t0:.0f}s", flush=True)
    resp = sess({"p": hex(p), "g": "0x2", "A": "0x4"})
    print("->", resp, flush=True)
    if rb == 256 and '"B"' in resp:
        # same p, but g of order | S (small subgroup) — does the server police g?
        g_small = pow(3, 2 * R, p)
        resp2 = sess({"p": hex(p), "g": hex(g_small), "A": "0x4"})
        print("-> small-order g:", resp2[:100], flush=True)
    time.sleep(5)
print("PROBE6 DONE", flush=True)
