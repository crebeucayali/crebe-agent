import fs from 'node:fs';
import path from 'node:path';

function mapear(lista=[]){
  return new Map(lista.map(x=>[x.id,x]));
}

export function compararReferencia(verificacion, referencia){
  const actual=mapear(verificacion.resultados||[]);
  const base=mapear(referencia.entidades||[]);
  const nuevas=[], ausentes=[], url_cambiada=[], estado_cambiado=[], incidencias_nuevas=[], incidencias_resueltas=[], incidencias_sin_cambio=[];

  for(const [id,a] of actual){
    const b=base.get(id);
    if(!b){
      nuevas.push({id,nombre:a.nombre,estado:a.estado_verificacion,url:a.url_original||null});
      continue;
    }
    if((a.url_original||null)!==(b.url_original||null)){
      url_cambiada.push({id,nombre:a.nombre,antes:b.url_original||null,ahora:a.url_original||null});
    }
    if(a.estado_verificacion!==b.estado_verificacion){
      const cambio={id,nombre:a.nombre,antes:b.estado_verificacion,ahora:a.estado_verificacion};
      estado_cambiado.push(cambio);
      if(b.estado_verificacion==='VERIFICADO' && a.estado_verificacion!=='VERIFICADO') incidencias_nuevas.push(cambio);
      if(b.estado_verificacion!=='VERIFICADO' && a.estado_verificacion==='VERIFICADO') incidencias_resueltas.push(cambio);
    } else if(a.estado_verificacion!=='VERIFICADO'){
      incidencias_sin_cambio.push({id,nombre:a.nombre,estado:a.estado_verificacion});
    }
  }

  for(const [id,b] of base){
    if(!actual.has(id)) ausentes.push({id,nombre:b.nombre,estado:b.estado_verificacion,url:b.url_original||null});
  }

  const cambios_relevantes=nuevas.length+ausentes.length+url_cambiada.length+estado_cambiado.length;
  return {
    referencia: referencia.fecha_referencia||null,
    entidades_actuales: actual.size,
    entidades_referencia: base.size,
    cambios_relevantes,
    requiere_atencion: cambios_relevantes>0,
    nuevas,ausentes,url_cambiada,estado_cambiado,incidencias_nuevas,incidencias_resueltas,incidencias_sin_cambio
  };
}

export function generarMarkdown(r){
  const l=['# Mantenimiento periódico del Directorio de Entidades','',`Referencia: ${r.referencia||'sin fecha'}`,`Entidades actuales: ${r.entidades_actuales}`,`Entidades de referencia: ${r.entidades_referencia}`,''];
  if(!r.requiere_atencion){
    l.push('## Resultado','','Sin cambios relevantes respecto de la referencia aprobada.','');
  } else {
    l.push('## Cambios relevantes','',`Total: ${r.cambios_relevantes}`,'');
    const seccion=(titulo,items,formato)=>{ if(!items.length) return; l.push(`### ${titulo}`,''); for(const x of items) l.push(`- ${formato(x)}`); l.push(''); };
    seccion('Entidades nuevas',r.nuevas,x=>`${x.nombre} (${x.estado})`);
    seccion('Entidades ausentes',r.ausentes,x=>`${x.nombre} (${x.estado})`);
    seccion('URL modificada',r.url_cambiada,x=>`${x.nombre}: ${x.antes||'—'} → ${x.ahora||'—'}`);
    seccion('Estado modificado',r.estado_cambiado,x=>`${x.nombre}: ${x.antes} → ${x.ahora}`);
  }
  l.push('## Incidencias conocidas sin cambio','');
  if(!r.incidencias_sin_cambio.length) l.push('Ninguna.');
  else for(const x of r.incidencias_sin_cambio) l.push(`- ${x.nombre}: ${x.estado}`);
  l.push('','> Esta ejecución es de supervisión. No modifica el Directorio ciudadano, Supabase ni la referencia aprobada.','');
  return l.join('\n');
}

async function main(){
  const args=process.argv.slice(2); const get=(n,d)=>{const i=args.indexOf(n);return i>=0?args[i+1]:d;};
  const verPath=get('--verification','reports/directorio-entidades/verificacion.json');
  const refPath=get('--reference','tracking/directorio-entidades-referencia.json');
  const outDir=get('--output','reports/directorio-entidades');
  const ver=JSON.parse(fs.readFileSync(verPath,'utf8'));
  const ref=JSON.parse(fs.readFileSync(refPath,'utf8'));
  const resultado=compararReferencia(ver,ref);
  fs.mkdirSync(outDir,{recursive:true});
  fs.writeFileSync(path.join(outDir,'mantenimiento-periodico.json'),JSON.stringify(resultado,null,2));
  fs.writeFileSync(path.join(outDir,'Mantenimiento_periodico_directorio.md'),generarMarkdown(resultado));
  console.log(JSON.stringify({cambios_relevantes:resultado.cambios_relevantes,requiere_atencion:resultado.requiere_atencion},null,2));
}

if(import.meta.url===`file://${process.argv[1]}`) main().catch(e=>{console.error(e);process.exit(1);});
