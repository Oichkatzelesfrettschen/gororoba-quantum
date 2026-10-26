import json,math,numpy as np
from scipy import stats
J=json.load(open("decoded.json"))
th=[k*math.pi/5 for k in range(5)]
T=np.array([[1/5]*5,[2/5*math.cos(2*t) for t in th],[2/5*math.sin(2*t) for t in th],[2/5*math.cos(4*t) for t in th],[2/5*math.sin(4*t) for t in th]])
sg={0:1,1:-1,2:-1,3:1}
def coef(rows,block=True,infl=1.0):
    W=[];z=[];v=[]
    idx={}
    for i,r in enumerate(rows):
        m=r["mode"]; N=sum(m[:4]) if block else sum(m)
        zz=(m[0]-m[3])/N; z.append(zz); v.append(((m[0]+m[3])/N-zz*zz)/N*infl); idx[(r["readout"],r["theta_index"],r["arm"],r["block"].startswith("mutation"))]=i
    W=np.zeros((10,64))
    for q,ro in enumerate(("x","y")):
        for k in range(5):
            for a in range(4):
                i=idx[(ro,k,a,False)]
                W[5*q:5*q+5,i]+=T[:,k]*sg[a]/4
    z=np.array(z); c=W@z; S=(W*np.array(v))@W.T
    return c,S
def gls(c,S,X):
    Si=np.linalg.inv(S); b=np.linalg.solve(X.T@Si@X,X.T@Si@c); r=c-X@b; return float(r@Si@r), b
# designs: params -> coefficients
def lin_design():
    X=np.zeros((10,4))
    X[0,0]=.5;X[1,0]=-.5;X[2,1]=.5   # X0,Xc2 from M11; Xs2 from M12
    X[5,2]=.5;X[6,2]=-.5;X[7,3]=.5   # Y0,Yc2 from M21; Ys2 from M22
    return X
L=lin_design()
G=np.zeros((10,2)); G[:,0]=L[:,0]+L[:,3]; G[:,1]=-L[:,1]+L[:,2]
A=np.hstack([L,np.eye(10)[:,[0]],np.eye(10)[:,[5]]])
for j,rows in J.items():
    c,S=coef(rows)
    print(j,"X0",round(c[0],6),"Ys2",round(c[7],6))
    for lab,X in (("gain",G),("linear",L),("affine",A)):
        q,b=gls(c,S,X); df=10-X.shape[1]
        print(f"  {lab}: chi2 {q:.3f} df {df} p {stats.chi2.sf(q,df):.3g}  inflated by 1.44: chi2 {q/1.44:.1f} p {stats.chi2.sf(q/1.44,df):.2g}")
    # drop the fourth harmonics: affine on the six c0/c2/s2 coefficients only (df 0) -> check that rejection is all in c4/s4?
    keep=[0,1,2,5,6,7]; q,_=gls(c[keep],S[np.ix_(keep,keep)],A[keep]); print("  affine restricted to six non-fourth-harmonic coefficients chi2",round(q,6))
    k4=[3,4,8,9]; q4=float(c[k4]@np.linalg.solve(S[np.ix_(k4,k4)],c[k4])); print("  fourth-harmonic coefficients alone chi2(4)",round(q4,3), "p",stats.chi2.sf(q4,4))
