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
import{r as e}from"./rolldown-runtime.js?v=1784873523001";import{Cn as t,Dn as n,Er as r,Zr as i,bn as a,kn as o,nn as s,qn as c}from"./vendor-utils.js?v=1784873523001";import{c as l,l as u,s as d,t as f,u as p}from"./view-mail.js?v=1784873523001";s();var m={class:`p-40px`},h=o({__name:`index`,setup(e){return(e,o)=>(c(),t(`div`,m,[a(`div`,null,` columns_source:`+i(r(u)),1),a(`div`,null,` column_map:`+i(r(l)),1),a(`div`,null,` cell_map:`+i(r(d)),1),a(`div`,null,` comp_map:`+i(r(p)),1),n(f)]))}}),g=e({default:()=>_}),_=h;export{g as t};