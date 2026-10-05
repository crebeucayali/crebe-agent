# Fase 5, Etapa 7: verificación funcional posterior

## Objetivo

Comprobar que las dos correcciones aplicadas en la Etapa 6 quedaron publicadas correctamente y que no introdujeron regresiones conocidas.

## Hallazgo F5E4-A1AE3BB801 — Contacto institucional

- El repositorio `noti-inclusivos` ya no contiene referencias a `accesos-complementarios/institucional/contacto.html`.
- Las referencias vigentes apuntan a `accesos-complementarios/paginas/contacto.html`.
- El destino vigente responde y contiene la página institucional de Contacto.
- GitHub Pages publicó el merge commit `b859109e1af623960628b9f1f6ef4a3a4a5d103c` mediante el workflow `37259993514`, con conclusión `success`.
- Estado: `CORREGIDO_VERIFICADO`.

## Hallazgo F5E4-E9B33D5047 — Archivo de publicaciones

- `noti-inclusivos/blog/index.html` existe en `main`.
- La ruta de compatibilidad redirige mediante `meta refresh` a `../articulos/` y conserva un enlace visible de respaldo.
- El canonical apunta a `https://crebeucayali.github.io/noti-inclusivos/articulos/`.
- GitHub Pages publicó el merge commit `6672b18d459cd73f3761982f68b6dbd90c28ec84` mediante el workflow `37260039033`, con conclusión `success`.
- Estado: `CORREGIDO_VERIFICADO`.

## Hallazgo F5E4-EAE63AF520 — Juegos Interactivos Accesibles

No fue corregido en la Etapa 6 porque no existe un destino publicado verificable. Mantiene el estado `BLOQUEADO_POR_DECISION_FUNCIONAL` y no se interpreta como regresión de una corrección.

## Nota sobre verificación web externa

Durante la comprobación se observó que un rastreador web externo devolvía una copia de `noti-inclusivos` rastreada la semana anterior y, por ello, todavía mostraba una referencia antigua. Esa copia no corresponde al estado actual publicado por GitHub Pages y no se utilizó como evidencia de regresión. La evidencia de cierre se basa en el estado actual de `main`, la inexistencia de referencias obsoletas en el código, la presencia de la ruta de compatibilidad y los dos despliegues oficiales de GitHub Pages finalizados correctamente.

## Cierre

- Hallazgos corregidos y verificados: 2.
- Hallazgos bloqueados por decisión funcional: 1.
- Regresiones detectadas en las correcciones: 0.
- Estado final: `ETAPA_7_COMPLETADA_VERIFICACION`.
- Etapa 8: no iniciada.
