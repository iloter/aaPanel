System.register(["./page_layout-legacy.js?v=1732601582185","./public-legacy.js?v=1732601582185","./vue-legacy.js?v=1732601582185","./naive-legacy.js?v=1732601582185","./common-legacy.js?v=1732601582185","./index.vue_vue_type_script_setup_true_lang-legacy15.js?v=1732601582185","./__commonjsHelpers__-legacy.js?v=1732601582185"],(function(t,e){"use strict";var a,n,i,l,s,o,r,d,u,c,m,p,y,x,v,A,f,h,g,b,_,M,S,w,C,I,k,B,T,N,O,q,W,J,Y,R,z,E,U,Q,L,$,F,G,P,j,V,Z,D,H,K,X,tt,et,at,nt,it,lt,st,ot,rt;return{setters:[t=>{a=t.a8,n=t.i,i=t.k,l=t.w,s=t._,o=t.I,r=t.bi,d=t.bj,u=t.bk,c=t.h,m=t.J,p=t.S,y=t.a0,x=t.a7,v=t.f,A=t.ba,f=t.m,h=t.E,g=t.n},t=>{b=t.b,_=t.q},t=>{M=t.O,S=t.P,w=t.M,C=t.d,I=t.r,k=t.aB,B=t.f,T=t.k,N=t.v,O=t.R,q=t.ap,W=t.t,J=t.W,Y=t.aq,R=t.ag,z=t.e,E=t.aC,U=t.Y,Q=t.F,L=t.L,$=t.c,F=t.Z,G=t.ac,P=t.Q,j=t.x,V=t.X},t=>{Z=t.D,D=t.bP,H=t.bQ,K=t.aa,X=t.bm,tt=t.bJ,et=t.bL,at=t.bo,nt=t.bl,it=t.bZ},t=>{lt=t.j,st=t.R,ot=t.I},t=>{rt=t._},null],execute:function(){var e=document.createElement("style");e.textContent=".n-radio-group .n-radio-button[data-v-510567b2]{padding:0 10px}\n",document.head.appendChild(e);const dt=t=>a.post("/config?action=SetControl",t,{requestOptions:{loading:n.global.t("Monitor.API.system_1"),successMessage:!0}}),ut=t=>a.post("/ajax?action=GetCpuIo",t),ct={class:"flex-center h-full"},mt=i({},[["render",function(t,e){const a=Z;return M(),S("div",ct,[w(a,{size:"large"})])}]]),pt=["title"],yt=C({__name:"index",setup(t){const e=I(null),a=I(null),{isFullscreen:n,toggle:i}=k(a),o=()=>{i()};return B((()=>{e.value&&(a.value=l(e.value,"n-card"))})),(t,a)=>{const i=s;return T((M(),S("div",{ref_key:"iconRef",ref:e,class:"inline-flex cursor-pointer ml-8px",title:t.$t("Monitor.System.index_27"),onClick:o},[w(i,{ref_key:"iconRef",ref:e,name:"base-full-exit",size:"22"},null,512)],8,pt)),[[N,O(n)]])}}}),xt={class:"flex"},vt=i(C({__name:"index",props:q({day:{default:30}},{value:{default:()=>[]},valueModifiers:{}}),emits:q(["refresh"],["update:value"]),setup(t,{emit:e}){const a=W(t,"day"),n=e,{t:i}=J(),l=Y(t,"value"),c=I(),m=I(),p=I("today"),y=I(null),x=I(!1),v=[{label:i("Public.Search.Yesterday"),value:"yesterday"},{label:i("Public.Search.Today"),value:"today"},{label:i("Public.Search.Last7"),value:"7"}],{x:A,y:f,width:h,height:g}=R(c),b=z((()=>A.value+h.value)),_=z((()=>f.value+g.value));E(m,(()=>{x.value=!1}));const C=t=>{"custom"!==t&&(y.value=null,l.value=N())},k=t=>{o(t)&&t[0]!==t[1]&&(l.value=t.map((t=>r(t))),x.value=!1)},B=()=>{x.value||(x.value=!0)},T=t=>{const e=new Date,n=lt(e,-a.value);return st(n).getTime()>=t||st(e).getTime()<t};function N(){const t=new Date;let e={start:st(t),end:t};switch(p.value){case"yesterday":e=d(lt(t,-1));break;case"7":e.start=st(lt(t,-6))}return[r(e.start),r(e.end)]}0===l.value.length&&(l.value=N());const q=()=>{n("refresh")};return(t,e)=>{const a=D,n=H,i=s,l=K,o=u,r=X;return M(),S("div",xt,[w(n,{value:O(p),"onUpdate:value":[e[0]||(e[0]=t=>G(p)?p.value=t:null),C],size:"small"},{default:U((()=>[(M(),S(Q,null,L(v,(t=>w(a,{key:t.value,value:t.value},{default:U((()=>[$(F(t.label),1)])),_:2},1032,["value"]))),64)),w(a,{ref_key:"customRef",ref:c,value:"custom",onClick:B},{default:U((()=>[$(F(t.$t("Public.Search.Custom")),1)])),_:1},512)])),_:1},8,["value"]),w(l,{size:"small",class:"ml-10px px-8px",onClick:q},{default:U((()=>[w(i,{name:"refresh",size:"14"})])),_:1}),w(r,{show:O(x),placement:"bottom",trigger:"manual",x:O(b),y:O(_),"show-arrow":!1,style:{padding:0}},{trigger:U((()=>e[2]||(e[2]=[P("div",{class:"hidden"},null,-1)]))),default:U((()=>[P("div",{ref_key:"popoverContentRef",ref:m},[w(o,{value:O(y),"onUpdate:value":[e[1]||(e[1]=t=>G(y)?y.value=t:null),k],type:"daterange",panel:!0,actions:null,"is-date-disabled":T},null,8,["value"])],512)])),_:1},8,["show","x","y"])])}}}),[["__scopeId","data-v-510567b2"]]),At=["title"],ft=C({__name:"index",setup(t){const e=I(null),a=I(null),{isFullscreen:n,toggle:i}=k(a),o=()=>{i()};return B((()=>{e.value&&(a.value=l(e.value,"n-card"))})),(t,a)=>{const i=s;return T((M(),S("div",{ref_key:"iconRef",ref:e,class:"inline-flex cursor-pointer ml-8px",title:t.$t("Monitor.System.index_26"),onClick:o},[w(i,{ref_key:"iconRef",ref:e,name:"base-full",size:"22"},null,512)],8,At)),[[N,!O(n)]])}}});function ht(){const{t:t}=J();function e(t,e){let a=0;const n=(e-t)/3600/1e3,i=n/24;return a=n<=1?.02:n<=3?.5:n<=6?1:n<=12?3:n<=20?6:n<=24?8:i<=3?14:i<=7?24:168,36e5*a}return{option:j({}),getAddTime:function(t,e){const a=new Date,n=a.getMonth()+1,i=e.split(" ")[0].split("/"),l=parseInt(i[0]),s=t.split(" "),o=s[0].split("/"),r=s[1].split(":"),d=parseInt(o[0]);let u=a.getFullYear();(d>n||12==d&&d==l)&&(u-=1);const c=parseInt(o[1]),m=parseInt(r[0]),p=parseInt(r[1]);return new Date(u,d-1,c,m,p).getTime()},getInterval:e,renderTooltip:function(){return{trigger:"axis",axisPointer:{type:"cross"},padding:0,backgroundColor:"rgba(255, 255, 255, 0.95)",borderColor:"#eee",position:(t,e,a,n,i)=>function(t,e){const a=e.size.contentSize[0],n=e.size.contentSize[1],i=window.innerWidth,s=window.innerHeight,o=l(t,"n-spin-content")?.getBoundingClientRect(),r=e.pos[0]+(o?.left||0),d=e.pos[1]+(o?.top||0);let u=0,c=0;return c=r+a+80<i?e.pos[0]+20:e.pos[0]-a-20,u=d+n+80<s?e.pos[1]+20:e.pos[1]-n-20,d-n<0&&(u=0-(o?.top||0)+10),[c,u]}(a,{pos:t,size:i})}},renderTable:function(e,a=""){let n="",i="",l=[{title:"PID",index:1},{title:t("Monitor.System.index_28"),width:"120px",index:2},{title:t("Monitor.System.index_29"),index:0,render:t=>`${t[0]}%`},{title:t("Monitor.System.index_30"),index:4}];return"memory"===a&&(l=[{title:"PID",index:1},{title:t("Monitor.System.index_28"),width:"120px",index:2},{title:t("Monitor.System.index_31"),index:0,render:t=>c(m(t[0]))},{title:t("Monitor.System.index_30"),index:4}]),"disk"===a&&(l=[{title:"PID",index:3},{title:t("Monitor.System.index_28"),width:"100px",index:4},{title:t("Monitor.System.index_32"),index:0,render:t=>c(m(t[0]))},{title:t("Monitor.System.index_18"),index:1,render:t=>c(m(t[1]))},{title:t("Monitor.System.index_19"),index:2,render:t=>c(m(t[2]))},{title:t("Monitor.System.index_30"),index:6}]),l.forEach((t=>{n+=`<th style="width: ${t.width||"auto"};">${t.title}</th>`})),e.forEach((t=>{let e="";l.forEach((a=>{e+=`<td style="width: ${a.width||"auto"};">\n\t\t\t\t\t${a.render?a.render(t):t[a.index]}\n\t\t\t\t</td>`})),i+=`<tr>${e}</tr>`})),`<div class="process-top5">\n\t\t\t<div class="process-header"></div>\n\t\t\t<table>\n\t\t\t\t<thead>${n}</thead>\n\t\t\t\t<tbody>${i}</tbody>\n\t\t\t</table>\n\t\t</div>`},renderDataZoom:function(t,e){return[{type:"inside",start:0,end:100,zoomLock:!0,...t},{type:"slider",bottom:24,start:0,end:100,handleIcon:"path://M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z",handleSize:"80%",handleStyle:{color:"#fff",shadowBlur:3,shadowColor:"rgba(0, 0, 0, 0.6)",shadowOffsetX:2,shadowOffsetY:2},...e}]},renderXAxis:function(t,a){return{type:"time",min:t,minInterval:e(t,a),axisLine:{lineStyle:{color:"#666"}},axisLabel:{formatter(t){const e=p(t,"MM-dd HH:mm").split(" ");return`${e[0]}\n${e[1]}`}}}},renderYAxis:function(t){return{name:t,scale:!0,min:0,splitLine:{show:!0,lineStyle:{color:"#ddd"}},nameTextStyle:{color:"#666",fontSize:12,align:"left"},axisLine:{lineStyle:{color:"#666"}}}},renderSeries:function(t,e){return{name:t,smooth:!0,symbol:"circle",showSymbol:!1,itemStyle:{color:e},lineStyle:{width:2,color:e}}}}}const gt={class:"flex items-center"},bt=C({__name:"system-load",props:{day:{default:30}},setup(t){const{t:e}=J(),n=new Date,i=I([r(st(n)),r(n)]),l=I(!1),{option:s,getAddTime:d,renderTooltip:u,renderTable:c,renderXAxis:v,renderYAxis:A,renderSeries:f,renderDataZoom:h}=ht(),{loading:g,setLoading:_}=b(),S=async()=>{try{_(!0);const{message:n}=await(t={start:i.value[0],end:i.value[1]},a.post("/ajax?action=get_load_average",t));if(o(n)){const t=[],a=[],o=[],r=[];for(let e=0;e<n.length;e++){const i=n[e];i.time=d(i.addtime,n[n.length-1].addtime),a.push([i.time,i.pro,i]),t.push([i.time,i.one,i]),o.push([i.time,i.five,i]),r.push([i.time,i.fifteen,i])}let y=i.value[1],g=i.value[0];n.length>0?(y=n[0].time,g=ot(n[n.length-1].time).getTime(),l.value=!1):l.value=!0,function(t,a,n){s.value={legend:{top:"16px",right:"16%",data:[e("Monitor.System.index_9"),e("Monitor.System.index_10"),e("Monitor.System.index_11")]},tooltip:{...u(),formatter(t){let a="",n="",i="";const l=Object.entries(t);return l.forEach((([t,s])=>{const{data:o}=s,[,r,d]=o;if(l.length>1&&"0"===t){const t=d.pro;n+=`<div class="select-data">\n\t\t\t\t\t\t\t<span style="display:inline-block;margin-right:4px;border-radius:10px;width:10px;height:10px;background-color:rgb(255, 140, 0);"></span>\n\t\t\t\t\t\t\t<span>${e("Monitor.System.index_14")}${x(t)?t.toFixed(2):0}%</span>\n\t\t\t\t\t\t</div>`}"0"===t&&(i=c(d.cpu_top)),a=s.axisValue,n+=`<div class="select-data">\n\t\t\t\t\t\t${s.marker}\n\t\t\t\t\t\t<span>${s.seriesName}：${x(r)?r.toFixed(2):0}%</span>\n\t\t\t\t\t</div>`})),`<div class="echarts-tooltip" style="width: 440px;">\n\t\t\t\t\t<div class="formatter-header">\n\t\t\t\t\t\t<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAABHNCSVQICAgIfAhkiAAAAgBJREFUWIXtWN1xgzAMlkQ3YoCaYaJji8AWPjJM3AEYCasPNT3XZ2xBk17b43uCiy190b8AOHHixN8GPkpQ3/cmfrfWukfIPUyw73vjvTci8oqIJndGRBwivk3TNPwoQWYeAOC689p4hOgugsFq971KYhBRt8f9pD3IzEOOnIg4ABiJqCOibpomBIARAMbw2xd47+/BAyqoLJiznIi4pmnGmjW2rK615IuGYEbBeLvdBs3dQALTuA0yqwZqageCYBOTOxLs8zy7tm0xltW2Lc7z7Er3qv+AmSV+DzF2GJfL5R6XpZqri0mSBjMRdd8hBwDQNM0Yv3vvTel8kaCIvEbPTpMQaUdJYa11cXbHOnIoJknsCkR8KxFbluW6WoOZi64LskyqI4dNC9YsEcN7f08VLcuy2WmIyGl1qQv1VuZuCUfEqrs1UBN8hLIVT2l1JWW5llYisqfVbRJMhZfKQVo6RMTtKUklixazOMxzJjxvloO1na1hUHNhmCE/dZTOFl0clxZN0FtrVbVSW76qBNNyUCodWqSDR62vFwkGa3zGFyKaPQGeInN3zJ2LoWr86cAAByaa3JqgGTxU8yARdYlrrsx81QydaxuEryObevBQj05bi9K6uQF8xNOaSJWNT+2BX780/a+1MwUzD5rFnYiq9fEpBGM869PHiRMn/jreAZxNPtSJHlfLAAAAAElFTkSuQmCC" alt="path" />\n\t\t\t\t\t\t<span>${e("Monitor.System.index_15")}${a?p(a):"--"}</span>\n\t\t\t\t\t</div>\n\t\t\t\t\t<div class="formatter-body">\n\t\t\t\t\t\t${n}\n\t\t\t\t\t\t${i}\n\t\t\t\t\t</div>\n\t\t\t\t</div>`}},dataZoom:h({xAxisIndex:[0,1]},{left:"5%",right:"5%",xAxisIndex:[0,1]}),grid:[{left:"5%",bottom:92,right:"55%",width:"40%",height:"auto"},{bottom:92,left:"55%",width:"40%",height:"auto"}],xAxis:[{...v(t,a),gridIndex:0},{...v(t,a),gridIndex:1}],yAxis:[{...A(e("Monitor.System.index_12")),gridIndex:0,max:function(t){return t.max>=100?Math.ceil(t.max):t.max>=80?100:m((t.max+10).toString().slice(0,1)+"0")}},{...A(e("Monitor.System.index_13")),gridIndex:1}],series:[{type:"line",xAxisIndex:0,yAxisIndex:0,data:n.pro,...f(e("Monitor.System.index_12"),"rgb(255, 140, 0)")},{type:"line",xAxisIndex:1,yAxisIndex:1,data:n.one,...f(e("Monitor.System.index_9"),"rgb(30, 144, 255)")},{type:"line",xAxisIndex:1,yAxisIndex:1,data:n.five,...f(e("Monitor.System.index_10"),"rgb(0, 178, 45)")},{type:"line",xAxisIndex:1,yAxisIndex:1,data:n.fifteen,...f(e("Monitor.System.index_11"),"rgb(147, 38, 255)")}]}}(g,y,{one:t,pro:a,five:o,fifteen:r})}}finally{_(!1)}var t};return S(),(t,e)=>{const a=ft,n=vt,o=yt,r=mt,d=y,u=tt;return M(),V(u,{class:"h-388px"},{header:U((()=>[P("div",gt,[P("span",null,F(t.$t("Monitor.System.index_8")),1),w(a)])])),"header-extra":U((()=>[w(n,{value:O(i),"onUpdate:value":[e[0]||(e[0]=t=>G(i)?i.value=t:null),S],day:t.day,onRefresh:S},null,8,["value","day"]),w(o)])),default:U((()=>[w(d,{class:"h-full",show:O(g)},{default:U((()=>[O(l)?(M(),V(r,{key:0})):(M(),V(rt,{key:1,type:"line",height:"100%",option:O(s)},null,8,["option"]))])),_:1},8,["show"])])),_:1})}}}),_t={class:"flex items-center"},Mt=C({__name:"system-cpu",props:{day:{default:30}},setup(t){const{t:e}=J(),a=new Date,n=I([r(st(a)),r(a)]),i=I(!1),{option:l,getAddTime:s,renderTooltip:d,renderTable:u,renderXAxis:c,renderYAxis:m,renderSeries:v,renderDataZoom:A}=ht(),{loading:f,setLoading:h}=b(),g=async()=>{try{h(!0);const{message:t}=await ut({start:n.value[0],end:n.value[1]});if(o(t)){const a=[];for(let e=0;e<t.length;e++){const n=t[e];n.time=s(n.addtime,t[t.length-1].addtime),a.push([n.time,n.pro,n])}let o=n.value[1],r=n.value[0];t.length>0?(o=t[0].time,r=ot(t[t.length-1].time).getTime(),i.value=!1):i.value=!0,function(t,a,n){l.value={tooltip:{...d(),formatter(t){let a="",n="",i="";return Object.entries(t).forEach((([t,e])=>{const{data:l}=e,[,s,o]=l;"0"===t&&(i=u(o.cpu_top)),a=e.axisValue,n+=`<div class="select-data">\n\t\t\t\t\t\t${e.marker}\n\t\t\t\t\t\t<span>${e.seriesName}：${x(s)?s.toFixed(2):0}%</span>\n\t\t\t\t\t</div>`})),`<div class="echarts-tooltip" style="width: 440px;">\n\t\t\t\t\t<div class="formatter-header">\n\t\t\t\t\t\t<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAABHNCSVQICAgIfAhkiAAAAgBJREFUWIXtWN1xgzAMlkQ3YoCaYaJji8AWPjJM3AEYCasPNT3XZ2xBk17b43uCiy190b8AOHHixN8GPkpQ3/cmfrfWukfIPUyw73vjvTci8oqIJndGRBwivk3TNPwoQWYeAOC689p4hOgugsFq971KYhBRt8f9pD3IzEOOnIg4ABiJqCOibpomBIARAMbw2xd47+/BAyqoLJiznIi4pmnGmjW2rK615IuGYEbBeLvdBs3dQALTuA0yqwZqageCYBOTOxLs8zy7tm0xltW2Lc7z7Er3qv+AmSV+DzF2GJfL5R6XpZqri0mSBjMRdd8hBwDQNM0Yv3vvTel8kaCIvEbPTpMQaUdJYa11cXbHOnIoJknsCkR8KxFbluW6WoOZi64LskyqI4dNC9YsEcN7f08VLcuy2WmIyGl1qQv1VuZuCUfEqrs1UBN8hLIVT2l1JWW5llYisqfVbRJMhZfKQVo6RMTtKUklixazOMxzJjxvloO1na1hUHNhmCE/dZTOFl0clxZN0FtrVbVSW76qBNNyUCodWqSDR62vFwkGa3zGFyKaPQGeInN3zJ2LoWr86cAAByaa3JqgGTxU8yARdYlrrsx81QydaxuEryObevBQj05bi9K6uQF8xNOaSJWNT+2BX780/a+1MwUzD5rFnYiq9fEpBGM869PHiRMn/jreAZxNPtSJHlfLAAAAAElFTkSuQmCC" alt="path" />\n\t\t\t\t\t\t<span>${e("Monitor.System.index_15")}${a?p(a):"--"}</span>\n\t\t\t\t\t</div>\n\t\t\t\t\t<div class="formatter-body">\n\t\t\t\t\t\t${n}\n\t\t\t\t\t\t${i}\n\t\t\t\t\t</div>\n\t\t\t\t</div>`}},grid:{bottom:92},dataZoom:A(),xAxis:{...c(t,a)},yAxis:{...m("CPU"),max:100},series:[{type:"line",data:n.cpu,...v("CPU","rgb(0, 153, 238)")}]}}(r,o,{cpu:a})}}finally{h(!1)}};return g(),(t,e)=>{const a=ft,s=vt,o=yt,r=mt,d=y,u=tt;return M(),V(u,{class:"h-388px"},{header:U((()=>[P("div",_t,[e[1]||(e[1]=P("span",null,"CPU",-1)),w(a)])])),"header-extra":U((()=>[w(s,{value:O(n),"onUpdate:value":[e[0]||(e[0]=t=>G(n)?n.value=t:null),g],day:t.day,onRefresh:g},null,8,["value","day"]),w(o)])),default:U((()=>[w(d,{class:"h-full",show:O(f)},{default:U((()=>[O(i)?(M(),V(r,{key:0})):(M(),V(rt,{key:1,type:"line",height:"100%",option:O(l)},null,8,["option"]))])),_:1},8,["show"])])),_:1})}}}),St={class:"flex items-center"},wt=C({__name:"system-memory",props:{day:{default:30}},setup(t){const{t:e}=J(),a=new Date,n=I([r(st(a)),r(a)]),i=I(!1),{option:l,getAddTime:s,renderTooltip:d,renderTable:u,renderXAxis:c,renderYAxis:m,renderSeries:v,renderDataZoom:A}=ht(),{loading:f,setLoading:h}=b(),g=async()=>{try{h(!0);const{message:t}=await ut({start:n.value[0],end:n.value[1]});if(o(t)){const a=[];for(let e=0;e<t.length;e++){const n=t[e];n.time=s(n.addtime,t[t.length-1].addtime),a.push([n.time,n.mem,n])}let o=n.value[1],r=n.value[0];t.length>0?(o=t[0].time,r=ot(t[t.length-1].time).getTime(),i.value=!1):i.value=!0,function(t,a,n){l.value={tooltip:{...d(),formatter(t){let a="",n="",i="";return Object.entries(t).forEach((([t,e])=>{const{data:l}=e,[,s,o]=l;"0"===t&&(i=u(o.memory_top,"memory")),a=e.axisValue,n+=`<div class="select-data">\n\t\t\t\t\t\t${e.marker}\n\t\t\t\t\t\t<span>${e.seriesName}：${x(s)?s.toFixed(2):0}%</span>\n\t\t\t\t\t</div>`})),`<div class="echarts-tooltip" style="width: 480px;">\n\t\t\t\t\t<div class="formatter-header">\n\t\t\t\t\t\t<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAABHNCSVQICAgIfAhkiAAAAgBJREFUWIXtWN1xgzAMlkQ3YoCaYaJji8AWPjJM3AEYCasPNT3XZ2xBk17b43uCiy190b8AOHHixN8GPkpQ3/cmfrfWukfIPUyw73vjvTci8oqIJndGRBwivk3TNPwoQWYeAOC689p4hOgugsFq971KYhBRt8f9pD3IzEOOnIg4ABiJqCOibpomBIARAMbw2xd47+/BAyqoLJiznIi4pmnGmjW2rK615IuGYEbBeLvdBs3dQALTuA0yqwZqageCYBOTOxLs8zy7tm0xltW2Lc7z7Er3qv+AmSV+DzF2GJfL5R6XpZqri0mSBjMRdd8hBwDQNM0Yv3vvTel8kaCIvEbPTpMQaUdJYa11cXbHOnIoJknsCkR8KxFbluW6WoOZi64LskyqI4dNC9YsEcN7f08VLcuy2WmIyGl1qQv1VuZuCUfEqrs1UBN8hLIVT2l1JWW5llYisqfVbRJMhZfKQVo6RMTtKUklixazOMxzJjxvloO1na1hUHNhmCE/dZTOFl0clxZN0FtrVbVSW76qBNNyUCodWqSDR62vFwkGa3zGFyKaPQGeInN3zJ2LoWr86cAAByaa3JqgGTxU8yARdYlrrsx81QydaxuEryObevBQj05bi9K6uQF8xNOaSJWNT+2BX780/a+1MwUzD5rFnYiq9fEpBGM869PHiRMn/jreAZxNPtSJHlfLAAAAAElFTkSuQmCC" alt="path" />\n\t\t\t\t\t\t<span>${e("Monitor.System.index_15")}${a?p(a):"--"}</span>\n\t\t\t\t\t</div>\n\t\t\t\t\t<div class="formatter-body">\n\t\t\t\t\t\t${n}\n\t\t\t\t\t\t${i}\n\t\t\t\t\t</div>\n\t\t\t\t</div>`}},grid:{bottom:92},dataZoom:A(),xAxis:{...c(t,a)},yAxis:{...m(e("Monitor.System.index_16")),max:100},series:[{type:"line",data:n.memory,...v("CPU","rgb(0, 153, 238)")}]}}(r,o,{memory:a})}}finally{h(!1)}};return g(),(t,e)=>{const a=ft,s=vt,o=yt,r=mt,d=y,u=tt;return M(),V(u,{class:"h-388px"},{header:U((()=>[P("div",St,[P("span",null,F(t.$t("Monitor.System.index_16")),1),w(a)])])),"header-extra":U((()=>[w(s,{value:O(n),"onUpdate:value":[e[0]||(e[0]=t=>G(n)?n.value=t:null),g],day:t.day,onRefresh:g},null,8,["value","day"]),w(o)])),default:U((()=>[w(d,{class:"h-full",show:O(f)},{default:U((()=>[O(i)?(M(),V(r,{key:0})):(M(),V(rt,{key:1,type:"line",height:"100%",option:O(l)},null,8,["option"]))])),_:1},8,["show"])])),_:1})}}}),Ct={class:"flex items-center"},It="KB",kt=C({__name:"system-disk",props:{day:{default:30}},setup(t){const{t:e}=J(),n=new Date,i=I([r(st(n)),r(n)]),l=I(!1),{option:s,getAddTime:d,renderTooltip:u,renderTable:v,renderXAxis:A,renderYAxis:f,renderSeries:h,renderDataZoom:g}=ht(),{loading:_,setLoading:S}=b(),C=t=>m(c(t,!1,3,It)),k=async()=>{try{S(!0);const{message:n}=await(t={start:i.value[0],end:i.value[1]},a.post("/ajax?action=GetDiskIo",t));if(o(n)){const t=[],a=[],o=[],r=[];for(let i=0;i<n.length;i++){const l=n[i],s=C(l.read_bytes),r=C(l.write_bytes),u=l.read_time+l.write_time;l.time=d(l.addtime,n[n.length-1].addtime),t.push([l.time,s,l,`${It}/s`]),a.push([l.time,r,l,`${It}/s`]),o.push([l.time,u,l,`${e("Public.Unit.Time",u)}/s`]),o.push([l.time,l.read_count+l.write_count,l,"ms"])}let c=i.value[1],m=i.value[0];n.length>0?(c=n[0].time,m=ot(n[n.length-1].time).getTime(),l.value=!1):l.value=!0,function(t,a,n){s.value={legend:{top:"16px",data:[e("Monitor.System.index_18"),e("Monitor.System.index_19"),e("Monitor.System.index_20"),e("Monitor.System.index_21")]},tooltip:{...u(),formatter(t){let a="",n="",i="";return Object.entries(t).forEach((([t,e])=>{const{data:l}=e,[,s,o,r]=l;"0"===t&&(i=v(o.disk_top,"disk")),a=e.axisValue,n+=`<div class="select-data">\n\t\t\t\t\t\t${e.marker}\n\t\t\t\t\t\t<span>${e.seriesName}：${x(s)?s.toFixed(2):0}  ${r}</span>\n\t\t\t\t\t</div>`})),`<div class="echarts-tooltip" style="width: 560px;">\n\t\t\t\t\t<div class="formatter-header">\n\t\t\t\t\t\t<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAABHNCSVQICAgIfAhkiAAAAgBJREFUWIXtWN1xgzAMlkQ3YoCaYaJji8AWPjJM3AEYCasPNT3XZ2xBk17b43uCiy190b8AOHHixN8GPkpQ3/cmfrfWukfIPUyw73vjvTci8oqIJndGRBwivk3TNPwoQWYeAOC689p4hOgugsFq971KYhBRt8f9pD3IzEOOnIg4ABiJqCOibpomBIARAMbw2xd47+/BAyqoLJiznIi4pmnGmjW2rK615IuGYEbBeLvdBs3dQALTuA0yqwZqageCYBOTOxLs8zy7tm0xltW2Lc7z7Er3qv+AmSV+DzF2GJfL5R6XpZqri0mSBjMRdd8hBwDQNM0Yv3vvTel8kaCIvEbPTpMQaUdJYa11cXbHOnIoJknsCkR8KxFbluW6WoOZi64LskyqI4dNC9YsEcN7f08VLcuy2WmIyGl1qQv1VuZuCUfEqrs1UBN8hLIVT2l1JWW5llYisqfVbRJMhZfKQVo6RMTtKUklixazOMxzJjxvloO1na1hUHNhmCE/dZTOFl0clxZN0FtrVbVSW76qBNNyUCodWqSDR62vFwkGa3zGFyKaPQGeInN3zJ2LoWr86cAAByaa3JqgGTxU8yARdYlrrsx81QydaxuEryObevBQj05bi9K6uQF8xNOaSJWNT+2BX780/a+1MwUzD5rFnYiq9fEpBGM869PHiRMn/jreAZxNPtSJHlfLAAAAAElFTkSuQmCC" alt="path" />\n\t\t\t\t\t\t<span>${e("Monitor.System.index_15")}${a?p(a):"--"}</span>\n\t\t\t\t\t</div>\n\t\t\t\t\t<div class="formatter-body">\n\t\t\t\t\t\t${n}\n\t\t\t\t\t\t${i}\n\t\t\t\t\t</div>\n\t\t\t\t</div>`}},grid:{bottom:92},dataZoom:g(),xAxis:{...A(t,a)},yAxis:{...f(e("Monitor.System.index_22",[It]))},series:[{type:"line",data:n.read,...h(e("Monitor.System.index_18"),"rgb(255, 70, 131)")},{type:"line",data:n.write,...h(e("Monitor.System.index_19"),"rgba(46, 165, 186, .7)")},{type:"line",data:n.countTotal,...h(e("Monitor.System.index_20"),"rgba(30, 144, 255)")},{type:"line",data:n.timeTotal,...h(e("Monitor.System.index_21"),"rgba(255, 140, 0)")}]}}(m,c,{read:t,write:a,timeTotal:o,countTotal:r})}}finally{S(!1)}var t};return k(),(t,e)=>{const a=ft,n=vt,o=yt,r=mt,d=y,u=tt;return M(),V(u,{class:"h-388px"},{header:U((()=>[P("div",Ct,[P("span",null,F(t.$t("Monitor.System.index_17")),1),w(a)])])),"header-extra":U((()=>[w(n,{value:O(i),"onUpdate:value":[e[0]||(e[0]=t=>G(i)?i.value=t:null),k],day:t.day,onRefresh:k},null,8,["value","day"]),w(o)])),default:U((()=>[w(d,{class:"h-full",show:O(_)},{default:U((()=>[O(l)?(M(),V(r,{key:0})):(M(),V(rt,{key:1,type:"line",height:"100%",option:O(s)},null,8,["option"]))])),_:1},8,["show"])])),_:1})}}}),Bt={class:"flex whitespace-pre-wrap items-center"},Tt={class:"w-100px"},Nt="KB",Ot=C({__name:"system-network",props:{day:{default:30}},setup(t){const{t:e}=J(),n=new Date,i=I([r(st(n)),r(n)]),l=I("all"),s=I([]),d=I(!1),{option:u,getAddTime:v,renderTooltip:A,renderXAxis:f,renderYAxis:h,renderSeries:g,renderDataZoom:_}=ht(),{loading:S,setLoading:C}=b(),k=t=>m(c(1024*t,!1,3,Nt)),B=t=>{s.value.length>0||(s.value=Object.keys(t).map((t=>({label:t,value:t}))),s.value.unshift({label:e("Public.All"),value:"all"}))},T=async()=>{try{C(!0);const{message:n}=await(t={start:i.value[0],end:i.value[1]},a.post("/ajax?action=GetNetWorkIo",t));if(o(n)){const t=[],a=[];for(let e=0;e<n.length;e++){const i=n[e],s="all"===l.value?i.up:i.up_packets[l.value],o="all"===l.value?i.down:i.down_packets[l.value],r=k(s),d=k(o);i.time=v(i.addtime,n[n.length-1].addtime),t.push([i.time,r,i,`${Nt}/s`]),a.push([i.time,d,i,`${Nt}/s`])}let s=i.value[1],o=i.value[0];n.length>0?(s=n[0].time,o=ot(n[n.length-1].time).getTime(),d.value=!1,B(n[0].down_packets)):(d.value=!0,B({})),function(t,a,n){u.value={legend:{top:"16px",data:[e("Monitor.System.index_24"),e("Monitor.System.index_25")]},tooltip:{...A(),formatter(t){let a="",n="";return Object.entries(t).forEach((([,t])=>{const{data:e}=t,[,i,,l]=e;a=t.axisValue,n+=`<div class="select-data">\n\t\t\t\t\t\t${t.marker}\n\t\t\t\t\t\t<span>${t.seriesName}：${x(i)?i.toFixed(2):0}  ${l}</span>\n\t\t\t\t\t</div>`})),`<div class="echarts-tooltip" style="width: 280px;">\n\t\t\t\t\t<div class="formatter-header">\n\t\t\t\t\t\t<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAABHNCSVQICAgIfAhkiAAAAgBJREFUWIXtWN1xgzAMlkQ3YoCaYaJji8AWPjJM3AEYCasPNT3XZ2xBk17b43uCiy190b8AOHHixN8GPkpQ3/cmfrfWukfIPUyw73vjvTci8oqIJndGRBwivk3TNPwoQWYeAOC689p4hOgugsFq971KYhBRt8f9pD3IzEOOnIg4ABiJqCOibpomBIARAMbw2xd47+/BAyqoLJiznIi4pmnGmjW2rK615IuGYEbBeLvdBs3dQALTuA0yqwZqageCYBOTOxLs8zy7tm0xltW2Lc7z7Er3qv+AmSV+DzF2GJfL5R6XpZqri0mSBjMRdd8hBwDQNM0Yv3vvTel8kaCIvEbPTpMQaUdJYa11cXbHOnIoJknsCkR8KxFbluW6WoOZi64LskyqI4dNC9YsEcN7f08VLcuy2WmIyGl1qQv1VuZuCUfEqrs1UBN8hLIVT2l1JWW5llYisqfVbRJMhZfKQVo6RMTtKUklixazOMxzJjxvloO1na1hUHNhmCE/dZTOFl0clxZN0FtrVbVSW76qBNNyUCodWqSDR62vFwkGa3zGFyKaPQGeInN3zJ2LoWr86cAAByaa3JqgGTxU8yARdYlrrsx81QydaxuEryObevBQj05bi9K6uQF8xNOaSJWNT+2BX780/a+1MwUzD5rFnYiq9fEpBGM869PHiRMn/jreAZxNPtSJHlfLAAAAAElFTkSuQmCC" alt="path" />\n\t\t\t\t\t\t<span>${e("Monitor.System.index_15")}${a?p(a):"--"}</span>\n\t\t\t\t\t</div>\n\t\t\t\t\t<div class="formatter-body">\n\t\t\t\t\t\t${n}\n\t\t\t\t\t</div>\n\t\t\t\t</div>`}},grid:{bottom:92},dataZoom:_(),xAxis:{...f(t,a)},yAxis:{...h(e("Monitor.System.index_22",[Nt]))},series:[{type:"line",data:n.up,...g(e("Monitor.System.index_24"),"rgb(255, 70, 131)")},{type:"line",data:n.down,...g(e("Monitor.System.index_25"),"rgba(46, 165, 186, .7)")}]}}(o,s,{up:t,down:a})}}finally{C(!1)}var t};return T(),(t,e)=>{const a=et,n=ft,o=vt,r=yt,c=mt,m=y,p=tt;return M(),V(p,{class:"h-388px"},{header:U((()=>[P("div",Bt,[P("span",null,F(t.$t("Monitor.System.index_23")),1),P("div",Tt,[w(a,{value:O(l),"onUpdate:value":[e[0]||(e[0]=t=>G(l)?l.value=t:null),T],options:O(s),size:"small","consistent-menu-width":!1},null,8,["value","options"])]),w(n)])])),"header-extra":U((()=>[w(o,{value:O(i),"onUpdate:value":[e[1]||(e[1]=t=>G(i)?i.value=t:null),T],day:t.day,onRefresh:T},null,8,["value","day"]),w(r)])),default:U((()=>[w(m,{class:"h-full",show:O(S)},{default:U((()=>[O(d)?(M(),V(c,{key:0})):(M(),V(rt,{key:1,type:"line",height:"100%",option:O(u)},null,8,["option"]))])),_:1},8,["show"])])),_:1})}}}),qt={class:"flex items-center flex-wrap"},Wt={class:"inline-flex items-center mr-32px"},Jt={class:"mr-12px"},Yt={class:"inline-flex items-center"},Rt={class:"mr-6px"},zt={class:"w-86px mr-12px"},Et={class:"inline-flex mx-32px"},Ut={class:"mr-16px"};t("default",C({__name:"index",setup(t){const{t:e}=J(),i=I({day:0,status:!1,size:0}),l=async t=>{await dt({type:t?1:0,day:i.value.day}),i.value.status=t},s=async()=>{i.value.day?/^-?\d+$/.test(`${i.value.day}`)?await dt({type:i.value.status?1:0,day:i.value.day}):f.error(e("Monitor.System.index_6")):f.error(e("Monitor.System.index_5"))},o=()=>{_({title:e("Monitor.System.index_4"),content:()=>w("span",{class:"text-error"},[e("Monitor.System.index_7")]),onConfirm:async()=>{await a.post("/config?action=SetControl",{type:"del"},{requestOptions:{loading:n.global.t("Monitor.API.system_2"),successMessage:!0}}),h()}})};return(async()=>{const{message:t}=await(e={type:-1},a.post("/config?action=SetControl",e));var e;v(t)&&(i.value=t)})(),(t,e)=>{const a=at,n=nt,r=K,d=g,u=tt,m=it,p=A;return M(),S("div",null,[w(u,{class:"p-16px mb-16px"},{default:U((()=>[P("div",qt,[P("div",Wt,[P("span",Jt,F(t.$t("Monitor.System.index_1")),1),w(a,{value:O(i).status,"onUpdate:value":l},null,8,["value"])]),P("div",Yt,[P("span",Rt,F(t.$t("Monitor.System.index_2")),1),P("div",zt,[w(n,{value:O(i).day,"onUpdate:value":e[0]||(e[0]=t=>O(i).day=t),min:1,"show-button":!1,placeholder:""},null,8,["value"])]),w(r,{onClick:s},{default:U((()=>[$(F(t.$t("Monitor.System.index_3")),1)])),_:1})]),P("div",Et,[w(d,{vertical:""})]),P("span",Ut,F(t.$t("Monitor.System.index_33"))+F(O(c)(O(i).size)),1),w(r,{onClick:o},{default:U((()=>[$(F(t.$t("Monitor.System.index_4")),1)])),_:1})])])),_:1}),w(p,{"x-gap":"16","y-gap":"16",cols:2},{default:U((()=>[w(m,{span:2},{default:U((()=>[w(bt,{day:O(i).day},null,8,["day"])])),_:1}),w(m,{span:1},{default:U((()=>[w(Mt,{day:O(i).day},null,8,["day"])])),_:1}),w(m,{span:1},{default:U((()=>[w(wt,{day:O(i).day},null,8,["day"])])),_:1}),w(m,{span:1},{default:U((()=>[w(kt,{day:O(i).day},null,8,["day"])])),_:1}),w(m,{span:1},{default:U((()=>[w(Ot,{day:O(i).day},null,8,["day"])])),_:1})])),_:1})])}}}))}}}));