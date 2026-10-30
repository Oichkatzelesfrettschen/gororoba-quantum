import re, pickle, sys, time
p=32009; NORD=int(sys.argv[1]); BR=int(sys.argv[2])
names=['T%d'%i for i in range(1,13)]+['h','t2','t3','t4','t5','t6','t7','t8']
R=PolynomialRing(GF(p),names); g=dict(zip(names,R.gens()))
txt=re.sub(r'T\((\d+)\)',r'T\1',open('norid.txt').read().strip().replace('\n',''))
N=[R(x) for x in txt.split(',')]
sel=pickle.load(open('sel.pkl','rb'))
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
S=PolynomialRing(K,'z'); z=S.gen()
q=[gg for gg in G0 if gg.degree(Tv.gen(10))==2][0]
qz=S(sum(c*z**m.degree(Tv.gen(10)) for c,m in zip(q.coefficients(),q.monomials())))
fa=list(qz.factor()); print('T11 quadratic factors',[(f.degree()) for f,_ in fa]); sys.stdout.flush()
r11=-fa[BR][0][0]/fa[BR][0][1]
pt={}
for gg in G0:
    # solve triangular: linear in leading var
    pass
sol={Tv.gens()[10]:r11}
for gg in G0:
    lv=[i for i in range(12) if gg.degree(Tv.gens()[i])>0]
    if not lv: continue
    i=max(lv, key=lambda i:-i) if False else lv[0]
    if i==10: continue
    if len(lv)==1 or gg.degree(Tv.gens()[i])==1:
        # linear in T_i: coefficient 1 expected
        c=gg.coefficient({Tv.gens()[i]:1}); rest=gg-c*Tv.gens()[i]
        val=-rest.subs({Tv.gens()[10]:r11})/c if rest!=0 else K(0)
        sol[Tv.gens()[i]]=K(val)
Tbase=[K(sol[Tv.gens()[i]]) if Tv.gens()[i] in sol else None for i in range(12)]
print('Tbase',Tbase); sys.stdout.flush()
# series ring
Sr=PolynomialRing(K,'s'); s=Sr.gen()
def trunc(f,n): return sum((f[i]*s**i for i in range(min(n,f.degree())+1)),Sr.zero()) if f!=0 else f
dep_names=['T%d'%i for i in range(1,13)]+['t2','t4','t6','t8']
x={}
for i in range(12): x['T%d'%(i+1)]=Sr(Tbase[i])
x['t2']=Sr(0);x['t4']=Sr(-u1);x['t6']=Sr(u2);x['t8']=Sr(0)
x['h']=s;x['t3']=Sr(u1);x['t5']=Sr(u2);x['t7']=Sr(u3)
def ev(f,n):
    out=Sr.zero()
    pw={}
    for e,c in f.dict().items():
        term=Sr(K(c))
        for i,nm in enumerate(names):
            if e[i]:
                key=(nm,e[i])
                if key not in pw:
                    r=Sr.one()
                    for _ in range(e[i]): r=trunc(r*x[nm],n)
                    pw[key]=r
                term=trunc(term*pw[key],n)
        out+=term
    return trunc(out,n)
Fs=[N[i] for i in sel]
depg=[g[n] for n in dep_names]
# Jacobian at s=0 base
M0=Matrix(K,[[K(f.derivative(v).subs({gg:0 for gg in []})) if False else None for v in depg] for f in Fs]) if False else None
def evpt(f):
    return ev(f,0)[0]
M0=Matrix(K,16,16)
for a,f in enumerate(Fs):
    for b,v in enumerate(depg):
        M0[a,b]=ev(f.derivative(v),0)[0]
t0=time.time(); d0=M0.det(); print('det M0',d0.factor() if d0!=0 else 0, time.time()-t0); sys.stdout.flush()
Minv=M0.inverse(); print('inv done',time.time()-t0); sys.stdout.flush()
for n in range(1,NORD+1):
    res=vector(K,[ev(f,n)[n] for f in Fs])
    corr=-Minv*res
    for b,nm in enumerate(dep_names): x[nm]=x[nm]+corr[b]*s**n
    print('order',n,'done',time.time()-t0); sys.stdout.flush()
# check all N vanish mod s^(NORD+1)
bad=sum(1 for f in N if ev(f,NORD)!=0)
print('residual nonzero eqs mod s^%d: %d of %d'%(NORD+1,bad,len(N))); sys.stdout.flush()
pickle.dump({nm:[str(c) for c in x[nm].list()] for nm in x},open('arc_br%d.pkl'%BR,'wb'))
