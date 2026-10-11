import test from 'node:test';
import assert from 'node:assert/strict';
import {compararReferencia,generarMarkdown} from '../directory_entities_maintenance_summary.mjs';

const referencia={
  fecha_referencia:'2026-10-11T19:04:14.493Z',
  entidades:[
    {id:'a',nombre:'A',estado_verificacion:'VERIFICADO',url_original:'https://a.pe'},
    {id:'b',nombre:'B',estado_verificacion:'ENLACE_ROTO',url_original:'https://b.pe'},
    {id:'c',nombre:'C',estado_verificacion:'VERIFICADO',url_original:'https://c.pe'}
  ]
};

test('sin cambios relevantes conserva solo incidencias conocidas',()=>{
  const ver={resultados:[
    {id:'a',nombre:'A',estado_verificacion:'VERIFICADO',url_original:'https://a.pe'},
    {id:'b',nombre:'B',estado_verificacion:'ENLACE_ROTO',url_original:'https://b.pe'},
    {id:'c',nombre:'C',estado_verificacion:'VERIFICADO',url_original:'https://c.pe'}
  ]};
  const r=compararReferencia(ver,referencia);
  assert.equal(r.cambios_relevantes,0);
  assert.equal(r.requiere_atencion,false);
  assert.equal(r.incidencias_sin_cambio.length,1);
});

test('detecta una nueva incidencia y una incidencia resuelta',()=>{
  const ver={resultados:[
    {id:'a',nombre:'A',estado_verificacion:'ENLACE_ROTO',url_original:'https://a.pe'},
    {id:'b',nombre:'B',estado_verificacion:'VERIFICADO',url_original:'https://b.pe'},
    {id:'c',nombre:'C',estado_verificacion:'VERIFICADO',url_original:'https://c.pe'}
  ]};
  const r=compararReferencia(ver,referencia);
  assert.equal(r.incidencias_nuevas.length,1);
  assert.equal(r.incidencias_resueltas.length,1);
  assert.equal(r.estado_cambiado.length,2);
});

test('detecta alta, baja y cambio de URL',()=>{
  const ver={resultados:[
    {id:'a',nombre:'A',estado_verificacion:'VERIFICADO',url_original:'https://a-nueva.pe'},
    {id:'b',nombre:'B',estado_verificacion:'ENLACE_ROTO',url_original:'https://b.pe'},
    {id:'d',nombre:'D',estado_verificacion:'VERIFICADO',url_original:'https://d.pe'}
  ]};
  const r=compararReferencia(ver,referencia);
  assert.equal(r.nuevas.length,1);
  assert.equal(r.ausentes.length,1);
  assert.equal(r.url_cambiada.length,1);
  assert.equal(r.cambios_relevantes,3);
});

test('el informe sin novedades no presenta cambios inexistentes',()=>{
  const r={referencia:'x',entidades_actuales:1,entidades_referencia:1,cambios_relevantes:0,requiere_atencion:false,nuevas:[],ausentes:[],url_cambiada:[],estado_cambiado:[],incidencias_nuevas:[],incidencias_resueltas:[],incidencias_sin_cambio:[]};
  const md=generarMarkdown(r);
  assert.match(md,/Sin cambios relevantes/);
  assert.doesNotMatch(md,/### Entidades nuevas/);
});
