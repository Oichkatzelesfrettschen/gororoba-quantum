import re, pickle, sys, itertools, json
p=32009; F=GF(p)
names=['T%d'%i for i in range(1,13)]+['h','t2','t3','t4','t5','t6','t7','t8']
R=PolynomialRing(F,names); g=dict(zip(names,R.gens()))
N=[R(x) for x in re.sub(r'T\((\d+)\)',r'T\1',open('norid.txt').read().strip().replace('\n','')).split(',')]
sel=pickle.load(open('sel.pkl','rb')); Fs=[N[i] for i in sel]
dep_names=['T%d'%i for i in range(1,13)]+['t2','t4','t6','t8']; depg=[g[n] for n in dep_names]
Rg=PolynomialRing(F,['t%d'%i for i in range(1,9)])
Gl=[Rg(x) for x in open('G.txt').read().strip().replace('\n','').split(',')]
Pr=[]
for fn in ['primeP1.txt','primeP2.txt']:
    ys=PolynomialRing(F,['y%d'%i for i in range(1,11)])
    Pr.append([ys(re.sub(r'y\((\d+)\)',r'y\1',x)) for x in open(fn).read().strip().split(',')])
tb=eval(open('tbase_branches.txt').read())
Sr=PolynomialRing(F,'s'); s=Sr.gen()
def tr(f,n): return Sr(f.list()[:n+1])
def ev(f,x,n):
    out=Sr.zero(); pw={}
    for e,c in f.dict().items():
        term=Sr(c)
        for i,nm in enumerate(f.parent().variable_names()):
            if e[i]:
                key=(i,e[i])
                if key not in pw:
                    r=Sr.one()
                    for _ in range(e[i]): r=tr(r*x[i],n)
                    pw[key]=r
                term=tr(term*pw[key],n)
        out+=term
    return tr(out,n)
def arc(a,b,kk,br,NORD):
    u1,u2,k=F(a),F(b),F(kk)
    if (k*k+3)==0: return None
    u3=-2*k/(k*k+3)
    ev_env={'u1':u1,'u2':u2,'k':k}
    tbv=[F(eval(sx.replace('^','**'),{}, {'u1':u1,'u2':u2,'k':k})) if True else 0 for sx in tb[br]]
    x=[Sr(0)]*20
    for i in range(12): x[i]=Sr(tbv[i])
    x[12]=s; x[13]=Sr(0); x[14]=Sr(u1); x[15]=Sr(-u1); x[16]=Sr(u2); x[17]=Sr(u2); x[18]=Sr(u3); x[19]=Sr(0)
    idx=[names.index(n) for n in dep_names]
    M0=Matrix(F,16,16,[[ev(f.derivative(v),x,0)[0] for v in depg] for f in Fs])
    if M0.det()==0: return 'singular'
    Mi=M0.inverse()
    for n in range(1,NORD+1):
        res=vector(F,[ev(f,x,n)[n] for f in Fs]); corr=-Mi*res
        for b_,i in enumerate(idx): x[i]=x[i]+corr[b_]*s**n
    return x
def leadF(x,NORD):
    # original t1=s, t_j = s*tt_j ; names order: h,t2..t8 at 12..19
    tt=[s]+[tr(s*x[13+j],NORD+1) for j in range(7)]  # t2..t8
    ser=[ev(G,tt,NORD+1) for G in Gl]
    nu=min(f.valuation() for f in ser if f!=0)
    return nu,[f[nu] for f in ser]
