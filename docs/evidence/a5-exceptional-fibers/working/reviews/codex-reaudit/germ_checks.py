import os,json,subprocess,time
from pathlib import Path
from audit import ROOT,BASE,load
import sys
sys.path.insert(0,str(ROOT/'gororoba_quantum'))
import parallel

def work(f):
 p,names,(J,G)=load(f)
 text=f.read_text().split('number I=')[0] if False else f.read_text()
 script=text+'\noption(redSB); int k; int j; int z; ideal S; ideal R;\n'
 for N in range(2,8):
  script+=f'S=std(J+maxideal({N})); R=reduce(G,S); z=0; for(j=1;j<=ncols(G);j++){{if(R[j]==0){{z++;}}}} "RESULT",{N},vdim(S),size(S),z;\n'
 script+='quit;\n'
 name=f.parent.name+'-'+f.stem;dest=Path(name+'-germ.sing');dest.write_text(script)
 start=time.monotonic();res=subprocess.run(['Singular','-q','--no-rc',str(dest)],stdin=subprocess.DEVNULL,capture_output=True,text=True,timeout=150)
 Path(name+'-germ.log').write_text(res.stdout+res.stderr)
 return {'file':str(f.relative_to(ROOT)),'rc':res.returncode,'seconds':round(time.monotonic()-start,3),'results':[line for line in res.stdout.splitlines() if line.startswith('RESULT')],'errors':[line for line in res.stdout.splitlines() if '?' in line]}
if __name__=='__main__':
 files=sorted(BASE.glob('p*/*.sing'))
 for row in parallel.ordered_map(work,files,min_items=1):print(json.dumps(row),flush=True)
