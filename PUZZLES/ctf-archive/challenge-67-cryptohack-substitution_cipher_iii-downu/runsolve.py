import sys, os, time
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from mq import *
inst=sys.argv[1]; tag=sys.argv[2]; nch=int(sys.argv[3]) if len(sys.argv)>3 else 10
MON,ct1,ct2=load_instance(inst)
fixed={8*k for k in range(nch)}
which=sys.argv[4] if len(sys.argv)>4 else '1'
ct={'1':ct1,'2':ct2}[which]
inp=os.path.join(D,f'{tag}.in'); out=os.path.join(D,f'{tag}.out')
free=build_input(MON,ct,fixed,inp)
print('free vars',len(free),'->',inp)
t0=time.time()
r=run_ms(inp,out,thr=2,tmo=1700)
print('rc',r.returncode,'secs',round(time.time()-t0,1))
vals,st=parse_param(out,free)
print('parse',st)
if vals and not (isinstance(vals,tuple)):
    bits=[0]*80
    for idx,j in enumerate(free): bits[j]=vals[idx]
    print('bad vs ct:',check(MON,bits,ct))
    print('bytes:',decode_ascii(bits))
else:
    print(open(out).read()[:300])
