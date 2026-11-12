from audit import ROOT
from pathlib import Path
import subprocess,json,time
b=ROOT/'docs/local/a5-failed-runs/build/arc'
names=','.join([f'T({i})' for i in range(1,13)]+['h','t2','t3','t4','t5','t6','t7','t8'])
Path('normalization-dimension.sing').write_text('ring r=32009,('+names+'),dp; ideal I='+ (b/'norid.txt').read_text()+'; option(redSB); ideal S=std(I); "RESULT normalization_dim",dim(S); quit;')
t=time.monotonic()
try:
 r=subprocess.run(['Singular','-q','--no-rc','normalization-dimension.sing'],stdin=subprocess.DEVNULL,capture_output=True,text=True,timeout=120)
 print(json.dumps({'rc':r.returncode,'seconds':time.monotonic()-t,'stdout':r.stdout,'stderr':r.stderr}))
except subprocess.TimeoutExpired as error:print(json.dumps({'status':'timeout','seconds':120,'stdout':str(error.stdout)}))
