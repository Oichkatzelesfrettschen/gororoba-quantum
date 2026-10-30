import re
p=32009
names=['T%d'%i for i in range(1,13)]+['h','t2','t3','t4','t5','t6','t7','t8']
R=PolynomialRing(GF(p),names); g=dict(zip(names,R.gens()))
txt=open('norid.txt').read().strip().replace('\n','')
txt=re.sub(r'T\((\d+)\)',r'T\1',txt)
N=[R(x) for x in txt.split(',')]
Tv=PolynomialRing(GF(p),names[:12])
cnt={}
for a in range(1,7):
  for b in range(1,6):
    c=2
    fix={g['h']:0,g['t2']:0,g['t3']:a,g['t4']:-a,g['t5']:b,g['t6']:b,g['t7']:c,g['t8']:0}
    I=Tv.ideal([Tv(str(x.subs(fix))) for x in N])
    # degree of fiber via vector space dim over F_p
    d=I.vector_space_dimension() if I.dimension()==0 else -1
    nr=len(I.variety()) if d>0 else 0
    cnt[(d,nr)]=cnt.get((d,nr),0)+1
print(cnt)
