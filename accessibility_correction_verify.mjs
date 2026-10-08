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
const output=process.argv[3] || 'reports/fase-8-etapa-7-verificacion.generated.json';
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
let contrastNodes=0;
const contrastDetail=[];
const overflowDetail=[];
const loadFailures=[];
for (const item of pages) {
  const page=await context.newPage();
  try {
    const res=await page.goto(item.url,{waitUntil:'domcontentloaded',timeout:15000});
    if (!res || res.status()>=400) {
      loadFailures.push({repo:item.repo,path:item.rel,status:res?.status()??null});
      await page.close();
      continue;
    }
    await page.waitForTimeout(400);
    await page.addScriptTag({content:axe.source});
    const ax=await page.evaluate(async()=>await axe.run(document,{runOnly:{type:'rule',values:['color-contrast']}}));
    const nodes=ax.violations.reduce((n,v)=>n+v.nodes.length,0);
    contrastNodes+=nodes;
    if (nodes>0) contrastDetail.push({repo:item.repo,path:item.rel,nodes,violations:ax.violations.map(v=>({id:v.id,nodes:v.nodes.length,targets:v.nodes.slice(0,10).map(n=>n.target)}))});

    const key=`${item.repo}/${item.rel}`;
    if (OVERFLOW_TARGETS.has(key)) {
      await page.setViewportSize({width:320,height:800});
      await page.waitForTimeout(150);
      const data=await page.evaluate(()=>({clientWidth:document.documentElement.clientWidth,scrollWidth:document.documentElement.scrollWidth}));
      overflowDetail.push({repo:item.repo,path:item.rel,...data,horizontalOverflow:data.scrollWidth>data.clientWidth+2});
    }
  } catch (e) {
    loadFailures.push({repo:item.repo,path:item.rel,error:String(e.message||e)});
  }
  await page.close();
}
await context.close();
await browser.close();

const overflowFailures=overflowDetail.filter(x=>x.horizontalOverflow);
const report={
  schema_version:1,
  fase:8,
  etapa:7,
  nombre:'Verificacion de correcciones controladas de accesibilidad',
  modo:'READ_ONLY_POST_CORRECTION_VERIFICATION',
  paginas_funcionales_observadas:pages.length,
  paginas_no_cargadas:loadFailures.length,
  contraste:{nodos_restantes:contrastNodes,paginas_afectadas:contrastDetail.length,detalle:contrastDetail},
  reflujo:{targets_verificados:overflowDetail.length,targets_con_overflow:overflowFailures.length,detalle:overflowDetail},
  guardrails:{repositorios_eva_modificados_por_verificador:false,supabase_modificado:false,etapa_8_iniciada:false}
};
fs.mkdirSync(path.dirname(output),{recursive:true});
fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({paginas:pages.length,loadFailures:loadFailures.length,contrastNodes,overflowTargets:overflowDetail.length,overflowFailures:overflowFailures.length},null,2));
if (loadFailures.length>0 || contrastNodes>0 || overflowFailures.length>0 || overflowDetail.length!==4) process.exitCode=1;
