;(() => {
	const hrefs = ["../css/feature-Terminal.css?v=1784873523001"]
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
import{Cn as e,Rn as t,Vn as n,Wn as r,ar as i,kn as a,nn as o,qn as s,y as c,yr as l}from"./vendor-utils.js?v=1784873523001";import{l as u}from"./vendor-vue.js?v=1784873523001";import{If as d}from"./app.js?v=1784873523001";import{Tf as f}from"./app-shared.js?v=1784873523001";import{a as p,i as m,n as h,r as g,t as _}from"./vendor-terminal.js?v=1784873523001";o();var v=p(),y=m(),b=g(),x=h(),S=_(),C=a({__name:`index`,props:{url:{default:`/ws_model`},id:{},data:{default:()=>[]}},emits:[`message`],setup(i,{emit:a}){let o=i,d=a,{t:p}=u(),{ws:m,status:h,send:g,close:_}=f(o.url,{verifyData:o.id?{id:o.id}:{},onMessage:(e,t)=>{let n=t.data;if(d(`message`,n),n.indexOf(`Authentication timeout.`)>-1&&(T.value=!0),(n.indexOf(`@127.0.0.1:`)!=-1||n.indexOf(`@localhost:`)!=-1)&&n.indexOf(`Authentication failed`)!=-1){_(),M();return}else if(n==`\\r\\nlogout\\r\\n`||n==`logout\\r\\n`||n==`\r
logout\r
`||n==`logout\r
`||n.search(/logout[\r\n]+$/)>-1){C.write(`\r`+p(`Component.Terminal.index_1`)+`\r`),M(),_();return}}}),C,w,T=l(!1),E=l(null),D=()=>{C=new v.Terminal({cursorBlink:!0,fontSize:14,fontFamily:`Monaco, Menlo, Consolas, 'Courier New', monospace`,theme:{background:`#333`,foreground:`#ececec`}}),w=new y.FitAddon,O(),k(),P(),I()},O=()=>{let e=m.value;e&&(C.loadAddon(w),C.loadAddon(new S.CanvasAddon),C.loadAddon(new x.WebLinksAddon),C.loadAddon(new b.AttachAddon(e)))},k=()=>{E.value&&C.open(E.value)},A=!1,j=()=>{A=!0},M=()=>{A=!1},N=()=>{let{data:e}=o;e.forEach(e=>{g(e)})},P=()=>{N(),C.focus(),C.onData(e=>{let t=m.value;e===`\r`&&T.value&&(T.value=!1,C.write(`\r
`),F()),t===null&&e===`\r`&&!A&&(j(),C.write(`\r
`+p(`Component.Terminal.index_2`)+`\r
`),F())})},F=()=>{P();let e=m.value;e&&C.loadAddon(new b.AttachAddon(e))},I=()=>{t(()=>{if(w.fit(),h.value!==`CLOSED`){let{cols:e,rows:t}=C;g({cols:e,rows:t,resize:1})}})},L=!0,R=new ResizeObserver(()=>{c(()=>{if(L){L=!1;return}I()},200)()}),z=()=>{let e=E.value;e&&R.observe(e)};return r(()=>{D(),z()}),n(()=>{_(),R==null||R.disconnect(),C==null||C.dispose()}),(t,n)=>(s(),e(`div`,{ref_key:`terminalRef`,ref:E,class:`w-full h-full`},null,512))}});o();var w=d(a({__name:`index`,props:{data:{},url:{}},emits:[`success`],setup(a,{expose:o,emit:d}){let{t:p}=u(),m=a,{data:h}=m,g=d,{ws:_,status:C,send:w,open:T,close:E}=f(m.url,{get verifyData(){return{...h}},onMessage:(e,t)=>{let n=t.data;if(n.indexOf(`Authentication timeout.`)>-1)k.value=!0;else if(n==`\\r\\nlogout\\r\\n`||n==`logout\\r\\n`||n==`\r
logout\r
`||n==`logout\r
`||n.search(/logout[\r\n]+$/)>-1){D.write(`\r`+p(`Component.Terminal.index_1`)+`\r`),L(),E();return}}}),D,O,k=l(!1),A=l(null),j=()=>{D=new v.Terminal({cursorBlink:!0,fontSize:14,fontFamily:`Monaco, Menlo, Consolas, 'Courier New', monospace`,theme:{background:`#333`,foreground:`#ececec`}}),O=new y.FitAddon,N(),P(),R(),B()},M=null,N=()=>{let e=_.value;e&&(D.loadAddon(O),D.loadAddon(new S.CanvasAddon),D.loadAddon(new x.WebLinksAddon),M=new b.AttachAddon(e),D.loadAddon(M),setTimeout(()=>{O.fit()},100))};i([_,C],([e,t])=>{if(t===`CLOSED`&&e){D.write(`\r
`+p(`Component.Terminal.index_2`)+`\r
`),setTimeout(()=>{T()},500);return}t===`OPEN`&&e&&(M&&M.dispose(),M=new b.AttachAddon(e),D.loadAddon(M),setTimeout(()=>{O.fit();let{cols:e,rows:t}=D;w({cols:e,rows:t,resize:1}),g(`success`)},100))},{immediate:!1});let P=()=>{A.value&&D.open(A.value)},F=!1,I=()=>{F=!0},L=()=>{F=!1},R=()=>{D.focus(),D.onData(e=>{let t=_.value;e===`\r`&&k.value&&(k.value=!1,D.write(`\r
`),z()),t===void 0&&e===`\r`&&!F&&(I(),D.write(`\r
`+p(`Component.Terminal.index_2`)+`\r
`),z())})},z=()=>{T(),R();let e=_.value;e&&D.loadAddon(new b.AttachAddon(e))},B=()=>{t(()=>{if(O.fit(),C.value!==`CLOSED`){let{cols:e,rows:t}=D;w({cols:e,rows:t,resize:1})}})},V=!0,H=new ResizeObserver(()=>{c(()=>{if(V){V=!1;return}B()},200)()}),U=()=>{let e=A.value;e&&H.observe(e)};return o({send:w}),r(async()=>{j(),U()}),n(()=>{H==null||H.disconnect(),E(),D==null||D.dispose()}),(t,n)=>(s(),e(`div`,{ref_key:`terminalRef`,ref:A,class:`w-full h-full`},null,512))}}),[[`__scopeId`,`data-v-2cd3b6dc`]]);export{C as n,w as t};