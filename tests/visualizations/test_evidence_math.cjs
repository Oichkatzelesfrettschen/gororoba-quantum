'use strict';
const assert=require('node:assert/strict');
const M=require('../../gororoba_quantum/visualizations/evidence_workbench/math.js');
let checks=0;
function test(name,fn){fn();checks++;console.log('PASS '+name);}
test('zero transverse interval leaves Z unidentified',()=>assert.deepEqual(M.blochRegion([0,0],[0,0]).z,[-1,1]));
test('empty positivity intersection',()=>assert.equal(M.blochRegion([.9,1],[.9,1]).empty,true));
test('outside disk raw point is not clipped',()=>assert.equal(M.completions(1,-.025390625),null));
test('invalid count types',()=>assert.throws(()=>M.simultaneous(true,10,2)));
test('finite safe counts',()=>assert.throws(()=>M.simultaneous(1,Infinity,2)));
test('simultaneous fixed family',()=>assert.ok(Math.abs(M.simultaneous(512,1024,52)[1]-.1221561114790031)<1e-14));
test('invalid interval',()=>assert.throws(()=>M.blochRegion([.5,.2],[0,0])));
test('MLE unchanged interior',()=>assert.deepEqual([M.constrainedXY(6,10,7,10).x,M.constrainedXY(6,10,7,10).y,M.constrainedXY(6,10,7,10).z],[.2-5.551115123125783e-17,.4-1.1102230246251565e-16,null]));
test('symmetric boundary MLE',()=>{const q=M.constrainedXY(10,10,10,10);assert.ok(Math.abs(q.x-Math.SQRT1_2)<1e-14);assert.ok(Math.abs(q.y-Math.SQRT1_2)<1e-14);assert.equal(q.z,null);});
test('raw boundary remains valid',()=>assert.equal(M.constrainedXY(10,10,5,10).changed,false));
test('raw above disk preserved separately',()=>{const q=M.constrainedXY(1024,1024,499,1024);assert.equal(q.changed,true);assert.ok(Math.hypot(q.x,q.y)<=1+1e-15);assert.equal(q.z,null);});
test('unequal-shot optimum is not radial clipping',()=>{const q=M.constrainedXY(100,100,10,10);assert.ok(q.x>q.y);assert.ok(Math.abs(Math.hypot(q.x,q.y)-1)<1e-14);});
test('quadrant symmetry',()=>{const a=M.constrainedXY(20,20,10,10),b=M.constrainedXY(0,20,0,10);assert.ok(Math.abs(a.x+b.x)<1e-14);assert.ok(Math.abs(a.y+b.y)<1e-14);});
test('exact rational norm',()=>assert.equal(M.normFactor({unit_probe_norm_factor_exact:'25/4'},'unit'),6.25));
test('rational bad denominator',()=>assert.throws(()=>M.fraction('1/0')));
test('CSV formula text escaped',()=>assert.equal(M.safeCSV('=1+1'),'"\'=1+1"'));
test('CSV numerical negative not escaped',()=>assert.equal(M.safeCSV(-.5),'"-0.5"'));
test('orthographic rotation preserves norm',()=>{const v=M.rotate([.2,.4,.7],.5,-.7);assert.ok(Math.abs(Math.hypot(...v)-Math.hypot(.2,.4,.7))<1e-14);});
const crypto=require('node:crypto');
const vm=require('node:vm');
const fs=require('node:fs');
const sha=text=>crypto.createHash('sha256').update(text).digest('hex');
const transport=text=>text.replace(/</g,'\\u003c').replace(/>/g,'\\u003e').replace(/&/g,'\\u0026');
const envelope=extra=>'{'+'"schema":"gororoba-evidence-workbench-v1","sources":[],"acquisitions":[],"optical":[],"ramsey":null'+(extra?','+extra:'')+'}\n';
for(const size of [0,1,3,55,56,57,63,64,65,127,128,129,1024,65537]){
    test('portable SHA-256 agrees with Node at '+size+' bytes',()=>{
        const bytes=Uint8Array.from({length:size},(_,i)=>(i*73+19)%256);
        assert.equal(M.sha256Portable(bytes),crypto.createHash('sha256').update(bytes).digest('hex'));
    });
}
test('standard SHA-256 abc vector',()=>assert.equal(M.sha256Portable(new TextEncoder().encode('abc')),'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'));
test('portable digest refuses non-byte input',()=>assert.throws(()=>M.sha256Portable([1,2,3])));
test('HTML escapes reverse without interpreting literal backslashes',()=>{
    const original=JSON.stringify({literal:'\\u003c',tag:'</script>&',two:'\\\\u003e',nested:'\\<',unicode:'μ'})+'\n';
    assert.equal(M.payloadText(transport(original)).text,original);
});
test('number spelling is never canonicalized in the browser',()=>{
    const original=envelope('"numbers":[1.0,-0.0,1e-09,1e+20,1.0000000000000002]');
    assert.equal(M.payloadText(transport(original)).text,original);
});
test('duplicate keys refused',()=>assert.throws(()=>M.parseFrozenJSON('{"a":1,"a":2}'),/Duplicate/));
test('escaped duplicate keys refused',()=>assert.throws(()=>M.parseFrozenJSON('{"a":1,"\\u0061":2}'),/Duplicate/));
test('nested duplicates refused',()=>assert.throws(()=>M.parseFrozenJSON('{"x":[{"k":0,"k":1}]}'),/Duplicate/));
for(const value of ['{"x":NaN}','{"x":Infinity}','{"x":1e999}','[01]','[1,]','{"x":1,}','{"x":+1}','{}{}','"a\nb"','"\\x20"','"\\u00gg"','"unterminated','{"x" 1}','[true false]']){
    test('malformed JSON rejected: '+JSON.stringify(value),()=>assert.throws(()=>M.parseFrozenJSON(value)));
}
test('deep structures refused before stack exhaustion',()=>assert.throws(()=>M.parseFrozenJSON('['.repeat(129)+'0'+']'.repeat(129)),/nesting/));
test('depth boundary accepted',()=>assert.ok(Object.isFrozen(M.parseFrozenJSON('['.repeat(128)+'0'+']'.repeat(128)))));
test('all containers immutable',()=>{const q=M.parseFrozenJSON('{"a":[{"b":2}]}');assert.ok(Object.isFrozen(q.a[0]));assert.throws(()=>{q.a[0].b=7;},TypeError);assert.throws(()=>q.a.push(2),TypeError);});
test('prototype-looking keys remain own data',()=>{const q=M.parseFrozenJSON('{"__proto__":{"polluted":true}}');assert.equal(q.__proto__.polluted,true);assert.equal({}.polluted,undefined);assert.ok(Object.hasOwn(q,'__proto__'));});
test('signed zero and strings preserved',()=>{const q=M.parseFrozenJSON('[null,true,false,-0.0,"\\ud83d\\ude80"]');assert.ok(Object.is(q[3],-0));assert.equal(q[4],String.fromCodePoint(0x1f680));});
test('node budget enforced',()=>assert.throws(()=>M.parseFrozenJSON('['+'0,'.repeat(M.PAYLOAD_LIMITS.nodes)+'0]'),/node budget/));
test('transport budget enforced',()=>assert.throws(()=>M.payloadText(' '.repeat(M.PAYLOAD_LIMITS.bytes+1)),/budget/));
async function asyncTest(name,fn){await fn();checks++;console.log('PASS '+name);}
(async()=>{
    const source=fs.readFileSync(require.resolve('../../gororoba_quantum/visualizations/evidence_workbench/math.js'),'utf8');
    const fallback=vm.createContext({TextEncoder,Uint8Array,Uint32Array,DataView,console});vm.runInContext(source,fallback);
    const native=vm.createContext({TextEncoder,Uint8Array,Uint32Array,DataView,console,crypto:crypto.webcrypto});vm.runInContext(source,native);
    for(const [name,api]of [['fallback',fallback.EvidenceMath],['native',native.EvidenceMath]]){
        await asyncTest(name+' verifies exact Python-compatible bytes',async()=>{
            const text=envelope('"v":[1.0,-0.0,1e-09],"html":"<>&","literal":"\\\\u003c"');
            const q=await api.verifyPayload(transport(text),sha(text));
            assert.equal(q.text,text);assert.equal(q.identity,sha(text));assert.ok(Object.isFrozen(q.data.v));
            assert.equal(q.engine,name==='native'?'WebCrypto SHA-256':'portable SHA-256');
        });
        await asyncTest(name+' rejects a changed count',async()=>{
            const text=envelope('"count":1024');await assert.rejects(api.verifyPayload(transport(text.replace('1024','1023')),sha(text)),/mismatch/);
        });
        await asyncTest(name+' rejects missing digest',async()=>{await assert.rejects(api.verifyPayload(envelope(),''),/SHA-256/);});
        await asyncTest(name+' rejects matching-digest malformed JSON',async()=>{const t=envelope('"x":1,"x":2');await assert.rejects(api.verifyPayload(t,sha(t)),/Duplicate/);});
        await asyncTest(name+' rejects unexpected schema',async()=>{const t=envelope().replace('workbench-v1','workbench-v2');await assert.rejects(api.verifyPayload(t,sha(t)),/envelope/);});
        await asyncTest(name+' detects lost final newline',async()=>{const t=envelope();await assert.rejects(api.verifyPayload(t.trimEnd(),sha(t)),/mismatch/);});
    }
    console.log(JSON.stringify({checks,status:'passed'}));
})().catch(err=>{console.error(err);process.exitCode=1;});
