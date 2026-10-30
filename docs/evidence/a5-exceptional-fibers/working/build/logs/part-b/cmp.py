import sys,pathlib
sys.path.insert(0,'.')
import fiber_cone_driver as d
a,b,n,out=sys.argv[1:5]
h=d.read_header(pathlib.Path(sys.argv[5]),32009)
o=d.run_singular(d.stage_compare(h,int(n),a,b),'cmp',pathlib.Path(out),1,120)
print(o.results,o.error)
