import fs from 'fs';
import path from 'path';
import { chromium } from 'playwright';
import axe from 'axe-core';

const REPOS = [
  'crebeucayali.github.io',
  'accesos-complementarios',
  'capacitaciones',
  'banco-digital-accesible',
  'materiales-educativos-accesibles',
  'noti-inclusivos',
  'repositorio-accesible',
  'DUA-3.0'
];
const OVERFLOW_TARGETS = new Set([
  'accesos-complementarios/paginas/contacto.html',
  'accesos-complementarios/recursos/contacto.html',
  'banco-digital-accesible/braille/teoria.html',
  'materiales-educativos-accesibles/generador/generador.html'
]);
function walkHtml(dir) {
  const out=[];
  for (const e of fs.readdirSync(dir,{withFileTypes:true})) {
    if (e.name === '.git') continue;
    const p=path.join(dir,e.name);
    if (e.isDirectory()) out.push(...walkHtml(p));
    else if (e.isFile() && e.name.endsWith('.html')) out.push(p);
  }
  return out;
}
function publicUrl(repo, rel) {
  const suffix=rel.replaceAll(path.sep,'/').replace(/index\.html$/,'');
  return repo==='crebeucayali.github.io'
    ? `https://crebeucayali.github.io/${suffix}`
    : `https://crebeucayali.github.io/${repo}/${suffix}`;
}
function isAuxiliary(rel) {
  const n=rel.replaceAll('\\','/');
  return /^google[0-9a-f]+\.html$/i.test(n) || n.startsWith('docs/referencias/');
}
const root=process.argv[2] || '_eva';
const output=process.argv[3] || 'reports/fase-8-etapa-6-diagnostico.generated.json';
const pages=[];
for (const repo of REPOS) {
  const repoDir=path.join(root,repo);
  for (const file of walkHtml(repoDir)) {
    const rel=path.relative(repoDir,file).replaceAll(path.sep,'/');
    if (!isAuxiliary(rel)) pages.push({repo,rel,url:publicUrl(repo,rel)});
  }
}

const browser=await chromium.launch({headless:true});
const context=await browser.newContext({viewport:{width:1280,height:900},bypassCSP:true});
const contrast=[];
const overflow=[];
for (const item of pages) {
  const page=await context.newPage();
  try {
    const res=await page.goto(item.url,{waitUntil:'domcontentloaded',timeout:15000});
    if (!res || res.status()>=400) { await page.close(); continue; }
    await page.waitForTimeout(400);
    await page.addScriptTag({content:axe.source});
    const ax=await page.evaluate(async()=>await axe.run(document,{runOnly:{type:'rule',values:['color-contrast']}}));
    for (const v of ax.violations) {
      for (const n of v.nodes) {
        const checks=[...(n.any||[]),...(n.all||[]),...(n.none||[])];
        contrast.push({
          repo:item.repo,
          path:item.rel,
          url:page.url(),
          target:n.target,
          html:n.html,
          failureSummary:n.failureSummary,
          checks:checks.map(c=>({id:c.id,message:c.message,data:c.data||null}))
        });
      }
    }
    const key=`${item.repo}/${item.rel}`;
    if (OVERFLOW_TARGETS.has(key)) {
      await page.setViewportSize({width:320,height:800});
      await page.waitForTimeout(150);
      const data=await page.evaluate(()=>{
        const visible=el=>{const s=getComputedStyle(el);const r=el.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0;};
        const candidates=[];
        for (const el of document.querySelectorAll('body *')) {
          if (!visible(el)) continue;
          const r=el.getBoundingClientRect();
          const s=getComputedStyle(el);
          const spills=r.right>322 || r.left<-2 || el.scrollWidth>el.clientWidth+2;
          if (!spills) continue;
          candidates.push({
            tag:el.tagName.toLowerCase(), id:el.id||'', className:String(el.className||'').slice(0,180),
            text:(el.textContent||'').trim().replace(/\s+/g,' ').slice(0,120),
            rect:{left:Math.round(r.left),right:Math.round(r.right),width:Math.round(r.width)},
            clientWidth:el.clientWidth, scrollWidth:el.scrollWidth,
            css:{width:s.width,minWidth:s.minWidth,maxWidth:s.maxWidth,whiteSpace:s.whiteSpace,position:s.position,transform:s.transform,overflowX:s.overflowX,display:s.display}
          });
        }
        candidates.sort((a,b)=>(b.rect.right-320)-(a.rect.right-320));
        return {clientWidth:document.documentElement.clientWidth,scrollWidth:document.documentElement.scrollWidth,candidates:candidates.slice(0,25)};
      });
      overflow.push({repo:item.repo,path:item.rel,url:page.url(),...data});
    }
  } catch (e) {
    overflow.push({repo:item.repo,path:item.rel,error:String(e.message||e)});
  }
  await page.close();
}
await context.close();
await browser.close();

const byRepo={};
for (const n of contrast) byRepo[n.repo]=(byRepo[n.repo]||0)+1;
const report={
  schema_version:1,
  fase:8,
  etapa:6,
  nombre:'Diagnostico tecnico de accesibilidad',
  modo:'READ_ONLY_DIAGNOSIS',
  contraste:{nodos:contrast.length,por_repo:byRepo,detalle:contrast},
  reflujo:{paginas:overflow.length,detalle:overflow},
  guardrails:{repositorios_eva_modificados:false,supabase_modificado:false,correcciones_aplicadas:0,etapa_7_iniciada:false}
};
fs.mkdirSync(path.dirname(output),{recursive:true});
fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({contraste_nodos:contrast.length,contraste_por_repo:byRepo,reflujo_paginas:overflow.length},null,2));
