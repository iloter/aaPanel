System.register(["./index.vue_vue_type_script_setup_true_lang-legacy6.js?v=1723125373998","./index-legacy.js?v=1723125373998","./useLoading-legacy.js?v=1723125373998","./site-legacy.js?v=1723125373998","./vue-legacy.js?v=1723125373998","./Select-legacy.js?v=1723125373998","./pinia-legacy.js?v=1723125373998","./Tag-legacy.js?v=1723125373998","./Empty-legacy.js?v=1723125373998"],(function(e,a){"use strict";var l,t,s,n,u,i,d,r,c,o,_,g,p,v,y,f,j,m,b;return{setters:[e=>{l=e._,t=e.a},e=>{s=e.cV,n=e.k,u=e.n},e=>{i=e.u},e=>{d=e.a,r=e.b3},e=>{c=e.l,o=e.ad,_=e.r,g=e.S,p=e.Z,v=e.P,y=e.V,f=e._,j=e.W,m=e.b},e=>{b=e._},null,null,null],execute:function(){const a={class:"p-20px"},w={class:"w-150px"};e("default",c({__name:"batch",props:{data:{}},setup(e,{expose:c}){const{t:P}=o(),h=e,{rows:x}=h.data,S=s(),H=_(null),k=_([]),{loading:E,setLoading:L}=i();return(async()=>{try{L(!0);const{message:e}=await d();n(e)&&e.length>0?(k.value=e.map((e=>({label:e.name,value:e.id}))),H.value=e[0].id):(H.value=null,k.value=[])}finally{L(!1)}})(),c({onConfirm:async({hide:e})=>{await r((()=>{if(null===H.value)throw u.error(P("Site.PHP.add_site_46")),new Error(P("Site.PHP.add_site_46"));return{id:H.value,site_ids:x.map((e=>e.id))}})()),S.setRefresh(!0),e()}}),(e,s)=>{const n=b,u=l,i=t;return g(),p("div",a,[v(i,null,{default:y((()=>[v(u,{label:e.$t("Site.PHP.add_site_22"),"show-feedback":!1},{default:y((()=>[f("div",w,[v(n,{value:j(H),"onUpdate:value":s[0]||(s[0]=e=>m(H)?H.value=e:null),loading:j(E),options:j(k)},null,8,["value","loading","options"])])])),_:1},8,["label"])])),_:1})])}}}))}}}));