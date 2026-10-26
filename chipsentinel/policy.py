"""Hypothesis-consistency and maximum expected partition entropy policies."""
import math, random
from functools import lru_cache
from .engine import alu

@lru_cache(None)
def vectors(seed=11,n=48):
    rng=random.Random(seed); allv=[(a,b,s) for a in range(16) for b in range(16) for s in range(4)]; rng.shuffle(allv)
    corners=[(a,b,s) for a,b in ((0,0),(15,15),(0,15),(15,0),(5,10),(10,5)) for s in range(4)]
    return tuple((corners+[v for v in allv if v not in corners])[:n])
@lru_cache(None)
def table(family):
    c=alu(family); return tuple(tuple(c.evaluate(v,h) for v in vectors()) for h in c.hypotheses())
def consistent(family,observations):
    t=table(family); return [i for i,row in enumerate(t) if all(row[o['index']]==o['observed'] for o in observations)]
def recommend(family,candidates,used,policy='active',seed=0):
    available=[i for i in range(len(vectors())) if i not in used]
    if not available: return None
    if policy=='fixed': return available[0]
    if policy=='random': return random.Random(seed+len(used)*7919).choice(available)
    t=table(family)
    def score(i):
        counts={}
        for h in candidates: counts[t[h][i]]=counts.get(t[h][i],0)+1
        n=max(len(candidates),1)
        return -sum((k/n)*math.log2(k/n) for k in counts.values())
    return max(available,key=lambda i:(score(i),-i))
def features(family,h,obs):
    c=alu(family); fault=c.hypotheses()[h]; t=table(family); n=max(len(obs),1)
    exact=sum(t[h][o['index']]==o['observed'] for o in obs)/n
    distance=sum((t[h][o['index']]^o['observed']).bit_count()/4 for o in obs)/n
    mismatch=sum(o['expected']!=o['observed'] for o in obs)/n
    gate=next((g for g in c.gates if g.id==fault.site),None)
    return [1,exact,distance,mismatch,float(fault.kind=='none'),len(gate.inputs)/5 if gate else 0,len(obs)/8]
def episode(family,fault_index,budget=8,policy='active',seed=0):
    c=alu(family); hidden=c.hypotheses()[fault_index]; obs=[]; sizes=[]
    for step in range(budget):
        cand=consistent(family,obs); idx=recommend(family,cand,[o['index'] for o in obs],policy,seed)
        if idx is None: break
        vec=vectors()[idx]; obs.append({'index':idx,'vector':vec,'expected':c.evaluate(vec),'observed':c.evaluate(vec,hidden)}); sizes.append(len(consistent(family,obs)))
    return obs,sizes
