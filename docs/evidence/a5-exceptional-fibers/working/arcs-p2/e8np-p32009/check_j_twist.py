"""Write j_twist.sing: compare the N+ ideals J and G of header.sing with the N- ones (header of NM_DIR) under t9 -> -t9,
generator by generator, up to sign.  usage: check_j_twist.py NM_DIR"""
import re
import sys
import config

nm = sys.argv[1]


def get(f, name):
    return re.search(r'ideal %s=(.*?);' % name, open(f).read(), re.S).group(1)


Jm, Gm = get(nm + '/header.sing', 'J'), get(nm + '/header.sing', 'G')
Jp, Gp = get('header.sing', 'J'), get('header.sing', 'G')
open('j_twist.sing', 'w').write(f'''// N+ against N- under t9 -> -t9 at p = {config.P}: generator-wise equality up to sign (global dp ordering).
ring r={config.P},(t1,t2,t3,t4,t5,t6,t7,t8,t9),dp;
number I={config.I};
ideal Jm={Jm};
ideal Gm={Gm};
ideal Jp={Jp};
ideal Gp={Gp};
map sg=r,t1,t2,t3,t4,t5,t6,t7,t8,-t9;
ideal Jt=sg(Jm); ideal Gt=sg(Gm);
int k; int plus; int minus; int neither;
plus=0; minus=0; neither=0;
for (k=1;k<=size(Jp);k++) {{ if (Jp[k]-Jt[k]==0) {{ plus++; }} else {{ if (Jp[k]+Jt[k]==0) {{ minus++; }} else {{ neither++; }} }} }}
"J: generators of N+ equal to N-(t9 -> -t9):", plus, " equal to minus that:", minus, " neither:", neither, " of", size(Jp);
plus=0; minus=0; neither=0;
for (k=1;k<=size(Gp);k++) {{ if (Gp[k]-Gt[k]==0) {{ plus++; }} else {{ if (Gp[k]+Gt[k]==0) {{ minus++; }} else {{ neither++; }} }} }}
"G: generators of N+ equal to N-(t9 -> -t9):", plus, " equal to minus that:", minus, " neither:", neither, " of", size(Gp);
quit;
''')
