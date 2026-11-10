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
    # e1+e10 inverses
    x=[Fraction(0)]*16; x[1]=1; x[10]=1
    xb=[-v if k else v for k,v in enumerate(x)]
    inv=[Fraction(v)/2 for v in xb]
    one=tuple(Fraction(int(k==0)) for k in range(16))
    print("x*xbar/2==1", mul(16,x,inv)==one, mul(16,inv,x)==one)
    z=[Fraction(0)]*16; z[4]=Fraction(1); z[15]=Fraction(-1)
    print("x*z", [v for v in mul(16,x,z) if v], "z*x", [v for v in mul(16,z,x) if v])
    inv2=[a+b for a,b in zip(inv,z)]
    print("second inverse two-sided", mul(16,x,inv2)==one, mul(16,inv2,x)==one)

if __name__ == '__main__':
    main()
