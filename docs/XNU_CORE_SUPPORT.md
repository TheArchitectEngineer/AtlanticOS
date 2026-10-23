# Soporte ARM64 y diagnóstico core — 2026-10-22

El perfil experimental compila **99 unidades derivadas de XNU** con el proveedor
de layout original explícito y probado; el estándar conserva 13. Esta ampliación
agrega 36 archivos upstream completos, con cambios acotados donde se indican,
y una unidad que conserva cuatro fragmentos nativos de formateo. No hay ejecución
XNU ni resultado físico AtlanticOS.

| Unidades añadidas | Código conservado |
|---|---|
| ipc/mach_kernelrpc.c, ipc_hash.c, ipc_service_port.c, mach_port.c | Traps, hash, etiquetas y operaciones Mach port |
| kern/priority.c, sched_average.c, timer_call.c, exception.c, static_if_common.c | Prioridades, promedios, llamadas de timer, excepciones y registro static-if |
| arm/locks_arm.c; kern/lock_rw.c, lock_mtx.c, lock_ticket.c, lock_ptr.c, lock_group.c | Implementaciones nativas de locks y atributos |
| arm64/copyio.c, bcopy.s, bzero.s, strnlen.s, strncmp.s, memcmp_zero.s | Acceso y rutinas de memoria ARM64 |
| arm/pmap/pmap_data.c; arm64/static_if.c | Datos pmap y parcheo nativo de ramas static-if |
| vm/vm32_user.c, vm_sanitize.c, vm_sanitize_error_compat.c | VM32 y sanitización de argumentos VM |
| vm/vm_map_store.c, vm_map_store_rb.c, vm_purgeable.c | Almacén de mapas y colas purgeable |
| arm64/pcb.c, cpu.c; arm/cpu_common.c, machine_routines_common.c; kern/ast.c | Contexto de máquina, CPU, AST y rutinas comunes |
| kern/debug.c, printf.c, atlantic_printf.c | Panic nativo, __doprnt y subconjunto snprintf/vsnprintf |

Los nombres abreviados de la tabla pertenecen al mismo directorio que su primer
archivo, salvo donde se indica otro. Todos los objetos y sus símbolos exigidos
se registran en el reporte base; vm_sanitize_error_compat aporta un descriptor
nativo de datos S, sin cambiarlo a función para satisfacer el check.

## Alcance del patch 0018

PCB y machine_routines_common dejan de incluir apple_arm64_cpu.h únicamente en
ARM64_BOARD_CONFIG_ATLANTIC_LAB. Este perfil no usa los helpers de MPIDR Apple.
El header sigue en el código de otras placas; no se inventan valores P/E de Apple
para el T700. Las dependencias preprocesadas de los archivos completos se comprueban.

En AST solo el reset del campo kperf_ast requiere CONFIG_KPERF, igual que la
declaración del campo en thread. Se conservan el borrado de AST, los handlers
nativos y la selección de contadores. La rama habilitada queda idéntica tras
preprocesar el bloque original y el adaptado.

panic_get_thread_proc_task conserva las tres validaciones de punteros Mach y
la salida task real. Cuando el firmware no incluye MACH_BSD, devuelve proc NULL
si se pidió esa salida: no hay contexto de proceso BSD disponible. Fuera de
firmware o con BSD seleccionado, el cuerpo preprocesado sigue idéntico al
original. No se elimina el núcleo de panic ni se desactivan sus assertions.

El include general libkern/libkern.h produjo conflictos auténticos entre tipos
Mach/BSD al intentar usarlo en debug.c. La solución es una declaración aislada
de snprintf/vsnprintf y cuatro fragmentos de bsd/kern/subr_prf.c conservados
sin modificar sus cuerpos. Siguen llamando a __doprnt de kern/printf.c.
printf-native.lock.json fija sus posiciones y hashes; el builder los coteja
con el commit upstream. Se conservan los avisos y licencias del archivo original.

