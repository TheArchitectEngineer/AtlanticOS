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
| thread.c | Objeto real con proveedor experimental explícito y guardas BSD | Sin enlazar ni ejecutar |
| vm_map.c, kalloc.c, zalloc.c | Objetos reales con proveedor experimental y patches 0007/0008 | Sin enlazar ni ejecutar |
| machine_routines.c / ipc_init.c | Objetos reales, inicializador IPC estático registrado | Sin ejecutar |
| pmap.c | Objeto real con patch 0009; cpu_ttep definido por upstream | Sin enlace, MMU o DMA ejecutados |
| task.c / task_ref.c | Objetos genuinos; vida útil y referencias nativas conservadas | Sin ejecutar |
| Metadata proc/task y get_bsdtask_info | Helpers XNU conservados, contextos privados separados y ABI cotejado | Sin asignación o protección RO ejecutada |
| VM residente / objetos / faults | Objetos genuinos; selección de header Apple limitada a placa de laboratorio | Sin gestión física de páginas ejecutada |
| Locks / ledgers / stack / waitq / turnstiles / SMR | Objetos genuinos y referencias originales | Sin concurrencia ejecutada |
| Dualq / processor / thread_act / thread_call / timer / refcnt | Cuerpos nativos y tabla de despacho original | Sin contexto/hilo/timer ejecutados |
| ipc_space / ipc_entry | Objetos genuinos | Otros componentes IPC siguen pendientes |
| ipc_importance / ipc_object / ipc_port / ipc_kmsg / ipc_mqueue / ipc_right | Objetos genuinos con importancia nativa y headers MIG correctos | Sin mensajes, colas o donación de prioridad ejecutados |
| ipc_kobject / getters RO de hilo | Dispatch nativo y siete helpers conservados con zonas/backrefs | Sin RPC o validación RO ejecutados |
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
5. `0005`: selector explícito de nuestra API de layouts C en kalloc.h; exige
   perfil de firmware de laboratorio y compilador probado. Conserva los checks
   upstream y las operaciones originales cuando el selector está desactivado.
6. `0006`: guards MACH_BSD para salidas de proceso, nombres y workqueues
   cooperativas en thread.c. Conserva la implementación Mach; no sustituye
   funciones con stubs. Permanecen dependencias BSD sin enlazar.
7. `0007`: condiciona TrustCache/API.h cuando firmware no selecciona su monitor
   PPL. Los usos de sus tipos ya están dentro de ese guard. Mantiene el include
   de los demás targets y todas las declaraciones y llamadas de protección.
8. `0008`: usa ZALLOC_ENABLE_LOGGING, ya definido, en los guards que tenían el
   nombre ZONE_ENABLE_LOGGING sin definición en este snapshot. Conserva los
   campos y funciones de logging del perfil DEVELOPMENT.
9. `0009`: separa los servicios Apple de monitor/trust caches del pmap de
   firmware; declara las consultas no soportadas como unavailable. Excluye
   SART/UAT solo en laboratorio, preserva RO no PPL y el panic IOMMU. Agrega la
   declaración adelantada del protector RO existente. No implementa IOMMU ni
   verificación alternativa. Véase [XNU_PMAP_BUILD](../docs/XNU_PMAP_BUILD.md).
10. `0010`: conserva el puntero RO de task y el subconjunto nativo de helpers
    proc/task. Retiene los allocators, flags de referencia, tokens, credenciales
    y validación de zonas originales, sin habilitar MACH_BSD o su userland.
    Once cuerpos de funciones se cotejan con el commit upstream por hash.
11. `0011`: condiciona callbacks de proceso/AMFI/watchport/deferred reclaim y
    memorystatus a sus features reales. Mantiene la lógica Mach/VM, no concede
    opt-out AMFI ni identidad init cuando faltan sus proveedores. No implementa
    los callbacks de IOKit que aún quedan sin resolver.
