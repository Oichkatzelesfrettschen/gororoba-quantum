load('numlib.sage')
def Fval(a,b,kk,br=0):
    x=arc(a,b,kk,br,2); nu,Fv=leadF(x,2); return nu,Fv
# degree in each variable for component 0..9
for var in range(3):
    pts=[]
    for t in range(2,16):
        args=[5,7,4]; args[var]=t
        nu,Fv=Fval(*args); pts.append((t,Fv,nu))
    print('var',var,'nu',set(n for _,_,n in pts))
    for c in range(10):
        # fit polynomial * (k^2+3)^j via rational reconstruction: use Lagrange on first 8 pts, test rest
        data=[(F(t),Fv[c]) for t,Fv,_ in pts]
        Pl=PolynomialRing(F,'x')
        for den_pow in ([0] if var<2 else [0,1,2,3,4]):
            dd=[(t, v*((t*t+3)**den_pow) if var==2 else v) for t,v in data]
            poly=Pl.lagrange_polynomial(dd[:10])
            if all(poly(t)==v for t,v in dd[10:]):
                print(' comp',c,'deg',poly.degree(),'den_pow',den_pow); break
        else: print(' comp',c,'no fit')
