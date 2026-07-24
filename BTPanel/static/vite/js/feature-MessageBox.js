;(() => {
	const hrefs = ["../css/feature-MessageBox.css?v=1784873523001"]
	const stylesheetSelector = "link[rel=stylesheet]"
	const loaded = new Set(Array.from(document.querySelectorAll(stylesheetSelector)).map(link => link.href))
	const version = "1784873523001"
	const findLoadedLink = href => Array.from(document.querySelectorAll(stylesheetSelector)).find(link => link.href === href)
	const removeAfterLoad = (freshLink, staleLink) => {
		const remove = () => staleLink.remove()
		if (freshLink.sheet) {
			requestAnimationFrame(remove)
			return
		}
		freshLink.addEventListener("load", remove, { once: true })
	}
	for (const link of Array.from(document.querySelectorAll(stylesheetSelector))) {
		const url = new URL(link.href, location.href)
		if (url.origin !== location.origin || url.searchParams.get("v") === version) continue
		url.searchParams.set("v", version)
		if (loaded.has(url.href)) {
			const freshLink = findLoadedLink(url.href)
			if (freshLink && freshLink !== link) removeAfterLoad(freshLink, link)
			continue
		}
		const freshLink = document.createElement("link")
		freshLink.rel = "stylesheet"
		freshLink.href = url.href
		link.parentNode?.insertBefore(freshLink, link.nextSibling)
		loaded.add(url.href)
		removeAfterLoad(freshLink, link)
	}
	for (const href of hrefs) {
		const url = new URL(href, import.meta.url).href
		if (loaded.has(url)) continue
		const link = document.createElement("link")
		link.rel = "stylesheet"
		link.href = url
		document.head.appendChild(link)
		loaded.add(url)
	}
})();
import{r as e}from"./rolldown-runtime.js?v=1784873523001";import{Cn as t,Dn as n,En as r,Er as i,Fn as a,Qn as o,Sn as s,Vn as c,Yn as l,Zr as u,_r as d,ar as f,bn as p,cr as m,kn as h,mn as g,mr as _,nn as v,qn as y,sr as b,xn as x,xr as S,yr as C}from"./vendor-utils.js?v=1784873523001";import{l as w,p as T}from"./vendor-vue.js?v=1784873523001";import{I as E,Tt as D,_ as O,ht as k,z as A}from"./vendor-naive.js?v=1784873523001";import{If as j,Oa as M,Sd as N,Xt as P,_p as F,cd as I,fd as ee,gp as L,ha as R,hd as z,i as B}from"./app.js?v=1784873523001";import{Xi as V,Yi as H,qi as U}from"./app-components.js?v=1784873523001";import{Tf as W,wf as G}from"./app-shared.js?v=1784873523001";import{l as K,u as q}from"./app-base.js?v=1784873523001";v();function J(e){return typeof e==`function`||Object.prototype.toString.call(e)===`[object Object]`&&!a(e)}var Y=h({name:`EmptyBox`,setup(e,{slots:t}){let r=B(),{t:i}=w(),a=()=>{G()};return()=>{var e;let o;return n(g,null,[r.taskCount===0?n(D,{class:`pt-80px`,size:`huge`,description:i(`Layout.MessageBox.index_1`)},null):n(g,null,[n(E,{class:`justify-between! flex-nowrap!`},{default:()=>[n(`span`,null,[i(`Layout.MessageBox.index_2`)]),n(k,{text:!0,type:`primary`,onClick:a},J(o=i(`Public.Status.Restart`))?o:{default:()=>[o]})]}),n(A,{class:`mt-12px! mb-16px!`},null),(e=t.default)==null?void 0:e.call(t)])])}}});v();var X={class:`h-460px overflow-auto`},Z={class:`install`},Q={key:0,class:`cmd`},te=j(h({__name:`index`,setup(e,{expose:a}){let d=B(),h=P(),_=I(),v=C(``),{send:S,close:w}=W(`/sock_shell`,{onMessage:(e,t)=>{let n=t.data;F(n)&&(v.value+=n)}}),T=()=>{S(`tail -n 100 -f /tmp/panelExec.log`)},D=async e=>{w(),await ee({id:e}),await _.getList()},O=()=>{if(_.taskList.length){let{type:e,status:t}=_.taskList[0];e===`execshell`&&(t===`-1`?(v.value=``,T()):setTimeout(async()=>{await _.getList(),O()},2e3))}};f(()=>d.taskCount,e=>{e&&O(),h.getMessageCount()}),c(()=>{w()});let A=async()=>{await _.getList(),d.taskCount!==0&&(O(),_.onRepetion())};return A(),a({init:A}),(e,a)=>{let c=k,d=E,f=o(`scroll-bottom`);return y(),x(i(Y),null,{default:b(()=>[p(`div`,X,[(y(!0),t(g,null,l(i(_).taskList,o=>(y(),t(`div`,{key:o.id},[o.type===`execshell`?(y(),t(g,{key:0},[n(d,{class:`justify-between! mb-8px`},{default:b(()=>[p(`span`,Z,u(o.name),1),p(`div`,null,[r(u(o.status===`0`?`waiting`:e.$t(`Soft.index_40`))+` `,1),a[0]||(a[0]=p(`img`,{src:`data:image/gif;base64,R0lGODlhDgACAIAAAHNzcwAAACH/C05FVFNDQVBFMi4wAwEAAAAh+QQFDgABACwAAAAAAgACAAACAoRRACH5BAUOAAEALAQAAAACAAIAAAIChFEAIfkEBQ4AAQAsCAAAAAIAAgAAAgKEUQAh+QQJDgABACwAAAAADgACAAACBoyPBpu9BQA7`},null,-1)),a[1]||(a[1]=p(`span`,{class:`px-5px`},`|`,-1)),n(c,{type:`primary`,text:``,onClick:e=>D(o.id)},{default:b(()=>[r(u(e.$t(`Public.Btn.Del`)),1)]),_:1},8,[`onClick`])])]),_:2},1024),o.status===`-1`?m((y(),t(`pre`,Q,[r(u(i(v)),1)])),[[f]]):s(``,!0)],64)):s(``,!0)]))),128))])]),_:1})}}}),[[`__scopeId`,`data-v-bd159bda`]]);v();var ne=h({__name:`index`,setup(e,{expose:t}){let r=P(),{loading:a,table:o,columns:s,search:c}=T(r),l=()=>{r.getMessageCount()};return t({init:l}),(e,t)=>{let r=U,u=H,d=V;return y(),x(d,null,{table:b(()=>[n(r,{loading:i(a),data:i(o).data,columns:i(s)},null,8,[`loading`,`data`,`columns`])]),pageRight:b(()=>[n(u,{page:i(c).p,"onUpdate:page":t[0]||(t[0]=e=>i(c).p=e),"page-size":i(c).limit,"onUpdate:pageSize":t[1]||(t[1]=e=>i(c).limit=e),"item-count":i(o).total,"page-slot":5,"show-size-picker":!1,onRefresh:l},null,8,[`page`,`page-size`,`item-count`])]),_:1})}}});v();var re=j(h({__name:`index`,setup(e,{expose:t}){let r=C(`None`),{loading:a,setLoading:o}=M(),s=async()=>{try{o(!0);let{message:e}=await z();L(e)&&(r.value=F(e.result)?e.result:`None`)}finally{o(!1)}};return s(),t({init:s}),(e,t)=>{let o=q,s=O;return y(),x(s,{class:`h-full`,show:i(a)},{default:b(()=>[n(o,{log:i(r)},null,8,[`log`])]),_:1},8,[`show`])}}}),[[`__scopeId`,`data-v-f3dc0026`]]);v();var ie={class:`h-550px`},ae=h({__name:`index`,setup(e,{expose:a}){let{t:o}=w(),s=B(),c=P(),l=C(`task`),u=d([{key:`task`,label:()=>n(`span`,null,[o(`Layout.MessageBox.index_3`),r(` (`),s.taskCount,r(`)`)]),component:S(te)},{key:`message`,label:()=>n(`span`,null,[o(`Layout.MessageBox.index_4`),r(` (`),c.listConut,r(`)`)]),component:S(ne)},{key:`log`,label:o(`Layout.MessageBox.index_5`),component:S(re)}]);return c.getMessageCount(),a({onClose:()=>{R()}}),(e,r)=>{let a=K;return y(),t(`div`,ie,[n(a,{value:i(l),"onUpdate:value":r[0]||(r[0]=e=>_(l)?l.value=e:null),ref:`tabsRef`,data:i(u)},null,8,[`value`,`data`])])}}}),oe=e({default:()=>$}),$=ae;v();var se=h({__name:`install-log`,props:{id:{}},setup(e,{expose:t}){let n=e,r=C(`None`),{loading:a,setLoading:o}=M(),s=async()=>{try{o(!0);let{message:e}=await N({path:`/www/server/panel/logs/installed/task_${n.id}.log`});L(e)&&(r.value=e.data)}catch(e){r.value=`None`}finally{o(!1)}};return s(),t({init:s}),(e,t)=>{let n=q;return y(),x(n,{log:i(r),loading:i(a)},null,8,[`log`,`loading`])}}}),ce=e({default:()=>le}),le=se;export{oe as n,ce as t};