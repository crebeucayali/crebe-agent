import test from 'node:test';
import assert from 'node:assert/strict';
import {extraerEntidades,crearId,detectarDuplicados,esValorInformativo,similitudNombre,verificarUrl,resumir} from '../directory_entities_verify.mjs';

test('extrae el arreglo entidades sin ejecutar el resto del archivo',()=>{
  const src='const entidades=[{nombre:"Entidad A",sigla:"EA",categoria:"Educación",ambito:"Nacional",servicio:"Servicio",direccion:"Dirección",telefono:"123",correo:"a@b.pe",horario:"8-5",web:"https://example.org",observacion:"Obs"}];\ndocument.body.innerHTML="x";';
  const lista=extraerEntidades(src);
  assert.equal(lista.length,1);
  assert.equal(lista[0].nombre,'Entidad A');
});

test('genera ids estables y no usa sigla como clave',()=>{
  const e={nombre:'Ministerio de Educación - MINEDU',ambito:'Nacional',web:'https://www.gob.pe/minedu',sigla:'MIN'};
  assert.equal(crearId(e),crearId(e));
  assert.match(crearId(e),/^ministerio-de-educacion-minedu-/);
});

test('descarta marcadores genéricos como señales de duplicidad',()=>{
  assert.equal(esValorInformativo('correo','Canales oficiales en gob.pe'),false);
  assert.equal(esValorInformativo('telefono','Verificar en canal oficial'),false);
  assert.equal(esValorInformativo('direccion','Atención virtual'),false);
  assert.equal(esValorInformativo('direccion','Municipalidad'),false);
  assert.equal(esValorInformativo('correo','contacto@entidad.gob.pe'),true);
});

test('la similitud de nombre evita asociar servicios distintos por datos compartidos',()=>{
  assert.equal(similitudNombre('CONADIS','Ministerio de Salud - MINSA') < 0.75,true);
  assert.equal(similitudNombre('Programa Nacional Cuna Más','Programa Nacional Warmi Ñan') < 0.75,true);
  assert.equal(similitudNombre('Entidad Regional Ucayali','Entidad Regional de Ucayali') >= 0.75,true);
});

test('posible duplicado exige nombre suficientemente similar y otra señal fuerte',()=>{
  const base={categoria:'Educación',servicio:'x',horario:'x',observacion:'x'};
  const lista=[
    {...base,nombre:'Entidad Regional Ucayali',sigla:'A',ambito:'Regional',direccion:'Calle 1',telefono:'111',correo:'a@x.pe',web:'https://a.pe'},
    {...base,nombre:'Entidad Regional de Ucayali',sigla:'B',ambito:'Regional',direccion:'Calle 2',telefono:'222',correo:'a@x.pe',web:'https://b.pe'},
    {...base,nombre:'Otra Entidad',sigla:'C',ambito:'Regional',direccion:'Calle 1',telefono:'111',correo:'a@x.pe',web:'https://a.pe'}
  ];
  const d=detectarDuplicados(lista);
  assert.equal(d.get(0).length,1);
  assert.equal(d.get(0)[0].nombre,'Entidad Regional de Ucayali');
  assert.deepEqual(d.get(2),[]);
});

test('nombres parecidos y mismo ámbito no bastan para declarar duplicado',()=>{
  const base={categoria:'Gobierno y trámites',servicio:'x',horario:'x',observacion:'x',telefono:'Verificar en canal oficial',correo:'Canales oficiales',direccion:'Municipalidad'};
  const lista=[
    {...base,nombre:'Municipalidad Distrital de Yarinacocha',sigla:'MDY',ambito:'Municipal',web:'https://www.gob.pe/muniyarinacocha'},
    {...base,nombre:'Municipalidad Distrital de Masisea',sigla:'MDM',ambito:'Municipal',web:'https://www.gob.pe/munimasisea'}
  ];
  const d=detectarDuplicados(lista);
  assert.deepEqual(d.get(0),[]);
  assert.deepEqual(d.get(1),[]);
});

test('un timeout persistente requiere revisión y no se declara enlace roto',async()=>{
  const original=globalThis.fetch;
  globalThis.fetch=async()=>{const e=new Error('aborted');e.name='AbortError';throw e;};
  try{
    const r=await verificarUrl('https://example.org',{reintentos:0,timeoutMs:10});
    assert.equal(r.estado,'REQUIERE_REVISION');
    assert.equal(r.http_status,null);
  }finally{globalThis.fetch=original;}
});

test('un 404 confirmado sí se clasifica como enlace roto',async()=>{
  const original=globalThis.fetch;
  globalThis.fetch=async()=>({status:404,url:'https://example.org'});
  try{
    const r=await verificarUrl('https://example.org',{reintentos:0,timeoutMs:10});
    assert.equal(r.estado,'ENLACE_ROTO');
    assert.equal(r.http_status,404);
  }finally{globalThis.fetch=original;}
});

test('resume únicamente los estados producidos',()=>{
  const r=resumir([{estado_verificacion:'VERIFICADO'},{estado_verificacion:'VERIFICADO'},{estado_verificacion:'REDIRECCION'}]);
  assert.deepEqual(r,{VERIFICADO:2,REDIRECCION:1});
});
