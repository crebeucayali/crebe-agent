import test from 'node:test';
import assert from 'node:assert/strict';
import {extraerEntidades,crearId,detectarDuplicados,resumir} from '../directory_entities_verify.mjs';

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

test('posible duplicado requiere al menos dos señales y una señal fuerte',()=>{
  const base={categoria:'Educación',servicio:'x',horario:'x',observacion:'x'};
  const lista=[
    {...base,nombre:'Entidad A',sigla:'A',ambito:'Nacional',direccion:'Calle 1',telefono:'111',correo:'a@x.pe',web:'https://a.pe'},
    {...base,nombre:'Entidad A',sigla:'B',ambito:'Nacional',direccion:'Calle 2',telefono:'222',correo:'b@x.pe',web:'https://b.pe'},
    {...base,nombre:'Entidad C',sigla:'C',ambito:'Regional',direccion:'Calle 3',telefono:'333',correo:'c@x.pe',web:'https://c.pe'}
  ];
  const d=detectarDuplicados(lista);
  assert.equal(d.get(0).length,1);
  assert.equal(d.get(0)[0].nombre,'Entidad A');
  assert.deepEqual(d.get(2),[]);
});

test('resume únicamente los estados producidos',()=>{
  const r=resumir([{estado_verificacion:'VERIFICADO'},{estado_verificacion:'VERIFICADO'},{estado_verificacion:'REDIRECCION'}]);
  assert.deepEqual(r,{VERIFICADO:2,REDIRECCION:1});
});
