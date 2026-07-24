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
import{r as e}from"./rolldown-runtime.js?v=1784873523001";import{Cn as t,Dn as n,En as r,On as i,kn as a,nn as o,qn as s,sr as c}from"./vendor-utils.js?v=1784873523001";import{ht as l}from"./vendor-naive.js?v=1784873523001";import{jf as u}from"./app.js?v=1784873523001";import{n as d,r as f}from"./vendor-pdf.js?v=1784873523001";o(),f();var p=a({__name:`index`,setup(e){let a=()=>{u({width:1430,height:744,bgColor:`transparent`,hideClose:!0,component:i(()=>d(()=>import(`./feature-FileEditor.js?v=1784873523001`).then(e=>e.t),[]))})},o=()=>{a()},f=()=>{};return(e,i)=>{let a=l;return s(),t(`div`,null,[n(a,{onClick:o},{default:c(()=>[...i[0]||(i[0]=[r(`测试`,-1)])]),_:1}),n(a,{onClick:f},{default:c(()=>[...i[1]||(i[1]=[r(`消息`,-1)])]),_:1})])}}}),m=e({default:()=>h}),h=p;export{m as t};