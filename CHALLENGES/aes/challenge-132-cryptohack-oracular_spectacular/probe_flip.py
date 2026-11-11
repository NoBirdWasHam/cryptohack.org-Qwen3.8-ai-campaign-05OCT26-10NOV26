#!/usr/bin/env python3
"""oracular_spectacular — LIVE PROBE:
1) confirm JSON-line protocol + greeting
2) get ct
3) measure the oracle flip rate: send N distinct random candidate queries
   (all wrong candidates with overwhelming probability) and count
   P(result == true).  For a wrong candidate: true_good=False, so
   P(true response) = P(flip) = f.  -> fraction of true ~= f.
4) time the round-trips.
"""
import socket, json, time, os

HOST, PORT = "socket.cryptohack.org", 13423
N = 2000

s = socket.create_connection((HOST, PORT), timeout=30)
s.settimeout(30)

def recv_obj():
    buf = b""
    while True:
        i = buf.find(b"{")
        if i >= 0:
            try:
                o, _ = json.JSONDecoder().raw_decode(buf[i:].decode("utf-8", "ignore"))
                return o
            except json.JSONDecodeError:
                pass
        d = s.recv(65536)
        if not d:
            raise EOFError("closed")
        buf += d

def send(obj):
    s.sendall((json.dumps(obj) + "\n").encode())

greet = b""
while b"\n" not in greet:
    d = s.recv(65536)
    if not d:
        raise EOFError("closed")
    greet += d
print("greeting text:", greet[:200])

send({"option": "encrypt"})
ct = recv_obj()["ct"]
ct = bytes.fromhex(ct)
print("ct len:", len(ct), "blocks:", len(ct)//16 - 1)
iv, B1, B2 = ct[:16], ct[16:32], ct[32:48]

t0 = time.time()
nt = 0
nq = 0
last_err = None
while nq < N:
    # random candidate modification of B1[15] (byte 31 of message)
    m = bytearray(B1)
    m[15] = os.urandom(1)[0]
    query = (iv + bytes(m) + B2).hex()
    try:
        send({"option": "unpad", "ct": query})
        o = recv_obj()
    except (EOFError, ConnectionResetError) as e:
        print("CONN DIED after", nq, "queries:", e, "last:", last_err)
        break
    if "result" in o:
        nt += 1
        last_err = None
    else:
        last_err = o
        print("non-result:", o)
        break
    nq += 1
dt = time.time() - t0
print(f"queries={nq} true={nt} frac_true={nt/max(nq,1):.4f}  ({dt/nq*1000:.1f} ms/query, total {dt:.1f}s)")
try:
    s.close()
except Exception:
    pass
