;(() => {
	const hrefs = []
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
import{r as e}from"./rolldown-runtime.js?v=1784873523001";import{Cn as t,Dn as n,En as r,Er as i,Ft as a,Rn as o,Wn as s,Zr as c,bn as l,kn as u,mn as d,nn as f,qn as p,yn as m,yr as h}from"./vendor-utils.js?v=1784873523001";import{l as g,s as _}from"./vendor-vue.js?v=1784873523001";import{G as v,k as y,tn as b,w as x,xt as S}from"./vendor-naive.js?v=1784873523001";import{Ff as C,Pf as w,jf as T}from"./app.js?v=1784873523001";f();var E={class:`w-400px p-20px`},D={class:`mb-12px text-14px`},O=u({__name:`progress`,props:{data:{}},emits:[`close`],setup(e,{emit:r}){let{title:o,data:s,api:u,callback:d}=e.data,f=r,g=h(0),_=h(0),v=m(()=>s.length);return(async()=>{for(let e=0;e<s.length;e++)try{if(u){let t=await u(s[e]);s[e].batchStatus=`success`,s[e].reqMsg=a(t,`message.result`,`Success`),_.value+=1,_.value===v.value?g.value=100:g.value=Math.round(_.value/v.value*100)}}catch(t){s[e].batchStatus=`error`,s[e].reqMsg=a(t,`message.result`,``)}d==null||d(s),f(`close`)})(),(e,r)=>{let a=x;return p(),t(`div`,E,[l(`div`,D,[l(`span`,null,c(e.$t(`Component.Batch.index_3`,i(o))),1),l(`span`,null,c(i(_))+`/`+c(i(v)),1)]),n(a,{type:`line`,status:`success`,percentage:i(g),height:24,"border-radius":4,"fill-border-radius":0,processing:!0,"show-indicator":!1,"indicator-placement":`inside`},null,8,[`percentage`])])}}});f();var k={class:`p-24px`},A={class:`flex items-center mb-24px`},j={class:`flex-1 ml-12px text-14px leading-22px`},M={class:`flex-1 ml-12px text-14px leading-22px`},N=u({__name:`index`,props:{data:{}},emits:[`setConfirm`],setup(e,{expose:r,emit:a}){let o=e,{title:s,desc:u,data:f,columns:m,api:_,done:y,onCustomApi:b}=o.data,x=a,{t:S}=g(),w=h([]),E=h([...m,{key:`batchStatus`,title:S(`Public.Table.Result`),align:`right`,width:200,render:e=>e.batchStatus===`success`?n(`span`,{class:`text-primary`},[e.reqMsg]):e.batchStatus===`error`?n(`span`,{class:`text-error`},[e.reqMsg]):n(`span`,{class:`text-warning`},[S(`Public.Status.Wait`)])}]),D=()=>{w.value=f.map(e=>({batchStatus:`wait`,...e}));let{status:e}=o.data;e===`done`&&F(f)},N=h(!1),P=h(``),F=e=>{let t=e.filter(e=>e.batchStatus===`success`).length,n=e.length-t;P.value=S(`Component.Confirm.index_3`,[s,e.length,t,n]),N.value=!0,x(`setConfirm`,{text:`Done`,disabled:!1}),y==null||y(e)},I=e=>{if(x(`setConfirm`,{disabled:!0}),b){b(w.value),e();return}T({title:s,hideClose:!0,data:{title:s,api:_,data:w.value,callback:F},component:O})};return D(),r({onConfirm:({hide:e})=>(N.value?e():I(e),!1)}),(e,r)=>{let a=C,o=v;return p(),t(`div`,k,[l(`div`,A,[i(N)?(p(),t(d,{key:1},[n(a,{name:`base-success`,size:`40`,class:`text-primary`}),l(`div`,M,c(i(P)),1)],64)):(p(),t(d,{key:0},[n(a,{name:`base-warning`,size:`40`,class:`text-warning`}),l(`div`,j,c(i(u)),1)],64))]),n(o,{"max-height":182,data:i(w),columns:i(E)},null,8,[`data`,`columns`])])}}}),P=e({default:()=>F}),F=N,I=e({default:()=>L});f();var L=u({name:`BtModal`,props:{data:{type:Object},content:{type:[String,Function],default:``}},emits:[`modalConfirm`,`close`],setup(e,{emit:t}){let{t:n}=g(),r=h(0),i=h(0),a=h(null),c=h(null);return c.value=null,r.value=Math.round(Math.random()*9+1),i.value=Math.round(Math.random()*9+1),s(()=>{o(()=>{a.value&&a.value.focus()})}),{sum:c,addend1:r,addend2:i,inputRef:a,onEnter:()=>{t(`modalConfirm`)},onConfirm:async()=>{if(c.value===r.value+i.value){var a,o;await((a=e.data)==null||(o=a.onConfirm)==null?void 0:o.call(a)),t(`close`)}else w.error(n(`Component.Confirm.index_5`));return!1}}},render(){let{t:e}=g();return n(`div`,{class:`p-20px`},[n(`div`,{class:`flex items-center`},[n(`div`,{class:`flex-1 text-12px leading-20px`},[b(this.content)])]),n(`div`,{class:`confirm-calc-box flex items-center h-48px mt-12px px-12px`,style:{backgroundColor:`var(--confirm-calc-bg)`}},[n(`div`,null,[e(`Component.Confirm.index_4`)]),n(`div`,{class:`confirm-calc-num mx-10px`},[this.addend1,r(` + `),this.addend2]),n(`div`,{class:`mr-10px`},[r(`=`)]),n(`div`,{class:`w-90px`},[n(y,{ref:`inputRef`,size:`small`,placeholder:``,inputProps:{name:`sum`,onKeyup:e=>{e.key===`Enter`&&this.onEnter()}},value:this.sum,showButton:!1,onUpdateValue:e=>{this.sum=e}},null)])])])}}),R=e({default:()=>z});f();var z=u({name:`BtModal`,props:{data:{type:Object}},emits:[`modalConfirm`],setup(e,{emit:t}){var n;let{t:r}=g(),i=h(null),a=h(``),c=(((n=e.data)==null?void 0:n.text)||``).trim().toLowerCase(),l=h(c.replace(/^./u,e=>e.toUpperCase()));return s(()=>{o(()=>{i.value&&i.value.focus()})}),{text:l,result:a,inputRef:i,onConfirm:async t=>{if(a.value.trim().toLowerCase()===c){var n,i;await((n=e.data)==null||(i=n.onConfirm)==null?void 0:i.call(n,t)),t.hide()}else w.error(r(`Component.Confirm.index_2`));return!1},onKeydownEnter:e=>{e.key===`Enter`&&t(`modalConfirm`)}}},render(){var e;return n(`div`,{class:`p-20px`},[n(`div`,{class:`flex items-center`},[n(C,{name:`base-warning`,size:`30`,color:`#f0a020`},null),n(`div`,{class:`flex-1  ml-12px text-14px leading-20px`},[b((e=this.data)==null?void 0:e.content)])]),n(`div`,{class:`mt-16px p-12px bg-[var(--data-base-del-input-bg)] rounded-8px`},[n(_,{tag:`div`,keypath:`Component.Confirm.manualInputVerification`,scope:`global`},{text_:()=>n(`span`,{class:`text-error`},[this.text])}),n(S,{ref:`inputRef`,size:`small`,class:`mt-8px`,placeholder:``,inputProps:{name:`confirm_text`},value:this.result,onUpdateValue:e=>{this.result=e},onKeydown:this.onKeydownEnter},null)])])}});export{O as a,P as i,I as n,F as r,R as t};