import React, {useEffect, useRef, useState} from 'react';
import {createRoot} from 'react-dom/client';
import './motion-theme.css';
import './style.css';

type Gate = {id:string; op:string; inputs:string[]};
type Candidate = {id:string; consistent:boolean; rank:number; score:number};
type Data = {
  circuit:{gates:Gate[]; family:string}; seed:number; hidden:string;
  observations:{index:number; vector:number[]; expected:number; observed:number}[];
  remaining:number; history:number[]; recommendation:number[]|null;
  candidates:Candidate[]; equivalence_class:string[];
};

function CircuitVolume({data}:{data:Data}) {
  const ref=useRef<HTMLCanvasElement>(null);
  const [angle,setAngle]=useState(.5);
  const [drag,setDrag]=useState<number|null>(null);
  useEffect(()=>{
    const canvas=ref.current!, ctx=canvas.getContext('2d')!;
    const w=canvas.width=1000, h=canvas.height=600;
    ctx.clearRect(0,0,w,h);
    const project=(x:number,y:number,z:number)=>{
      const xx=x*Math.cos(angle)-z*Math.sin(angle), zz=x*Math.sin(angle)+z*Math.cos(angle);
      return [w/2+xx*1.32,h/2+y*1.02-zz*.44];
    };
    const points=new Map<string,number[]>();
    ['a','b','sel',...data.circuit.gates.map(g=>g.id)].forEach((id,i)=>{
      points.set(id,project((i%4-1.5)*140,(Math.floor(i/4)-2)*100,Math.sin(i)*75));
    });
    ctx.lineWidth=1.3; ctx.strokeStyle='#5E594F';
    data.circuit.gates.forEach(g=>g.inputs.forEach(source=>{
      const a=points.get(source)!, b=points.get(g.id)!;
      ctx.beginPath(); ctx.moveTo(a[0],a[1]); ctx.lineTo(b[0],b[1]); ctx.stroke();
    }));
    points.forEach((p,id)=>{
      const gate=data.circuit.gates.find(g=>g.id===id);
      const possible=data.candidates.some(c=>c.consistent&&c.id.startsWith(id+':'));
      ctx.fillStyle=possible?'#E7E2D6':'#F7F4EC';
      ctx.strokeStyle=possible?'#111111':'#5E594F';
      ctx.lineWidth=possible?2.5:1;
      ctx.setLineDash(possible?[]:[3,3]);
      ctx.fillRect(p[0]-61,p[1]-29,122,58); ctx.strokeRect(p[0]-61,p[1]-29,122,58);
      ctx.setLineDash([]);
      if(possible){ctx.fillStyle='#111111';ctx.fillRect(p[0]+49,p[1]-22,5,5);}
      ctx.textAlign='center'; ctx.font='700 17px Helvetica, Arial, sans-serif';
      ctx.fillStyle='#111111'; ctx.fillText(gate?.op||id.toUpperCase(),p[0],p[1]-3);
      ctx.font='12px Menlo, Consolas, monospace';ctx.fillStyle='#5E594F';ctx.fillText(id,p[0],p[1]+16);
    });
  },[data,angle]);
  return <div className="diagram-viewport" tabIndex={0} aria-label="Circuit diagram viewport; scroll horizontally on small screens">
    <canvas ref={ref} aria-label="Rotatable 3D circuit graph. Solid outlined nodes have consistent fault hypotheses."
      onPointerDown={e=>{setDrag(e.clientX);e.currentTarget.setPointerCapture(e.pointerId)}}
      onPointerMove={e=>{if(drag!==null){setAngle(angle+(e.clientX-drag)/160);setDrag(e.clientX)}}}
      onPointerUp={()=>setDrag(null)} onPointerCancel={()=>setDrag(null)}/>
  </div>;
}

function Contraction({data,paired}:{data:Data;paired:Data|null}) {
  const total=data.candidates.length;
  return <><svg className="plot" viewBox="0 0 460 200" role="img" aria-label="Candidate count after each active and fixed test">
    <path d="M40 20V163H445" stroke="#111111" fill="none"/>
    {[0,Math.round(total/2),total].map(v=><g key={v}>
      <line x1="40" x2="445" y1={160-v/total*132} y2={160-v/total*132} stroke="#E7E2D6"/>
      <text x="29" y={164-v/total*132} textAnchor="end" fill="#5E594F" fontSize="11">{v}</text>
    </g>)}
    {[data,paired].map((d,j)=>d&&<polyline key={j}
      points={d.history.map((v,i)=>`${50+i*54},${160-v/total*132}`).join(' ')}
      fill="none" stroke={j?'#5E594F':'#111111'} strokeDasharray={j?'5 4':undefined} strokeWidth={j?1.5:2.5}/>)}
    {data.history.map((_,i)=><text key={i} x={50+i*54} y="183" textAnchor="middle" fill="#5E594F" fontSize="11">{i+1}</text>)}
  </svg><div className="chart-key"><span><i/> Active separation</span><span><i className="dashed"/> Fixed sequence</span><span>Test number →</span></div></>;
}

