import os, sys, random, math, json
os.environ.setdefault("FLAG","FLAG-REDACTED-SEE-FLAGS-MIRROR")
HERE = r"~/AppData/Local/hermes/cache/scratch/w6e"
sys.path.insert(0, HERE)
sys.path.insert(0, HERE + r"/fisd")
from fis_dist import replay_b0
import fischlin_lib as FL

# ---- DP for optimal thresholds (16 attempts, leak w0 each attempt) ----
pm = 1/64.0
qprob = 63/64.0
Emax = 1024
dist = [(k, pm*qprob**k) for k in range(Emax)]
V = [0.0]*(17)
# V[n]: max success prob with n attempts remaining
def succ_stop0(o): return 1.0/(1.0+o)
V[1] = sum(pk*(0.5*( (1-o)*1.0 + o*succ_stop0(o) ) + 0.5*succ_stop0(o)) for k,pk in dist for o in [(63/64.0)**k])
# fix: compute cleanly
V[1] = 0.0
for k,pk in dist:
    o = qprob**k
    V[1] += pk*( 0.5*((1-o)*1.0 + o*succ_stop0(o)) + 0.5*succ_stop0(o) )
for n in range(2,17):
    s=0.0
    for k,pk in dist:
        o = qprob**k
        cont = V[n-1]
        stop = succ_stop0(o)
        d = max(cont, stop)
        s += pk*( 0.5*((1-o)*1.0 + o*d) + 0.5*d )
    V[n]=s
print("V[1..16]:", [round(V[n],6) for n in range(1,17)])
print("round success V16 =", V[16], " session (64 rounds) =", V[16]**64)
# thresholds: at n remaining, stop-answer0 iff succ_stop0(o) >= V[n-1]
thr = {}
for n in range(2,17):
    t = next((k for k in range(Emax) if succ_stop0(qprob**k) >= V[n-1]), Emax)
    thr[n]=t
print("thresholds by attempts-remaining n:", thr)

# ---- validation of distinguisher against real proofs ----
random.seed(1234)
import fischlin_lib
stats = {"b0":0,"b0_hit":0,"b0_finalok":0,"b1":0,"b1_hit":0}
for i in range(300):
    w0,w1,y0,y1 = FL.gen_round()
    b = i % 2
    pr = FL.fischlin_proof(w0,w1,y0,y1,b)
    hit, fok = replay_b0(pr, w0)
    if b==0:
        stats["b0"]+=1; stats["b0_hit"]+= (hit is not None); stats["b0_finalok"]+=fok
    else:
        stats["b1"]+=1; stats["b1_hit"]+= (hit is not None)
print("distinguisher on local proofs:", stats)
