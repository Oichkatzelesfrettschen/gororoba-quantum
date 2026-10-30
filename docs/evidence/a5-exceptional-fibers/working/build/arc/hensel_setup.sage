import re, pickle
p=32009
names=['T%d'%i for i in range(1,13)]+['h','t2','t3','t4','t5','t6','t7','t8']
R=PolynomialRing(GF(p),names); g=dict(zip(names,R.gens()))
txt=open('norid.txt').read().strip().replace('\n','')
txt=re.sub(r'T\((\d+)\)',r'T\1',txt)
N=[R(x) for x in txt.split(',')]
V=R.gens()
dep_names=['T%d'%i for i in range(1,13)]+['t2','t4','t6','t8']
dep=[g[n] for n in dep_names]
# numeric base point (u1,u2,k)=(3,5,4): u3=-2k/(k^2+3), branch via T11 root
def basept(u1,u2,k,br):
    F=GF(p); u3=F(-2*k)/(k*k+3); m=F(1)  # m placeholder
    mm=None
    return None
# use m-free formula: T-system from earlier Groebner with u3 generic: T11 quadratic
# rederive numerically through ideal
Tv=PolynomialRing(GF(p),names[:12])
def pts(u1,u2,u3):
    fix={g['h']:0,g['t2']:0,g['t3']:u1,g['t4']:-u1,g['t5']:u2,g['t6']:u2,g['t7']:u3,g['t8']:0}
    I=Tv.ideal([Tv(str(x.subs(fix))) for x in N])
    out=[]
    for pt in I.variety():
        d=dict(fix)
        for kk,v in pt.items(): d[g[str(kk)]]=v
        out.append(d)
    return out
F=GF(p)
k=F(4); u3=-2*k/(k*k+3); 
P0=pts(F(3),F(5),u3)
print(len(P0))
d=P0[0]
M=Matrix(GF(p),[[x.derivative(v).subs(d) for v in dep] for x in N])
print('rank',M.rank())
# choose 16 independent rows with fewest terms
order=sorted(range(len(N)),key=lambda i:len(N[i].monomials()))
sel=[];cur=Matrix(GF(p),0,16)
for i in order:
    row=M[i]
    t=cur.stack(row)
    if t.rank()>cur.nrows():
        cur=t; sel.append(i)
    if len(sel)==16: break
print(sel, [len(N[i].monomials()) for i in sel])
pickle.dump(sel,open('sel.pkl','wb'))
