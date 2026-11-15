#!/usr/bin/env python3
# local simulator of evil_twisted_mind server for end-to-end testing
import re, os, socket, json, ast, threading, random
src = open("13418.py").read()
p = int(re.search(r"modulus\s*=\s*(\d+)", src).group(1))
a = -3
b = int(re.search(r"^b\s*=\s*(\d+)", src, re.M).group(1))
order = int(re.search(r"^order\s*=\s*(\d+)", src, re.M).group(1))
def sxz(X1,Z1,m):
    XX=X1*X1%m; ZZ=Z1*Z1%m
    A=2*((X1+Z1)**2-XX-ZZ)%m
    aZZ=a*ZZ%m
    X3=((XX-aZZ)**2-2*b*A*ZZ)%m
    Z3=(A*(XX+aZZ)+4*b*ZZ*ZZ)%m
    return (X3,Z3)
def sdiff(X1,Z1,X2,Z2,xd,m):
    X1Z2=X1*Z2%m; X2Z1=X2*Z1%m; Z1Z2=Z1*Z2%m
    T=(X1Z2+X2Z1)*(X1*X2+a*Z1Z2)%m
    Z3=(X1Z2-X2Z1)**2%m
    X3=(2*T+4*b*Z1Z2**2-xd*Z3)%m
    return (X3,Z3)
def ladder_full(scalar,x0,m):
    if scalar==0: return (1,0)
    R0=(x0,1); R1=sxz(*R0,m)
    n=scalar.bit_length(); pbit=0; bit=0
    for i in range(n-2,-1,-1):
        bit=(scalar>>i)&1
        pbit^=bit
        if pbit: R0,R1=R1,R0
        R1=sdiff(*R0,*R1,x0,m)
        R0=sxz(*R0,m)
        pbit=bit
    if bit: R0=R1
    return R0
def scalarmult(s,x0):
    X,Z=ladder_full(s,x0,p)
    return X*pow(Z,-1,p)%p
rng = random.Random(int(os.environ.get("SIM_SEED","42")))
k0 = rng.randrange(0, 1<<192)
priv = min(k0 % order, (order - k0) % order)
print("SIM privkey:", priv, flush=True)
srv = socket.socket(); srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("127.0.0.1", 13419)); srv.listen(1)
print("SIM listening 13419", flush=True)
c, _ = srv.accept()
f = c.makefile("rwb")
f.write(b"Welcome!\nYou can submit only 1 elliptic curve point (x coordinate only).\nYou have 60 seconds to submit the private key in decimal format.\n"); f.flush()
attempts = 1
while True:
    line = f.readline()
    if not line: break
    try: msg = ast.literal_eval(line.decode())
    except Exception: break
    if msg.get("option") == "get_pubkey":
        if attempts == 0:
            f.write((json.dumps({"error":"no more"})+"\n").encode()); f.flush(); continue
        x0 = int(msg["x0"])
        try:
            pk = scalarmult(priv, x0)
            resp = {"pubkey": pk}
        except Exception:
            resp = {"error": "boom"}
        attempts -= 1
        f.write((json.dumps(resp)+"\n").encode()); f.flush()
    elif msg.get("option") == "get_flag":
        ok = int(msg["privkey"]) % order == priv
        f.write((json.dumps({"message":"ok" if ok else "wrong",
                             "flag":"crypto{SIMULATED_LOCAL_TEST}" if ok else None})+"\n").encode())
        f.flush()
        print("SIM guess:", str(msg["privkey"])[:24], "->", "CORRECT" if ok else "WRONG", flush=True)
        if ok: break
c.close(); srv.close()
