# Fase 5. Funcionamiento real de EVA

## Etapa 1. Inventario funcional

Objetivo: identificar de forma reproducible qué elementos de los ocho repositorios EVA deben ejecutar una acción antes de iniciar pruebas funcionales.

Esta etapa no corrige fallos y no certifica funcionamiento. Su finalidad es construir la base de pruebas de la siguiente etapa.

## Alcance

Repositorios incluidos:

1. `crebeucayali/crebeucayali.github.io`
2. `crebeucayali/accesos-complementarios`
3. `crebeucayali/capacitaciones`
4. `crebeucayali/banco-digital-accesible`
5. `crebeucayali/materiales-educativos-accesibles`
6. `crebeucayali/noti-inclusivos`
7. `crebeucayali/repositorio-accesible`
8. `crebeucayali/DUA-3.0`

## Elementos inventariados

Por cada archivo HTML se registran, cuando existen:

- enlaces y su destino;
- botones y tipo declarado;
- formularios, método y destino;
- controles de formulario;
- recursos embebidos mediante `iframe`, `video`, `audio` y `source`;
- página y URL esperada;
- alcance público/auxiliar o administrativo;
- huella Git del archivo fuente;
- línea aproximada del elemento;
- etiqueta visible o accesible disponible;
- comportamiento esperado que puede inferirse sin ejecutar la interfaz.

En los archivos JavaScript se registra evidencia estática de:

- `addEventListener`;
- `fetch`;
- referencias a Supabase;
- Web Share API;
- `window.open`;
- cambios de ubicación;
- `localStorage`;
- `sessionStorage`.

## Método

`inventory.py` realiza la captura de fuentes de los ocho repositorios mediante solicitudes de lectura a GitHub. La captura se guarda temporalmente durante el workflow.

`functional_inventory.py` procesa esa misma captura. No vuelve a interpretar una versión diferente de los repositorios dentro de la misma ejecución.

Los resultados se generan en:

- `reports/functional-inventory/functional-inventory.json`
- `reports/functional-inventory/Informe_fase_5_etapa_1.md`

Los artefactos de GitHub Actions se conservan durante 30 días.

## Límites de seguridad

Durante esta etapa el agente:

- no pulsa botones;
- no abre enlaces externos como prueba;
- no envía formularios;
- no ejecuta el JavaScript de EVA;
- no inicia sesión;
- no consulta ni modifica datos de Supabase;
- no modifica ninguno de los ocho repositorios EVA;
- no crea issues, ramas o pull requests en los repositorios EVA.

Una coincidencia estática indica que existe un elemento o una referencia en el código. No demuestra que funcione correctamente.

## Criterio de cierre

La Etapa 1 puede considerarse completada cuando:

1. los ocho repositorios estén incluidos;
2. no existan fallos de lectura en la captura usada;
3. el inventario funcional se genere correctamente;
4. las pruebas automatizadas del agente sean satisfactorias;
5. el workflow de la Etapa 1 finalice correctamente;
6. no se haya modificado ningún repositorio EVA.

Estado previsto tras cumplir todos los criterios:

`ETAPA_1_COMPLETADA_INVENTARIO_FUNCIONAL`

Hasta entonces el estado es:

`ETAPA_1_EN_VALIDACION`

## Paso siguiente

La Etapa 2 utilizará este inventario para definir casos de prueba y resultados esperados. Los botones genéricos cuyo comportamiento no pueda inferirse de forma segura en esta etapa deberán resolverse allí mediante la relación entre HTML, JavaScript y función institucional esperada.
