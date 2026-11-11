import sys, time, os, hashlib, types, random
sys.argv = ["x", "local"]
import solve as S
code = open("chal.py").read().split("\nchallenge_generator_1()")[0].replace("signal.alarm(300)", "pass")
g = {"__name__": "chal_local"}
g.update(dict(os=os, hashlib=hashlib, signal=__import__("types").SimpleNamespace(alarm=lambda n: None)))
exec(code, g)
what = sys.argv[1] if len(sys.argv) > 1 else "c34"
if "c4" in what:
    for trial in range(3):
        G4 = g["Generator4"]()
        t0 = time.time()
        k4 = S.c4_attack(G4.func_gen, G4.p, G4.q)
        print("local C4 trial", trial, ":", k4 == G4.key, "(%.1fs)" % (time.time()-t0), flush=True)
