# Estado del port real — 2026-10-21

Upstream: apple-oss-distributions/xnu, xnu-12377.1.9,
f6217f891ac0bb64f3d375211650a4c1ff8ca1ea. El snapshot auditado en xnu-upstream
permanece intacto. La serie se aplica a un checkout privado de laboratorio;
no contiene BootShim ni código de plataforma de ports ajenos.

| Componente | Estado comprobado | Ejecución |
|---|---|---|
| Entry ARM64 original | QEMU EL1/EL2→EL1h, stack/contador/vectores y BRK | EMULATED; no XNU ni G20 |
| MIG y config oficiales | Compilados como herramientas host | HOST_TESTED |
| startup.c / kernel_bootstrap | Objeto AArch64 Mach-O, símbolos reales | Sin enlazar ni ejecutar |
| sched_prim.c / scheduler | Objeto AArch64 Mach-O compilado | No ejecutado |
| clock.c / reloj Mach | Objeto AArch64 Mach-O compilado | Sin IRQ/timer probado |
| vm_init.c / bootstrap VM | Objeto AArch64 Mach-O compilado | Sin VM inicializada |
| vm_kern.c / allocator kernel | Objeto AArch64 Mach-O compilado | Sin asignaciones ejecutadas |
| start.s / start_first_cpu | Ensamblado con patch de tunables exclusivo del laboratorio | Sin MMU ni bootstrap ejecutados |
| cswitch.s / Switch_context | Ensamblado con offsets generados por el target | Sin cambio de hilo ejecutado |
| locore.s / vectores | Ensamblado con SFLAGS upstream | Sin excepción XNU ejecutada |
| machine_routines_asm.s | Rutinas de registros/TTB ensambladas | No ejecutadas |
| arm_init.c | Bootstrap C y const_boot_args compilados | No ejecutado |
| arm_vm_init.c | Inicialización VM y bootstrap_pagetables compilados | Sin mapa VM operativo |
| thread.c y vm_map.c | Probes fallidos, diagnósticos conservados | Pendientes |
| Entry XNU, pmap y contexto integrados | Sin construir/enlazar como conjunto | UNIMPLEMENTED |
| Platform Expert y BSP G20 | Sin drivers AtlanticOS funcionales | UNIMPLEMENTED |
| Handoff EDK2 y RAM física | Sin prueba | UNIMPLEMENTED / UNMEASURED |

## Serie original

1. `0001`: perfil ARMv8-A/Cortex-A57 de laboratorio, un CPU y metadata de caché
   para QEMU. Selección en board_config y proc_reg. No importa
   apple_arm64_common, VMAPPLE, AIC, PAC Apple, SME, CTRR, KTRR o SPTM. Los dos
   slots fijos KPC son metadata requerida por los headers; PMU no está
   habilitado y CONFIG_CPU_COUNTERS produce error.
2. `0002`: CommandLine de 1024 bytes para un ABI interno cuyo productor
   AtlanticOS todavía debe implementarse. Evita depender del header iBoot
   ausente. No crea un iBoot vacío ni activa TARGET_OS_SIMULATOR. Las aserciones
   ARM64 comprueban boot_args de 1152 bytes y sus offsets. No reinterpretar un
   buffer OEM o un FDT Linux como esa estructura.
3. `0003`: separa las llamadas de firma/trust caches de Apple del bootstrap
   CONFIG_ATLANTIC_FIRMWARE; rechaza mezclar ese modo con MACH_BSD o IOKIT.
   No agrega verificadores que devuelvan éxito ni reemplazos de VM/IPC. Mueve
   la declaración serverperfmode fuera del guard BSD: startup.c define ese
   tunable aun sin BSD y vm_kern.c lo utiliza. Su definición real se conserva.
4. `0004`: excluye el include y la llamada a tunables Apple en start.s solo para
   ATLANTIC_ARM64_LAB. No crea un proveedor vacío ni hereda los ajustes de otro
   SoC. Los targets upstream restantes conservan su ruta. No satisface la
   investigación de erratas y configuración de CPU del G20.

El modo firmware se plantea sin userland ni carga dinámica de código. La
verificación propia de payloads continúa sin implementar y en estado deny;
este recorte no satisface ese requisito. Todavía hay dependencias sin enlazar,
incluidas workq_init, bsd_scale_setup y OSKextRemoveKextBootstrap. No se afirma
que BSD/IOKit/kexts hayan sido eliminados correctamente de un kernel completo.

Preimágenes, postimágenes y hashes de la serie:
[patches.lock.json](patches.lock.json), sobre bytes canónicos LF. Los archivos
upstream conservan sus avisos y licencias. El código original de perfil,
pruebas y herramientas es MIT; no cambia la licencia de XNU modificado.

## Límites restantes

thread.c utiliza APIs de proceso BSD fuera de guards y el builtin
`__builtin_xnu_types_compatible`, ausente en los Clang probados. No se han
silenciado las declaraciones implícitas ni los chequeos de tipos para compilarlo.
vm_map.c aún alcanza TrustCache/API.h mediante headers de code signing.
Se debe completar ese límite de funcionalidades y preservar una política de
ejecución explícita, sin sustituirla por respuestas de éxito.

Los once objetos siguen teniendo símbolos sin resolver. No hay kernel, entry
XNU operativo, VM/hilo en ejecución, IRQ G20, handoff EDK2 ni medición de RAM.
La aceptación sigue exigiendo evidencia física de rutas sustantivas Mach/XNU.
Compilar estos objetos es un avance de implementación, no su aceptación.

Receta y alcance: [XNU_LAB_BUILD](../docs/XNU_LAB_BUILD.md).
