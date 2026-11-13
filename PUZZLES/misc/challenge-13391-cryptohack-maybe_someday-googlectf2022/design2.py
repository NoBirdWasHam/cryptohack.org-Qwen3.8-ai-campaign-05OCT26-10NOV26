# Design 20 shared queries (K_j, t_j), response models:
#  K=0   : r = 1 if s>=t else haszero64((s-t) mod 2^512)
#  K=255 : r = 1 if s< t else haszero64((s-t) mod 2^512)
#  else  : r = haszero64((s-t) mod 2^512)
import hashlib, json, random
M = 1<<512
CANDS = sorted(int.from_bytes(hashlib.sha512(i.to_bytes(2,'big')).hexdigest().encode(),'big') for i in range(65536))
def haszero(x):
    return 0 in x.to_bytes(64,'big')
def R(K, t, s):
    if K==0:  return 1 if s>=t else int(haszero((s-t)%M))
    if K==255:return 1 if s< t else int(haszero((s-t)%M))
    return int(haszero((s-t)%M))
random.seed(1)
QS=[]  # (K,t)
def patterns():
    d={}
    for i,s in enumerate(CANDS):
        key=tuple(R(K,t,s) for K,t in QS)
        d.setdefault(key,[]).append(i)
    return d
for step in range(20):
    d=patterns()
    big=max(d.values(),key=len)
    if len(big)==1: break
    best=None
    for K in (0,255,137):
        # quantiles within the big group
        vals=[CANDS[i] for i in big]
        ts=[vals[len(vals)*j//10] for j in range(1,10)]+[random.randrange(M) for _ in range(300)]
        for t in ts:
            cnt=sum(R(K,t,CANDS[i]) for i in big)
            score=max(cnt,len(big)-cnt)
            if best is None or score<best[0] or (score==best[0] and len(d)<best[3]):
                best=(score,K,t,len(d))
    _,K,t,_=best
    QS.append((K,t))
    print('q',len(QS),'biggest->',best[0])
d=patterns()
sizes=sorted((len(v) for v in d.values()),reverse=True)
print('queries:',len(QS),'classes:',len(d),'unique:',sum(1 for v in d.values() if len(v)==1),'largest:',sizes[:6])
json.dump([[K,str(t)] for K,t in QS],open('design_qs.json','w'))
print('saved design_qs.json')
