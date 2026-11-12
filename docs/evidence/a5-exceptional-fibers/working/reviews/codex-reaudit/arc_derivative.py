import ast,pickle,re,json
from pathlib import Path
import flint
from audit import parse,rank,ROOT
p=32009
class Dual:
 def __init__(self,x):self.v=x.v if isinstance(x,Dual) else ((x%p,0,0,0) if isinstance(x,int) else tuple(a%p for a in x))
 def __add__(self,b):b=Dual(b);return Dual(tuple(a+c for a,c in zip(self.v,b.v)))
 __radd__=__add__
 def __neg__(self):return Dual(tuple(-a for a in self.v))
 def __sub__(self,b):return self+-Dual(b)
 def __rsub__(self,b):return Dual(b)+-self
 def __mul__(self,b):
  b=Dual(b);a=self.v;c=b.v;return Dual((a[0]*c[0],*(a[0]*c[j]+a[j]*c[0] for j in range(1,4))))
 __rmul__=__mul__
 def __pow__(self,k):
  if k<0:return self.inv()**(-k)
  ans=Dual(1)
  for _ in range(k):ans=ans*self
  return ans
 def inv(self):
  a=self.v;q=pow(a[0],-1,p);return Dual((q,*(-v*q*q for v in a[1:])))
 def __truediv__(self,b):return self*Dual(b).inv()
 def __rtruediv__(self,b):return Dual(b)*self.inv()
zero=Dual(0)
def seriesmul(a,b):return [sum((a[j]*b[i-j] for j in range(i+1)),zero) for i in range(3)]
def evaluate(poly,values):
 out=[zero]*3;cache={}
 for ex,c in poly.items():
  v=[Dual(c),zero,zero]
  for i,e in enumerate(ex):
   if e:
    if (i,e) not in cache:
     q=[Dual(1),zero,zero]
     for _ in range(e):q=seriesmul(q,values[i])
     cache[i,e]=q
    v=seriesmul(v,cache[i,e])
  out=[a+b for a,b in zip(out,v)]
 return out
def derivative(poly,i):
 out={}
 for ex,c in poly.items():
  if ex[i]:
   powers=list(ex);powers[i]-=1;out[tuple(powers)]=c*ex[i]%p
 return out
if __name__=='__main__':
 base=ROOT/'docs/local/a5-failed-runs/build/arc'
 names=[f'T{i}' for i in range(1,13)]+['h','t2','t3','t4','t5','t6','t7','t8']
 N=[parse(t,names,p) for t in re.sub(r'T\((\d+)\)',r'T\1',(base/'norid.txt').read_text()).replace('\n','').split(',')]
 G=[parse(t,[f't{i}' for i in range(1,9)],p) for t in (base/'G.txt').read_text().replace('\n','').split(',')]
 selection=pickle.loads((base/'sel.pkl').read_bytes());Fs=[N[int(i)] for i in selection];dep=list(range(12))+[13,15,17,19]
 branches=ast.literal_eval((base/'tbase_branches.txt').read_text())
 primes=[[parse(t,[f'y({i})' for i in range(1,11)],p) for t in (base/f'primeP{j}.txt').read_text().replace('\n','').split(',')] for j in [1,2]]
 u1=Dual((5,1,0,0));u2=Dual((7,0,1,0));k=Dual((4,0,0,1));u3=-2*k/(k*k+3)
 for branch in [0,1]:
  vals=[eval(t.replace('^','**'),{'__builtins__':{}},{'u1':u1,'u2':u2,'k':k}) for t in branches[branch]]
  vals=list(map(Dual,vals))+[zero,zero,u1,-u1,u2,u2,u3,zero]
  x=[[v,zero,zero] for v in vals];x[12]=[zero,Dual(1),zero]
  M=[[evaluate(derivative(f,i),x)[0] for i in dep] for f in Fs]
  mat=flint.nmod_mat(16,16,[v.v[0] for row in M for v in row],p);inv=mat.inv()
  def solve(v):return [sum(int(inv[i,j])*v[j] for j in range(16))%p for i in range(16)]
  for order in [1,2]:
   residual=[evaluate(f,x)[order] for f in Fs];v0=solve([-r.v[0] for r in residual]);dv=[]
   for direction in range(1,4):dv.append(solve([-residual[i].v[direction]-sum(M[i][j].v[direction]*v0[j] for j in range(16)) for i in range(16)]))
   for j,i in enumerate(dep):x[i][order]=x[i][order]+Dual((v0[j],*(dv[q][j] for q in range(3))))
  residual_count=sum(any(any(c.v) for c in evaluate(f,x)) for f in N)
  t=[[zero,Dual(1),zero]]+[[zero,x[13+j][0],x[13+j][1]] for j in range(7)]
  F=[evaluate(g,t)[2] for g in G]
  F0=[v.v[0] for v in F];jac=[{j:(v.v[j+1]*F0[0]-v.v[0]*F[0].v[j+1])%p for j in range(3)} for v in F[1:]]
  jac=[{j:c for j,c in row.items() if c} for row in jac]
  incidence=[]
  for ideal in primes:
   incidence.append(sum(evaluate(g,[[v,zero,zero] for v in F])[0].v[0]!=0 for g in ideal))
  print(json.dumps({'branch':branch,'selected_relation_count':len(Fs),'all_normalization_relations':len(N),'Jacobian_det':int(mat.det()),'dual_residual_nonzero_through_s2':residual_count,'F_at_point':F0,'projective_derivative_rank':rank(jac,p),'nonvanishing_prime_generators':incidence}),flush=True)
