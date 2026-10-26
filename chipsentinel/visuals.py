"""Render saved results in Editorial Swiss tokens; numeric outputs are never written.
Palette adapted from motionstyle_swiss (MIT); see THIRD_PARTY_NOTICES.md.
"""
from pathlib import Path
import csv,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation,PillowWriter
from .engine import alu
from .policy import episode
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/images';OUT.mkdir(exist_ok=True)
plt.rcParams.update({'figure.facecolor':'#F3F0E8','axes.facecolor':'#F7F4EC','axes.edgecolor':'#111111','text.color':'#111111','axes.labelcolor':'#5E594F','xtick.color':'#5E594F','ytick.color':'#5E594F','grid.color':'#E7E2D6','font.family':['Helvetica Neue','Helvetica','Arial','DejaVu Sans'],'font.size':10})
d=json.loads((ROOT/'results/metrics.json').read_text());rows=list(csv.DictReader((ROOT/'results/episodes.csv').open()));colors=['#5E594F','#111111','#E10600'];names=['fixed','random','active']
fig,axs=plt.subplots(2,2,figsize=(13,8));fig.suptitle('CHIPSENTINEL / DIAGNOSIS UNDER AMBIGUITY',x=.06,ha='left',fontsize=20,fontweight='bold')
axs[0,0].bar(names,[d['summary'][n]['remaining'] for n in names],color=colors);axs[0,0].set(title='A / Remaining fault hypotheses',ylabel='Candidates after 8 tests')
axs[0,1].boxplot([[float(r['tests_to_k3_capped9']) for r in rows if r['policy']==n] for n in names],tick_labels=names,patch_artist=False,medianprops={'color':'#E10600'},boxprops={'color':'#111111'},whiskerprops={'color':'#111111'},capprops={'color':'#111111'},flierprops={'markeredgecolor':'#5E594F'});axs[0,1].set(title='B / Test effort across held-out episodes',ylabel='Tests to ≤3 (9 = censored)',ylim=(0,10))
x=list(range(3));axs[1,0].bar([a-.18 for a in x],[100*d['summary'][n]['top1_exact'] for n in names],width=.36,color='#111111',label='Exact hypothesis');axs[1,0].bar([a+.18 for a in x],[100*d['summary'][n]['top1_equivalent'] for n in names],width=.36,color='#E10600',label='Equivalent behavior');axs[1,0].set(xticks=x,xticklabels=names,ylabel='Top-1 accuracy (%)',title='C / Learned ranking and equivalent faults',ylim=(0,110));axs[1,0].legend(frameon=False,fontsize=8)
for policy,color in zip(names,colors):
 obs,sizes=episode(6,28,8,policy,0);axs[1,1].plot(range(1,9),sizes,'o-',label=policy,color=color)
axs[1,1].set(title='D / Counterexample episode · family 6 / fault 28',xlabel='Number of applied vectors',ylabel='Consistent candidates');axs[1,1].legend(frameon=False)
for ax in axs.flat: ax.grid(axis='y',alpha=.4);ax.spines[['top','right']].set_visible(False)
fig.text(.06,.025,f'SYNTHETIC ONLY · {d["episodes_per_policy"]} held-out episodes / policy · train families 0–3 · test families 6–7 · seed 8100+',fontsize=9,color='#5E594F');fig.tight_layout(rect=(.02,.05,1,.93));fig.savefig(OUT/'evaluation.png',dpi=170);plt.close(fig)
c=alu(6);fig=plt.figure(figsize=(12,6));ax=fig.add_subplot(projection='3d');ax.set_facecolor('#F3F0E8');g=c.gates;pos={id:(i%4,i//4,(i%3)*.7) for i,id in enumerate(['a','b','sel']+[x.id for x in g])}
for gate in g:
 for source in gate.inputs:
  a,b=pos[source],pos[gate.id];ax.plot([a[0],b[0]],[a[1],b[1]],[a[2],b[2]],color='#5E594F',linewidth=1.5)
for id,p in pos.items(): ax.scatter(*p,s=180,c='#E10600' if id.startswith('alu') else '#111111',marker='s');ax.text(p[0],p[1],p[2]+.13,id,fontsize=8,color='#111111')
ax.set_title('CHIPSENTINEL / 3D NETLIST TOPOLOGY',loc='left',pad=20,color='#111111');ax.set_axis_off();ax.view_init(25,-55);fig.tight_layout();fig.savefig(OUT/'circuit-3d.png',dpi=160)
def update(frame): ax.view_init(25,frame*6-55);return []
FuncAnimation(fig,update,frames=30).save(OUT/'circuit-orbit.gif',writer=PillowWriter(fps=10));plt.close(fig)