function App() {
  const [data,setData]=useState<Data|null>(null), [paired,setPaired]=useState<Data|null>(null);
  const [seed,setSeed]=useState(31), [family,setFamily]=useState(6), [budget,setBudget]=useState(3);
  const [reveal,setReveal]=useState(false), [busy,setBusy]=useState(false), [error,setError]=useState('');
  useEffect(()=>{
    const controller=new AbortController();setBusy(true);setError('');
    Promise.all(['active','fixed'].map(policy=>fetch('/api/diagnose',{
      method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({family,seed,budget,policy}),signal:controller.signal
    }).then(r=>{if(!r.ok)throw Error('The simulation request failed.');return r.json()})))
      .then(([a,b])=>{setData(a);setPaired(b)})
      .catch(e=>{if(e.name!=='AbortError')setError(String(e))})
      .finally(()=>{if(!controller.signal.aborted)setBusy(false)});
    return()=>controller.abort();
  },[family,seed,budget]);
  const download=()=>{
    const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));
    a.download='chip-sentinel-transcript.json';a.click();URL.revokeObjectURL(a.href);
  };
  const candidates=data?.candidates.filter(c=>c.consistent).sort((a,b)=>a.rank-b.rank).slice(0,7)||[];
  return <main>
    <header className="masthead"><div className="index-mark">CS / 01 <span>Digital systems</span></div>
      <p>4-bit ALU · Synthetic diagnostic bench</p><span className="revision">V1.0 / LOCAL</span></header>
    <div className="title-row"><h1>ChipSentinel</h1><p>Fault localization<br/>Evidence before certainty.</p>
      <div className="run-state" role="status">{busy?'Applying test vectors':'Observation set ready'}<span className="registration-rule"/></div></div>
    <div className="bench">
      <aside className="settings">
        <h2><span>01</span> Test setup</h2>
        <label>Netlist family<select value={family} onChange={e=>setFamily(+e.target.value)}>
          {Array.from({length:8},(_,i)=><option key={i} value={i}>ALU {i}{i>5?' / held out':''}</option>)}</select></label>
        <label>Episode seed<input type="number" min="0" max="100000" value={seed} onChange={e=>setSeed(Math.max(0,Math.min(100000,+e.target.value)))}/></label>
        <label className="budget-label">Evidence budget <output>{budget} / 8</output><input aria-label="Evidence budget" type="range" min="0" max="8" value={budget} onChange={e=>setBudget(+e.target.value)}/></label>
        <button className="run-test" disabled={budget===8||busy} onClick={()=>setBudget(Math.min(8,budget+1))}>Run next test <span>→</span></button>
        <button className="export" onClick={download} disabled={!data}>Export evidence .json</button>
        <dl className="readouts">
          <div><dt>Active candidates</dt><dd>{data?.remaining??'—'}</dd></div>
          <div><dt>Fixed candidates</dt><dd>{paired?.remaining??'—'}</dd></div>
          <div><dt>Applied vectors</dt><dd>{data?.observations.length??'—'}</dd></div>
          <div><dt>Equivalent signatures</dt><dd>{data?.equivalence_class.length??'—'}</dd></div>
        </dl>
        <p className="small-note">One fault per episode. Equal test budgets. No physical silicon validation.</p>
      </aside>
      <div className="work-area">
        {error&&<p role="alert" className="error">{error}</p>}
        {data&&<>
          <div className="topology-row">
            <section className="schematic">
              <div className="section-title"><h2><span>02</span> Circuit topology</h2><p>{data.circuit.family} / 3D projection</p></div>
              <CircuitVolume data={data}/>
              <div className="diagram-caption"><span><i className="solid-square"/> Possible site</span><span><i className="dashed-square"/> Excluded by evidence</span><span>Drag to rotate</span></div>
              <div className="truth-row"><label><input type="checkbox" checked={reveal} onChange={e=>setReveal(e.target.checked)}/> Reveal injected fault</label><p>{reveal?`Injected fault: ${data.hidden}`:'Ground truth hidden'}</p></div>
            </section>
            <section className="ranking">
              <div className="section-title"><h2><span>03</span> Candidate register</h2></div>
              <p className="column-note">Learned score ≠ probability</p>
              <table className="rank-table"><thead><tr><th>Rank / hypothesis</th><th>Score</th></tr></thead><tbody>
                {candidates.map(c=><tr key={c.id}><td><div className="hypothesis"><span className="rank-index">{String(c.rank).padStart(2,'0')}</span><div><strong>{c.id.split(':')[0]}</strong><small>{c.id.split(':')[1]}</small></div></div></td><td>{c.score.toFixed(3)}<div className="score-rule"><i style={{width:`${c.score*100}%`}}/></div></td></tr>)}
              </tbody></table>
              <p className="small-note">Shown: seven leading consistent hypotheses. Identical signatures may remain indistinguishable.</p>
              <div className="next-vector"><span>Next active vector</span><strong>{data.recommendation?.join(' / ')||'Budget complete'}</strong><small>A / B / OP</small></div>
            </section>
          </div>
          <div className="evidence-row">
            <section className="evidence"><div className="section-title"><h2><span>04</span> Evidence ledger</h2><p>Outputs / binary</p></div>
              <div className="table-viewport"><table className="evidence-table"><thead><tr><th>Test</th><th>A / B / OP</th><th>Expected</th><th>Observed</th><th>Result</th></tr></thead><tbody>
                {data.observations.map((o,i)=><tr key={i}><td>{String(i+1).padStart(2,'0')}</td><td>{o.vector.join(' / ')}</td><td>{o.expected.toString(2).padStart(4,'0')}</td><td>{o.observed.toString(2).padStart(4,'0')}</td><td className={o.expected===o.observed?'pass':'difference'}>{o.expected===o.observed?'PASS':'DIFF'}</td></tr>)}
              </tbody></table></div>
              {data.observations.length===0&&<p className="empty-state">No evidence yet. Apply the first test vector.</p>}
            </section>
            <section className="contraction"><div className="section-title"><h2><span>05</span> Candidate contraction</h2><p>Fewer is narrower</p></div><Contraction data={data} paired={paired}/></section>
          </div>
        </>}
      </div>
    </div>
    <footer><span>CS / DIAGNOSTIC RECORD</span><p>Simulated circuits only. Scores describe this synthetic model.</p><span>Family {family} / Seed {seed}</span></footer>
  </main>;
}
createRoot(document.getElementById('root')!).render(<App/>);
