import re, pickle, sys
p=32009; F=GF(p^2,'a')
nT=10
names=['T%d'%i for i in range(1,nT+1)]+['h','t1','t2','t4','t5','t6','t7','t8']
R=PolynomialRing(F,names); g=dict(zip(names,R.gens()))
N=[R(x) for x in re.sub(r'T\((\d+)\)',r'T\1',open('c3/norid.txt').read().strip().replace('\n','')).split(',')]
dep_names=['T%d'%i for i in range(1,nT+1)]+['t2','t4','t6','t8']; depg=[g[n] for n in dep_names]
nd=len(dep_names)
Rg=PolynomialRing(F,['t%d'%i for i in range(1,9)])
Gl=[Rg(x) for x in open('G.txt').read().strip().replace('\n','').split(',')]
Pr=[]
for fn in ['primeP1.txt','primeP2.txt']:
    ys=PolynomialRing(F,['y%d'%i for i in range(1,11)])
    Pr.append([ys(re.sub(r'y\((\d+)\)',r'y\1',x)) for x in open(fn).read().strip().split(',')])
Sr=PolynomialRing(F,'s'); s=Sr.gen()
def tr(f,n): return Sr(f.list()[:n+1])
def ev(f,x,n):
    out=Sr.zero(); pw={}
    for e,c in f.dict().items():
        term=Sr(c)
        for i in range(len(e)):
            if e[i]:
                key=(i,e[i])
                if key not in pw:
                    r=Sr.one()
                    for _ in range(e[i]): r=tr(r*x[i],n)
                    pw[key]=r
                term=tr(term*pw[key],n)
        out+=term
    return tr(out,n)
Tv=PolynomialRing(F,names[:nT])
def basepts(a,b,c):
    fix={g['h']:0,g['t1']:a,g['t2']:0,g['t4']:-1,g['t5']:b,g['t6']:b,g['t7']:c,g['t8']:0}
    I=Tv.ideal([Tv(str(e.subs(fix))) for e in N])
    if I.dimension()!=0: return 'posdim'
    out=[]
    for pt in I.variety(F):
        out.append([pt[Tv.gens()[i]] for i in range(nT)])
    return out
def arc3(a,b,c,Tb,NORD):
    x=[Sr(v) for v in Tb]+[s,Sr(a),Sr(0),Sr(-1),Sr(b),Sr(b),Sr(c),Sr(0)]
    idx=[names.index(n) for n in dep_names]
    # select nd independent rows greedy at base
    M=Matrix(F,len(N),nd,[[ev(f.derivative(v),x,0)[0] for v in depg] for f in N])
    if M.rank()<nd: return ('rank',M.rank())
    sel=[];cur=Matrix(F,0,nd)
    for i in sorted(range(len(N)),key=lambda i:len(N[i].monomials())):
        t=cur.stack(M[i])
        if t.rank()>cur.nrows(): cur=t; sel.append(i)
        if len(sel)==nd: break
    M0=Matrix(F,[M[i] for i in sel]); Mi=M0.inverse()
    for n in range(1,NORD+1):
        res=vector(F,[ev(N[i],x,n)[n] for i in sel]); corr=-Mi*res
        for b_,i in enumerate(idx): x[i]=x[i]+corr[b_]*s**n
    return x
def leadF3(x,NORD):
    # t=(h*tt): tt3=1 -> t3=s ; names: h,t1,t2,t4,t5,t6,t7,t8 at nT..nT+7
    X=x[nT:]
    tt=[tr(s*X[1],NORD+1),tr(s*X[2],NORD+1),s,tr(s*X[3],NORD+1),tr(s*X[4],NORD+1),tr(s*X[5],NORD+1),tr(s*X[6],NORD+1),tr(s*X[7],NORD+1)]
    ser=[ev(G,tt,NORD+1) for G in Gl]
    nu=min(f.valuation() for f in ser if f!=0)
    return nu,[f[nu] for f in ser]
if len(sys.argv)>1:
    NORD=int(sys.argv[1])
    for (a,b,c) in [(0,5,7),(0,3,2),(0,1,1),(0,2,9)]:
        bp=basepts(F(a),F(b),F(c))
        print((a,b,c),'basepts',bp if bp=='posdim' else len(bp)); sys.stdout.flush()
        if bp=='posdim': continue
        for Tb in bp:
            x=arc3(F(a),F(b),F(c),Tb,NORD)
            if isinstance(x,tuple): print('  ',x); continue
            res=sum(1 for f in N if ev(f,x,NORD)!=0)
            nu,Fv=leadF3(x,NORD)
            inP=[all(pg(*Fv)==0 for pg in Pp) for Pp in Pr]
            print('  resid',res,'nu',nu,'F',[str(v) for v in Fv],'inP1,P2',inP); sys.stdout.flush()
