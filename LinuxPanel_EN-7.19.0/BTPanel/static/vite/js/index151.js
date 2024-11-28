import{c as e,g as t}from"./__commonjsHelpers__.js?v=1732601582185";import{r as n,a0 as a}from"./page_layout.js?v=1732601582185";import{bc as r}from"./naive.js?v=1732601582185";import{d as i,W as o,r as s,e as l,w as u,n as c,f as d,M as p}from"./vue.js?v=1732601582185";var g,f,h={exports:{}};g=h,f=function(e){var t=/(?:^|\s)lang(?:uage)?-([\w-]+)(?=\s|$)/i,n=0,a={},r={manual:e.Prism&&e.Prism.manual,disableWorkerMessageHandler:e.Prism&&e.Prism.disableWorkerMessageHandler,util:{encode:function e(t){return t instanceof i?new i(t.type,e(t.content),t.alias):Array.isArray(t)?t.map(e):t.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/\u00a0/g," ")},type:function(e){return Object.prototype.toString.call(e).slice(8,-1)},objId:function(e){return e.__id||Object.defineProperty(e,"__id",{value:++n}),e.__id},clone:function e(t,n){var a,i;switch(n=n||{},r.util.type(t)){case"Object":if(i=r.util.objId(t),n[i])return n[i];for(var o in a={},n[i]=a,t)t.hasOwnProperty(o)&&(a[o]=e(t[o],n));return a;case"Array":return i=r.util.objId(t),n[i]?n[i]:(a=[],n[i]=a,t.forEach((function(t,r){a[r]=e(t,n)})),a);default:return t}},getLanguage:function(e){for(;e;){var n=t.exec(e.className);if(n)return n[1].toLowerCase();e=e.parentElement}return"none"},setLanguage:function(e,n){e.className=e.className.replace(RegExp(t,"gi"),""),e.classList.add("language-"+n)},currentScript:function(){if("undefined"==typeof document)return null;if("currentScript"in document)return document.currentScript;try{throw new Error}catch(a){var e=(/at [^(\r\n]*\((.*):[^:]+:[^:]+\)$/i.exec(a.stack)||[])[1];if(e){var t=document.getElementsByTagName("script");for(var n in t)if(t[n].src==e)return t[n]}return null}},isActive:function(e,t,n){for(var a="no-"+t;e;){var r=e.classList;if(r.contains(t))return!0;if(r.contains(a))return!1;e=e.parentElement}return!!n}},languages:{plain:a,plaintext:a,text:a,txt:a,extend:function(e,t){var n=r.util.clone(r.languages[e]);for(var a in t)n[a]=t[a];return n},insertBefore:function(e,t,n,a){var i=(a=a||r.languages)[e],o={};for(var s in i)if(i.hasOwnProperty(s)){if(s==t)for(var l in n)n.hasOwnProperty(l)&&(o[l]=n[l]);n.hasOwnProperty(s)||(o[s]=i[s])}var u=a[e];return a[e]=o,r.languages.DFS(r.languages,(function(t,n){n===u&&t!=e&&(this[t]=o)})),o},DFS:function e(t,n,a,i){i=i||{};var o=r.util.objId;for(var s in t)if(t.hasOwnProperty(s)){n.call(t,s,t[s],a||s);var l=t[s],u=r.util.type(l);"Object"!==u||i[o(l)]?"Array"!==u||i[o(l)]||(i[o(l)]=!0,e(l,n,s,i)):(i[o(l)]=!0,e(l,n,null,i))}}},plugins:{},highlightAll:function(e,t){r.highlightAllUnder(document,e,t)},highlightAllUnder:function(e,t,n){var a={callback:n,container:e,selector:'code[class*="language-"], [class*="language-"] code, code[class*="lang-"], [class*="lang-"] code'};r.hooks.run("before-highlightall",a),a.elements=Array.prototype.slice.apply(a.container.querySelectorAll(a.selector)),r.hooks.run("before-all-elements-highlight",a);for(var i,o=0;i=a.elements[o++];)r.highlightElement(i,!0===t,a.callback)},highlightElement:function(t,n,a){var i=r.util.getLanguage(t),o=r.languages[i];r.util.setLanguage(t,i);var s=t.parentElement;s&&"pre"===s.nodeName.toLowerCase()&&r.util.setLanguage(s,i);var l={element:t,language:i,grammar:o,code:t.textContent};function u(e){l.highlightedCode=e,r.hooks.run("before-insert",l),l.element.innerHTML=l.highlightedCode,r.hooks.run("after-highlight",l),r.hooks.run("complete",l),a&&a.call(l.element)}if(r.hooks.run("before-sanity-check",l),(s=l.element.parentElement)&&"pre"===s.nodeName.toLowerCase()&&!s.hasAttribute("tabindex")&&s.setAttribute("tabindex","0"),!l.code)return r.hooks.run("complete",l),void(a&&a.call(l.element));if(r.hooks.run("before-highlight",l),l.grammar)if(n&&e.Worker){var c=new Worker(r.filename);c.onmessage=function(e){u(e.data)},c.postMessage(JSON.stringify({language:l.language,code:l.code,immediateClose:!0}))}else u(r.highlight(l.code,l.grammar,l.language));else u(r.util.encode(l.code))},highlight:function(e,t,n){var a={code:e,grammar:t,language:n};if(r.hooks.run("before-tokenize",a),!a.grammar)throw new Error('The language "'+a.language+'" has no grammar.');return a.tokens=r.tokenize(a.code,a.grammar),r.hooks.run("after-tokenize",a),i.stringify(r.util.encode(a.tokens),a.language)},tokenize:function(e,t){var n=t.rest;if(n){for(var a in n)t[a]=n[a];delete t.rest}var r=new l;return u(r,r.head,e),s(e,r,t,r.head,0),function(e){for(var t=[],n=e.head.next;n!==e.tail;)t.push(n.value),n=n.next;return t}(r)},hooks:{all:{},add:function(e,t){var n=r.hooks.all;n[e]=n[e]||[],n[e].push(t)},run:function(e,t){var n=r.hooks.all[e];if(n&&n.length)for(var a,i=0;a=n[i++];)a(t)}},Token:i};function i(e,t,n,a){this.type=e,this.content=t,this.alias=n,this.length=0|(a||"").length}function o(e,t,n,a){e.lastIndex=t;var r=e.exec(n);if(r&&a&&r[1]){var i=r[1].length;r.index+=i,r[0]=r[0].slice(i)}return r}function s(e,t,n,a,l,d){for(var p in n)if(n.hasOwnProperty(p)&&n[p]){var g=n[p];g=Array.isArray(g)?g:[g];for(var f=0;f<g.length;++f){if(d&&d.cause==p+","+f)return;var h=g[f],m=h.inside,v=!!h.lookbehind,b=!!h.greedy,y=h.alias;if(b&&!h.pattern.global){var w=h.pattern.toString().match(/[imsuy]*$/)[0];h.pattern=RegExp(h.pattern.source,w+"g")}for(var E=h.pattern||h,k=a.next,x=l;k!==t.tail&&!(d&&x>=d.reach);x+=k.value.length,k=k.next){var A=k.value;if(t.length>e.length)return;if(!(A instanceof i)){var S,C=1;if(b){if(!(S=o(E,x,e,v))||S.index>=e.length)break;var T=S.index,P=S.index+S[0].length,N=x;for(N+=k.value.length;T>=N;)N+=(k=k.next).value.length;if(x=N-=k.value.length,k.value instanceof i)continue;for(var L=k;L!==t.tail&&(N<P||"string"==typeof L.value);L=L.next)C++,N+=L.value.length;C--,A=e.slice(x,N),S.index-=x}else if(!(S=o(E,0,A,v)))continue;T=S.index;var R=S[0],z=A.slice(0,T),j=A.slice(T+R.length),O=x+A.length;d&&O>d.reach&&(d.reach=O);var H=k.prev;if(z&&(H=u(t,H,z),x+=z.length),c(t,H,C),k=u(t,H,new i(p,m?r.tokenize(R,m):R,y,R)),j&&u(t,k,j),C>1){var I={cause:p+","+f,reach:O};s(e,t,n,k.prev,x,I),d&&I.reach>d.reach&&(d.reach=I.reach)}}}}}}function l(){var e={value:null,prev:null,next:null},t={value:null,prev:e,next:null};e.next=t,this.head=e,this.tail=t,this.length=0}function u(e,t,n){var a=t.next,r={value:n,prev:t,next:a};return t.next=r,a.prev=r,e.length++,r}function c(e,t,n){for(var a=t.next,r=0;r<n&&a!==e.tail;r++)a=a.next;t.next=a,a.prev=t,e.length-=r}if(e.Prism=r,i.stringify=function e(t,n){if("string"==typeof t)return t;if(Array.isArray(t)){var a="";return t.forEach((function(t){a+=e(t,n)})),a}var i={type:t.type,content:e(t.content,n),tag:"span",classes:["token",t.type],attributes:{},language:n},o=t.alias;o&&(Array.isArray(o)?Array.prototype.push.apply(i.classes,o):i.classes.push(o)),r.hooks.run("wrap",i);var s="";for(var l in i.attributes)s+=" "+l+'="'+(i.attributes[l]||"").replace(/"/g,"&quot;")+'"';return"<"+i.tag+' class="'+i.classes.join(" ")+'"'+s+">"+i.content+"</"+i.tag+">"},!e.document)return e.addEventListener?(r.disableWorkerMessageHandler||e.addEventListener("message",(function(t){var n=JSON.parse(t.data),a=n.language,i=n.code,o=n.immediateClose;e.postMessage(r.highlight(i,r.languages[a],a)),o&&e.close()}),!1),r):r;var d=r.util.currentScript();function p(){r.manual||r.highlightAll()}if(d&&(r.filename=d.src,d.hasAttribute("data-manual")&&(r.manual=!0)),!r.manual){var g=document.readyState;"loading"===g||"interactive"===g&&d&&d.defer?document.addEventListener("DOMContentLoaded",p):window.requestAnimationFrame?window.requestAnimationFrame(p):window.setTimeout(p,16)}return r}("undefined"!=typeof window?window:"undefined"!=typeof WorkerGlobalScope&&self instanceof WorkerGlobalScope?self:{}),g.exports&&(g.exports=f),void 0!==e&&(e.Prism=f);const m=t(h.exports);!function(e){function t(e){return RegExp("(^(?:"+e+"):[ \t]*(?![ \t]))[^]+","i")}e.languages.http={"request-line":{pattern:/^(?:CONNECT|DELETE|GET|HEAD|OPTIONS|PATCH|POST|PRI|PUT|SEARCH|TRACE)\s(?:https?:\/\/|\/)\S*\sHTTP\/[\d.]+/m,inside:{method:{pattern:/^[A-Z]+\b/,alias:"property"},"request-target":{pattern:/^(\s)(?:https?:\/\/|\/)\S*(?=\s)/,lookbehind:!0,alias:"url",inside:e.languages.uri},"http-version":{pattern:/^(\s)HTTP\/[\d.]+/,lookbehind:!0,alias:"property"}}},"response-status":{pattern:/^HTTP\/[\d.]+ \d+ .+/m,inside:{"http-version":{pattern:/^HTTP\/[\d.]+/,alias:"property"},"status-code":{pattern:/^(\s)\d+(?=\s)/,lookbehind:!0,alias:"number"},"reason-phrase":{pattern:/^(\s).+/,lookbehind:!0,alias:"string"}}},header:{pattern:/^[\w-]+:.+(?:(?:\r\n?|\n)[ \t].+)*/m,inside:{"header-value":[{pattern:t(/Content-Security-Policy/.source),lookbehind:!0,alias:["csp","languages-csp"],inside:e.languages.csp},{pattern:t(/Public-Key-Pins(?:-Report-Only)?/.source),lookbehind:!0,alias:["hpkp","languages-hpkp"],inside:e.languages.hpkp},{pattern:t(/Strict-Transport-Security/.source),lookbehind:!0,alias:["hsts","languages-hsts"],inside:e.languages.hsts},{pattern:t(/[^:]+/.source),lookbehind:!0}],"header-name":{pattern:/^[^:]+/,alias:"keyword"},punctuation:/^:/}}};var n,a,r,i=e.languages,o={"application/javascript":i.javascript,"application/json":i.json||i.javascript,"application/xml":i.xml,"text/xml":i.xml,"text/html":i.html,"text/css":i.css,"text/plain":i.plain},s={"application/json":!0,"application/xml":!0};for(var l in o)if(o[l]){n=n||{};var u=s[l]?(r=void 0,r=(a=l).replace(/^[a-z]+\//,""),"(?:"+a+"|\\w+/(?:[\\w.-]+\\+)+"+r+"(?![+\\w.-]))"):l;n[l.replace(/\//g,"-")]={pattern:RegExp("("+/content-type:\s*/.source+u+/(?:(?:\r\n?|\n)[\w-].*)*(?:\r(?:\n|(?!\n))|\n)/.source+")"+/[^ \t\w-][\s\S]*/.source,"i"),lookbehind:!0,inside:o[l]}}n&&e.languages.insertBefore("http","header",n)}(Prism),Prism.languages.log={string:{pattern:/"(?:[^"\\\r\n]|\\.)*"|'(?![st] | \w)(?:[^'\\\r\n]|\\.)*'/,greedy:!0},exception:{pattern:/(^|[^\w.])[a-z][\w.]*(?:Error|Exception):.*(?:(?:\r\n?|\n)[ \t]*(?:at[ \t].+|\.{3}.*|Caused by:.*))+(?:(?:\r\n?|\n)[ \t]*\.\.\. .*)?/,lookbehind:!0,greedy:!0,alias:["javastacktrace","language-javastacktrace"],inside:Prism.languages.javastacktrace||{keyword:/\bat\b/,function:/[a-z_][\w$]*(?=\()/,punctuation:/[.:()]/}},level:[{pattern:/\b(?:ALERT|CRIT|CRITICAL|EMERG|EMERGENCY|ERR|ERROR|FAILURE|FATAL|SEVERE)\b/,alias:["error","important"]},{pattern:/\b(?:WARN|WARNING|WRN)\b/,alias:["warning","important"]},{pattern:/\b(?:DISPLAY|INF|INFO|NOTICE|STATUS)\b/,alias:["info","keyword"]},{pattern:/\b(?:DBG|DEBUG|FINE)\b/,alias:["debug","keyword"]},{pattern:/\b(?:FINER|FINEST|TRACE|TRC|VERBOSE|VRB)\b/,alias:["trace","comment"]}],property:{pattern:/((?:^|[\]|])[ \t]*)[a-z_](?:[\w-]|\b\/\b)*(?:[. ]\(?\w(?:[\w-]|\b\/\b)*\)?)*:(?=\s)/im,lookbehind:!0},separator:{pattern:/(^|[^-+])-{3,}|={3,}|\*{3,}|- - /m,lookbehind:!0,alias:"comment"},url:/\b(?:file|ftp|https?):\/\/[^\s|,;'"]*[^\s|,;'">.]/,email:{pattern:/(^|\s)[-\w+.]+@[a-z][a-z0-9-]*(?:\.[a-z][a-z0-9-]*)+(?=\s)/,lookbehind:!0,alias:"url"},"ip-address":{pattern:/\b(?:\d{1,3}(?:\.\d{1,3}){3})\b/,alias:"constant"},"mac-address":{pattern:/\b[a-f0-9]{2}(?::[a-f0-9]{2}){5}\b/i,alias:"constant"},domain:{pattern:/(^|\s)[a-z][a-z0-9-]*(?:\.[a-z][a-z0-9-]*)*\.[a-z][a-z0-9-]+(?=\s)/,lookbehind:!0,alias:"constant"},uuid:{pattern:/\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b/i,alias:"constant"},hash:{pattern:/\b(?:[a-f0-9]{32}){1,2}\b/i,alias:"constant"},"file-path":{pattern:/\b[a-z]:[\\/][^\s|,;:(){}\[\]"']+|(^|[\s:\[\](>|])\.{0,2}\/\w[^\s|,;:(){}\[\]"']*/i,lookbehind:!0,greedy:!0,alias:"string"},date:{pattern:RegExp(/\b\d{4}[-/]\d{2}[-/]\d{2}(?:T(?=\d{1,2}:)|(?=\s\d{1,2}:))/.source+"|"+/\b\d{1,4}[-/ ](?:\d{1,2}|Apr|Aug|Dec|Feb|Jan|Jul|Jun|Mar|May|Nov|Oct|Sep)[-/ ]\d{2,4}T?\b/.source+"|"+/\b(?:(?:Fri|Mon|Sat|Sun|Thu|Tue|Wed)(?:\s{1,2}(?:Apr|Aug|Dec|Feb|Jan|Jul|Jun|Mar|May|Nov|Oct|Sep))?|Apr|Aug|Dec|Feb|Jan|Jul|Jun|Mar|May|Nov|Oct|Sep)\s{1,2}\d{1,2}\b/.source,"i"),alias:"number"},time:{pattern:/\b\d{1,2}:\d{1,2}:\d{1,2}(?:[.,:]\d+)?(?:\s?[+-]\d{2}:?\d{2}|Z)?\b/,alias:"number"},boolean:/\b(?:false|null|true)\b/i,number:{pattern:/(^|[^.\w])(?:0x[a-f0-9]+|0o[0-7]+|0b[01]+|v?\d[\da-f]*(?:\.\d+)*(?:e[+-]?\d+)?[a-z]{0,3}\b)\b(?!\.\w)/i,lookbehind:!0},operator:/[;:?<=>~/@!$%&+\-|^(){}*#]/,punctuation:/[\[\].,]/},function(){if("undefined"!=typeof Prism&&"undefined"!=typeof document){var e="line-numbers",t=/\n(?!$)/g,n=Prism.plugins.lineNumbers={getLine:function(t,n){if("PRE"===t.tagName&&t.classList.contains(e)){var a=t.querySelector(".line-numbers-rows");if(a){var r=parseInt(t.getAttribute("data-start"),10)||1,i=r+(a.children.length-1);n<r&&(n=r),n>i&&(n=i);var o=n-r;return a.children[o]}}},resize:function(e){r([e])},assumeViewportIndependence:!0},a=void 0;window.addEventListener("resize",(function(){n.assumeViewportIndependence&&a===window.innerWidth||(a=window.innerWidth,r(Array.prototype.slice.call(document.querySelectorAll("pre."+e))))})),Prism.hooks.add("complete",(function(n){if(n.code){var a=n.element,i=a.parentNode;if(i&&/pre/i.test(i.nodeName)&&!a.querySelector(".line-numbers-rows")&&Prism.util.isActive(a,e)){a.classList.remove(e),i.classList.add(e);var o,s=n.code.match(t),l=s?s.length+1:1,u=new Array(l+1).join("<span></span>");(o=document.createElement("span")).setAttribute("aria-hidden","true"),o.className="line-numbers-rows",o.innerHTML=u,i.hasAttribute("data-start")&&(i.style.counterReset="linenumber "+(parseInt(i.getAttribute("data-start"),10)-1)),n.element.appendChild(o),r([i]),Prism.hooks.run("line-numbers",n)}}})),Prism.hooks.add("line-numbers",(function(e){e.plugins=e.plugins||{},e.plugins.lineNumbers=!0}))}function r(e){if(0!=(e=e.filter((function(e){var t=function(e){if(!e)return null;return window.getComputedStyle?getComputedStyle(e):e.currentStyle||null}(e)["white-space"];return"pre-wrap"===t||"pre-line"===t}))).length){var n=e.map((function(e){var n=e.querySelector("code"),a=e.querySelector(".line-numbers-rows");if(n&&a){var r=e.querySelector(".line-numbers-sizer"),i=n.textContent.split(t);r||((r=document.createElement("span")).className="line-numbers-sizer",n.appendChild(r)),r.innerHTML="0",r.style.display="block";var o=r.getBoundingClientRect().height;return r.innerHTML="",{element:e,lines:i,lineHeights:[],oneLinerHeight:o,sizer:r}}})).filter(Boolean);n.forEach((function(e){var t=e.sizer,n=e.lines,a=e.lineHeights,r=e.oneLinerHeight;a[n.length-1]=void 0,n.forEach((function(e,n){if(e&&e.length>1){var i=t.appendChild(document.createElement("span"));i.style.display="block",i.textContent=e}else a[n]=r}))})),n.forEach((function(e){for(var t=e.sizer,n=e.lineHeights,a=0,r=0;r<n.length;r++)void 0===n[r]&&(n[r]=t.children[a++].getBoundingClientRect().height)})),n.forEach((function(e){var t=e.sizer,n=e.element.querySelector(".line-numbers-rows");t.style.display="none",t.innerHTML="",e.lineHeights.forEach((function(e,t){n.children[t].style.height=e+"px"}))}))}}}(),function(){if("undefined"!=typeof Prism&&"undefined"!=typeof document){var e=[],t={},n=function(){};Prism.plugins.toolbar={};var a=Prism.plugins.toolbar.registerButton=function(n,a){var r;r="function"==typeof a?a:function(e){var t;return"function"==typeof a.onClick?((t=document.createElement("button")).type="button",t.addEventListener("click",(function(){a.onClick.call(this,e)}))):"string"==typeof a.url?(t=document.createElement("a")).href=a.url:t=document.createElement("span"),a.className&&t.classList.add(a.className),t.textContent=a.text,t},n in t?console.warn('There is a button with the key "'+n+'" registered already.'):e.push(t[n]=r)},r=Prism.plugins.toolbar.hook=function(a){var r=a.element.parentNode;if(r&&/pre/i.test(r.nodeName)&&!r.parentNode.classList.contains("code-toolbar")){var i=document.createElement("div");i.classList.add("code-toolbar"),r.parentNode.insertBefore(i,r),i.appendChild(r);var o=document.createElement("div");o.classList.add("toolbar");var s=e,l=function(e){for(;e;){var t=e.getAttribute("data-toolbar-order");if(null!=t)return(t=t.trim()).length?t.split(/\s*,\s*/g):[];e=e.parentElement}}(a.element);l&&(s=l.map((function(e){return t[e]||n}))),s.forEach((function(e){var t=e(a);if(t){var n=document.createElement("div");n.classList.add("toolbar-item"),n.appendChild(t),o.appendChild(n)}})),i.appendChild(o)}};a("label",(function(e){var t=e.element.parentNode;if(t&&/pre/i.test(t.nodeName)&&t.hasAttribute("data-label")){var n,a,r=t.getAttribute("data-label");try{a=document.querySelector("template#"+r)}catch(i){}return a?n=a.content:(t.hasAttribute("data-url")?(n=document.createElement("a")).href=t.getAttribute("data-url"):n=document.createElement("span"),n.textContent=r),n}})),Prism.hooks.add("complete",r)}}(),function(){function e(e,n){e.addEventListener("click",(function(){!function(e){navigator.clipboard?navigator.clipboard.writeText(e.getText()).then(e.success,(function(){t(e)})):t(e)}(n)}))}function t(e){var t=document.createElement("textarea");t.value=e.getText(),t.style.top="0",t.style.left="0",t.style.position="fixed",document.body.appendChild(t),t.focus(),t.select();try{var n=document.execCommand("copy");setTimeout((function(){n?e.success():e.error()}),1)}catch(a){setTimeout((function(){e.error(a)}),1)}document.body.removeChild(t)}"undefined"!=typeof Prism&&"undefined"!=typeof document&&(Prism.plugins.toolbar?Prism.plugins.toolbar.registerButton("copy-to-clipboard",(function(t){var n=t.element,a=function(e){var t={copy:"Copy","copy-error":"Press Ctrl+C to copy","copy-success":"Copied!","copy-timeout":5e3};for(var n in t){for(var a="data-prismjs-"+n,r=e;r&&!r.hasAttribute(a);)r=r.parentElement;r&&(t[n]=r.getAttribute(a))}return t}(n),r=document.createElement("button");r.className="copy-to-clipboard-button",r.setAttribute("type","button");var i=document.createElement("span");return r.appendChild(i),s("copy"),e(r,{getText:function(){return n.textContent},success:function(){s("copy-success"),o()},error:function(){s("copy-error"),setTimeout((function(){!function(e){window.getSelection().selectAllChildren(e)}(n)}),1),o()}}),r;function o(){setTimeout((function(){s("copy")}),a["copy-timeout"])}function s(e){i.textContent=a[e],r.setAttribute("data-copy-state",e)}})):console.warn("Copy to Clipboard plugin loaded before Toolbar plugin."))}();const v=n({height:"100%","&[class*='language-']":{border:"none",margin:0},".line-numbers":{whiteSpace:"pre-wrap"}}),b=i({name:"BtPrism",props:{lang:{type:String,default:"logs"},content:{type:String,default:""},loading:{type:Boolean,default:!1},wrap:{type:Boolean,default:!1},fontSize:{type:[String,Number],default:"14px"},rows:{type:Number,default:100},preStyle:{type:Object,default:()=>{}}},setup(e){const{t:t}=o(),n=s(null),i=s(null),g=s(""),f=l((()=>{const t=e.wrap?{wordWrap:"break-word"}:{};return{fontSize:r(e.fontSize),...t,...e.preStyle}})),h=l((()=>""===e.content?[t("Component.Logs.index_1")]:e.content.split("\n").slice(-1*(e.rows+1))));u((()=>h.value),(()=>{b()}));const b=async()=>{g.value=m.highlight(h.value.join("\n"),m.languages[e.lang],e.lang),await c(),i.value&&m.highlightElement(i.value),y()},y=()=>{n.value&&(n.value.scrollTop=n.value.scrollHeight)};return d((()=>{b()})),()=>p(a,{show:e.loading},{default:()=>[p("pre",{ref:n,class:[v,"language-".concat(e.lang),"line-numbers"],style:f.value},[p("code",{ref:i,innerHTML:g.value},null)])]})}});export{b as _};