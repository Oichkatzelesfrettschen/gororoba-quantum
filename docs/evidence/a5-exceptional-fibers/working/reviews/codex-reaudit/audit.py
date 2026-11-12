import os
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import re,json,itertools,hashlib,time,importlib.util
from pathlib import Path
ROOT=Path('~/Projects/gororoba-workspace/gororoba-quantum')
BASE=ROOT/'docs/evidence/a5-exceptional-fibers/working/build/inputs'
def parse(text,names,p):
 out={}
 for term in re.findall(r'[+-]?[^+-]+',text.replace(' ','')):
  sign=-1 if term.startswith('-') else 1; term=term.lstrip('+-'); ex=[0]*len(names); c=sign
  for factor in term.split('*'):
   if factor.isdigit():c*=int(factor)
   else:
    name,_,power=factor.partition('^');ex[names.index(name)]+=int(power or 1)
  key=tuple(ex);out[key]=(out.get(key,0)+c)%p
 return {k:c for k,c in out.items() if c}
def load(f):
 t=f.read_text();p=int(re.search(r'ring r=(\d+)',t)[1]);names=re.search(r'ring r=\d+,\(([^)]+)\)',t)[1].split(',')
 return p,names,[[parse(v,names,p) for v in re.search(r'ideal '+kind+r'=([^;]+)',t)[1].split(',')] for kind in ['J','G']]
def rank(rows,p):
 piv={}
 for original in rows:
  row=original.copy()
  while row:
   key=max(row);c=row[key]
   if key not in piv:
    inv=pow(c,-1,p);piv[key]={m:v*inv%p for m,v in row.items()};break
   for m,v in piv[key].items():
    value=(row.get(m,0)-c*v)%p
    if value:row[m]=value
    else:row.pop(m,None)
 return len(piv)
def flip(poly,mask,p):return {m:(-c if sum(e for e,b in zip(m,mask) if b)%2 else c)%p for m,c in poly.items()}
def main():
 for folder in sorted(BASE.glob('p*')):
  rec=json.loads((folder/'receipt.json').read_text()); print(json.dumps({'receipt':str(folder.relative_to(ROOT)), 'header_hashes_match':all(hashlib.sha256((folder/r['header_file']).read_bytes()).hexdigest()==r['header_sha256'] for r in rec['incidences'])}),flush=True)
  data={}
  for f in sorted(folder.glob('*.sing')):
   p,names,(J,G)=load(f);data[f.stem]=(p,names,J,G);rj,rg=rank(J,p),rank(G,p)
   masks=[]
   for mask in itertools.product((0,1),repeat=len(names)):
    if rank(J+[flip(g,mask,p) for g in J],p)==rj and rank(G+[flip(g,mask,p) for g in G],p)==rg:masks.append([v for v,b in zip(names,mask) if b])
   orders={};degrees={}
   for g in G:
    a=min(map(sum,g));b=max(map(sum,g));orders[a]=orders.get(a,0)+1;degrees[b]=degrees.get(b,0)+1
   print(json.dumps({'header':str(f.relative_to(ROOT)),'p':p,'n':len(names),'J_count':len(J),'J_rank':rj,'G_count':len(G),'G_rank':rg,'G_orders':orders,'G_degrees':degrees,'sign_group':masks}),flush=True)
  for a,b,vars in [('e8-np','e8-nm',['t8','t9']),('xp-np','xm-nm',['t9']),('w8-np','w8-nm',['t9']),('iso-np','iso-nm',[])]:
   if a not in data or b not in data:continue
   p,names,J,G=data[a];_,_,K,H=data[b];mask=[v in vars for v in names];jm=[flip(g,mask,p) for g in J];gm=[flip(g,mask,p) for g in G]
   signs=[]
   for u,v in zip(gm,H):signs.append(1 if u==v else -1 if u=={m:-c%p for m,c in v.items()} else 0)
   print(json.dumps({'map':[folder.name,a,b],'flips':vars,'J_ranks':[rank(J,p),rank(K,p),rank(K+jm,p)],'G_ranks':[rank(G,p),rank(H,p),rank(H+gm,p)],'same_index_G_signs':signs}),flush=True)
if __name__=='__main__':main()
