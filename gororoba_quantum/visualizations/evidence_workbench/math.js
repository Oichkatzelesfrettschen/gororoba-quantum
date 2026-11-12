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
    return {requireValue,finite,interval,simultaneous,blochRegion,completions,constrainedXY,covarianceCell,fraction,normFactor,safeCSV,rotate};
});
