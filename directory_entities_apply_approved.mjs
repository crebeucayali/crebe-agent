import fs from 'node:fs';
import path from 'node:path';

export function aprobacionesValidas(propuestasDoc,aprobacionesDoc){
  const propuestas=new Map((propuestasDoc.propuestas||[]).filter(p=>p.accion==='ACTUALIZAR_URL').map(p=>[p.id,p]));
  const validas=[];
  for(const a of aprobacionesDoc.aprobaciones||[]){
    if(a.estado!=='APROBADO') continue;
    const p=propuestas.get(a.id);
    if(!p) throw new Error(`Aprobación sin propuesta vigente: ${a.id}`);
    if(!p.huella || a.huella!==p.huella) throw new Error(`Huella no coincide para ${a.id}`);
    if(a.valor_nuevo!==p.valor_nuevo) throw new Error(`Valor nuevo no coincide para ${a.id}`);
    validas.push({id:a.id,nombre:p.nombre,valor_actual:p.valor_actual,valor_nuevo:p.valor_nuevo,huella:p.huella});
  }
  return validas;
}

export function aplicarUrlsEnCopia(texto,aprobaciones){
  let salida=texto;
  for(const a of aprobaciones){
    const antiguo=`web:\"${a.valor_actual}\"`;
    const nuevo=`web:\"${a.valor_nuevo}\"`;
    const ocurrencias=salida.split(antiguo).length-1;
    if(ocurrencias!==1) throw new Error(`Se esperaba una coincidencia exacta para ${a.nombre}; encontradas: ${ocurrencias}`);
    salida=salida.replace(antiguo,nuevo);
  }
  return salida;
}

async function main(){
  const args=process.argv.slice(2); const get=(n,d)=>{const i=args.indexOf(n);return i>=0?args[i+1]:d;};
  const source=get('--source','target/directorios/directorio-ciudadano.js');
  const proposals=get('--proposals','reports/directorio-entidades/propuestas.json');
  const approvals=get('--approvals','config/directorio-entidades-aprobaciones.json');
  const output=get('--output','reports/directorio-entidades/directorio-ciudadano.propuesto.js');
  const texto=fs.readFileSync(source,'utf8');
  const propuestasDoc=JSON.parse(fs.readFileSync(proposals,'utf8'));
  const aprobacionesDoc=JSON.parse(fs.readFileSync(approvals,'utf8'));
  const validas=aprobacionesValidas(propuestasDoc,aprobacionesDoc);
  const salida=aplicarUrlsEnCopia(texto,validas);
  fs.mkdirSync(path.dirname(output),{recursive:true});
  fs.writeFileSync(output,salida);
  console.log(JSON.stringify({aprobaciones_validas:validas.length,archivo_generado:output,modifica_repositorio_objetivo:false},null,2));
}

if(import.meta.url===`file://${process.argv[1]}`) main().catch(e=>{console.error(e);process.exit(1);});
