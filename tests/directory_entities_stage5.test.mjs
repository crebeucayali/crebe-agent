import test from 'node:test';
import assert from 'node:assert/strict';
import {construirPropuestas,huellaPropuesta} from '../directory_entities_proposals.mjs';
import {aprobacionesValidas,aplicarUrlsEnCopia} from '../directory_entities_apply_approved.mjs';

const verificacion={resultados:[
  {id:'a',nombre:'Entidad A',estado_verificacion:'ENLACE_ROTO',url_original:'https://vieja.test',nivel_confianza:'ALTA'},
  {id:'b',nombre:'Entidad B',estado_verificacion:'REDIRECCION',url_original:'https://b.test',nivel_confianza:'ALTA'},
  {id:'c',nombre:'Entidad C',estado_verificacion:'REQUIERE_REVISION',url_original:'https://c.test',nivel_confianza:'BAJA'}
]};

const catalogo={candidatos:[
  {id:'a',nombre:'Entidad A',accion_sugerida:'ACTUALIZAR_URL',url_actual:'https://vieja.test',url_candidata:'https://nueva.test',motivo:'cambio',evidencia:[]},
  {id:'b',nombre:'Entidad B',accion_sugerida:'MANTENER_URL',url_actual:'https://b.test',url_candidata:'https://destino.test',motivo:'mantener',evidencia:[]},
  {id:'c',nombre:'Entidad C',accion_sugerida:'REVISAR_MANUALMENTE',url_actual:'https://c.test',url_candidata:null,motivo:'revisar',evidencia:[]}
]};

test('genera propuesta de actualización solo si la candidata valida',async()=>{
  const verificar=async()=>({estado:'VERIFICADO',http_status:200,url_final:'https://nueva.test',nivel_confianza:'ALTA',observacion:'ok'});
  const p=await construirPropuestas(verificacion,catalogo,{verificar});
  assert.equal(p[0].accion,'ACTUALIZAR_URL');
  assert.equal(p[0].estado_aprobacion,'PENDIENTE_APROBACION');
  assert.ok(p[0].huella);
  assert.equal(p[1].accion,'MANTENER_URL');
  assert.equal(p[2].accion,'REVISAR_MANUALMENTE');
});

test('candidata inválida no produce actualización',async()=>{
  const verificar=async()=>({estado:'ENLACE_ROTO',http_status:404,url_final:null,nivel_confianza:'ALTA',observacion:'404'});
  const p=await construirPropuestas({resultados:[verificacion.resultados[0]]},{candidatos:[catalogo.candidatos[0]]},{verificar});
  assert.equal(p[0].accion,'REVISAR_MANUALMENTE');
  assert.equal(p[0].estado_aprobacion,'NO_APLICA');
});

test('la huella cambia si cambia el valor nuevo',()=>{
  const base={id:'a',accion:'ACTUALIZAR_URL',valor_actual:'https://vieja.test',valor_nuevo:'https://nueva.test'};
  assert.notEqual(huellaPropuesta(base),huellaPropuesta({...base,valor_nuevo:'https://otra.test'}));
});

test('sin aprobación no se aplica ningún cambio',()=>{
  const propuesta={id:'a',nombre:'Entidad A',accion:'ACTUALIZAR_URL',valor_actual:'https://vieja.test',valor_nuevo:'https://nueva.test'};
  propuesta.huella=huellaPropuesta(propuesta);
  const validas=aprobacionesValidas({propuestas:[propuesta]},{aprobaciones:[]});
  assert.deepEqual(validas,[]);
  const src='const entidades=[{nombre:"Entidad A",web:"https://vieja.test"}];';
  assert.equal(aplicarUrlsEnCopia(src,validas),src);
});

test('aprobación exacta genera cambio solo sobre la copia',()=>{
  const propuesta={id:'a',nombre:'Entidad A',accion:'ACTUALIZAR_URL',valor_actual:'https://vieja.test',valor_nuevo:'https://nueva.test'};
  propuesta.huella=huellaPropuesta(propuesta);
  const validas=aprobacionesValidas({propuestas:[propuesta]},{aprobaciones:[{id:'a',estado:'APROBADO',huella:propuesta.huella,valor_nuevo:'https://nueva.test'}]});
  const src='const entidades=[{nombre:"Entidad A",web:"https://vieja.test"}];';
  const salida=aplicarUrlsEnCopia(src,validas);
  assert.match(salida,/https:\/\/nueva\.test/);
  assert.match(src,/https:\/\/vieja\.test/);
});

test('una huella distinta bloquea la aprobación',()=>{
  const propuesta={id:'a',nombre:'Entidad A',accion:'ACTUALIZAR_URL',valor_actual:'https://vieja.test',valor_nuevo:'https://nueva.test'};
  propuesta.huella=huellaPropuesta(propuesta);
  assert.throws(()=>aprobacionesValidas({propuestas:[propuesta]},{aprobaciones:[{id:'a',estado:'APROBADO',huella:'incorrecta',valor_nuevo:'https://nueva.test'}]}),/Huella no coincide/);
});
