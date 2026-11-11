# Connect live: PoW, additive stream l_t = t, capture q,n1..n4, extract positions.
import socket, hashlib, itertools, sys, json
from math import gcd
from functools import reduce

HOST, PORT = "archive.cryptohack.org", 42957

def recv_until(sock, timeout=20):
    sock.settimeout(timeout)
    data = b""
    while True:
        try:
            c = sock.recv(4096)
            if not c: break
            data += c
            if data.count(b"\n") >= 2 and not data.endswith(b"e\n"): 
                pass
        except Exception:
            break
    return data

def pow_answer(s):
    # 26 zero bits in sha256((s+ans)) as long
    import multiprocessing, hashlib
    def chunk(lohi):
        lo,hi = lohi
        h=hashlib.sha256
        for i in range(lo,hi):
            cand = hex(i)[2:] if i else ""
            # use printable hex-ish answer; length <= 8
            if h((s+cand).encode()).digest()[0] < 4:  # top 6 bits zero
                d = int.from_bytes(h((s+cand).encode()).digest(),'big')
                if d == (d>>26)<<26:
                    return cand
        return None
    procs = multiprocessing.cpu_count()
    span = 1<<28
    per = span//procs
    with multiprocessing.Pool(procs) as p:
        for r in p.imap_unordered(chunk, [(k*per,(k+1)*per) for k in range(procs)]):
            if r is not None: return r
    return None

def main():
    sk = socket.create_connection((HOST,PORT), timeout=15)
    f = sk.makefile("rwb")
    def readline(): return f.readline().decode().strip()
    def sendline(s): f.write((str(s)+"\n").encode()); f.flush()
    print("L1:", readline())
    salt = readline()
    print("L2:", salt)
    ans = pow_answer(salt)
    print("POW:", ans)
    sendline(ans)
    q = int(readline())
    print("q:", q, q.bit_length())
    print("L4:", readline())  # hello line
    sendline(1); sendline(1); sendline(1)   # a=1, x=1, b=1 => l_t = t
    ns = []
    for i in range(4):
        line = readline()
        if not line: print("EOF before n%d"%i); break
        ns.append(int(line)); print("n%d"%i, len(line))
    json.dump({"q":str(q), "ns":[str(x) for x in ns]}, open("live_instance.json","w"))
    # factor n_i mod q -> T products
    for i,nn in enumerate(ns):
        r = nn % q
        print("n%d mod q ="%i, r)
