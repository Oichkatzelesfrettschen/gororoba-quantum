import re,pickle
p=32009
names=['T%d'%i for i in range(1,13)]+['h','t2','t3','t4','t5','t6','t7','t8']
R=PolynomialRing(GF(p),names)
txt=re.sub(r'T\((\d+)\)',r'T\1',open('norid.txt').read().strip().replace('\n',''))
N=[R(x) for x in txt.split(',')]
P=PolynomialRing(GF(p),'u1,u2,k'); u1,u2,k=P.gens(); K=P.fraction_field()
u3=-2*k/(k^2+3)
Tv=PolynomialRing(K,names[:12],order='lex')
vals=[0,0,u1,-u1,u2,u2,u3,0]
def sub0(x):
    out=Tv.zero(); Tg=Tv.gens()
    for e,c in x.dict().items():
        term=Tv(K(c))
        for i in range(12): term*=Tg[i]**e[i]
        for j in range(8):
            if e[12+j]: term*=K(vals[j])**e[12+j]
        out+=term
    return out
G0=Tv.ideal([e for e in (sub0(x) for x in N) if e!=0]).groebner_basis()
Tg=Tv.gens()
S=PolynomialRing(K,'z'); z=S.gen()
q=[gg for gg in G0 if gg.degree(Tg[10])==2][0]
qz=sum(c*z**m.degree(Tg[10]) for c,m in zip(q.coefficients(),q.monomials()))
fa=list(S(qz).factor())
res=[]
for f,_ in fa:
    r11=-f[0]/f[1]
    sol={10:r11}
    for gg in G0:
        lv=[i for i in range(12) if gg.degree(Tg[i])>0]
        if len(lv)==0 or lv[0]==10: continue
        i=lv[0]
        if gg.degree(Tg[i])==1:
            c=gg.coefficient({Tg[i]:1}); rest=gg-c*Tg[i]
            sol[i]=K(-rest.subs({Tg[10]:r11})/c) if rest!=0 else K(0)
    res.append([str(sol[i]) for i in range(12)])
    print(res[-1])
open('tbase_branches.txt','w').write(repr(res))
