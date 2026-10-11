import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import crypto from 'node:crypto';

const ESTADOS = new Set(['VERIFICADO','REDIRECCION','ENLACE_ROTO','CAMBIO_DETECTADO','POSIBLE_DUPLICADO','REQUIERE_REVISION']);

export function extraerEntidades(texto){
  const inicio = texto.indexOf('const entidades=[');
  if(inicio < 0) throw new Error('No se encontró const entidades=[');
  const desde = texto.indexOf('[', inicio);
  let profundidad = 0, enCadena = false, escape = false, fin = -1;
  for(let i=desde;i<texto.length;i++){
    const c = texto[i];
    if(enCadena){
      if(escape) escape=false;
      else if(c==='\\') escape=true;
      else if(c==='"') enCadena=false;
      continue;
    }
    if(c==='"'){ enCadena=true; continue; }
    if(c==='[') profundidad++;
    else if(c===']'){
      profundidad--;
      if(profundidad===0){ fin=i; break; }
    }
  }
  if(fin < 0) throw new Error('No se pudo cerrar el arreglo entidades');
  const literal = texto.slice(desde, fin+1);
  const entidades = vm.runInNewContext(literal, Object.create(null), {timeout:1000});
  if(!Array.isArray(entidades)) throw new Error('El origen no produjo un arreglo');
  return entidades.map(x => ({...x}));
}

export function normalizarTexto(valor=''){
  return String(valor).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();
}

export function crearId(entidad){
  const base = normalizarTexto(entidad.nombre).replace(/ /g,'-').slice(0,64) || 'entidad';
  const huella = crypto.createHash('sha1').update(`${entidad.nombre}|${entidad.ambito}|${entidad.web}`).digest('hex').slice(0,8);
  return `${base}-${huella}`;
}

export function detectarDuplicados(entidades){
  const resultado = new Map(entidades.map((_,i)=>[i,[]]));
  for(let i=0;i<entidades.length;i++) for(let j=i+1;j<entidades.length;j++){
    const a=entidades[i], b=entidades[j];
    const senales=[];
    if(normalizarTexto(a.nombre) && normalizarTexto(a.nombre)===normalizarTexto(b.nombre)) senales.push('nombre_normalizado');
    if(a.web && b.web && String(a.web).replace(/\/$/,'')===String(b.web).replace(/\/$/,'')) senales.push('url');
    if(a.telefono && b.telefono && normalizarTexto(a.telefono)===normalizarTexto(b.telefono)) senales.push('telefono');
    if(a.correo && b.correo && normalizarTexto(a.correo)===normalizarTexto(b.correo)) senales.push('correo');
    if(a.direccion && b.direccion && normalizarTexto(a.direccion)===normalizarTexto(b.direccion)) senales.push('direccion');
    if(a.ambito && b.ambito && normalizarTexto(a.ambito)===normalizarTexto(b.ambito)) senales.push('ambito');
    const fuertes = senales.filter(s=>s!=='ambito');
    if(senales.length>=2 && fuertes.length>=1){
      resultado.get(i).push({indice:j,nombre:b.nombre,senales});
      resultado.get(j).push({indice:i,nombre:a.nombre,senales});
    }
  }
  return resultado;
}

async function fetchConTimeout(url, timeoutMs){
  const ac = new AbortController();
  const t=setTimeout(()=>ac.abort(), timeoutMs);
  try{
    return await fetch(url,{method:'GET',redirect:'follow',signal:ac.signal,headers:{'user-agent':'CREBE-Agent/1.0 (+https://github.com/crebeucayali/crebe-agent)','accept':'text/html,application/xhtml+xml,application/json;q=0.8,*/*;q=0.5'}});
  } finally { clearTimeout(t); }
}

export async function verificarUrl(url,{reintentos=2,timeoutMs=8000}={}){
  if(!url) return {estado:'REQUIERE_REVISION',http_status:null,url_final:null,nivel_confianza:'BAJA',observacion:'Registro sin URL.'};
  let original;
  try{ original=new URL(url); if(!['http:','https:'].includes(original.protocol)) throw new Error('protocolo'); }
  catch{ return {estado:'REQUIERE_REVISION',http_status:null,url_final:null,nivel_confianza:'BAJA',observacion:'URL ausente o inválida.'}; }
  let ultimoError='';
  for(let intento=0; intento<=reintentos; intento++){
    try{
      const r=await fetchConTimeout(original.href,timeoutMs);
      const status=r.status;
      const finalUrl=r.url || original.href;
      if(status>=200 && status<400){
        const redirigida = finalUrl.replace(/\/$/,'')!==original.href.replace(/\/$/,'');
        return {estado:redirigida?'REDIRECCION':'VERIFICADO',http_status:status,url_final:finalUrl,nivel_confianza:'ALTA',observacion:redirigida?'La URL redirige a otra dirección.':'La URL respondió correctamente.'};
      }
      if(status===404 || status===410) return {estado:'ENLACE_ROTO',http_status:status,url_final:finalUrl,nivel_confianza:'ALTA',observacion:`Respuesta HTTP ${status}.`};
      if(status===403 || status===429) return {estado:'REQUIERE_REVISION',http_status:status,url_final:finalUrl,nivel_confianza:'MEDIA',observacion:`Respuesta HTTP ${status}; podría existir bloqueo automatizado o límite de solicitudes.`};
      if(status>=500){ ultimoError=`HTTP ${status}`; if(intento<reintentos) continue; return {estado:'REQUIERE_REVISION',http_status:status,url_final:finalUrl,nivel_confianza:'MEDIA',observacion:`Fallo de servidor persistente (${status}); no se clasifica como cierre institucional.`}; }
      return {estado:'REQUIERE_REVISION',http_status:status,url_final:finalUrl,nivel_confianza:'MEDIA',observacion:`Respuesta HTTP ${status} requiere revisión.`};
    }catch(e){ ultimoError=e?.name==='AbortError'?'timeout':String(e?.message||e); if(intento<reintentos) continue; }
  }
  return {estado:'ENLACE_ROTO',http_status:null,url_final:null,nivel_confianza:'MEDIA',observacion:`Sin respuesta válida tras ${reintentos+1} intentos: ${ultimoError}`};
}

