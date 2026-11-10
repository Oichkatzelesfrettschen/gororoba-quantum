import sys, itertools
sys.path.insert(0, "gororoba_quantum")
from fractions import Fraction
from cd_core import cd_sign, cd_multiply_exact, sedenion_zero_divisor_corpus
def omega(D,a,b,c):
    return cd_sign(D,a,b)*cd_sign(D,a^b,c)*cd_sign(D,b,c)*cd_sign(D,a,b^c)
def mul(D,x,y): return cd_multiply_exact(D,x,y)
def assoc_vec(D,a,b,c):
    e=lambda i:[Fraction(int(k==i)) for k in range(D)]
    l=mul(D,mul(D,e(a),e(b)),e(c)); r=mul(D,e(a),mul(D,e(b),e(c)))
    return [x-y for x,y in zip(l,r)]
def main():
    for D in (4,8,16,32,64):
        na=0; dep_bad=0; rep_bad=0; omega_mismatch=0
        for a,b,c in itertools.permutations(range(1,D),3):
            w=omega(D,a,b,c)
            if w==-1: na+=1
            if c==a^b and w==-1: dep_bad+=1
        closed=(D-2)*(D-4)*(D+6)//2 if D>4 else 0
        print(f"D={D} N_enum={na} N_closed={closed} dependent_nonassoc={dep_bad}")
    # omega vs actual associator, D<=32
    for D in (8,16,32):
        bad=0
        for a,b,c in itertools.product(range(D),repeat=3):
            v=assoc_vec(D,a,b,c); w=omega(D,a,b,c)
            nz=[(i,x) for i,x in enumerate(v) if x!=0]
            if w==1 and nz: bad+=1
            if w==-1 and not (len(nz)==1 and nz[0][0]==a^b^c and abs(nz[0][1])==2): bad+=1
        print(f"D={D} omega-vs-associator mismatches={bad}")
    # ANF degree of c -> [omega(a,b,c)==-1] over F2, max and min over a,b
    def anf_deg(f,n):
        t=list(f)
        for i in range(n):
            for m in range(1<<n):
                if m>>i&1: t[m]^=t[m^(1<<i)]
        return max((bin(m).count("1") for m in range(1<<n) if t[m]),default=-1)
    for n in (3,4,5,6):
        D=1<<n; degs=set()
        for a in range(D):
            for b in range(D):
                degs.add(anf_deg([int(omega(D,a,b,c)==-1) for c in range(D)],n))
        print(f"n={n} ANF degree of c->omega over (a,b): {sorted(degs)}")
    # sedenion two-blade ZD census vs cd_core corpus
    D=16; rows=set()
    for i,j,k,l in itertools.product(range(1,16),repeat=4):
        if i<j and k<l and len({i,j,k,l})==4:
            for t in (1,-1):
                for s in (1,-1):
                    x=[Fraction(0)]*16; y=[Fraction(0)]*16
                    x[i]=1;x[j]=t;y[k]=1;y[l]=s
                    if all(v==0 for v in mul(16,x,y)): rows.add((i,j,t,k,l,s))
    print("sedenion two-blade zero products", len(rows), "pairs", len({(r[0],r[1]) for r in rows}), "signed elements", len({r[:3] for r in rows}), "cd_core corpus", len(sedenion_zero_divisor_corpus()))
    # A5 two-blade census
    D=32; pairs=set(); n=0
    for i,j,k,l in itertools.product(range(1,32),repeat=4):
        if i<j and k<l and len({i,j,k,l})==4 and i^j==k^l:
            if cd_sign(D,i,k)*cd_sign(D,j,l)*cd_sign(D,i,l)*cd_sign(D,j,k)==1:
                n+=2; pairs.add((i,j))
    print("A5 two-blade zero products", n, "index pairs", len(pairs), "signed elements", 2*len(pairs))
    # e1+e10 inverses
    x=[Fraction(0)]*16; x[1]=1; x[10]=1
    xb=[-v if k else v for k,v in enumerate(x)]
    inv=[Fraction(v)/2 for v in xb]
    one=[Fraction(int(k==0)) for k in range(16)]
    print("x*xbar/2==1", mul(16,x,inv)==one, mul(16,inv,x)==one)
    z=[Fraction(0)]*16; z[4]=Fraction(1); z[15]=Fraction(-1)
    print("x*z", [v for v in mul(16,x,z) if v], "z*x", [v for v in mul(16,z,x) if v])
    inv2=[a+b for a,b in zip(inv,z)]
    print("second inverse two-sided", mul(16,x,inv2)==one, mul(16,inv2,x)==one)

if __name__ == '__main__':
    main()
