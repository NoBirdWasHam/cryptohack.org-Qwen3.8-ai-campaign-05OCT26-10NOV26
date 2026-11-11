# probe11: server architecture tests
import sys, time, base64, hashlib
from sbase import S

def permutate(p, q): return bytes([p[x] for x in q])

def main():
    # conn A
    a = S()
    a.send("\U0001f5a5\ufe0f")
    PA, SA = a.auth_begin()
    print("A salt", SA.hex(), flush=True)
    print("A garb:", repr(a.auth_answer("0"*64)), flush=True)
    sa = base64.b64encode(SA).decode()
    h1 = a.spy(list(range(21)), sa); print("A spy1", repr(h1[:40]), flush=True)
    h2 = a.spy(list(range(21)), sa); print("A spy2", repr(h2[:40]), flush=True)
    print("pepper fixed per conn:", h1 == h2, flush=True)
    # unknown command test
    a.s.settimeout(3)
    for cmd in ["help", "?", "\U0001f4a3"]:
        try:
            a.send(cmd)
            time.sleep(0.5)
            o = a.s.recv(4096)
            print("cmd", repr(cmd), "->", repr(o[:40]), flush=True)
        except Exception as e:
            print("cmd", repr(cmd), "->", type(e).__name__, flush=True)
    a.s.settimeout(55)
    a.s.close()
    # conn B: stale salt from conn A
    b = S()
    b.send("\U0001f5a5\ufe0f")
    PB, SB = b.auth_begin()
    print("B garb:", repr(b.auth_answer("0"*64)), flush=True)
    print("B spy(A salt):", repr(b.spy(list(range(21)), sa)[:40]), flush=True)
    print("B spy(B salt):", repr(b.spy(list(range(21)), base64.b64encode(SB).decode())[:40]), flush=True)
    # dictionary auth attempts
    CANDS = [b"cryptohack000000", b"cryptohackcrypt0", b"signinpleaseag", b"password12345678",
             b"administratorx", b"letmein123456789", b"changeme1234567", b"hkcert21hkcert21",
             b"mystizmystizmyst", b"S3J5cHRvSGFjayE=", b"AAAAAAAAAAAAAAAA", b"\x00"*16,
             b"cryptohack{you", b"y0u_c4n7_3avedr", b"p3pp3r_4nd_s4lt", b"sign_in_please__"]
    for cand in CANDS:
        b.send("\U0001f5a5\ufe0f")
        P, Sx = b.auth_begin()
        h = hashlib.sha256(permutate(cand + Sx + b"\x00", P)).hexdigest()
        o = b.auth_answer(h)
        print("cand", cand[:20], "->", repr(o[:30]), flush=True)
        if "\U0001f3c1" in o:
            print("FLAG:", o, flush=True)
            break
    b.s.close()

if __name__ == "__main__":
    main()