12. `0012`: excluye AppleFeatures.h solo cuando ARM64_BOARD_CONFIG_ATLANTIC_LAB
    ya selecciona la placa sin PAC. Conserva el include en otras placas. El
    running-timer KPERF de processor.c usa el mismo guard que el enum original;
    el static_assert que verifica tamaño de la tabla sigue activo.
13. `0013`: limita el campo de proceso de kobject al bloque MACF que lo usa y
    conserva fuera el acceso RO del hilo. El índice real de política sigue
    disponible para los hooks de trazado aunque MACF no esté seleccionado.
14. `0014`: conserva siete accessors RO originales de bsd_kern.c, incluida
    validación de zona/propietario y el TASK_NULL temprano. Las 18 funciones
    conservadas se cotejan por hash/posición con XNU antes de compilar.
15. `0015`: selecciona KernelUser real de MIG en vm_map para firmware y limita
    las interfaces Arcade a su proveedor seleccionado. Cinco comparaciones de
    generación conservan salida byte a byte fuera de firmware o con Arcade
    activado. No se declara mach_msg ni un conversor falso para hacer compilar.
16. `0016`: corrige dos casts a un parámetro size inexistente en las ramas
    nativas de reclamación diferida desactivada de vm_user.c. Usa los parámetros
    actuales, conserva KERN_NOT_SUPPORTED y deja intacto el proveedor habilitado.
17. `0017`: en firmware registra los receptores BSD e IOKit solo si sus proveedores
    están seleccionados. Conserva la tabla original fuera de firmware y cuando
    ambos proveedores están activos; los emisores de excepciones Mach siguen
    seleccionados por el configurador nativo. No habilita BSD o IOKit ficticios.
18. `0018`: excluye un header de MPIDR Apple no utilizado por el perfil genérico
    de laboratorio en pcb.c y machine_routines_common.c. El reset de kperf_ast
    usa el mismo guard CONFIG_KPERF que su campo. Panic conserva sus validaciones
    Mach y devuelve contexto proc NULL solo en firmware sin MACH_BSD. Cuatro
    fragmentos de snprintf/vsnprintf se conservan con licencia y hashes nativos;
    llaman a __doprnt de XNU y sus declaraciones se verifican contra el archivo
    BSD original completo. No se declara un panic o formatter ejecutado.
19. `0019`: conserva __kernel_ptr/data/dual_semantics mediante anotaciones
    estándar consumidas por la API original v2, solo con el selector explícito.
    Mantiene las declaraciones nativas y exige versión 2 del compilador. No
    altera los tipos UPL, sus allocations ni la assertion de cola data-only.
    El control sin selector conserva los macros upstream; su ABI se compara
    con el del contexto anotado. Véase XNU_USAGE_SEMANTICS.md.
20. `0020`: declara los dos punteros de almacenamiento de zone_leaks como
    vm_offset_t *, el mismo tipo usado por su allocation/free existentes. Su
    identidad C/ABI con uintptr_t no sustituye la metadata de uso. No cambia el
    algoritmo de diagnóstico ni silencia la assertion que detectó la diferencia.
21. `0021`: incluye las definiciones nativas BRK aunque no se seleccione la
    colección de telemetría. Excluye el helper MPIDR Apple solo en laboratorio.
    En firmware, las rutas recuperables y su prueba requieren el proveedor real;
    las rutas fatales, assertions y cuerpo de handler hard se conservan.
    Se auditan selección, registros, instrucciones y relocation del callback.

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

Thread.c compila con el selector experimental y el compilador original probado,
como documenta [XNU_THREAD_BUILD](../docs/XNU_THREAD_BUILD.md). El modo estándar
no activa el selector y todavía necesita proveedor para las operaciones Apple.
No se han silenciado declaraciones implícitas ni los chequeos de tipos.
Vm_map.c compila tras acotar ese include al monitor seleccionado. Todavía tiene
dependencias de protección sin proveedor en el conjunto; no se inventa una
política de ejecución ni se sustituye por respuestas de éxito. Task.c compila
con metadata nativa conjunta; su vida útil real aún exige pruebas runtime.
Pmap compila tras
separar los servicios Apple no seleccionados, sin ejecutarse.

