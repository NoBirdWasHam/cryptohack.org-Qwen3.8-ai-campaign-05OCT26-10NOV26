import ast, sys, os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from mq import load_instance, check, decode_ascii
def decode_v2(outpath):
    raw=open(outpath).read().strip()
    if not raw: return None,'EMPTY'
    if raw.startswith('[-1]'): return None,'UNSAT'
    obj=ast.literal_eval((raw[:-1] if raw.endswith(':') else raw).replace(' ',''))
    inner=obj[1]
    names=inner[3]
    tail=inner[5]
    vl=tail[1][2] if len(tail[1])>=3 else tail[1]
    assert len(vl)==len(names), (len(vl),len(names))
    vals={}
    for nm,item in zip(names,vl):
        tot=0
        for c,es in item:
            if c==0: continue
            for e in es:
                if e==0: tot^=(c&1)
                else: raise SystemExit('nonconstant term %r %r'%(c,es))
        vals[nm]=tot&1
    return vals,'OK'
if __name__=='__main__':
    outp=sys.argv[1]; inst=sys.argv[2]; which=sys.argv[3]
    MON,ct1,ct2=load_instance(inst)
    ct={'1':ct1,'2':ct2}[which]
    vals,st=decode_v2(outp)
    print('status',st)
    if vals:
        bits=[vals.get('x%d'%j,0) for j in range(80)]
        print('bad vs ct:',check(MON,bits,ct))
        print('ascii:',decode_ascii(bits))