export async function ejecutar(entidades,{concurrencia=6}={}){
  const duplicados=detectarDuplicados(entidades);
  const resultados=new Array(entidades.length);
  let cursor=0;
  async function worker(){
    while(true){
      const i=cursor++; if(i>=entidades.length) return;
      const e=entidades[i];
      const ver=await verificarUrl(e.web);
      const posibles=duplicados.get(i)||[];
      let estado=ver.estado;
      let observacion=ver.observacion;
      if(posibles.length){
        if(estado==='VERIFICADO') estado='POSIBLE_DUPLICADO';
        observacion += ` Posible duplicado con: ${posibles.map(x=>x.nombre).join('; ')}.`;
      }
      if(!ESTADOS.has(estado)) throw new Error(`Estado no permitido: ${estado}`);
      resultados[i]={id:crearId(e),nombre:e.nombre,estado_verificacion:estado,ultima_verificacion:new Date().toISOString(),http_status:ver.http_status,url_original:e.web||null,url_final:ver.url_final,tipo_cambio:estado==='REDIRECCION'?'URL_REDIRECCION':(posibles.length?'POSIBLE_DUPLICADO':null),nivel_confianza:ver.nivel_confianza,observacion_verificacion:observacion,duplicados_posibles:posibles.map(x=>({nombre:x.nombre,senales:x.senales}))};
    }
  }
  await Promise.all(Array.from({length:Math.max(1,Math.min(concurrencia,entidades.length||1))},worker));
  return resultados;
}

export function resumir(resultados){
  const conteo={};
  for(const r of resultados) conteo[r.estado_verificacion]=(conteo[r.estado_verificacion]||0)+1;
  return conteo;
}

function informeMarkdown(resultados, origen){
  const conteo=resumir(resultados);
  const lineas=['# Verificación de Directorio de Entidades','',`Fuente: \`${origen}\``,`Fecha: ${new Date().toISOString()}`,'',`Entidades revisadas: ${resultados.length}`,''];
  for(const estado of ['VERIFICADO','REDIRECCION','ENLACE_ROTO','CAMBIO_DETECTADO','POSIBLE_DUPLICADO','REQUIERE_REVISION']) lineas.push(`- ${estado}: ${conteo[estado]||0}`);
  const incidencias=resultados.filter(r=>r.estado_verificacion!=='VERIFICADO');
  lineas.push('','## Incidencias y revisiones');
  if(!incidencias.length) lineas.push('No se detectaron incidencias técnicas.');
  else for(const r of incidencias) lineas.push(`- **${r.nombre}**: ${r.estado_verificacion}. ${r.observacion_verificacion}`);
  lineas.push('','> Ejecución de solo lectura. No se modificó el directorio público ni sus datos.','');
  return lineas.join('\n');
}

async function main(){
  const args=process.argv.slice(2); const get=(n,d)=>{const i=args.indexOf(n);return i>=0?args[i+1]:d;};
  const origen=get('--source','target/directorios/directorio-ciudadano.js');
  const salida=get('--output','reports/directorio-entidades');
  const texto=fs.readFileSync(origen,'utf8');
  const entidades=extraerEntidades(texto);
  const resultados=await ejecutar(entidades,{concurrencia:Number(get('--concurrency','6'))});
  fs.mkdirSync(salida,{recursive:true});
  fs.writeFileSync(path.join(salida,'verificacion.json'),JSON.stringify({modo:'solo_lectura',fuente:origen,conteo:resumir(resultados),resultados},null,2));
  fs.writeFileSync(path.join(salida,'Informe_directorio_entidades.md'),informeMarkdown(resultados,origen));
  console.log(JSON.stringify({entidades:resultados.length,conteo:resumir(resultados)},null,2));
}

if(import.meta.url===`file://${process.argv[1]}`) main().catch(e=>{console.error(e);process.exit(1);});