Los trece objetos estándar y 132 experimentales tienen símbolos sin resolver. No hay kernel, entry
XNU operativo, VM/hilo en ejecución, IRQ G20, handoff EDK2 ni medición de RAM.
La aceptación sigue exigiendo evidencia física de rutas sustantivas Mach/XNU.
Compilar estos objetos es un avance de implementación, no su aceptación.

Receta y alcance: [XNU_LAB_BUILD](../docs/XNU_LAB_BUILD.md).
El [cierre core](../docs/XNU_CORE_CLOSURE.md) registra los probes que siguen
fallando y la limitación comprobada de -static en LLD 19.1.7.
La [integración RPC](../docs/XNU_RPC_BUILD.md) agrega los C y descriptores
generados de sus recetas nativas, sin convertirlos en servicios ejecutados.
La [integración de proveedores](../docs/XNU_RPC_PROVIDERS.md) agrega quince
unidades nativas, incluida vm_user tras corregir los casts; pageout sigue pendiente.

La [ampliación de proveedores de arranque](../docs/XNU_BOOT_PROVIDERS.md) añade
16 fuentes upstream sin modificar, con el mismo patchset 0021. Los parsers PE
y SecureDT compilan en su contexto PEXPERT_KERNEL_PRIVATE; no constituyen aún
el Platform Expert original de AtlanticOS. El enlace estricto de 149 objetos
falla con 672 diagnósticos indefinidos, cero duplicados y ninguna imagen.
La situación de pageout y SLEH en revisiones anteriores se conserva como historia;
ambos ya están seleccionados en el build experimental actual.

El patch 0022 añade dos archivos originales MIT, cotejados con sus fuentes en
xnu-port/platform/. El [núcleo PE](../docs/XNU_PLATFORM_EXPERT.md) usa tipos XNU
auténticos, SecureDT y panic nativos; todavía no se ejecuta ni aporta el BSP.
El enlace de aquella revisión de 150 objetos falla con 669 diagnósticos indefinidos, cero
duplicados y ningún archivo. atlantic_pe_platform sigue como import fuerte.

El patch 0023 añade el adaptador original de caché genérica. El builder verifica
su mirror y selecciona además siete fuentes upstream de memoria física,
caché, atómicos, estado de tareas y memory_object. Su auditoría comprueba el salto
al proveedor nativo, las instrucciones y el ABI; no ejecuta esas operaciones.
Detalles, límites de IO coherente y pruebas físicas pendientes en
[XNU_MEMORY_PROVIDERS](../docs/XNU_MEMORY_PROVIDERS.md).
Seis fuentes quedan intactas; el patch 0024 solo excluye en firmware el fallback
vacío de kdp_register_callout de loose_ends.c, conservando el registro real de
debug.c. No hay símbolos weak ni permiso de duplicados para resolver la colisión.
El enlace de esa ampliación de 158 objetos conserva 609 diagnósticos indefinidos y cero
duplicados; no produce imagen. Pasan 89/57 checks de alcance/ABI/objetos, sin
ejecución del kernel o los proveedores de memoria.

El patch 0025 condiciona cuatro llamadas de startup.c a sus componentes BSD/IOKit
en firmware. No aporta implementaciones de esas APIs ni elimina la inicialización
Mach. El [alcance de bootstrap](../docs/XNU_BOOTSTRAP_SCOPE.md) se comprueba en
fuente y startup.o real: 97/65 checks totales. El enlace actual conserva 605
diagnósticos indefinidos, cero duplicados y ninguna imagen, con las mismas 132
unidades experimentales. No hay ejecución del bootstrap o del kernel.
