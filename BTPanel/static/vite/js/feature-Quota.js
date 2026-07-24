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
import{r as e}from"./rolldown-runtime.js?v=1784873523001";import{Cn as t,Dn as n,En as r,Er as i,Ft as a,On as o,Sn as s,Zr as c,_r as l,bn as u,kn as d,nn as f,qn as p,sr as m,xn as h,yn as g,yr as _}from"./vendor-utils.js?v=1784873523001";import{l as v}from"./vendor-vue.js?v=1784873523001";import{P as y,bt as b,k as x,w as S,wt as C,xt as w,yt as T}from"./vendor-naive.js?v=1784873523001";import{ap as E,jf as D,ln as O,mn as k}from"./app.js?v=1784873523001";import{Ki as A}from"./app-components.js?v=1784873523001";import{Cf as j,Sf as M}from"./app-shared.js?v=1784873523001";import{n as N,r as P}from"./vendor-pdf.js?v=1784873523001";f(),P();var F={class:`leading-20px`},I=d({__name:`index`,props:{type:{default:`site`},data:{},callback:{}},setup(e){let{t:s}=v(),l=e,d=g(()=>{let{data:e}=l,{quota:t}=e;return!t.size}),f=g(()=>{if(d.value)return 0;let{data:e}=l,t=a(e,`quota.used`,0),n=a(e,`quota.size`,0);return n=n*1024*1024,n===0?0:t/n*100}),_=g(()=>{let{data:e}=l;return E(a(e,`quota.used`,0))}),y=g(()=>{let{data:e}=l;return`${a(e,`quota.size`,0).toFixed(2)} MB`}),b=g(()=>f.value<90?`success`:`error`),x=new Map([[`site`,`Site`],[`ftp`,`FTP`],[`database`,`Database`]]),w=()=>{D({title:`${s(`Component.Quota.index_5`,[l.data.name,x.get(l.type)||`--`])}`,width:480,minHeight:222,footer:!0,data:{type:l.type,info:l.data,callback:l.callback},component:o(()=>N(()=>Promise.resolve().then(()=>G),void 0))})};return(e,a)=>{let o=k,s=S,l=C;return i(d)?(p(),h(o,{key:0,onClick:w},{default:m(()=>[r(c(e.$t(`Component.Quota.index_2`)),1)]),_:1})):(p(),t(`div`,{key:1,class:`cursor-pointer`,onClick:w},[n(l,{placement:`bottom-start`,"arrow-point-to-center":!0},{trigger:m(()=>[n(s,{type:`line`,status:i(b),percentage:i(f),height:12,"border-radius":2,"show-indicator":!1},null,8,[`status`,`percentage`])]),default:m(()=>[u(`div`,F,[u(`p`,null,c(e.$t(`Component.Quota.index_3`,[i(_)])),1),u(`p`,null,c(e.$t(`Component.Quota.index_12`,[i(y)])),1),u(`p`,null,c(e.$t(`Component.Quota.index_4`)),1)])]),_:1})]))}}}),L=e({default:()=>R}),R=I;f();var z={class:`px-20px py-24px`},B={class:`w-160px`},V={class:`w-160px`},H={class:`text-error`},U={key:0},W=d({__name:`quota-config`,props:{data:{}},setup(e,{expose:o}){let{type:d,info:f,callback:h}=e.data,g=l({used:`0`,size:0}),v=_(`MB`);return(()=>{let e=a(f,`quota.used`,0);if(e>0){let t=E(e).split(` `);g.used=t[0],v.value=t[1]}g.size=a(f,`quota.size`,0)})(),o({onConfirm:async({hide:e})=>{(d===`site`||d===`ftp`)&&await j({size:g.size,quota_type:d,path:a(f,`path`,``)}),d===`database`&&await M({size:g.size,db_name:a(f,`name`,``)}),h==null||h(),e()}}),(e,a)=>{let o=w,l=T,f=b,h=y,_=x,S=A,C=O;return p(),t(`div`,z,[n(S,{"label-width":`180`},{default:m(()=>[n(h,{label:e.$t(`Component.Quota.index_6`)},{default:m(()=>[u(`div`,B,[n(f,null,{default:m(()=>[n(o,{value:i(g).used,"onUpdate:value":a[0]||(a[0]=e=>i(g).used=e),disabled:!0},null,8,[`value`]),n(l,{class:`w-44px text-center`},{default:m(()=>[r(c(i(v)),1)]),_:1})]),_:1})])]),_:1},8,[`label`]),n(h,{label:e.$t(`Component.Quota.index_7`)},{default:m(()=>[u(`div`,V,[n(f,null,{default:m(()=>[n(_,{value:i(g).size,"onUpdate:value":a[1]||(a[1]=e=>i(g).size=e),min:0,"show-button":!1},null,8,[`value`]),n(l,{class:`w-44px text-center`},{default:m(()=>[...a[2]||(a[2]=[r(`MB`,-1)])]),_:1})]),_:1})])]),_:1},8,[`label`])]),_:1}),n(C,{class:`mt-8px`},{default:m(()=>[u(`li`,H,c(e.$t(`Component.Quota.index_8`)),1),u(`li`,null,c(e.$t(`Component.Quota.index_9`)),1),i(d)===`database`?s(``,!0):(p(),t(`li`,U,c(e.$t(`Component.Quota.index_10`)),1)),u(`li`,null,c(e.$t(`Component.Quota.index_11`)),1)]),_:1})])}}}),G=e({default:()=>K}),K=W;export{L as t};