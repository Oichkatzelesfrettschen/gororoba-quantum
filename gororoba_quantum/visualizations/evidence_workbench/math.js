/* Numerical display contracts. No DOM, acquisition, randomness or hidden fit. */
(function (root, factory) {
    'use strict';
    const api = factory();
    if (typeof module === 'object' && module.exports) module.exports = api;
    else root.EvidenceMath = api;
})(globalThis, function () {
    'use strict';
    function requireValue(ok, message) { if (!ok) throw new Error(message); }
    function finite(x) { return typeof x === 'number' && Number.isFinite(x); }
    function interval(a) {
        requireValue(Array.isArray(a) && a.length === 2 && a.every(finite)
            && -1 <= a[0] && a[0] <= a[1] && a[1] <= 1, 'Invalid expectation interval');
        return a;
    }
    function simultaneous(k, n, familySize, alpha = 0.05) {
        requireValue(Number.isSafeInteger(k) && Number.isSafeInteger(n) && n > 0 && k >= 0 && k <= n, 'Invalid counts');
        requireValue(Number.isSafeInteger(familySize) && familySize > 0 && finite(alpha) && alpha > 0 && alpha < 1, 'Invalid family');
        const x = 2 * k / n - 1, h = Math.sqrt(2 * Math.log(2 * familySize / alpha) / n);
        return [Math.max(-1, x - h), Math.min(1, x + h)];
    }
    function blochRegion(x, y) {
        interval(x); interval(y);
        const near = a => Math.max(a[0], Math.min(0, a[1]));
        const r = Math.hypot(near(x), near(y));
        if (r > 1) return {empty: true, z: null, minimumTransverseRadius: r};
        const z = Math.sqrt(Math.max(0, (1 - r) * (1 + r)));
        return {empty: false, z: [-z, z], minimumTransverseRadius: r};
    }
    function completions(x, y) {
        requireValue(finite(x) && finite(y), 'Invalid transverse coordinate');
        const r = Math.hypot(x, y);
        return r > 1 ? null : [-Math.sqrt(Math.max(0, (1-r)*(1+r))), Math.sqrt(Math.max(0, (1-r)*(1+r)))];
    }
    function logBinomial(k, n, expectation) {
        const p = (1 + expectation) / 2;
        if (p < 0 || p > 1) return -Infinity;
        return (k ? k * Math.log(p) : 0) + (n-k ? (n-k) * Math.log1p(-p) : 0);
    }
    function constrainedXY(kx, nx, ky, ny) {
        // Maximization on the transverse disk only. Z remains unidentified.
        simultaneous(kx, nx, 1); simultaneous(ky, ny, 1);
        const rx = 2*kx/nx-1, ry = 2*ky/ny-1;
        const score = (x,y) => logBinomial(kx,nx,x) + logBinomial(ky,ny,y);
        if (Math.hypot(rx,ry) <= 1) return {x:rx,y:ry,z:null,changed:false,logLikelihood:score(rx,ry),lambda:0};
        function axis(raw,n,lambda) {
            const a = Math.abs(raw);
            if (a === 0) return 0;
            if (a === 1 && lambda <= n/2) return Math.sign(raw);
            let lo = 0, hi = a;
            for (let i=0;i<80;i++) {
                const t=(lo+hi)/2;
                const derivative = a === 1 ? n/(1+t)-lambda*t : n*(a-t)/(1-t*t)-lambda*t;
                if (derivative > 0) lo=t; else hi=t;
            }
            return Math.sign(raw)*(lo+hi)/2;
        }
        const coordinates = lambda => [axis(rx,nx,lambda),axis(ry,ny,lambda)];
        let lo=0,hi=Math.max(nx,ny);
        for (let i=0;Math.hypot(...coordinates(hi))>1;i++) {
            requireValue(i<64,'Constrained estimator failed to bracket'); hi*=2;
        }
        for (let i=0;i<80;i++) {
            const mid=(lo+hi)/2;
            if (Math.hypot(...coordinates(mid))>1) lo=mid; else hi=mid;
        }
        const [x,y]=coordinates(hi);
        return {x,y,z:null,changed:true,logLikelihood:score(x,y),lambda:hi};
    }
    function covarianceCell(pub, diagnostics, event, metric, i, j) {
        const group=pub[event], derived=diagnostics[event], n=pub.shots;
        requireValue(group && derived && i>=0 && j>=0 && i<group.members.length && j<group.members.length,'Invalid matrix cell');
        const a=derived.joint_counts[i][i],b=derived.joint_counts[j][j],both=derived.joint_counts[i][j];
        const value=metric==='correlation'?derived.correlation[i][j]:metric==='joint'?both/n:group.covariance[i][j];
        return {value,counts:[n-a-b+both,b-both,a-both,both],n,left:group.members[i],right:group.members[j],
            undefinedReason:value===null?'Correlation is undefined for a constant event.':null};
    }
    function fraction(text) {
        requireValue(typeof text==='string' && text.length<=128 && /^[+-]?\d+(?:\/[+-]?\d+)?$/.test(text),'Invalid rational');
        const [n,d=1]=text.split('/').map(Number);
        requireValue(finite(n)&&finite(d)&&d!==0,'Invalid rational denominator');
        return n/d;
    }
    function normFactor(metadata, mode) {
        if (mode==='probability') return 1;
        return fraction(metadata[mode==='unit'?'unit_probe_norm_factor_exact':'unnormalized_probe_norm_factor_exact']);
    }
    function safeCSV(value) {
        const text=value===null||value===undefined?'':String(value);
        const safe=typeof value==='string'&&/^[=+\-@\t\r]/.test(text)?"'"+text:text;
        return '"'+safe.replace(/"/g,'""')+'"';
    }
    function rotate(v,yaw,pitch) {
        const u=Math.cos(yaw)*v[0]-Math.sin(yaw)*v[1];
        const w=Math.sin(yaw)*v[0]+Math.cos(yaw)*v[1];
        return [u,Math.cos(pitch)*v[2]-Math.sin(pitch)*w,Math.sin(pitch)*v[2]+Math.cos(pitch)*w];
    }
    // Undo only the renderer's three HTML escapes. JSON spelling, including
    // 1.0, -0.0, exponents, escaped backslashes and the final newline, is retained.
    const PAYLOAD_LIMITS = Object.freeze({bytes:64*1024*1024,depth:128,nodes:1000000});
    function payloadText(transport) {
        requireValue(typeof transport==='string' && transport.length<=PAYLOAD_LIMITS.bytes,
            'Embedded payload exceeds the text budget');
        const decoded=transport.replace(/\\(?:["\\/bfnrt]|u[0-9a-fA-F]{4})/g,
            token=>({'\\u003c':'<','\\u003e':'>','\\u0026':'&'}[token]??token));
        const bytes=new TextEncoder().encode(decoded);
        requireValue(bytes.length<=PAYLOAD_LIMITS.bytes,'Embedded payload exceeds the byte budget');
        return {text:decoded,bytes};
    }
    function sha256Portable(bytes) {
        requireValue(bytes instanceof Uint8Array && bytes.length<=PAYLOAD_LIMITS.bytes,'Invalid digest input');
        const k=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
            0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
            0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
            0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
            0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
            0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
            0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
            0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
        const hash=new Uint32Array([0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19]);
        const padded=new Uint8Array(Math.ceil((bytes.length+9)/64)*64);
        padded.set(bytes);padded[bytes.length]=128;
        const data=new DataView(padded.buffer),bits=bytes.length*8;
        data.setUint32(padded.length-8,Math.floor(bits/0x100000000));
        data.setUint32(padded.length-4,bits>>>0);
        const w=new Uint32Array(64),rotr=(x,n)=>(x>>>n)|(x<<(32-n));
        for(let offset=0;offset<padded.length;offset+=64){
            for(let i=0;i<16;i++)w[i]=data.getUint32(offset+4*i);
            for(let i=16;i<64;i++){
                const x=w[i-15],y=w[i-2];
                w[i]=(w[i-16]+(rotr(x,7)^rotr(x,18)^(x>>>3))+w[i-7]+(rotr(y,17)^rotr(y,19)^(y>>>10)))>>>0;
            }
            let [a,b,c,d,e,f,g,h]=hash;
            for(let i=0;i<64;i++){
                const t1=(h+(rotr(e,6)^rotr(e,11)^rotr(e,25))+((e&f)^(~e&g))+k[i]+w[i])>>>0;
                const t2=((rotr(a,2)^rotr(a,13)^rotr(a,22))+((a&b)^(a&c)^(b&c)))>>>0;
                h=g;g=f;f=e;e=(d+t1)>>>0;d=c;c=b;b=a;a=(t1+t2)>>>0;
            }
            [a,b,c,d,e,f,g,h].forEach((v,i)=>{hash[i]=(hash[i]+v)>>>0;});
        }
        return Array.from(hash,v=>v.toString(16).padStart(8,'0')).join('');
    }
    function parseFrozenJSON(text) {
        // Bounded parser rejects duplicate names before freezing each container.
        // Scientific schema and acquisition validation remain the builder's job.
        requireValue(typeof text==='string' && text.length<=PAYLOAD_LIMITS.bytes,'JSON exceeds text budget');
        let pos=0,nodes=0;
        const ws=()=>{while(pos<text.length && /[ \t\n\r]/.test(text[pos]))pos++;};
        function string(){
            const start=pos;requireValue(text[pos++]==='"','Expected JSON string');
            while(pos<text.length){
                const ch=text[pos++];
                if(ch==='"')return JSON.parse(text.slice(start,pos));
                requireValue(ch.charCodeAt(0)>=32,'Control character in JSON string');
                if(ch==='\\'){
                    const esc=text[pos++];
                    requireValue(typeof esc==='string' && '"\\/bfnrtu'.includes(esc),'Invalid JSON escape');
                    if(esc==='u'){
                        requireValue(/^[0-9a-fA-F]{4}$/.test(text.slice(pos,pos+4)),'Invalid Unicode escape');pos+=4;
                    }
                }
            }
            throw new Error('Unterminated JSON string');
        }
        function value(depth){
            requireValue(++nodes<=PAYLOAD_LIMITS.nodes,'JSON exceeds node budget');ws();
            const ch=text[pos];
            if(ch==='{'||ch==='['){
                requireValue(depth<PAYLOAD_LIMITS.depth,'JSON exceeds nesting budget');
                const object=ch==='{',out=object?{}:[],end=object?'}':']',keys=new Set();pos++;ws();
                if(text[pos]===end){pos++;return Object.freeze(out);}
                for(;;){
                    if(object){
                        ws();const key=string();requireValue(!keys.has(key),'Duplicate JSON key: '+key);keys.add(key);
                        ws();requireValue(text[pos++]===':','Expected JSON colon');
                        Object.defineProperty(out,key,{value:value(depth+1),enumerable:true,writable:false,configurable:false});
                    }else out.push(value(depth+1));
                    ws();const next=text[pos++];if(next===end)return Object.freeze(out);
                    requireValue(next===',','Expected JSON separator');
                }
            }
            if(ch==='"')return string();
            for(const [token,result]of [['true',true],['false',false],['null',null]]){
                if(text.startsWith(token,pos)){pos+=token.length;return result;}
            }
            const number=/-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/y;
            number.lastIndex=pos;const found=number.exec(text);
            requireValue(found!==null,'Invalid JSON value');pos=number.lastIndex;
            const result=Number(found[0]);requireValue(Number.isFinite(result),'Non-finite JSON number');return result;
        }
        const result=value(0);ws();requireValue(pos===text.length,'Trailing JSON content');return result;
    }
    async function verifyPayload(transport,identity) {
        requireValue(typeof identity==='string' && /^[0-9a-f]{64}$/.test(identity),'Invalid payload SHA-256');
        const recovered=payloadText(transport);
        let actual,engine;
        if(globalThis.crypto?.subtle){
            const digest=await globalThis.crypto.subtle.digest('SHA-256',recovered.bytes);
            actual=Array.from(new Uint8Array(digest),v=>v.toString(16).padStart(2,'0')).join('');engine='WebCrypto SHA-256';
        }else{actual=sha256Portable(recovered.bytes);engine='portable SHA-256';}
        requireValue(actual===identity,'Embedded payload SHA-256 mismatch; visualization withheld');
        const data=parseFrozenJSON(recovered.text);
        requireValue(data && data.schema==='gororoba-evidence-workbench-v1'
            && Array.isArray(data.sources) && Array.isArray(data.acquisitions) && Array.isArray(data.optical)
            && (data.ramsey===null || (data.ramsey && Array.isArray(data.ramsey.rows))),
            'Invalid workbench envelope');
        return Object.freeze({data,text:recovered.text,identity:actual,engine,bytes:recovered.bytes.length});
    }
    return {PAYLOAD_LIMITS,payloadText,sha256Portable,parseFrozenJSON,verifyPayload,requireValue,finite,interval,simultaneous,blochRegion,completions,constrainedXY,covarianceCell,fraction,normFactor,safeCSV,rotate};
});
