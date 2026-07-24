;(() => {
	const hrefs = ["../css/feature-Charts.css?v=1784873523001"]
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
import{r as e}from"./rolldown-runtime.js?v=1784873523001";import{Cn as t,Er as n,Jr as r,Rn as i,Vn as a,Wn as o,ar as s,f as c,kn as l,n as u,nn as d,qn as f,y as p,yr as m}from"./vendor-utils.js?v=1784873523001";import{rn as h}from"./vendor-naive.js?v=1784873523001";import{If as g}from"./app.js?v=1784873523001";import{D as _,E as v,M as y,O as b,T as x,_ as S,a as C,c as w,d as T,f as E,h as D,i as O,k,l as A,m as j,o as M,p as N,s as P,u as F,x as I}from"./vendor-charts.js?v=1784873523001";d(),y([N,S,A,D,M,P,F,v,k,C,O]);var L=b,R=l({__name:`index`,props:{width:{type:[Number,String],default:`100%`},height:{type:[Number,String],default:`200px`},dataZoom:{type:Boolean,default:!1},option:{type:Object,required:!0}},setup(e,{expose:c}){let l=e,u=m(null),d=null;function g(){u.value!==null&&(d=L.getInstanceByDom(u.value),d==null&&(d=L.init(u.value)),d.setOption(l.option,!0))}function _(){var e;u.value!==null&&((e=L.getInstanceByDom(u.value))==null||e.resize())}s(()=>l.option,e=>{e&&i(()=>{g()})},{immediate:!0,deep:!0});let v=p(_,300,{maxWait:800});return o(()=>{g(),window.addEventListener(`resize`,v)}),a(()=>{var e;u.value&&((e=L.getInstanceByDom(u.value))==null||e.dispose(),window.removeEventListener(`resize`,v))}),c({getChart:()=>d}),(i,a)=>(f(),t(`div`,{ref_key:`chartRef`,ref:u,style:r({width:n(h)(e.width),height:n(h)(e.height)})},null,4))}}),z=e({default:()=>B}),B=R;y([N,S,A,D,M,P,F,j,_,k,C,O]);var V=b;d();var H=l({__name:`index`,props:{width:{type:[Number,String],default:`100%`},height:{type:[Number,String],default:`200px`},dataZoom:{type:Boolean,default:!1},option:{type:Object,required:!0}},setup(e,{expose:l}){let u=e,d=m(null);function g(){if(d.value===null)return;let e=V.getInstanceByDom(d.value);e==null&&(e=V.init(d.value)),e.setOption(u.option,!0),requestAnimationFrame(()=>e.resize())}function _(){var e;d.value!==null&&((e=V.getInstanceByDom(d.value))==null||e.resize())}s(()=>u.option,e=>{e&&i(()=>{g()})},{immediate:!0,deep:!0});let v=p(_,80,{maxWait:240});return c(d,()=>{v()}),o(()=>{i(()=>{g(),window.addEventListener(`resize`,v)})}),a(()=>{var e;d.value&&((e=V.getInstanceByDom(d.value))==null||e.dispose(),window.removeEventListener(`resize`,v))}),l({resize:_,getChart:()=>V.getInstanceByDom(d.value)}),(i,a)=>(f(),t(`div`,{ref_key:`chartRef`,ref:d,class:`bt-line-chart`,style:r({width:n(h)(e.width),height:n(h)(e.height)})},null,4))}}),U=e({default:()=>W}),W=g(H,[[`__scopeId`,`data-v-ba6e3b19`]]);y([E,N,S,A,D,M,P,F,w,I,k,C,O,T]);var G=b;d();var K=l({__name:`index`,props:{width:{type:[Number,String],default:`100%`},height:{type:[Number,String],default:`200px`},dataZoom:{type:Boolean,default:!1},option:{type:Object,required:!0}},setup(e,{expose:c}){let l=e,d=m(null),g=!0;async function _(){if(g){let{data:e}=await u.get(`/static/vite/data/world.json`);G.registerMap(`world`,e),g=!1}if(d.value===null)return;let e=G.getInstanceByDom(d.value);e==null&&(e=G.init(d.value)),e.setOption(l.option,!0)}function v(){var e;d.value!==null&&((e=G.getInstanceByDom(d.value))==null||e.resize())}s(()=>l.option,e=>{e&&i(()=>{_()})},{immediate:!0,deep:!0});let y=p(v,300,{maxWait:800});return o(async()=>{window.addEventListener(`resize`,y)}),a(()=>{var e;d.value&&((e=G.getInstanceByDom(d.value))==null||e.dispose(),window.removeEventListener(`resize`,y))}),c({resize:v}),(i,a)=>(f(),t(`div`,{ref_key:`chartRef`,ref:d,style:r({width:n(h)(e.width),height:n(h)(e.height)})},null,4))}}),q=e({default:()=>J}),J=K;y([E,N,S,A,D,M,P,F,x,k,C,O]);var Y=b;d();var X=l({__name:`index`,props:{width:{type:[Number,String],default:`100%`},height:{type:[Number,String],default:`200px`},dataZoom:{type:Boolean,default:!1},option:{type:Object,required:!0}},setup(e){let c=e,l=m(null);function u(){if(l.value===null)return;let e=Y.getInstanceByDom(l.value);e==null&&(e=Y.init(l.value)),e.setOption(c.option,!0)}function d(){var e;l.value!==null&&((e=Y.getInstanceByDom(l.value))==null||e.resize())}s(()=>c.option,e=>{e&&i(()=>{u()})},{immediate:!0,deep:!0});let g=p(d,300,{maxWait:800});return o(()=>{i(()=>{u(),window.addEventListener(`resize`,g)})}),a(()=>{var e;l.value&&((e=Y.getInstanceByDom(l.value))==null||e.dispose(),window.removeEventListener(`resize`,g))}),(i,a)=>(f(),t(`div`,{ref_key:`chartRef`,ref:l,style:r({width:n(h)(e.width),height:n(h)(e.height)})},null,4))}}),Z=e({default:()=>Q}),Q=X;export{z as a,U as i,q as n,G as r,Z as t};