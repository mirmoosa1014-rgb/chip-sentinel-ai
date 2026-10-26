"""Version 1 bit-vector netlists. LSB bit 0, deterministic open wires read zero."""
from dataclasses import dataclass
from functools import lru_cache

@dataclass(frozen=True)
class Gate:
    id: str
    op: str
    inputs: tuple[str, ...]
    width: int = 4

@dataclass(frozen=True)
class Fault:
    site: str = 'no-fault'
    kind: str = 'none'
    def label(self): return f'{self.site}:{self.kind}'

class Circuit:
    def __init__(self, gates, output, family='custom'):
        self.gates=tuple(gates); self.output=output; self.family=family; known={'a','b','sel'}
        arities={'AND':2,'OR':2,'XOR':2,'ADD':2,'BUF':1,'NOT':1,'MUX':5}
        for g in self.gates:
            if g.id in known or g.op not in arities or g.width!=4 or len(g.inputs)!=arities[g.op] or any(x not in known for x in g.inputs):
                raise ValueError('invalid, cyclic, duplicate, or forward-referencing netlist')
            known.add(g.id)
        if output not in known: raise ValueError('missing output')
    def evaluate(self, vector, fault=Fault(), trace=False):
        a,b,sel=vector
        if any(type(x)!=int for x in vector) or not(0<=a<16 and 0<=b<16 and 0<=sel<4): raise ValueError('input vector out of bounds')
        if fault.kind not in ('none','stuck0','stuck1','invert','open') or (fault.kind!='none' and fault.site not in [g.id for g in self.gates]): raise ValueError('invalid fault')
        v={'a':a,'b':b,'sel':sel}
        for g in self.gates:
            x=[v[i] for i in g.inputs]; mask=(1<<g.width)-1
            if g.op=='AND': y=x[0]&x[1]
            elif g.op=='OR': y=x[0]|x[1]
            elif g.op=='XOR': y=x[0]^x[1]
            elif g.op=='NOT': y=~x[0]
            elif g.op=='BUF': y=x[0]
            elif g.op=='MUX': y=x[1+(x[0]&3)]
            else:
                y=0; carry=0
                for bit in range(g.width):
                    p=(x[0]>>bit)&1; q=(x[1]>>bit)&1
                    y|=(p^q^carry)<<bit; carry=(p&q)|(carry&(p^q))
            if fault.site==g.id:
                if fault.kind in ('stuck0','open'): y=0
                elif fault.kind=='stuck1': y=mask
                elif fault.kind=='invert': y=~y
            v[g.id]=y&mask
        y=v[self.output]
        return (y, v) if trace else y
    def flags(self,vector,fault=Fault()):
        y=self.evaluate(vector,fault); return {'zero':int(y==0),'negative':(y>>3)&1}
    def hypotheses(self): return [Fault()]+[Fault(g.id,k) for g in self.gates for k in ('stuck0','stuck1','invert','open')]
    def json(self): return {'version':1,'family':self.family,'width':4,'output':self.output,'gates':[{'id':g.id,'op':g.op,'inputs':g.inputs,'width':g.width} for g in self.gates]}

@lru_cache(None)
def alu(family=0):
    if family not in range(8): raise ValueError('unknown circuit family')
    gates=[]
    # Each family changes the buffer topology, preserving ALU arithmetic.
    for p in ('a','b'):
        source=p
        for j in range(1+family%3):
            name=f'input.{p}.{j}'; gates.append(Gate(name,'BUF',(source,))); source=name
        if p=='a': aa=source
        else: bb=source
    gates += [Gate('alu.add','ADD',(aa,bb)),Gate('alu.and','AND',(aa,bb)),Gate('alu.or','OR',(aa,bb))]
    if family>=4:
        gates += [Gate('xor.union','OR',(aa,bb)),Gate('xor.both','AND',(aa,bb)),Gate('xor.not','NOT',('xor.both',)),Gate('alu.xor','AND',('xor.union','xor.not'))]
    else: gates.append(Gate('alu.xor','XOR',(aa,bb)))
    gates.append(Gate('select','MUX',('sel','alu.add','alu.and','alu.or','alu.xor')))
    for j in range(family//3): gates.append(Gate(f'out.{j}','BUF',((gates[-1].id),)))
    return Circuit(gates,gates[-1].id,f'alu-{family}')

class RegisterBank:
    """Four 4-bit registers. Reads observe old state; parallel writes commit on edge."""
    def __init__(self): self.values=[0]*4
    def edge(self,writes=None,reset=False):
        old=self.values[:]
        if reset: self.values=[0]*4
        else:
            nxt=old[:]
            for dst,src in (writes or {}).items():
                if dst not in range(4) or src not in range(4): raise ValueError('register index')
                nxt[dst]=old[src]&15
            self.values=nxt
        return self.values[:]
