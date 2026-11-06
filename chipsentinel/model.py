"""Small logistic candidate ranker, trained using simulator-only labels."""
import json, math, random
from pathlib import Path
from .policy import episode,features
from .engine import alu
MODEL=Path(__file__).resolve().parents[1]/'models/ranker.json'
def sigmoid(x): return 1/(1+math.exp(-max(-40,min(40,x))))
def train():
    rng=random.Random(130); rows=[]
    for fam in (0,1,2,3):
        for seed in range(35):
            hidden=rng.randrange(len(alu(fam).hypotheses())); obs,_=episode(fam,hidden,1+seed%6,'random',seed)
            for h in range(len(alu(fam).hypotheses())): rows.append((features(fam,h,obs),int(h==hidden)))
    w=[0.0]*7
    for epoch in range(100):
        gradient=[0.0]*7
        for x,y in rows:
            # Balance candidate classes for training; outputs are ranking scores, not calibrated probabilities.
            e=(sigmoid(sum(a*b for a,b in zip(w,x)))-y)*(25 if y else 1)
            for j in range(7): gradient[j]+=e*x[j]
        for j in range(7): w[j]-=.15*(gradient[j]/len(rows)+.001*w[j])
    data={'schema':['bias','consistency_fraction','bit_error_fraction','observed_fault_fraction','normal_candidate','gate_fanin','test_fraction'],'weights':w,'train_families':[0,1,2,3],'validation_families':[4,5],'test_families':[6,7],'seed':130,'rows':len(rows),'calibrated':False}
    MODEL.parent.mkdir(exist_ok=True); MODEL.write_text(json.dumps(data,indent=2)); return data

def rank(family,observations):
    try:
        model=json.loads(MODEL.read_text());w=model['weights']
        schema=['bias','consistency_fraction','bit_error_fraction','observed_fault_fraction','normal_candidate','gate_fanin','test_fraction']
        if model['schema']!=schema or len(w)!=7 or not all(type(v) in (int,float) and math.isfinite(v) for v in w):raise ValueError('Invalid ranker schema')
    except (OSError,ValueError,KeyError,TypeError):
        return [{'index':i,'score':0.0} for i in range(len(alu(family).hypotheses()))]
    result=[{'index':h,'score':sigmoid(sum(a*b for a,b in zip(w,features(family,h,observations))))} for h in range(len(alu(family).hypotheses()))]
    return sorted(result,key=lambda r:(-r['score'],r['index']))
