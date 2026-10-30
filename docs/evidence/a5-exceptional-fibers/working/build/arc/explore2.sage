import re
p=32009
names=['T%d'%i for i in range(1,13)]+['h','t2','t3','t4','t5','t6','t7','t8']
R=PolynomialRing(GF(p),names)
g=dict(zip(names,R.gens()))
txt=open('norid.txt').read().strip().replace('\n','')
txt=re.sub(r'T\((\d+)\)',r'T\1',txt)
N=[R(x) for x in txt.split(',')]
print(len(N))
V=R.gens()
# points over E: h=0,t8=0? choose t3=a,t5=b,t7=c, t2=0,t4=-a,t6=b,t8=0
for (a,b,c) in [(3,5,7),(11,13,17)]:
    fix={g['h']:0,g['t2']:0,g['t3']:a,g['t4']:-a,g['t5']:b,g['t6']:b,g['t7']:c,g['t8']:0}
    Tn=[x.subs(fix) for x in N]
    Tv=PolynomialRing(GF(p),names[:12]); 
    I=Tv.ideal([Tv(str(x)) for x in Tn])
    print('dim fiber',I.dimension(), I.variety() if I.dimension()==0 else '')
    for pt in (I.variety() if I.dimension()==0 else []):
        full=dict(fix); 
        for k,v in pt.items(): full[g[str(k)]]=v
        full={k:v for k,v in full.items()}
        M=Matrix(GF(p),[[x.derivative(v).subs(full) for v in V] for x in N])
        print('pt',pt,'rank',M.rank())
