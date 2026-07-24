;(() => {
	const hrefs = ["../css/feature-Feedback.css?v=1784873523001"]
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
import{r as e}from"./rolldown-runtime.js?v=1784873523001";import{Cn as t,Dn as n,En as r,Er as i,On as a,Sn as o,Yn as s,Zr as c,_r as l,bn as u,kn as d,mn as f,mr as p,nn as m,nr as h,qn as g,qr as _,sr as v,xn as y,yr as b}from"./vendor-utils.js?v=1784873523001";import{l as x,o as S,p as C}from"./vendor-vue.js?v=1784873523001";import{F as w,I as T,P as E,Y as D,ht as O}from"./vendor-naive.js?v=1784873523001";import{$d as k,Ff as A,If as j,Pf as M,Qd as ee,gf as te,gp as N,hf as P,i as F,jf as I,pp as L}from"./app.js?v=1784873523001";import{N as R}from"./app-components.js?v=1784873523001";import{Bf as z}from"./app-shared.js?v=1784873523001";import{n as B,r as V}from"./vendor-pdf.js?v=1784873523001";m();var H={class:`banner`},U={class:`banner-title`},W={class:`ml-8px`},G={class:`pt-24px px-32px`},K={class:`mt-16px text-primary`},q={class:`flex justify-center mt-20px`},J=d({__name:`submit`,props:{entryId:{}},emits:[`close`],setup(e,{emit:a}){let{t:o}=x(),s=S(),l=a,d=``,f=e,m=b(``),h=()=>{let e=s.currentRoute.value.path,t={site:502,wp:503,ftp:504,database:505,docker:506,security:507,waf:508,mail:509,files:510,logs:511,ssl_domain:512,aapanelsub:513,terminal:514,crontab:515,softs:516,setting:517,control:518};for(let n in t)if(e.includes(n))return t[n];return 501},_=()=>({questions:{[d]:m.value},submit_entry:f.entryId||h()}),y=async()=>{if(m.value.trim()===``){M.error(o(`Component.Feedback.index_5`));return}await P(_()),l(`close`),C()},C=()=>{let e=I({hideClose:!0,content:()=>n(`div`,{class:`flex-center flex-col w-230px h-124px bg-#F1F9F3`},[n(`img`,{class:`w-56px`,src:z},null),n(`div`,{class:`mt-16px`},[o(`Component.Feedback.index_6`)])])});setTimeout(()=>{e.hide()},3e3)};return(async()=>{let{message:e}=await ee();N(e)&&L(e.res)&&e.res.length>0&&(d=e.res[0].id)})(),(e,a)=>{let o=R,s=O;return g(),t(`div`,null,[u(`div`,H,[u(`div`,U,[u(`span`,W,c(e.$t(`Component.Feedback.index_1`)),1)])]),u(`div`,G,[n(o,{value:i(m),"onUpdate:value":a[0]||(a[0]=e=>p(m)?m.value=e:null),rows:6},{default:v(()=>[u(`p`,null,c(e.$t(`Component.Feedback.index_2`)),1),u(`p`,null,c(e.$t(`Component.Feedback.index_3`)),1)]),_:1},8,[`value`]),u(`div`,K,c(e.$t(`Component.Feedback.index_4`)),1),u(`div`,q,[n(s,{type:`primary`,class:`w-120px`,onClick:y},{default:v(()=>[r(c(e.$t(`Public.Btn.Submit`)),1)]),_:1})])])])}}}),ne=e({default:()=>Y}),Y=j(J,[[`__scopeId`,`data-v-5cf3b033`]]);m();var X={class:`flex border-1px border-solid border-#f3adaa`},Z=[`onClick`],re={class:`flex border-1px border-solid border-#f4cf8f`},ie=[`onClick`],ae={class:`flex border-1px border-solid border-#b8e29f`},oe=[`onClick`],se=j(d({__name:`rating`,props:{value:{},valueModifiers:{}},emits:[`update:value`],setup(e){let n=h(e,`value`),r=e=>{n.value=e};return(e,i)=>{let a=T;return g(),y(a,{class:`justify-center! mb-16px`,size:20},{default:v(()=>[u(`div`,null,[u(`div`,X,[(g(),t(f,null,s(6,e=>u(`div`,{key:e,class:_([`rating-item`,`danger-item`,{active:n.value===e}]),onClick:t=>r(e)},[u(`span`,null,c(e),1)],10,Z)),64))]),i[0]||(i[0]=u(`div`,{class:`rating-label danger-text`},`No`,-1))]),u(`div`,null,[u(`div`,re,[(g(),t(f,null,s(2,e=>u(`div`,{key:e+6,class:_([`rating-item`,`warning-item`,{active:n.value===e+6}]),onClick:t=>r(e+6)},[u(`span`,null,c(e+6),1)],10,ie)),64))]),i[1]||(i[1]=u(`div`,{class:`rating-label warning-text`},`Yes`,-1))]),u(`div`,null,[u(`div`,ae,[(g(),t(f,null,s(2,e=>u(`div`,{key:e+8,class:_([`rating-item`,`success-item`,{active:n.value===e+8}]),onClick:t=>r(e+8)},[u(`span`,null,c(e+8),1)],10,oe)),64))]),i[2]||(i[2]=u(`div`,{class:`rating-label success-text`},`Must`,-1))])]),_:1})}}}),[[`__scopeId`,`data-v-d5502028`]]);m();var ce={class:`banner`},le={class:`banner-title`},ue={class:`ml-8px`},de={key:0,class:`px-24px`},fe={class:`text-primary`},pe={class:`flex justify-center my-20px`},me=d({__name:`form`,emits:[`close`],setup(e,{emit:a}){let{t:d}=x(),m=b(0),h=a,_=l({}),S=l({}),C=b(null),T=b([]),D=async()=>{var e;await((e=C.value)==null?void 0:e.validate()),await te({questions:JSON.stringify(T.value.reduce((e,t)=>(e[t.id]=_[t.id],e),{})),rate:m.value,product_type:1}),h(`close`),A()},A=()=>{let e=I({hideClose:!0,content:()=>n(`div`,{class:`flex-center flex-col w-230px h-124px bg-#F1F9F3`},[n(`img`,{class:`w-56px`,src:z},null),n(`div`,{class:`mt-16px`},[d(`Component.Feedback.index_6`)])])});setTimeout(()=>{e.hide()},3e3)};return(async()=>{let{message:e}=await k();N(e)&&(T.value=e.res,e.res.forEach(e=>{_[e.id]=``}),e.res.forEach(e=>{e.required===1&&(S[e.id]={required:!0,message:e.question,trigger:[`blur`,`change`]})}))})(),(e,a)=>{let l=R,d=E,h=w,b=O;return g(),t(`div`,null,[u(`div`,ce,[u(`div`,le,[u(`span`,ue,c(e.$t(`Component.Feedback.index_1`)),1)])]),a[1]||(a[1]=u(`div`,{class:`text-center text-20px font-bold my-20px`},`Would you recommend aaPanel?`,-1)),n(se,{value:i(m),"onUpdate:value":a[0]||(a[0]=e=>p(m)?m.value=e:null)},null,8,[`value`]),i(m)?(g(),t(`div`,de,[n(h,{model:i(_),rules:i(S),ref_key:`formRef`,ref:C},{default:v(()=>[(g(!0),t(f,null,s(i(T),e=>(g(),y(d,{label:e.question,path:e.id,key:e.id},{default:v(()=>[n(l,{value:i(_)[e.id],"onUpdate:value":t=>i(_)[e.id]=t,placeholder:e.hint},null,8,[`value`,`onUpdate:value`,`placeholder`])]),_:2},1032,[`label`,`path`]))),128))]),_:1},8,[`model`,`rules`]),u(`div`,fe,c(e.$t(`Component.Feedback.index_4`)),1),u(`div`,pe,[n(b,{type:`primary`,class:`w-120px`,onClick:D},{default:v(()=>[r(c(e.$t(`Public.Btn.Submit`)),1)]),_:1})])])):o(``,!0)])}}}),Q=e({default:()=>he}),he=j(me,[[`__scopeId`,`data-v-e70d5400`]]);m(),V();var ge={class:`nps-container`},_e=d({__name:`index`,setup(e){let{aiAssistant:r}=C(F()),s=S(),c=()=>{I({width:600,component:a(()=>B(()=>Promise.resolve().then(()=>Q),void 0))})},l=async()=>{s.push(`/ai/chat`)};return(e,a)=>{let s=D,d=A;return g(),t(`div`,ge,[i(r).isShow?(g(),y(s,{key:0,trigger:`hover`,placement:`left`},{trigger:v(()=>[u(`div`,{class:`nps-box`,onClick:l},[...a[0]||(a[0]=[u(`i`,{class:`i-common-ai w-18px h-18px`},null,-1)])])]),default:v(()=>[a[1]||(a[1]=u(`span`,null,`Click open AI Assistant`,-1))]),_:1})):o(``,!0),n(s,{trigger:`hover`,placement:`left`},{trigger:v(()=>[u(`div`,{class:`nps-box`,onClick:c},[n(d,{name:`common-demand`,size:18})])]),default:v(()=>[a[2]||(a[2]=u(`span`,null,`Click open survey`,-1))]),_:1})])}}}),ve=e({default:()=>$}),$=j(_e,[[`__scopeId`,`data-v-5d33e650`]]);export{ve as n,ne as r,$ as t};