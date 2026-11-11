/* Offline evidence UI: input validation belongs to the source-bound builder. */
(function () {
    'use strict';
    const $ = id => document.getElementById(id), M = window.EvidenceMath;
    const D = JSON.parse($('payload').textContent), identity = $('payloadIdentity').textContent;
    const NS = 'http://www.w3.org/2000/svg', svg = $('plot');
    const state = {view:'ramsey',index:0,acquisition:0,pub:0,member:'',cohort:0,predictor:'',condition:'all',qubit:'all',delay:'all',geometry:'xy',extent:'detail',uncertainty:true,mle:false,yaw:-30,pitch:25,event:'event_zero',metric:'covariance',sector:'',probe:'',norm:'probability',opticalMode:'scatter',color:'condition',theme:'light',exact:true,preparation:false,replay:false,memberFilter:''};
    const views=['ramsey','dependence','blocks','members','rank','optical','provenance'];
    let renderedRows=[],csvHeaders=[],csvRows=[],context={},timer=null,lastTableKey=null,framePending=false;
    const fmt=(x,n=5)=>x===null||x===undefined?'unavailable':Number(x).toFixed(n);
    const make=(tag,attrs={},text)=>{const e=document.createElementNS(NS,tag);Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,String(v)));if(text!==undefined)e.textContent=String(text);return e;};
    const html=(tag,text)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=String(text);return e;};
    function palette(){const dark=state.theme==='dark';return {bg:dark?'#192330':'#ffffff',ink:dark?'#edf2fa':'#192638',muted:dark?'#b5c3d7':'#47586e',grid:dark?'#415065':'#ccd4e0',colors:dark?['#9ac5ff','#ffbb80','#b3d4a2','#e6b6ed']:['#245ba4','#9e4900','#326735','#7b3e85'],selected:dark?'#edf2fa':'#192638'};}
    function announce(message){$('status').textContent=message;}
    function error(err){$('error').hidden=false;$('error').textContent=String(err);}
    function options(id,rows,value){const e=$(id);e.replaceChildren();for(const [v,label] of rows){const option=html('option',label);option.value=String(v);e.append(option);}e.value=String(value);if(!e.value&&e.options.length)e.selectedIndex=0;return e.value;}
    function inspect(title,value){$('selectedSummary').textContent=title;$('record').textContent=JSON.stringify(value,null,2);}
    function note(title,scope,legend){$('plotTitle').textContent=title;$('scope').textContent=scope;$('legend').textContent=legend;context={view:state.view,title,scope,legend,bundle_sha256:identity,revision:D.revision,state:{...state},sources:D.sources};svg.replaceChildren(make('title',{},title),make('desc',{},scope+' '+legend),make('rect',{width:900,height:600,fill:palette().bg}));}
    function text(x,y,t,extra={}){const width=svg.getBoundingClientRect().width||900,base=Number(extra['font-size']||13),scale=Math.max(1,900/width);const attrs={x,y,fill:palette().ink,'font-family':'system-ui,sans-serif',...extra,'font-size':base*scale,'data-base-size':base};svg.append(make('text',attrs,t));}
    function line(x1,y1,x2,y2,extra={}){svg.append(make('line',{x1,y1,x2,y2,stroke:palette().grid,'stroke-width':1,...extra}));}
    function axes(xrange,yrange,xlabel,ylabel,equal=false){
        let [xl,xh]=xrange,[yl,yh]=yrange;const narrow=svg.getBoundingClientRect().width<600,left=narrow?120:80,right=865,top=narrow?70:42,bottom=515;
        if(xh===xl){xl-=.5;xh+=.5;}if(yh===yl){yl-=.5;yh+=.5;}
        if(equal){const unit=Math.min((right-left)/(xh-xl),(bottom-top)/(yh-yl));const cx=(xl+xh)/2,cy=(yl+yh)/2;xl=cx-(right-left)/unit/2;xh=cx+(right-left)/unit/2;yl=cy-(bottom-top)/unit/2;yh=cy+(bottom-top)/unit/2;}
        const px=x=>left+(x-xl)/(xh-xl)*(right-left),py=y=>bottom-(y-yl)/(yh-yl)*(bottom-top);
        const clip=make('clipPath',{id:'plotClip'});clip.append(make('rect',{x:left,y:top,width:right-left,height:bottom-top}));const defs=make('defs');defs.append(clip);svg.append(defs);
        for(let i=0;i<=4;i++){const x=xl+(xh-xl)*i/4,y=yl+(yh-yl)*i/4;line(left,py(y),right,py(y));text(left-10,py(y)+4,fmt(y,narrow?2:3),{'text-anchor':'end'});text(px(x),bottom+22,fmt(x,narrow?2:3),{'text-anchor':'middle'});}
        text((left+right)/2,580,narrow?xlabel.replace(' (dimensionless)','').replace(' (retained register order)','').replace(' (block center)',''):xlabel,{'text-anchor':'middle'});text(left,narrow?40:23,narrow?ylabel.replace('Reference geometry, no physical distance implied','Projected display v').replace('Observed minus frozen prediction','Observation - prediction'):ylabel,{'font-weight':600});
        return {px,py,left,right,top,bottom,xl,xh,yl,yh};
    }
    function ranges(values,pad=.08){if(!values.length)return [0,1];const lo=Math.min(...values),hi=Math.max(...values),d=(hi-lo)||Math.max(1,Math.abs(lo))*.1;return [lo-pad*d,hi+pad*d];}
    function table(headers,rows,select){csvHeaders=headers;csvRows=rows;const key=JSON.stringify([headers,rows,Boolean(select),$('plotTitle').textContent]);if(key===lastTableKey)return;lastTableKey=key;const t=html('table'),caption=html('caption',$('plotTitle').textContent),head=html('thead'),tr=html('tr');if(select)tr.append(html('th','Select'));for(const h of headers)tr.append(html('th',h));head.append(tr);const body=html('tbody');rows.forEach((row,i)=>{const r=html('tr');if(select){const td=html('td'),b=html('button','Inspect '+(i+1));b.type='button';b.addEventListener('click',()=>select(i));td.append(b);r.append(td);}for(const value of row)r.append(html('td',value===null?'unavailable':String(value)));body.append(r);});t.append(caption,head,body);$('table').replaceChildren(t);}
    function marker(x,y,color,shape=0,open=false,selected=false,callback=null){
        const r=selected?7:5;let e;
        if(shape%4===1)e=make('path',{d:`M${x} ${y-r}L${x+r} ${y}L${x} ${y+r}L${x-r} ${y}Z`});
        else if(shape%4===2)e=make('rect',{x:x-r,y:y-r,width:2*r,height:2*r});
        else if(shape%4===3)e=make('path',{d:`M${x} ${y-r-1}L${x+r} ${y+r}L${x-r} ${y+r}Z`});
        else e=make('circle',{cx:x,cy:y,r});
        e.setAttribute('fill',open?palette().bg:color);e.setAttribute('stroke',color);e.setAttribute('stroke-width',2);e.setAttribute('clip-path','url(#plotClip)');
        if(callback){e.style.cursor='pointer';e.addEventListener('click',callback);}svg.append(e);
        if(selected)svg.append(make('circle',{cx:x,cy:y,r:r+5,fill:'none',stroke:palette().selected,'stroke-width':1.5,'clip-path':'url(#plotClip)'}));
        return e;
    }
    function missing(message){note('Unavailable in this bundle',message,'No substitute or synthetic observation is drawn.');text(450,270,message,{'text-anchor':'middle','font-size':16});table(['Status'],[[message]]);inspect('Evidence not supplied',{message});renderedRows=[];}
    function ramseyRows(){return (D.ramsey?.rows||[]).filter(p=>(state.condition==='all'||p.condition===state.condition)&&(state.qubit==='all'||String(p.qubit)===state.qubit)&&(state.delay==='all'||String(p.t)===state.delay));}
    function ramseyColor(p){if(state.color==='monochrome')return palette().ink;const all=D.ramsey.rows;const vals=[...new Set(all.map(x=>state.color==='qubit'?x.qubit:x.condition))];return palette().colors[vals.indexOf(state.color==='qubit'?p.qubit:p.condition)%4];}
    function selectIndex(i){state.index=i;render();}
    function ramsey(){
        if(!D.ramsey)return missing('No Ramsey count table is embedded.');
        const rows=ramseyRows(),all=D.ramsey.rows;renderedRows=rows;state.index=Math.min(state.index,Math.max(0,rows.length-1));
        if(!rows.length)return missing('The selected filters contain no acquired setting.');
        const selected=rows[state.index],family=D.ramsey.coordinate_family_size;
        note(state.geometry==='xy'?'Measured transverse expectations':state.geometry==='bloch'?'Bloch-compatible expectation set':'X/Y/delay setting space',
            `Raw count estimates remain unchanged. The coordinate family contains ${family} estimates. `+(state.geometry==='bloch'?'The sphere and compatibility set are mathematical constraints, not measured Z or a state trajectory.':'X and Y use separately prepared circuits. Delay is an experimental setting.'),
            'Condition uses shape; qubit uses filled/open markers. The selection ring is independent. Rectangular bounds are 95% simultaneous Hoeffding bounds under stationary independent shots within each circuit; they are not the registered endpoint tests.');
        const conditions=[...new Set(all.map(p=>p.condition))],qubits=[...new Set(all.map(p=>p.qubit))];
        const key=conditions.map((c,i)=>['circle','diamond','square','triangle'][i%4]+' = '+c).join('; ')+'; '+qubits.map((q,i)=>(i%2?'open':'filled')+' = Q'+q).join('; ');
        const assumption='Physical compatibility and likelihood overlays assume a common prepared state and calibrated Pauli readout. The statistical bounds alone cover circuit outcome means, not unknown readout bias.';
        $('legend').textContent+=' '+key+' '+assumption;context.legend=$('legend').textContent;
        const choose=i=>()=>selectIndex(i);
        if(state.geometry==='xy'){
            const use=state.uncertainty?all.flatMap(p=>[...p.simultaneous_x]):all.map(p=>p.x),ys=state.uncertainty?all.flatMap(p=>p.simultaneous_y):all.map(p=>p.y);
            const a=axes(state.extent==='full'?[-1.1,1.1]:ranges(use),state.extent==='full'?[-1.1,1.1]:ranges(ys),'X expectation (dimensionless)','Y expectation (dimensionless)',true);
            svg.append(make('circle',{cx:a.px(0),cy:a.py(0),r:Math.abs(a.px(1)-a.px(0)),fill:'none',stroke:palette().muted,'stroke-dasharray':'5 5','clip-path':'url(#plotClip)'}));
            if(state.uncertainty){const x=selected.simultaneous_x,y=selected.simultaneous_y;svg.append(make('rect',{x:a.px(x[0]),y:a.py(y[1]),width:a.px(x[1])-a.px(x[0]),height:a.py(y[0])-a.py(y[1]),fill:'none',stroke:palette().muted,'stroke-width':1.5,'stroke-dasharray':'3 3','clip-path':'url(#plotClip)'}));}
            rows.forEach((p,i)=>{const e=marker(a.px(p.x),a.py(p.y),ramseyColor(p),conditions.indexOf(p.condition),qubits.indexOf(p.qubit)%2===1,i===state.index,choose(i));e.append(make('title',{},`${p.condition}; Q${p.qubit}; delay ${p.t} us; X=${p.x}; Y=${p.y}`));});
            if(state.mle){const q=M.constrainedXY(selected.kx,selected.nx,selected.ky,selected.ny);marker(a.px(q.x),a.py(q.y),palette().ink,1,true,false);text(a.left,a.bottom+45,'Open diamond: constrained X/Y likelihood estimate, not an extra observation.');}
        }else{
            const tx=ranges(all.map(p=>p.t),0),xr=ranges(all.map(p=>p.x)),yr=ranges(all.map(p=>p.y)),half=Math.max(xr[1]-xr[0],yr[1]-yr[0])/2;
            const settingTransform=p=>[(p.x-(xr[0]+xr[1])/2)/half,(p.y-(yr[0]+yr[1])/2)/half,2*(p.t-tx[0])/(tx[1]-tx[0]||1)-1];
            const rotate=v=>M.rotate(v,state.yaw*Math.PI/180,state.pitch*Math.PI/180);
            const fullSetting=all.map(settingTransform).concat([[0,0,0],[1,0,0],[0,1,0],[0,0,1]]).map(rotate);
            const displayX=state.geometry==='setting'?ranges(fullSetting.map(v=>v[0]),.18):[-1.22,1.22];
            const displayY=state.geometry==='setting'?ranges(fullSetting.map(v=>v[1]),.18):[-1.22,1.22];
            const a=axes(displayX,displayY,'Orthographic display coordinate','Reference geometry, no physical distance implied',true);
            const camera=v=>{const q=rotate(v);return [a.px(q[0]),a.py(q[1])];};
            const path=(vs,color,dash='')=>{svg.append(make('polyline',{points:vs.map(v=>camera(v).join(',')).join(' '),fill:'none',stroke:color,'stroke-width':1,'stroke-dasharray':dash,'clip-path':'url(#plotClip)'}));};
            if(state.geometry==='bloch'){
                for(let axis=0;axis<3;axis++){const vs=Array.from({length:97},(_,i)=>{const t=i*Math.PI/48,v=[0,0,0];v[(axis+1)%3]=Math.cos(t);v[(axis+2)%3]=Math.sin(t);return v;});path(vs,palette().grid);}
                [[1,0,0,'X'],[0,1,0,'Y'],[0,0,1,'Z: unmeasured']].forEach(v=>{path([[0,0,0],v.slice(0,3)],palette().muted);const p=camera(v.slice(0,3));text(p[0]+5,p[1]-7,v[3]);});
                if(state.uncertainty){const [xl,xh]=selected.simultaneous_x,[yl,yh]=selected.simultaneous_y;for(let i=0;i<=14;i++){const x=xl+(xh-xl)*i/14,upper=[],lower=[];for(let j=0;j<=28;j++){const y=yl+(yh-yl)*j/28,z=M.completions(x,y);if(z){upper.push([x,y,z[1]]);lower.push([x,y,z[0]]);}}if(upper.length>1){path(upper,palette().colors[0]);path(lower,palette().colors[0]);}}}
                const z=M.completions(selected.x,selected.y);if(z)path([[selected.x,selected.y,z[0]],[selected.x,selected.y,z[1]]],palette().selected,'4 3');
                rows.forEach((p,i)=>{const q=camera([p.x,p.y,0]);marker(q[0],q[1],ramseyColor(p),conditions.indexOf(p.condition),qubits.indexOf(p.qubit)%2===1,i===state.index,choose(i));});
                text(a.left,a.bottom+45,'Plane markers project X/Y; none asserts Z = 0. Surface lines bound possible states.');
            }else{
                const transform=settingTransform;
                [[1,0,0,'X'],[0,1,0,'Y'],[0,0,1,'Executed delay (us)']].forEach(v=>{path([[0,0,0],v.slice(0,3)],palette().muted);const p=camera(v.slice(0,3));text(p[0]+5,p[1]-7,v[3]);});
                rows.forEach((p,i)=>{const q=camera(transform(p));marker(q[0],q[1],ramseyColor(p),conditions.indexOf(p.condition),qubits.indexOf(p.qubit)%2===1,i===state.index,choose(i));});
                text(a.left,a.bottom+45,`Delay range ${tx[0]} to ${tx[1]} us; independent display scaling, no interpolated motion.`);
            }
        }
        table(['Condition','Qubit','Delay us','X zeros','NX','Y zeros','NY','X','Y','R transverse'],rows.map(p=>[p.condition,p.qubit,p.t,p.kx,p.nx,p.ky,p.ny,p.x,p.y,p.r]),selectIndex);
        inspect(`${selected.condition} / Q${selected.qubit} / ${selected.t} us`,{...selected,constrained_xy:state.mle?M.constrainedXY(selected.kx,selected.nx,selected.ky,selected.ny):'not displayed',compatible_z_projection:state.uncertainty?M.blochRegion(selected.simultaneous_x,selected.simultaneous_y):'not displayed',interpretation:'Z projection describes an admissible set under the stated coordinate coverage, not a measured Z interval.'});
    }
    function active(){return D.acquisitions[state.acquisition]||null;}
    function selectedPub(){const a=active();return a?.payload.pubs[state.pub]||null;}
    function sourceLabel(){const a=active();return a?.payload.evidence_kind==='synthetic_fixture'?'SYNTHETIC FIXTURE / NO HARDWARE EVIDENCE':'RETAINED HARDWARE COUNTS';}
    function memberList(){const a=active(),p=selectedPub();if(!a||!p)return [];const q=state.memberFilter.toLowerCase();return Object.entries(a.payload.members).filter(([name,v])=>v.job_id===p.job_id&&v.pub===p.name&&name.toLowerCase().includes(q));}
    function selectMember(name){state.member=name;$('member').value=name;render();}
    function syncAcquisition(){const a=active();if(!a)return;state.pub=Math.min(state.pub,a.payload.pubs.length-1);options('pub',a.payload.pubs.map((p,i)=>[i,`${p.job_id} / ${p.name} / ${p.shots} shots`]),state.pub);const members=memberList();state.member=options('member',members.map(([name])=>[name,name]),state.member);}
    function dependence(){
        const a=active(),p=selectedPub();if(!a||!p)return missing('No portable acquisition is embedded.');
        const group=p[state.event],diagnostic=a.dependence.find(v=>v.job_id===p.job_id&&v.pub===p.name),names=group.members;
        note(sourceLabel()+' / same-PUB '+state.metric,`${p.job_id} / ${p.name}; ${p.shots} shared returned shot positions. ${a.verification}.`,
            'Descriptive event statistics only. Constant-event correlations are unavailable, not zero. Shared positions are not paired with other PUBs. Dependence does not establish crosstalk causality.');
        if(!names.length){text(450,270,'No deterministic-error events exist in this PUB.',{'text-anchor':'middle'});table(['Status'],[['No eligible events']]);inspect('No error matrix',{pub:p.name,event:state.event});renderedRows=[];return;}
        const size=names.length,cell=Math.min(55,430/size),left=(900-size*cell)/2,top=68,limit=state.metric==='covariance'?.25:1;
        const flat=[];
        for(let i=0;i<size;i++)for(let j=0;j<size;j++)flat.push(M.covarianceCell(p,diagnostic,state.event,state.metric,i,j));
        renderedRows=flat;state.index=Math.min(state.index,flat.length-1);
        for(let i=0;i<size;i++){text(left-12,top+(i+.6)*cell,String(i+1),{'text-anchor':'end'});text(left+(i+.5)*cell,top-12,String(i+1),{'text-anchor':'middle'});for(let j=0;j<size;j++){const idx=i*size+j,v=flat[idx].value,color=v===null?palette().grid:v<0?palette().colors[0]:palette().colors[1],opacity=v===null?.45:.12+.88*Math.min(1,Math.abs(v)/limit);const r=make('rect',{x:left+j*cell,y:top+i*cell,width:cell-2,height:cell-2,fill:color,'fill-opacity':opacity,stroke:idx===state.index?palette().selected:'none','stroke-width':3});r.style.cursor='pointer';r.append(make('title',{},`${names[i]} / ${names[j]}: ${v===null?'undefined':v}`));r.addEventListener('click',()=>selectIndex(idx));svg.append(r);if(size<=10)text(left+(j+.5)*cell,top+(i+.6)*cell,v===null?'NA':fmt(v,3),{'text-anchor':'middle','font-size':11});}}
        text(450,top+size*cell+35,`Fixed scale: ${state.metric==='joint'?'0 to 1':state.metric==='covariance'?'-0.25 to +0.25':'-1 to +1'}; row/column identities are in the table.`,{'text-anchor':'middle'});
        table(['Row member','Column member',state.metric,'N','Neither','Right only','Left only','Both'],flat.map(p=>[p.left,p.right,p.value,p.n,...p.counts]),selectIndex);
        const chosen=flat[state.index];inspect('Selected event pair',{job_id:p.job_id,pub:p.name,event:state.event,metric:state.metric,...chosen,contingency_order:['neither','right only','left only','both'],scope:'within one PUB; no causal or temporal conclusion'});
    }
    function members(){
        const a=active(),m=a?.payload.members[state.member];if(!m)return missing('No member matches the selected PUB and filter.');
        note(sourceLabel()+' / outcome distribution',`${m.job_id} / ${m.pub} / ${state.member}; n=${m.shots}.`,
            'Observed counts use filled circles. Exact, preparation and execution-calibration predictions use separate markers. Model residual uncertainty is not supplied.');
        const width=m.counts.length,ax=axes([-.5,width-.5],[0,1.04],'Classical outcome index (retained register order)','Probability');
        const layers=[['Observed',m.probabilities,0,false],...($('exact').checked?[['Exact',m.ideal_probabilities,1,true]]:[]),...($('preparation').checked?[['Preparation',m.preparation_model.probabilities,2,true]]:[]),...($('replay').checked&&m.execution_replay.status==='calibration_bound'?[['Execution replay',m.execution_replay.probabilities,3,true]]:[])];
        state.index=Math.min(state.index,width-1);for(const [label,values,shape,open] of layers)values.forEach((p,i)=>{const e=marker(ax.px(i),ax.py(p),palette().colors[shape],shape,open,label==='Observed'&&i===state.index,()=>selectIndex(i));e.append(make('title',{},`${label}; outcome ${i}; ${p}`));});
        renderedRows=m.counts.map((k,i)=>({outcome:i,count:k,probability:k/m.shots}));
        table(['Outcome bits','Count','Observed','Exact','Preparation','Execution replay'],m.counts.map((k,i)=>[i.toString(2).padStart(Math.log2(width),'0'),k,k/m.shots,m.ideal_probabilities[i],m.preparation_model.probabilities[i],m.execution_replay.probabilities?.[i]??null]),selectIndex);
        inspect(state.member,{...m,selected_outcome:state.index,selected_count:m.counts[state.index],verification:a.verification});
    }
    function blocks(){
        const a=active(),m=a?.payload.members[state.member];if(!m)return missing('No member matches the selected PUB and filter.');
        note(sourceLabel()+' / returned shot-index blocks',`${m.job_id} / ${m.pub} / ${state.member}; contiguous blocks reproduce the full event-zero count.`,
            'Block centers are returned array indices, not timestamps. No drift test, stationarity claim, or lag-time interpretation is assigned.');
        const b=m.shot_order_blocks,ax=axes([0,Math.max(1,m.shots-1)],[0,1],'Returned shot position (block center)','Observed P(outcome = 0)');renderedRows=b;state.index=Math.min(state.index,b.length-1);
        b.forEach((p,i)=>{const x=(p.start_shot+p.stop_shot_exclusive-1)/2;line(ax.px(p.start_shot),ax.py(p.event_zero_probability),ax.px(p.stop_shot_exclusive-1),ax.py(p.event_zero_probability),{stroke:palette().colors[0],'stroke-width':2});marker(ax.px(x),ax.py(p.event_zero_probability),palette().colors[0],0,false,i===state.index,()=>selectIndex(i));});
        line(ax.left,ax.py(m.probabilities[0]),ax.right,ax.py(m.probabilities[0]),{stroke:palette().muted,'stroke-dasharray':'5 5'});
        table(['Start inclusive','Stop exclusive','Shots','Zero count','P0'],b.map(v=>[v.start_shot,v.stop_shot_exclusive,v.shots,Math.round(v.shots*v.event_zero_probability),v.event_zero_probability]),selectIndex);
        inspect('Selected shot-index block',{member:state.member,job_id:m.job_id,pub:m.pub,...b[state.index],scope:'descriptive service-returned index window'});
    }
    function syncRank(){const a=active();if(!a||a.payload.family!=='rank-sector')return;const ms=Object.values(a.payload.members).filter(m=>m.metadata.role==='packed');const sectors=[...new Set(ms.map(m=>m.metadata.sector))].sort((a,b)=>a-b);state.sector=options('sector',sectors.map(v=>[v,'Sector '+v]),state.sector);const probes=[...new Set(ms.filter(m=>String(m.metadata.sector)===state.sector).map(m=>m.metadata.probe))];state.probe=options('probe',probes.map(v=>[v,v]),state.probe);}
    function rank(){
        const a=active();if(!a||a.payload.family!=='rank-sector')return missing('Select an embedded rank-sector acquisition.');
        const rows=Object.entries(a.payload.members).filter(([,m])=>m.metadata.role==='packed'&&String(m.metadata.sector)===state.sector&&m.metadata.probe===state.probe).sort((x,y)=>M.fraction(x[1].metadata.parameter_exact)-M.fraction(y[1].metadata.parameter_exact));
        if(!rows.length)return missing('No rank-sector probe matches the selection.');
        const points=rows.map(([name,m])=>({name,m,t:M.fraction(m.metadata.parameter_exact),factor:M.normFactor(m.metadata,state.norm)})),label=state.norm==='probability'?'LCU success probability':state.norm==='unit'?'Encoded squared norm, unit probe':'Encoded squared norm, unnormalized probe';
        note(sourceLabel()+' / sector '+state.sector,`Probe ${state.probe}. Exact LCU normalization factors are validated as rational identities before rendering.`,
            'Filled circles are measured probabilities multiplied by the declared factor; open diamonds are exact references. These responses do not directly measure rank or topology.');
        const ymax=Math.max(1,...points.map(p=>Math.max(p.m.probabilities[0],p.m.ideal_probabilities[0])*p.factor))*1.08,ax=axes(ranges(points.map(p=>p.t)),[0,ymax],'Exact path parameter t',label);renderedRows=points;state.index=Math.min(state.index,points.length-1);
        points.forEach((p,i)=>{marker(ax.px(p.t),ax.py(p.m.ideal_probabilities[0]*p.factor),palette().colors[1],1,true);marker(ax.px(p.t),ax.py(p.m.probabilities[0]*p.factor),palette().colors[0],0,false,i===state.index,()=>selectIndex(i));});
        table(['Member','Exact t','Factor','Shots','Observed P0','Scaled observation','Scaled exact'],points.map(p=>[p.name,p.m.metadata.parameter_exact,p.factor,p.m.shots,p.m.probabilities[0],p.m.probabilities[0]*p.factor,p.m.ideal_probabilities[0]*p.factor]),selectIndex);
        inspect(points[state.index].name,{...points[state.index].m.metadata,counts:points[state.index].m.counts,scale:state.norm,applied_factor:points[state.index].factor});
    }
    function syncOptical(){const c=D.optical[state.cohort];if(c)state.predictor=options('predictor',c.prediction_fields.map(v=>[v,v]),state.predictor);}
    function optical(){
        const c=D.optical[state.cohort];if(!c)return missing('No retained optical cohort is embedded.');const rows=c.payload.rows;
        note((c.evidence_kind==='synthetic_fixture'?'SYNTHETIC FIXTURE / NO HARDWARE EVIDENCE / ':'Optical holdout / ')+c.label,`${rows.length} held-out rows; predictor ${state.predictor}. Cohorts remain separate and original decisions are retained.`,
            'No regression or new significance test is fitted on these held-out rows. Residual error bars are withheld without the required covariance.');
        const xs=rows.map(p=>p[state.predictor]),ys=rows.map(p=>state.opticalMode==='scatter'?p.observed:p.observed-p[state.predictor]),range=ranges(xs.concat(state.opticalMode==='scatter'?ys:[])),ax=axes(range,ranges(ys),`Frozen ${state.predictor}`,state.opticalMode==='scatter'?'Observed statistic':'Observed minus frozen prediction');
        if(state.opticalMode==='scatter')line(ax.px(Math.max(ax.xl,ax.yl)),ax.py(Math.max(ax.xl,ax.yl)),ax.px(Math.min(ax.xh,ax.yh)),ax.py(Math.min(ax.xh,ax.yh)),{stroke:palette().muted,'stroke-dasharray':'5 5'});
        else if(ax.yl<=0&&ax.yh>=0)line(ax.left,ax.py(0),ax.right,ax.py(0),{stroke:palette().muted,'stroke-dasharray':'5 5'});
        renderedRows=rows;state.index=Math.min(state.index,rows.length-1);rows.forEach((p,i)=>marker(ax.px(xs[i]),ax.py(ys[i]),state.color==='monochrome'?palette().ink:palette().colors[0],0,false,i===state.index,()=>selectIndex(i)));
        table(['Row','Job','Mesh','Observed',state.predictor,'Residual','Counting variance','Prediction variance'],rows.map((p,i)=>[i,p.job??'not supplied',JSON.stringify(p.mesh),p.observed,p[state.predictor],p.observed-p[state.predictor],p.counting_variance??null,p.prediction_variance??null]),selectIndex);
        inspect('Retained optical row',{cohort:c.label,source_schema:c.payload.schema,primary:c.payload.primary,outcome:c.payload.outcome??c.payload.primary?.reading,row_index:state.index,row:rows[state.index],scope:c.scope});
    }
    function provenance(){
        note('Source identities and validation boundaries','Package identity: '+identity,'A digest verifies bytes relative to a declared manifest, not the truth or authenticity of a scientific claim.');
        text(80,130,`${D.sources.length} source objects / ${D.acquisitions.length} acquisitions / ${D.optical.length} optical cohorts`);
        text(80,175,'No acquisition, inference decision, or source file is edited by this interface.');
        table(['Source name','Evidence kind','Bytes','SHA-256'],D.sources.map(s=>[s.name,s.kind,s.bytes,s.sha256]));
        $('sourceTable').replaceChildren($('table').firstChild.cloneNode(true));
        const data={schema:D.schema,revision:D.revision,bundle_sha256:identity,boundaries:D.boundaries,acquisitions:D.acquisitions.map(a=>({family:a.payload.family,evidence_kind:a.payload.evidence_kind,payload_sha256:a.payload.payload_sha256,verification:a.verification,raw_replays:a.raw_replays?.length??0,boundary:a.boundary??'Source-file and raw-bitstring verification were not requested.'}))};
        $('verification').textContent=JSON.stringify(data,null,2);inspect('Verification scope',data);renderedRows=[];
    }
    function render(){try{
        $('error').hidden=true;
        document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===state.view)));
        $('ramseyControls').hidden=state.view!=='ramsey';const acquisitionView=['dependence','members','blocks','rank'].includes(state.view);$('acquisitionControls').hidden=!acquisitionView;
        $('dependenceControls').hidden=state.view!=='dependence';$('memberControls').hidden=state.view!=='members';$('rankControls').hidden=state.view!=='rank';$('opticalControls').hidden=state.view!=='optical';$('provenance').hidden=state.view!=='provenance';
        const transverse=state.geometry==='xy';
        $('extent').disabled=!transverse;$('mle').disabled=!transverse;
        $('yaw').disabled=transverse;$('pitch').disabled=transverse;
        $('uncertainty').disabled=state.geometry==='setting';
        $('color').closest('label').hidden=!['ramsey','optical'].includes(state.view);
        $('color').querySelector('option[value="qubit"]').disabled=state.view!=='ramsey';
        if(state.view==='optical'&&state.color==='qubit'){state.color='condition';$('color').value='condition';}
        ({ramsey,dependence,members,blocks,rank,optical,provenance}[state.view])();
        $('previous').disabled=renderedRows.length<2;$('next').disabled=renderedRows.length<2;context.state={...state};
        window.__workbenchReady=true;
    }catch(err){window.__workbenchReady=false;error(err);}}
    function stop(){if(timer)clearTimeout(timer);timer=null;$('play').textContent='Play acquired settings';}
    function nextDelay(){if(!D.ramsey)return;const times=[...new Set(D.ramsey.rows.map(p=>p.t))].sort((a,b)=>a-b),i=times.findIndex(t=>String(t)===state.delay);state.delay=String(times[(i+1)%times.length]);$('delay').value=state.delay;state.index=0;render();}
    function download(blob,name){const u=URL.createObjectURL(blob),a=html('a');a.href=u;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),2000);}
    function wrap(s,n){const words=s.split(/\s+/),lines=[];let row='';for(const w of words){if(row.length+w.length+1>n){lines.push(row);row=w;}else row+=(row?' ':'')+w;}if(row)lines.push(row);return lines;}
    function exported(){const p=palette(),notes=[context.scope,context.legend,`Evidence source: ${D.revision}; bundle SHA-256 ${identity}`,`Selected context: ${JSON.stringify(state)}`].flatMap(v=>wrap(v,108));const total=650+notes.length*17,out=make('svg',{xmlns:NS,width:900,height:total,viewBox:`0 0 900 ${total}`});out.append(make('title',{},context.title),make('metadata',{},JSON.stringify(context)),make('rect',{width:900,height:total,fill:p.bg}),make('text',{x:20,y:27,fill:p.ink,'font-size':18,'font-family':'system-ui,sans-serif'},context.title));const clone=svg.cloneNode(true);clone.setAttribute('x','0');clone.setAttribute('y','40');clone.setAttribute('width','900');clone.setAttribute('height','600');clone.removeAttribute('tabindex');clone.querySelectorAll('[data-base-size]').forEach(e=>e.setAttribute('font-size',e.dataset.baseSize));out.append(clone);notes.forEach((t,i)=>out.append(make('text',{x:20,y:655+i*17,fill:p.ink,'font-size':12,'font-family':'system-ui,sans-serif'},t)));return {text:new XMLSerializer().serializeToString(out),height:total};}
    async function exportPNG(){try{const result=exported(),u=URL.createObjectURL(new Blob([result.text],{type:'image/svg+xml'}));try{const image=new Image();await new Promise((resolve,reject)=>{image.onload=resolve;image.onerror=()=>reject(new Error('PNG unavailable; SVG remains available'));image.src=u;});const canvas=document.createElement('canvas');canvas.width=1800;canvas.height=result.height*2;const c=canvas.getContext('2d');M.requireValue(c,'No 2D rasterizer');c.scale(2,2);c.drawImage(image,0,0);const blob=await new Promise(resolve=>canvas.toBlob(resolve,'image/png'));M.requireValue(blob,'PNG serialization failed');download(blob,'evidence-'+state.view+'.png');}finally{URL.revokeObjectURL(u);}}catch(err){error(err);}}
    function saveState(){return {schema:'gororoba-workbench-view-v1',bundle_sha256:identity,state:{...state}};}
    function restore(value){M.requireValue(value?.schema==='gororoba-workbench-view-v1'&&value.bundle_sha256===identity,'Saved view belongs to another source bundle');const candidate=value.state;M.requireValue(candidate&&typeof candidate==='object','Missing view state');const enums={view:views,geometry:['xy','bloch','setting'],extent:['detail','full'],event:['event_zero','deterministic_error'],metric:['covariance','correlation','joint'],norm:['probability','unit','unnormalized'],opticalMode:['scatter','residual'],color:['condition','qubit','monochrome'],theme:['light','dark']};for(const [key,allowed]of Object.entries(enums))M.requireValue(allowed.includes(candidate[key]),'Invalid saved '+key);for(const key of ['index','acquisition','pub','cohort'])M.requireValue(Number.isSafeInteger(candidate[key])&&candidate[key]>=0&&candidate[key]<=100000,'Invalid saved index');for(const key of ['yaw','pitch'])M.requireValue(M.finite(candidate[key])&&Math.abs(candidate[key])<=180,'Invalid camera');for(const key of ['uncertainty','mle','exact','preparation','replay'])M.requireValue(typeof candidate[key]==='boolean','Invalid display flag');for(const key of ['condition','qubit','delay','member','sector','probe','predictor','memberFilter'])M.requireValue(typeof candidate[key]==='string'&&candidate[key].length<=512,'Invalid saved selector');M.requireValue(!D.acquisitions.length||candidate.acquisition<D.acquisitions.length,'Acquisition index outside bundle');M.requireValue(!D.optical.length||candidate.cohort<D.optical.length,'Cohort index outside bundle');const all=D.ramsey?.rows||[];for(const key of ['condition','qubit','delay'])M.requireValue(candidate[key]==='all'||all.some(p=>String(p[key==='delay'?'t':key])===candidate[key]),'Saved filter is not in the source cohort');stop();for(const key of Object.keys(state))state[key]=candidate[key];syncControls();render();announce('Source-bound view restored.');}
    function syncControls(){document.documentElement.dataset.theme=state.theme;for(const key of ['condition','qubit','delay','geometry','extent','yaw','pitch','event','metric','norm','opticalMode','color','acquisition','cohort'])$(key).value=String(state[key]);for(const key of ['uncertainty','mle','exact','preparation','replay'])$(key).checked=state[key];$('memberFilter').value=state.memberFilter;syncAcquisition();syncRank();syncOptical();}
    document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>{stop();state.view=b.dataset.view;state.index=0;if(state.view==='rank'&&active()?.payload.family!=='rank-sector'){const i=D.acquisitions.findIndex(a=>a.payload.family==='rank-sector');if(i>=0){state.acquisition=i;$('acquisition').value=String(i);state.pub=0;syncAcquisition();}}syncRank();render();}));
    for(const key of ['condition','qubit','delay','geometry','extent','event','metric','norm','opticalMode','color'])$(key).addEventListener('change',()=>{stop();state[key]=$(key).value;state.index=0;render();});
    for(const key of ['uncertainty','mle','exact','preparation','replay'])$(key).addEventListener('change',()=>{state[key]=$(key).checked;render();});
    function scheduleRender(){if(!framePending){framePending=true;requestAnimationFrame(()=>{framePending=false;render();});}}
    for(const key of ['yaw','pitch'])$(key).addEventListener('input',()=>{state[key]=Number($(key).value);scheduleRender();});
    window.addEventListener('resize',scheduleRender);
    $('acquisition').addEventListener('change',()=>{state.acquisition=Number($('acquisition').value);state.pub=0;state.index=0;state.member='';syncAcquisition();syncRank();render();});
    $('pub').addEventListener('change',()=>{state.pub=Number($('pub').value);state.index=0;state.member='';syncAcquisition();render();});
    $('memberFilter').addEventListener('input',()=>{state.memberFilter=$('memberFilter').value;syncAcquisition();render();});$('member').addEventListener('change',()=>{state.member=$('member').value;state.index=0;render();});
    $('sector').addEventListener('change',()=>{state.sector=$('sector').value;state.probe='';state.index=0;syncRank();render();});$('probe').addEventListener('change',()=>{state.probe=$('probe').value;state.index=0;render();});
    $('cohort').addEventListener('change',()=>{state.cohort=Number($('cohort').value);state.index=0;syncOptical();render();});$('predictor').addEventListener('change',()=>{state.predictor=$('predictor').value;render();});
    function step(d){if(renderedRows.length){state.index=(state.index+d+renderedRows.length)%renderedRows.length;render();announce(`Selected record ${state.index+1} of ${renderedRows.length}.`);}}
    $('previous').addEventListener('click',()=>step(-1));$('next').addEventListener('click',()=>step(1));svg.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key)){e.preventDefault();step(['ArrowLeft','ArrowUp'].includes(e.key)?-1:1);}});
    $('nextDelay').addEventListener('click',()=>{stop();nextDelay();});$('play').addEventListener('click',()=>{if(timer){stop();return;}if(matchMedia('(prefers-reduced-motion: reduce)').matches){announce('Reduced motion is enabled; use Next acquired delay.');return;}let steps=0;const total=new Set(D.ramsey?.rows.map(p=>p.t)||[]).size;if(!total)return;$('play').textContent='Pause';const tick=()=>{nextDelay();if(++steps>=total){stop();return;}timer=setTimeout(tick,1100);};timer=setTimeout(tick,0);});matchMedia('(prefers-reduced-motion: reduce)').addEventListener?.('change',stop);document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
    $('theme').addEventListener('click',()=>{state.theme=state.theme==='dark'?'light':'dark';document.documentElement.dataset.theme=state.theme;render();});
    for(const [id,target]of [['toControls','controls'],['backToPlot','plot'],['toInspector','inspector']])$(id).addEventListener('click',()=>{$(target).scrollIntoView({block:'start'});$(target).focus({preventScroll:true});});
    $('exportSVG').addEventListener('click',()=>download(new Blob([exported().text],{type:'image/svg+xml'}),'evidence-'+state.view+'.svg'));$('exportPNG').addEventListener('click',exportPNG);
    $('exportCSV').addEventListener('click',()=>{const contextRows=[['Evidence view',context.title],['Scope',context.scope],['Bundle SHA-256',identity],[]];const rows=[...contextRows,csvHeaders,...csvRows];download(new Blob([rows.map(r=>r.map(M.safeCSV).join(',')).join('\r\n')+'\r\n'],{type:'text/csv;charset=utf-8'}),'evidence-'+state.view+'.csv');});
    $('exportData').addEventListener('click',()=>download(new Blob([JSON.stringify(D,null,2)],{type:'application/json'}),'evidence-workbench-data.json'));
    $('saveView').addEventListener('click',()=>download(new Blob([JSON.stringify(saveState(),null,2)],{type:'application/json'}),'evidence-workbench-view.json'));
    $('restoreView').addEventListener('change',async()=>{try{const f=$('restoreView').files[0];if(!f)return;M.requireValue(f.size<=65536,'Saved view exceeds budget');restore(JSON.parse(await f.text()));}catch(err){error(err);}finally{$('restoreView').value='';}});
    const rows=D.ramsey?.rows||[];options('condition',[['all','All conditions'],...[...new Set(rows.map(p=>p.condition))].map(v=>[v,v])],'all');options('qubit',[['all','All physical qubits'],...[...new Set(rows.map(p=>p.qubit))].map(v=>[v,'Q'+v])],'all');options('delay',[['all','All acquired delays'],...[...new Set(rows.map(p=>p.t))].sort((a,b)=>a-b).map(v=>[v,v+' us'])],'all');
    options('acquisition',D.acquisitions.map((a,i)=>[i,a.payload.family+' / '+a.payload.evidence_kind]),0);options('cohort',D.optical.map((c,i)=>[i,c.label+' / '+c.payload.rows.length+' rows']),0);
    state.theme=matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';if(!rows.length)state.view=D.acquisitions.length?'dependence':D.optical.length?'optical':'provenance';
    $('summary').textContent=`${rows.length} Ramsey pairs / ${D.acquisitions.reduce((s,a)=>s+Object.keys(a.payload.members).length,0)} acquisition members / ${D.optical.length} optical cohorts`;
    window.EvidenceWorkbench={data:D,state,math:M,render,restore,saveState,exported,ramseyRows};
    syncControls();render();
})();
