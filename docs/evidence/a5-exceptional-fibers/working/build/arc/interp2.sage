import pickle
load('numlib.sage')
import itertools
Q=PolynomialRing(F,'u1,u2,k'); U1,U2,Kk=Q.gens()
mons=[U1**a*U2**b*Kk**c for a in range(2) for b in range(2) for c in range(3)]
out={}
for br in (0,1):
    pts=[(a,b,c) for a in (1,2,3,4) for b in (1,2,3) for c in (2,3,4,5)]
    rows=[];vals=[[] for _ in range(10)]
    data=[]
    for (a,b,c) in pts:
        x=arc(a,b,c,br,2)
        if x is None or x=='singular': continue
        nu,Fv=leadF(x,2); assert nu==2
        data.append(((a,b,c),Fv))
    A=Matrix(F,[[m(*pt) for m in mons] for pt,_ in data])
    print('br',br,'pts',len(data),'rank',A.rank())
    comps=[]
    for i in range(10):
        rhs=vector(F,[Fv[i]*(pt[2]**2+3) for pt,Fv in data])
        try:
            sol=A.solve_right(rhs)
        except ValueError:
            print('comp',i,'not in span'); sol=None; break
        comps.append(sum(c*m for c,m in zip(sol,mons)))
    else:
        den=Kk**2+3
        # verify on fresh points
        bad=0
        for (a,b,c) in [(5,7,6),(6,3,7),(9,4,2),(11,13,17),(20,31,8),(100,200,300),(15,1,9),(8,8,8)]:
            x=arc(a,b,c,br,2); nu,Fv=leadF(x,2)
            if any(Fv[i]*(c*c+3)!=comps[i](a,b,c) for i in range(10)): bad+=1
        print('br',br,'fresh mismatches',bad)
        out[br]=comps
        for i,cp in enumerate(comps): print(' F%d*(k^2+3) ='%(i+1),cp)
pickle.dump({br:[str(c) for c in out[br]] for br in out},open('Fnum.pkl','wb'))
