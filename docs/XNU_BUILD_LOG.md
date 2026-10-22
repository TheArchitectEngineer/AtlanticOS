# Adaptación de build XNU — investigación activa

Upstream sigue intacto en f6217f891ac0bb64f3d375211650a4c1ff8ca1ea.
Un make -n real en Debian/WSL con SDKROOT=/ y salidas dirigidas a work/ terminó
con exit 2 antes de compilar. Se registraron llamadas a /usr/bin/xcrun ausente,
sw_vers ausente y sysctl hw.memsize/hw.physicalcpu de macOS no disponibles.
La consulta vacía de memoria impidió construir la jerarquía de paralelismo.

El log está en evidence/entry-lab-20261020/xnu-upstream-dry-run.log. Este intento
es diagnóstico, no demuestra que portar el build sin SDK Apple sea imposible.
No se hicieron stubs de funciones kernel ni de seguridad para ocultar errores.

Se está examinando bootstrap_cmds oficial (MIG), commit
c71d2d72f48995baaea76148f61002e5299841de / bootstrap_cmds-138, como herramienta
de generación. No es un port de XNU ni un BSP. Su código usa headers Mach y
conserva avisos APSL/CMU por archivo; no se integra todavía un binario generado.

Actualización: [MIG_HOST_BUILD](MIG_HOST_BUILD.md) contiene una receta original
Linux para construir migcom genuino de ese upstream, con puente host aislado y
aserciones de metadata. El experimento generó interfaces ARM64 clock/mach_host/
mach_port KernelServer. No se compilaron los C generados ni el kernel. Se añade
CI específica para repetir esa generación desde las fuentes oficiales fijadas.

Actualización 2026-10-21: [XNU_LAB_BUILD](XNU_LAB_BUILD.md) conecta config y MIG
oficiales a cinco unidades reales, compiladas como objetos Mach-O AArch64.
La receta sustituye la orquestación de ese subconjunto con parámetros explícitos;
no simula un SDK ni acredita el Makefile completo. La serie original tiene
preimágenes y postimágenes fijadas, un perfil ARMv8-A de laboratorio y un ABI
interno probado. El snapshot de auditoría sigue intacto.

El probe extendido devuelve exit 1: thread.c requiere separar APIs BSD y resolver
builtins Apple de tipos/metadata; vm_map.c alcanza TrustCache/API.h ausente.
No se ocultaron esos errores con headers vacíos, funciones de éxito ni warnings
desactivados. El enlace y la ejecución XNU continúan pendientes, así como pmap,
Platform Expert, contexto, IRQ y drivers AtlanticOS. El perfil de laboratorio
no selecciona VMAPPLE ni CPU Apple y no acredita compatibilidad del G20.

Ampliación 2026-10-21: genassym.c genera 137 offsets/constantes del target, con
aserciones de layout y rechazo de un offset alterado. Start.s y cswitch.s se
ensamblan como dos objetos genuinos adicionales; el patch 0004 aísla tunables
Apple en el laboratorio. Siete unidades compilan, sin enlace ni ejecución.
El inventario agregado de símbolos pendientes orienta el cierre de dependencias;
no sustituye un enlace real. Se conservan los fallos de thread.c y vm_map.c.

La ampliación posterior compila locore.s, machine_routines_asm.s, arm_init.c y
arm_vm_init.c sin parches adicionales. El flag ASSEMBLER que faltaba en los
probes se toma de SFLAGS_GEN upstream, junto con __ASSEMBLER__. Ahora son once
objetos, con símbolos reales de bootstrap/vectores y buffers upstream; sin
enlace ni ejecución. Cpu_ttep se conserva como dependencia sin resolver, no
como un dato inventado. Las pruebas Python suman 74, ocho de ellas del extractor.

Experimento de compilador: compiler-port/ contiene una extensión original sobre
LLVM 19.1.7 que calcula metadata de layouts C con el AST del target. Se construyó
el compilador completo y pasaron 18 comprobaciones con fixtures propios. No
suplanta los builtins privados Apple ni un SDK. Un probe de thread.c con un
header experimental explícito deja diez errores BSD y ya no reporta errores
de esas operaciones. El build normal de once objetos todavía no lo activa.

Integración posterior: patches 0005/0006 añaden selector explícito del proveedor
y guards MACH_BSD. El modo estándar vuelve a compilar once unidades; el
experimental compila doce, incluido thread.c, con 137 offsets y comprobaciones
de kalloc/ABI. Se rechazaron pruebas de compilador incompletas o de otro binario.
Vm_map.c continúa fallando por TrustCache/API.h. No hay enlace ni ejecución.
Receta, advertencias y límites: [XNU_THREAD_BUILD](XNU_THREAD_BUILD.md).

La CI 39626520147 reconstruyó el compilador mediante la receta pública y aprobó
sus 18 checks y doce unidades XNU. Los inputs y 137 constantes coinciden con el
reporte local. La preparación pública local verificó 11.996 archivos fuente.

La ampliación siguiente añade 0007/0008: include TrustCache condicionado por el
monitor seleccionado y nombre consistente del guard de logging. Compilan trece
unidades estándar y diecisiete experimentales, incluidos vm_map, kalloc y zalloc.
Tres checks de dependencia exigen TrustCache real para PPL y targets upstream.
El probe extendido retorna 1 por task.c y pmap; conserva ambos fallos.
Receta y alcance: [XNU_VM_ALLOCATOR_BUILD](XNU_VM_ALLOCATOR_BUILD.md).

Patch 0009 separa los servicios Apple de monitor y trust caches de pmap en el
firmware de laboratorio, conserva RO no PPL y señala las consultas no soportadas
como unavailable. El build experimental terminó con 18 objetos y cero fallos.
Dos APIs de trust caches rechazaron sus consumidores; los checks del objeto
exigen funciones sustantivas y ausencia de esos proveedores/dependencias.
Task.c continúa pendiente; XNU_TASK_LIFETIME.md documenta su asignación conjunta
con proc y metadata RO. No se han creado tareas ni tablas durante ejecución.
