;(() => {
	const hrefs = ["../css/legacy-layout.css?v=1784873523001"]
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
import{r as e}from"./rolldown-runtime.js?v=1784873523001";import{$n as t,Dn as n,En as r,Er as i,Jr as a,On as o,Zn as s,Zr as c,bn as l,f as u,hn as d,kn as f,nn as p,qn as m,sr as h,xn as g,yn as _,yr as v}from"./vendor-utils.js?v=1784873523001";import{a as y,l as b,n as x,p as S}from"./vendor-vue.js?v=1784873523001";import{D as C,E as w,I as T,O as E,T as D,ht as O}from"./vendor-naive.js?v=1784873523001";import{Af as k,Ff as A,If as j,Lf as M,gs as N,hs as P,i as F,jf as I,mn as L,n as R}from"./app.js?v=1784873523001";import{n as z,r as B}from"./vendor-pdf.js?v=1784873523001";import{t as V}from"./feature-Feedback.js?v=1784873523001";p(),B();function H(){I({width:800,minHeight:`550`,title:M.global.t(`Layout.MessageBox.index_6`),component:o(()=>z(()=>import(`./feature-MessageBox.js?v=1784873523001`).then(e=>e.n),[]))})}p();var U={class:`sider-header`},W={class:`text`},G=j(f({__name:`LayoutSider`,setup(e){let t=y(),r=P(),{address:a,taskCount:o}=S(F()),{t:s}=b(),u=_(()=>{var e;return(e=t.meta)!=null&&e.activeMenu?t.meta.activeMenu:t.name}),d=_(()=>{let e=[];return r.showMenus.forEach(t=>{e.push({key:t.name,label:f(t)})}),e.push({key:`logout`,label:f({to:``,icon:`logout`,name:``,label:s(`Layout.Sider.logout_1`),showName:``})}),e}),f=e=>()=>n(x,{class:`n-menu-item-link ${e.icon}`,to:{name:e.to}},{default:()=>[e.label]}),p=e=>{e===`logout`&&v(),R(`panel_menu_old`,e)},v=()=>{k({title:s(`Layout.Sider.logout_2`),content:s(`Layout.Sider.logout_3`),onConfirm:()=>{window.location.href=`/login?dologin=True`}})};return r.generateRoutes(),r.generateHideNames(),(e,t)=>{let r=D,s=w;return m(),g(s,{width:184,style:{zIndex:998}},{default:h(()=>[l(`div`,U,[t[1]||(t[1]=l(`img`,{class:`w-22px mr-8px`,src:`data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABYAAAAQCAYAAAAS7Y8mAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAdgAAAHYBTnsmCAAAABx0RVh0U29mdHdhcmUAQWRvYmUgRmlyZXdvcmtzIENTNui8sowAAAGPSURBVDiNldQ9ixRBEAbgZ3Zn1fVOuQU/wK9AMDDS1MvuRxj5CwTBP2CiYmYmGBsYGRsaa2qkkSiCgRd4y3ri3XqzbdDV7Lgs7uwLRc90V1dXv29VVymluxiiRoVkNaoYG7wN+9chpTTBBn7jKA5YhYR+JPQEDxYd6rAPeIwDnOgQuMEIz3F8mUMdC9/wqkPAxb1P0Yv/6ziLX/hTy9c6jXPYXSPwBQywF+Mz7GCCSRGMbqK1Ufwbmb4beI9TuNZFqFWoZCH7Mp0XcaX33y3dUDKfmRdD1bM+BYuoWtaEKeIdyqSvg5+RZSWX6Ri3ZUqmRbxjcqnsx3cyF7Utbpmf4YxcapXcWFNcjiSbOk7Yxhu5BocRaGBeoyXYNII32MTJsJ7cvR/D92aN1xFsFA6HYZ/iiiWjTVyVGyrhBz7jXSQxxq3wPahxJ7JuX30sd9IoshviC77KzdSmag+XYm4QNq0tF+0e7sc1SwPs4xFeLPHvt2ibsfwl24rFl/KLV/jdCho2ZC3a+I6HOB9rR38B10ZjDE49T6kAAAAASUVORK5CYII=`,alt:``},null,-1)),l(`div`,W,c(i(a)),1),l(`div`,{id:`task`,class:`message`,onClick:t[0]||(t[0]=(...e)=>i(H)&&i(H)(...e))},c(i(o)),1)]),n(r,{value:i(u),"root-indent":0,options:i(d),"onUpdate:value":p},null,8,[`value`,`options`])]),_:1})}}}),[[`__scopeId`,`data-v-3dfbd727`]]);p();var K=f({__name:`LayoutMain`,setup(e){let r=[],a=(e,t)=>{e.forEach(e=>{var n,r;(n=e.meta)!=null&&n.keepAlive&&e.name&&t.push(e.name),!(e==null||(r=e.children)==null)&&r.length&&a(e.children,t)})};a(N,r);let o=_(()=>Math.random());return(e,a)=>{let c=s(`router-view`);return m(),g(c,{key:i(o)},{default:h(({Component:e,route:i})=>[(m(),g(d,{include:r},[(m(),g(t(e),{key:i.path}))],1024)),n(V)]),_:1})}}});p();var q={class:`mr-6px`},J={class:`flex items-center`},Y=f({__name:`LayoutFooter`,setup(e){let t=new Date().getFullYear(),a=()=>{window.open(`https://t.me/aapanel_official`)},o=()=>{window.open(`https://discord.gg/Tya5yceBpd`)},s=()=>{window.open(`mailto:support@aapanel.com`)};return(e,u)=>{let d=L,f=A,p=O,_=T,v=C;return m(),g(v,{id:`layout-footer`},{default:h(()=>[n(_,{class:`h-52px`,justify:`center`,align:`center`},{default:h(()=>[l(`div`,null,[l(`span`,q,c(e.$t(`Layout.Footer.index_1`,[i(t)])),1),n(d,{href:`https://www.aapanel.com`,target:`_blank`},{default:h(()=>[...u[0]||(u[0]=[r(`(www.aapanel.com)`,-1)])]),_:1})]),l(`div`,J,[n(d,{href:`http://forum.aapanel.com`,target:`_blank`},{default:h(()=>[...u[1]||(u[1]=[r(`Forum`,-1)])]),_:1}),n(d,{class:`ml-12px`,href:`https://doc.aapanel.com/web/#/3?page_id=117`,target:`_blank`},{default:h(()=>[r(c(e.$t(`Layout.Footer.index_3`)),1)]),_:1}),u[5]||(u[5]=l(`span`,{class:`ml-12px`},`Support: `,-1)),n(p,{class:`ml-8px`,secondary:``,size:`small`,onClick:a},{default:h(()=>[n(f,{name:`telegram`,color:`#A6ADB3`}),u[2]||(u[2]=l(`span`,{class:`ml-4px`},`Telegram`,-1))]),_:1}),n(p,{class:`ml-8px`,secondary:``,size:`small`,onClick:o},{default:h(()=>[n(f,{name:`discord`,size:`14`,color:`#A6ADB3`}),u[3]||(u[3]=l(`span`,{class:`ml-4px`},`Discord`,-1))]),_:1}),n(p,{class:`ml-8px`,secondary:``,size:`small`,onClick:s},{default:h(()=>[n(f,{name:`email`,size:`14`,color:`#A6ADB3`}),u[4]||(u[4]=l(`span`,{class:`ml-4px`},`Email: support@aapanel.com`,-1))]),_:1})])]),_:1})]),_:1})}}});p();var X=f({__name:`index`,setup(e){let t=F(),{mainHeight:r,bodyMinWidth:o}=S(t),s=_(()=>r.value===0?`auto`:`${r.value}px`),c=v();return u(c,e=>{let{width:n,height:r}=e[0].contentRect,i=document.querySelector(`#layout-footer`),a=i==null?void 0:i.getBoundingClientRect(),o=(a==null?void 0:a.height)||0;t.setMainWidth(n),t.setMainHeight(r-o)}),(e,t)=>{let r=E;return m(),g(r,{class:`h-full`,"has-sider":``},{default:h(()=>[n(G),n(r,{ref_key:`layoutRef`,ref:c,id:`layout-content`,class:`bt-layout`,style:a({minWidth:i(o)+`px`})},{default:h(()=>[l(`div`,{id:`layout-main`,style:a({minHeight:i(s)})},[n(K)],4),n(Y)]),_:1},8,[`style`])]),_:1})}}}),Z=e({default:()=>Q}),Q=j(X,[[`__scopeId`,`data-v-11e34eb6`]]);export{Z as t};