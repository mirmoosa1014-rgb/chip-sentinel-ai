import unittest
from chipsentinel.engine import alu,Fault,Circuit,Gate,RegisterBank
from chipsentinel.policy import episode,consistent,recommend,table,vectors
from chipsentinel.model import rank
from chipsentinel.api import diagnose
class EngineTests(unittest.TestCase):
 def test_exhaustive_oracle(self):
  for fam in range(8):
   c=alu(fam)
   for a in range(16):
    for b in range(16):
     for s in range(4): self.assertEqual(c.evaluate((a,b,s)),[(a+b)&15,a&b,a|b,a^b][s])
 def test_faults(self):
  c=Circuit([Gate('x','BUF',('a',))],'x')
  for k,want in [('stuck0',0),('open',0),('stuck1',15),('invert',10)]: self.assertEqual(c.evaluate((5,0,0),Fault('x',k)),want)
 def test_invalid(self):
  for gates in [[Gate('x','BUF',('missing',))],[Gate('a','BUF',('a',))],[Gate('x','BUF',('a',),8)]]:
   with self.assertRaises(ValueError): Circuit(gates,'x')
  with self.assertRaises(ValueError): alu().evaluate((16,0,0))
 def test_parallel_state(self):
  r=RegisterBank();r.values=[1,2,3,4];self.assertEqual(r.edge({0:1,1:0}),[2,1,3,4]);self.assertEqual(r.edge(reset=True),[0]*4)
 def test_replay_and_hidden_independence(self):
  self.assertEqual(episode(6,5),episode(6,5));self.assertEqual(recommend(6,[0,1,2],[]),recommend(6,[0,1,2],[]))
  obs,_=episode(6,5);self.assertIn(5,consistent(6,obs))
 def test_equivalence(self):
  c=alu(6);hs=c.hypotheses();a=next(i for i,h in enumerate(hs) if h.kind=='stuck0');b=next(i for i,h in enumerate(hs) if h.kind=='open' and h.site==hs[a].site);self.assertEqual(table(6)[a],table(6)[b])
 def test_no_fault(self):
  obs,_=episode(6,0);self.assertIn(0,consistent(6,obs))
 def test_model_and_split(self):
  import json
  from chipsentinel.model import MODEL
  m=json.loads(MODEL.read_text());self.assertFalse(set(m['train_families'])&set(m['test_families']));self.assertEqual(len(rank(6,[])),len(alu(6).hypotheses()))
 def test_api_bounds(self):
  a=diagnose({'family':6,'budget':3,'seed':31});self.assertEqual(len(a['observations']),3)
  with self.assertRaises(ValueError): diagnose({'budget':100})
if __name__=='__main__': unittest.main()
