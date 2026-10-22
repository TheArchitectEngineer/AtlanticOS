# Cierre incremental Mach / VM / IPC — 2026-10-21

El carril experimental compila 39 unidades genuinas XNU ARM64; el estándar
mantiene 13. No existe todavía kernel enlazado o ejecutado. Las unidades añadidas
cierran proveedores reales de páginas, referencias, espera y scheduler, pero
no resuelven todo el conjunto ni verifican su comportamiento runtime.

| Unidades añadidas a las 22 anteriores | Implementación conservada |
|---|---|
| vm_object.c / vm_fault.c | Bootstrap de objetos, asignación/liberación, faults, wiring y entrada pmap |
| vm_resident.c | Bootstrap de páginas, grab/release y memoria sustraída para pmap |
| locks.c / ledger.c / stack.c | Locks genéricos, contabilidad Mach y pilas de hilo |
| smr.c / waitq.c / turnstile.c | Recuperación diferida, espera e inheritor/priority propagation |
| thread_call.c / timer.c / thread_act.c | Callouts, contabilidad de tiempo y control de hilo |
| sched_dualq.c / processor.c | Tabla dualq con funciones estáticas nativas e inicialización de procesador |
| libkern/os/refcnt.c | Operaciones nativas de referencias y sus verificaciones |
| ipc_space.c / ipc_entry.c | Espacios y entradas de puertos IPC |

No se cuentan prototipos o unidades vacías: el driver exige símbolos de código
y binding reales. Dualq tiene funciones locales t y una tabla externa S; el
driver comprueba su inicializador y la tabla en lugar de exigir una función
externa inventada. La unidad refcnt usa el contexto BSD privado real, igual
que la unidad de metadata proc/task; no habilita userland BSD.

Patch 0012 contiene dos cambios de selección. vm_resident.c conserva el include
AppleFeatures.h fuera de la placa de laboratorio, que usa ARMv8-A sin PAC. No
se crea un header Apple vacío ni se declara soporte PAC. processor.c condiciona
el timer KPERF exactamente como el enum de timer_call.h. Se mantiene el assert
de tamaño de la tabla y los timers de quantum/preemption/perfcontrol.

## Probes que siguen fallando

| Unidad | Bloqueo observado | Próxima comprobación |
|---|---|---|
| vm_pageout.c | El check kalloc rechaza un header upl con punteros y trailer upl_page_info de datos | Auditar contrato de UPL y su allocation/free; conservar el rechazo, sin declarar los datos como punteros |
| ipc_kobject.c | Falta mach/mach_notify.h generado | Ampliar generación con MIG real y roles upstream |
| ipc_kmsg.c | Falta device/device_server.h generado | Generar interfaz device oficial en su rol kernel-server |
| ipc_port / ipc_object / ipc_mqueue / ipc_right | APIs de watchports/special reply y flags condicionados a IMPORTANCE_INHERITANCE | Resolver selección y semántica nativa de importancia; no agregar declaraciones o cuerpos ficticios |

Esos errores provienen de probes conservados con comandos y diagnósticos. No
se atribuyen a un fallo del teléfono. No se eliminan los checks de tipos para
obtener un build aprobado. El comando --probe-remaining los intenta y devuelve
no cero si fallan; el carril normal no los cuenta como compilados.

## Enlazador: limitación comprobada

LLD Mach-O 19.1.7 no implementa -static. Con -fatal_warnings lo rechaza como
error. Su Writer upstream también agrega LC_LOAD_DYLINKER y LC_MAIN a MH_EXECUTE
y marca MH_DYLDLINK. Por eso quitar el flag, ignorar warnings o permitir símbolos
sin resolver no demostraría un kernel estático correcto. Se inspeccionó la
fuente oficial fijada cd708029e0b2869e80abe31ddb175f7c35361f90 del archivo LLVM
cuyo hash ya verifica la receta del compilador.

El intento real de 39 objetos también rechaza -image_base por no implementado
y señala -no_pie como ignorado para arm64. Termina con exit 1, informa 972
símbolos indefinidos y no produce archivo. Esos rechazos son bloqueos reales
del toolchain y del conjunto de dependencias, no una imagen parcialmente válida.

El inventario por nombre cuenta 2.593 definiciones y 986 nombres sin proveedor;
no coincide exactamente con los diagnósticos del linker, que resuelve también
símbolos sintéticos de secciones. Hay dos helpers Blocks repetidos entre
task_ref y locks: llvm-nm -m los identifica como weak private external; no se
presentan como duplicados fuertes ni como funciones core implementadas a mano.

tools/diagnose_xnu_link.py intenta un enlace real con todos los objetos del
reporte, undefined=error, warnings fatales, sin dead strip ni bibliotecas falsas.
Guarda el código de salida, diagnósticos, versión/hash del linker y ausencia de
imagen. Que la herramienta termine correctamente significa que registró el
rechazo; no que enlazó XNU. Una salida inesperada se conserva sin aceptarla y
la herramienta devuelve error para exigir auditoría de imagen.

La solución necesita un linker estático auténtico o una extensión comprobada,
layout de segmentos/permisos, entrada válida y resolución de relocations. La
aceptación posterior debe verificar ausencia de imports/dyld, init_entry_set,
metadata de zonas/kalloc, símbolos Mach y rangos virtuales/físicos antes de
ejecutar XNU. Aún faltan Platform Expert, BSP, IRQ/timer y muchos proveedores.

Fuentes primarias: [LLD Driver](https://github.com/llvm/llvm-project/blob/cd708029e0b2869e80abe31ddb175f7c35361f90/lld/MachO/Driver.cpp),
[Writer](https://github.com/llvm/llvm-project/blob/cd708029e0b2869e80abe31ddb175f7c35361f90/lld/MachO/Writer.cpp),
[header Mach-O](https://github.com/llvm/llvm-project/blob/cd708029e0b2869e80abe31ddb175f7c35361f90/lld/MachO/SyntheticSections.cpp).
La evidencia de esta ampliación está en
[xnu-core-closure-20261021](../evidence/xnu-core-closure-20261021/manifest.json).

Los tamaños de archivos o estructuras no miden RAM residente. No hubo acceso
al G20, modificaciones Android, boot temporal, recuperación física probada ni
handoff EDK2. Las pruebas runtime de tareas, VM y scheduler siguen pendientes.
