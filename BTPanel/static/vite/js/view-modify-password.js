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
import{r as e}from"./rolldown-runtime.js?v=1784873523001";import{Cn as t,Dn as n,En as r,Er as i,Zr as a,_r as o,bn as s,kn as c,mn as l,nn as u,qn as d,sr as f,wt as p,yr as m}from"./vendor-utils.js?v=1784873523001";import{l as h,s as g}from"./vendor-vue.js?v=1784873523001";import{P as _,ht as v,xt as y}from"./vendor-naive.js?v=1784873523001";import{Af as b,Eu as x,bu as S,mn as C,up as w}from"./app.js?v=1784873523001";import{Ki as T}from"./app-components.js?v=1784873523001";import{bf as E}from"./app-shared.js?v=1784873523001";import{c as D}from"./app-form.js?v=1784873523001";u();var O={class:`flex-center flex-col pt-8%`},k={class:`pt-44px`},A={class:`mb-24px text-center text-20p`},j={class:`flex justify-end mt-16px`},M=c({__name:`index`,setup(e){let{t:c}=h(),u=m(null),M=o({password1:``,password2:``,userpassword:``}),N={password1:{trigger:[`blur`,`input`],validator:()=>p(M.password1)?Error(c(`Config.Panel.index_67`)):M.password1.length<6?Error(c(`Password.index_6`)):!0},password2:{trigger:[`blur`,`input`],validator:()=>p(M.password2)?Error(c(`Config.Panel.index_69`)):M.password1===M.password2||Error(c(`Config.Panel.index_70`))},userpassword:{trigger:[`blur`,`input`],required:!0,message:c(`Config.Panel.index_67`)}},P=async()=>{var e;await((e=u.value)==null?void 0:e.validate()),await x({password1:E(M.password1),password2:E(M.password2),userpassword:E(M.userpassword)}),w(`/login?dologin=True`,1500)},F=()=>{b({title:c(`Password.index_7`),content:()=>n(l,null,[n(g,{tag:`div`,scope:`global`,keypath:`Password.index_8`},{text_1:()=>n(`span`,{class:`text-error`},[c(`Password.index_9`)])})]),onConfirm:async()=>{await S(),w(`/login?dologin=True`,1500)}})};return(e,o)=>{let c=y,l=_,p=D,m=v,h=C,g=T;return d(),t(`div`,O,[s(`div`,k,[s(`h3`,A,a(e.$t(`Password.index_1`)),1)]),n(g,{ref_key:`formRef`,ref:u,model:i(M),rules:N,size:`large`,class:`w-500px p-32px pt-0`},{default:f(()=>[n(l,{path:`userpassword`},{default:f(()=>[n(c,{value:i(M).userpassword,"onUpdate:value":o[0]||(o[0]=e=>i(M).userpassword=e),placeholder:e.$t(`Old Password`)},null,8,[`value`,`placeholder`])]),_:1}),n(l,{path:`password1`},{default:f(()=>[n(p,{value:i(M).password1,"onUpdate:value":o[1]||(o[1]=e=>i(M).password1=e),length:10,default:!1,placeholder:e.$t(`Password.index_2`)},null,8,[`value`,`placeholder`])]),_:1}),n(l,{path:`password2`},{default:f(()=>[n(c,{value:i(M).password2,"onUpdate:value":o[2]||(o[2]=e=>i(M).password2=e),placeholder:e.$t(`Password.index_3`)},null,8,[`value`,`placeholder`])]),_:1}),n(l,{"show-feedback":!1},{default:f(()=>[n(m,{type:`primary`,block:``,onClick:P},{default:f(()=>[r(a(e.$t(`Password.index_4`)),1)]),_:1})]),_:1}),s(`div`,j,[n(h,{onClick:F},{default:f(()=>[r(a(e.$t(`Password.index_5`)),1)]),_:1})])]),_:1},8,[`model`])])}}}),N=e({default:()=>P}),P=M;export{N as t};