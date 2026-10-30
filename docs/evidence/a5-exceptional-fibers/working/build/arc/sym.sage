import pickle,re
p=32009; F=GF(p)
Q=PolynomialRing(F,'u1,u2,k'); u1,u2,k=Q.gens()
Fn=pickle.load(open('Fnum.pkl','rb'))
ys=PolynomialRing(F,['y%d'%i for i in range(1,11)])
Pr=[[ys(re.sub(r'y\((\d+)\)',r'y\1',x)) for x in open(fn).read().strip().split(',')] for fn in ['primeP1.txt','primeP2.txt']]
Kf=Q.fraction_field()
for br in (0,1):
    num=[Q(x) for x in Fn[br]]
    # containment (numerators scale a common (k^2+3)^-1 factor, generators homogeneous)
    for pi,Pp in enumerate(Pr):
        vals=[g(*num) for g in Pp]
        nz=sum(1 for v in vals if v!=0)
        print('br',br,'prime',pi+1,'generators nonvanishing:',nz,'of',len(Pp))
    # exact generic rank of projective map (u1,u2,k)->[num]
    q=0
    J=Matrix(Kf,[[ (num[i].derivative(v)*num[q]-num[i]*num[q].derivative(v)) for v in (u1,u2,k)] for i in range(10) if i!=q])
    print('br',br,'generic Jacobian rank (chart y1)',J.rank())
    # base locus
    I=Q.ideal(num); print('br',br,'base locus ideal dim',I.dimension(),'prim',[ (c.gens()) for c in I.minimal_associated_primes()])
