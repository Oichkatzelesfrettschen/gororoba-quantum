import re
p=32009
names=['T%d'%i for i in range(1,13)]+['h','t2','t3','t4','t5','t6','t7','t8']
R=PolynomialRing(GF(p),names); g=dict(zip(names,R.gens()))
txt=open('norid.txt').read().strip().replace('\n','')
txt=re.sub(r'T\((\d+)\)',r'T\1',txt)
N=[R(x) for x in txt.split(',')]
P=PolynomialRing(GF(p),'u1,u2,m'); u1,u2,m=P.gens()
K=P.fraction_field()
u3=(1/m-m)/2
Tv=PolynomialRing(K,names[:12],order='lex')
fix={g['h']:0,g['t2']:0,g['t3']:u1,g['t4']:-u1,g['t5']:u2,g['t6']:u2,g['t7']:u3,g['t8']:0}
eqs=[]
for x in N:
    y=x.subs({k:v for k,v in fix.items()}) if False else None
# substitute manually
def sub(x):
    d=x.dict(); out=Tv.zero()
    Tg=Tv.gens()
    for e,c in d.items():
        term=Tv(c)
        for i in range(12): term*=Tg[i]**e[i]
        hv=fix[g['h']]; 
        vals=[0,0,u1,-u1,u2,u2,u3,0]   # h,t2,t3,t4,t5,t6,t7,t8
        for j in range(8):
            ex=e[12+j]
            if ex: term*=K(vals[j])**ex
        out+=term
    return out
eqs=[sub(x) for x in N]
eqs=[e for e in eqs if e!=0]
I=Tv.ideal(eqs)
G=I.groebner_basis()
print(len(G))
for gg in G: print(gg)
