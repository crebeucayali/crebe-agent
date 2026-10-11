import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {verificarUrl} from './directory_entities_verify.mjs';

export function huellaPropuesta(p){
  return crypto.createHash('sha256').update(JSON.stringify({
    id:p.id,
    accion:p.accion,
    valor_actual:p.valor_actual,
    valor_nuevo:p.valor_nuevo
  })).digest('hex').slice(0,16);
}

export async function construirPropuestas(verificacion,catalogo,{verificar=verificarUrl}={}){
  const candidatos=new Map((catalogo.candidatos||[]).map(c=>[c.id,c]));
  const propuestas=[];
  for(const r of verificacion.resultados||[]){
    if(r.estado_verificacion==='VERIFICADO') continue;
    const c=candidatos.get(r.id);
    if(!c){
      propuestas.push({
        id:r.id,nombre:r.nombre,estado_origen:r.estado_verificacion,
        accion:'REVISAR_MANUALMENTE',campo:null,valor_actual:r.url_original||null,valor_nuevo:null,
        confianza:'BAJA',estado_aprobacion:'NO_APLICA',
        motivo:'No existe candidato controlado para este hallazgo.',evidencia:[]
      });
      continue;
    }
    if(c.accion_sugerida==='MANTENER_URL'){
      propuestas.push({
        id:r.id,nombre:r.nombre,estado_origen:r.estado_verificacion,
        accion:'MANTENER_URL',campo:'web',valor_actual:c.url_actual,valor_nuevo:c.url_actual,
        confianza:'ALTA',estado_aprobacion:'NO_APLICA',motivo:c.motivo,evidencia:c.evidencia||[]
      });
      continue;
    }
    if(c.accion_sugerida==='REVISAR_MANUALMENTE' || !c.url_candidata){
      propuestas.push({
        id:r.id,nombre:r.nombre,estado_origen:r.estado_verificacion,
        accion:'REVISAR_MANUALMENTE',campo:'web',valor_actual:c.url_actual||r.url_original||null,valor_nuevo:null,
        confianza:r.nivel_confianza||'BAJA',estado_aprobacion:'NO_APLICA',motivo:c.motivo,evidencia:c.evidencia||[]
      });
      continue;
    }
    const validacion=await verificar(c.url_candidata,{reintentos:1,timeoutMs:8000});
    const utilizable=['VERIFICADO','REDIRECCION'].includes(validacion.estado);
    const p={
      id:r.id,nombre:r.nombre,estado_origen:r.estado_verificacion,
      accion:utilizable?'ACTUALIZAR_URL':'REVISAR_MANUALMENTE',campo:'web',
      valor_actual:c.url_actual||r.url_original||null,
      valor_nuevo:utilizable?c.url_candidata:null,
      url_candidata_validacion:validacion,
      confianza:utilizable?'ALTA':'BAJA',
      estado_aprobacion:utilizable?'PENDIENTE_APROBACION':'NO_APLICA',
      motivo:c.motivo,evidencia:c.evidencia||[]
    };
    if(utilizable) p.huella=huellaPropuesta(p);
    propuestas.push(p);
  }
  return propuestas;
}

export function resumirPropuestas(propuestas){
  const out={};
  for(const p of propuestas) out[p.accion]=(out[p.accion]||0)+1;
  return out;
}

function markdown(propuestas){
  const lineas=['# Propuestas controladas para el Directorio de Entidades','',
    '> Este informe no modifica datos. Toda propuesta ACTUALIZAR_URL requiere aprobación explícita y coincidencia exacta de huella.',''];
  for(const p of propuestas){
    lineas.push(`## ${p.nombre}`,'',`- Estado detectado: ${p.estado_origen}`,`- Acción: ${p.accion}`,`- URL actual: ${p.valor_actual||'—'}`,`- URL propuesta: ${p.valor_nuevo||'—'}`,`- Aprobación: ${p.estado_aprobacion}`);
    if(p.huella) lineas.push(`- Huella: ${p.huella}`);
    lineas.push(`- Motivo: ${p.motivo}`,'');
  }
  return lineas.join('\n');
}

async function main(){
  const args=process.argv.slice(2); const get=(n,d)=>{const i=args.indexOf(n);return i>=0?args[i+1]:d;};
  const verPath=get('--verification','reports/directorio-entidades/verificacion.json');
  const catPath=get('--candidates','config/directorio-entidades-candidatos.json');
  const outDir=get('--output','reports/directorio-entidades');
  const ver=JSON.parse(fs.readFileSync(verPath,'utf8'));
  const cat=JSON.parse(fs.readFileSync(catPath,'utf8'));
  const propuestas=await construirPropuestas(ver,cat);
  fs.mkdirSync(outDir,{recursive:true});
  fs.writeFileSync(path.join(outDir,'propuestas.json'),JSON.stringify({modo:'propuesta_controlada',generado:new Date().toISOString(),resumen:resumirPropuestas(propuestas),propuestas},null,2));
  fs.writeFileSync(path.join(outDir,'Propuestas_directorio_entidades.md'),markdown(propuestas));
  console.log(JSON.stringify({propuestas:propuestas.length,resumen:resumirPropuestas(propuestas)},null,2));
}

if(import.meta.url===`file://${process.argv[1]}`) main().catch(e=>{console.error(e);process.exit(1);});