tools/test_xnu_core_scope.py comprueba nueve casos por carril: dependencias de
los dos archivos ARM64, dos selecciones KPERF, tres contextos de panic y dos
checks ABI de formateo. El positivo compila el archivo BSD original completo con
las declaraciones nuevas; el negativo cambia int a long y exige el conflicto de
vsnprintf. No se usan tipos inventados ni una implementación host del formateador.
Estas comprobaciones no ejecutan panic, locks, CPU, sanitización o printf.

## Resultado del enlace y límites actuales

El mismo LLD estático v2 probado en la entrega anterior intenta enlazar los
99 objetos base y 26 RPC seleccionados por CFILES. El resultado es exit 1:
**805 diagnósticos de símbolos sin resolver, cero duplicados, ningún archivo de
salida**. La revisión anterior de 62 + 26 registró 1.094 diagnósticos con ese
mismo linker. La reducción es evidencia de proveedores incorporados; no mide
el porcentaje restante hasta arrancar. El estándar de 13 + 26 conserva su rechazo
de opciones estáticas y 829 diagnósticos.

Los 42 probes RPC por carril, la selección de 26, el ABI de 21 descriptores y
los 14 proveedores requeridos por kobject experimental vuelven a comprobarse.
También pasan los checks anteriores de pmap, metadata, MIG y tabla de dispatch:
30 comprobaciones de alcance/ABI por carril contando las nueve nuevas. Las 137
constantes genassym coinciden entre ambos carriles. Pasan las 78 pruebas host.
Las 54 comprobaciones y 15 fixtures del linker se reutilizan por hash del mismo
binario e inputs; no se declara un nuevo build del linker.

Cuatro probes actuales, con el compilador experimental y headers de este build,
siguen fallando. Se conservan sus errores; no son pruebas aprobadas:

| Fuente sin integrar | Fallo observado / investigación necesaria |
|---|---|
| ipc/ipc_policy.c | Acceso a tro_proc_ro ausente en este contexto; resolver metadata y política nativas de proceso, con su lifetime |
| ipc/mach_debug.c | Tipos y callbacks IOKit usados por la descripción de objetos; delimitar esa función según su proveedor real |
| arm64/sleh.c | MPIDR Apple y constantes de traps del compilador; definir el port y ABI de excepciones sin inventar códigos Apple |
| vm/vm_pageout.c | Assertion auténtica del allocator: struct upl con array upl_page_info data-only; preservar el contrato de tipos y segregación |

tools/probe_xnu_core.py reproduce esos cuatro intentos y registra sus comandos,
hashes y errores. No silencia declaraciones implícitas ni modifica tipos para
forzar compilación. Además quedan muchos proveedores sin resolver; cuatro
probes fallidos no representan todo el trabajo pendiente.

La [evidencia de esta revisión](../evidence/xnu-core-support-20261022/manifest.json)
contiene 243 artefactos comprobados por hash, incluidos logs de los fallos y
los intentos de enlace. La compilación local no acredita una CI de 99 unidades;
la reproducción remota se identifica por commit y run cuando termine.

## Reproducir

Después de preparar el compilador experimental, MIG y el build base según
XNU_LAB_BUILD.md y XNU_THREAD_BUILD.md:

```sh
python3 tools/build_xnu_lab.py --layout-compiler <clang-probado> --layout-proof <reporte-layout>
python3 tools/test_xnu_core_scope.py --build <reporte-base> --output work/core-scope-tests
python3 tools/build_xnu_rpc.py --build <reporte-base>
python3 tools/test_xnu_rpc.py --build <reporte-base> --rpc <reporte-rpc>
python3 tools/probe_xnu_core.py --build <reporte-base> --output work/core-probes
```

En WSL con el checkout NTFS se agrega --windows-git a los builders. El reporte
del compilador debe corresponder al binario real y sus fixtures actuales.

La siguiente puerta exige resolver proveedores nativos y Platform Expert,
auditar una imagen enlazada y después ejecutar un bootstrap XNU sustantivo.
El BSP físico G20, el método temporal OEM y la recuperación independiente
continúan pendientes. Cada BSP mantiene su implementación y evidencia separadas;
el perfil de laboratorio no concede compatibilidad al teléfono. No hay handoff
EDK2 ni medición de RAM firmware; el objetivo de menos de 100 MiB sigue abierto.
