from pathlib import Path
from .engine import alu
from .policy import vectors,consistent,recommend,features,table
from .model import rank

def diagnose(payload):
    family=payload.get('family',6); seed=payload.get('seed',31); budget=payload.get('budget',4)
    if type(family)!=int or family not in range(8) or type(seed)!=int or not 0<=seed<=100000 or type(budget)!=int or not 0<=budget<=8: raise ValueError('family 0–7, seed 0–100000, budget 0–8 required')
    import random
    c=alu(family); hypotheses=c.hypotheses(); hidden=random.Random(seed).randrange(len(hypotheses)); observations=[]; history=[]
    policy=payload.get('policy','active')
    if policy not in ('active','fixed','random'): raise ValueError('invalid policy')
    for step in range(budget):
        cand=consistent(family,observations); idx=recommend(family,cand,[o['index'] for o in observations],policy,seed)
        vec=vectors()[idx]; observations.append({'index':idx,'vector':vec,'expected':c.evaluate(vec),'observed':c.evaluate(vec,hypotheses[hidden])}); history.append(len(consistent(family,observations)))
    cand=consistent(family,observations); ranking=rank(family,observations); ranks={r['index']:i+1 for i,r in enumerate(ranking)}
    return {'circuit':c.json(),'seed':seed,'hidden':hypotheses[hidden].label(),'observations':observations,'remaining':len(cand),'history':history,'recommendation':vectors()[recommend(family,cand,[o['index'] for o in observations])] if budget<8 else None,'candidates':[{'id':h.label(),'consistent':i in cand,'rank':ranks[i],'score':next(r['score'] for r in ranking if r['index']==i)} for i,h in enumerate(hypotheses)],'equivalence_class':[h.label() for i,h in enumerate(hypotheses) if table(family)[i]==table(family)[hidden]],'truth_kind':'synthetic simulation'}

# Optional FastAPI adapter. Portable fallback server is available via python -m chipsentinel.server.
try:
    from fastapi import FastAPI,HTTPException
    app=FastAPI(title='ChipSentinel AI',version='1.0.0')
    @app.post('/api/diagnose')
    def endpoint(payload:dict):
        try: return diagnose(payload)
        except ValueError as e: raise HTTPException(422,str(e))
    @app.get('/api/health')
    def health(): return {'status':'ok','mode':'synthetic'}
except ImportError:
    app=None
