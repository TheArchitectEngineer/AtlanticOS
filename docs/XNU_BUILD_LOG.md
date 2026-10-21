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
