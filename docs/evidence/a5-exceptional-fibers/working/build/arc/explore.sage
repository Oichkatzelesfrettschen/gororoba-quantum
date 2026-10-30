p=32009
R=PolynomialRing(GF(p),'h,t1,t2,t3,t4,t5,t6,t7,t8')
h,t1,t2,t3,t4,t5,t6,t7,t8=R.gens()
S=[R(x) for x in open('strict_transform.txt').read().strip().replace('\n','').split(',')]
print(len(S), [x.degree() for x in S])
# chart t1=1: L: t2=t8=0, t5=t6, t3=-t4, free (t3,t5,t7)
import itertools
vars8=[h,t1,t2,t3,t4,t5,t6,t7,t8]
for (a,b,c) in [(3,5,7),(11,13,17),(2,9,4)]:
    pt={h:0,t1:1,t2:0,t3:a,t4:-a,t5:b,t6:b,t7:c,t8:0}
    # check on S
    print('onS',all(x.subs(pt)==0 for x in S))
    M=Matrix(GF(p),[[x.derivative(v).subs(pt) for v in vars8] for x in S])
    print('rank',M.rank(), 'kernel dim',9-M.rank())
    # columns without t1 (chart)
    M2=M.delete_columns([1]); print('rank chart',M2.rank())
    print(M2.right_kernel())
