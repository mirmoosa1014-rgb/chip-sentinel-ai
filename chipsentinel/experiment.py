import argparse,json,csv,time,statistics,random
from pathlib import Path
from .engine import alu
from .policy import episode,consistent,table
from .model import train,rank
ROOT=Path(__file__).resolve().parents[1]
def run(n):
    started=time.perf_counter();model=train();rows=[];failures=[]
    for family in (6,7):
      for seed in range(n):
        hidden=random.Random(8100+seed).randrange(len(alu(family).hypotheses()))
        for policy in ('fixed','random','active'):
            obs,sizes=episode(family,hidden,8,policy,seed);candidates=consistent(family,obs); ranking=rank(family,obs)
            equivalent=[i for i,row in enumerate(table(family)) if row==table(family)[hidden]]
            first=next((i+1 for i,k in enumerate(sizes) if k<=3),9)
            row={'family':family,'seed':seed,'policy':policy,'hidden':hidden,'remaining':sizes[-1],'tests_to_k3_capped9':first,'top1_exact':int(ranking[0]['index']==hidden),'top3_exact':int(hidden in [r['index'] for r in ranking[:3]]),'top1_equivalent':int(ranking[0]['index'] in equivalent),'equivalence_size':len(equivalent),'consistency_top1_exact':int(candidates[0]==hidden),'consistency_top3_exact':int(hidden in candidates[:3])}; rows.append(row)
            if not row['top1_exact'] and len(failures)<3: failures.append({'row':row,'observations':obs,'prediction':alu(family).hypotheses()[ranking[0]['index']].label(),'true':alu(family).hypotheses()[hidden].label()})
    # Explicit normal episodes measure deterministic specificity; ML alone can disagree.
    normal=[]
    for fam in (6,7):
        obs,_=episode(fam,0,8,'active');normal.append({'family':fam,'consistent_false_alarm':int(0 not in consistent(fam,obs)),'ml_false_alarm':int(rank(fam,obs)[0]['index']!=0)})
    summary={p:{k:statistics.mean(r[k] for r in rows if r['policy']==p) for k in ('remaining','tests_to_k3_capped9','top1_exact','top3_exact','top1_equivalent','consistency_top1_exact','consistency_top3_exact')} for p in ('fixed','random','active')}
    out=ROOT/'results';out.mkdir(exist_ok=True)
    with (out/'episodes.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    result={'episodes_per_policy':2*n,'budget':8,'pool_vectors':48,'summary':summary,'normal_episodes':normal,'elapsed_seconds':time.perf_counter()-started,'test_families':[6,7],'train_families':model['train_families'],'counterexamples':failures,'censoring':'9 means not narrowed to <=3 after eight tests'}
    (out/'metrics.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));return rows,result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--full',action='store_true');a=p.parse_args();run(80 if a.full else 15)
