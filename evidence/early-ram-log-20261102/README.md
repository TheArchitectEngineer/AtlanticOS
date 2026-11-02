# Logging RAM original — 2026-11-02

Dos componentes originales integrados: 157 unidades experimentales / 13 estándar.
Pasan 178/150 checks de alcance/ABI/objetos. Se conservan 155 fuentes anteriores,
137 constantes de layout y 70 headers MIG; 42 probes RPC, 26 seleccionados.
Enlace estático experimental: 183 objetos, 463 nombres indefinidos, cero
duplicados, exit 1 y ninguna imagen. Resuelve kprintf/PE_kputc sin imports nuevos.
La lane estándar no incluye estos componentes en su base y usa LLD upstream.

6 000 registros modelados y 16 000 intentos concurrentes por ejecución host,
ASan/UBSan en ambas lanes; una ejecución aparte con ThreadSanitizer en exp.
Los counts de assertions y contención son variables, no tests independientes.
Se publican los dos objetos integrados, probes estándar, IR/disassembly,
rechazos ABI y configuración, informes completos y logs del enlace. El log
del conflicto de headers previo a seleccionar el contexto core es histórico.
local-inventory.json liga los archivos completos que permanecen bajo work/;
los archivos no incluidos en este manifiesto no se presentan como publicados.

publish_audit.py conserva las verificaciones/rutas locales del empaquetado.
La asamblea genassym cambia rutas de depuración por el nuevo port_id; coincide
al sustituir solo esa ruta, y las 137 constantes/header permanecen idénticos.
No se afirma reproducción binaria completa. La CI limpia anterior era de 155
unidades; sus resultados no se atribuyen a estas 157.

El host ejecuta solo transporte/capturador originales. No hay ejecución del
formatter nativo, adaptador ARM64, XNU, G20 o EDK2. No hay exportación física
de logs ni medición de RAM. 16 432 bytes de BSS es tamaño de objeto; no consumo
total. Se exige RAM normal/shareable mapeada: fuera del preflight MMU-off.
