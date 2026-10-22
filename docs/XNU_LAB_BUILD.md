# Build incremental XNU ARM64 — 2026-10-21

El perfil original atlanticlab compila trece unidades reales del XNU fijado:
bootstrap, scheduler, reloj, inicialización de VM, allocator, entrada ARM64 y
cambio de contexto, vectores, rutinas de máquina, arm_init, arm_vm_init e IPC. Produce
objetos AArch64 Mach-O sin enlazar. No genera una imagen de teléfono ni ejecuta
XNU. El arranque físico y el handoff continúan pendientes.

## Receta y procedencia

Desde Linux/WSL x86_64, con Clang/LLVM 19 o posterior, bison, flex, tcsh,
unifdef, perl y git:

```sh
python3 tools/fetch_xnu.py
python3 tools/fetch_mig.py
python3 tools/build_mig.py
python3 tools/build_xnu_lab.py
```

Si las fuentes ya están en un checkout Windows en /mnt/g, omitir los fetch y
usar `--windows-git` en ambos builds para comprobar integridad con git.exe.
Compilador y generadores siguen siendo Linux. No se simulan xcrun, sw_vers ni
un SDK. El driver sustituye la orquestación de build de este subconjunto;
no demuestra que el Makefile completo funcione.

La primera CI usó Clang 18.1.3 y falló las cinco unidades en bits.h porque no
reconocía __builtin_clzg/ctzg. CI selecciona ahora LLVM 19 explícitamente y el
driver comprueba ambas capacidades para el target antes de preparar fuentes.
No se reemplazan esas operaciones por macros ni se ocultan los errores.
En Ubuntu se instala además libclang-rt-19-dev explícitamente: contiene el
runtime ASan/UBSan del generador host y no forma parte del kernel objetivo.

La [CI del commit daaed8e](https://github.com/h0nda1337/AtlanticOS/actions/runs/39605850951)
aprobó generación y las cinco compilaciones con Ubuntu Clang 19.1.1.
La evidencia local usa Debian Clang 19.1.7. Ambos resultados son de objetos
sin enlace; esa CI no intenta las dos unidades que aún fallan en el probe.

La [CI de 6a2bb69](https://github.com/h0nda1337/AtlanticOS/actions/runs/39611682795)
amplía el resultado a once unidades con Clang 19.1.1. Su reporte descargado y el
local comparten hashes de inputs/parches y las mismas 137 constantes de layout.
No se afirma igualdad byte a byte de objetos entre versiones del compilador.

El driver comprueba commit y limpieza de xnu-upstream, crea un checkout separado
LF bajo work/xnu-lab-sources y aplica la serie con Git al índice. Verifica
hashes de parches, preimágenes, postimágenes y diferencias esperadas. Rechaza
cambios locales inesperados conservándolos para inspección. No modifica el
snapshot utilizado en la auditoría de Fase 0.

Config se construye desde SETUP/config con ASan/UBSan; doconf oficial usa un
MASTER propio. El chequeo de leaks del generador host está desactivado; la prueba
cubre errores de acceso y UB de estos inputs fijados, no todos los posibles
archivos de configuración.

Se comprobó que doconf puede terminar con exit 0 tras un fallo de config.
El driver exige además Makefile, meta_features.h y opciones coherentes. En el
primer experimento las tablas CRLF de Windows causaron errores del parser;
el checkout de build usa los bytes LF del commit.

MIG genera headers sender y KernelServer según las listas y roles de
osfmk/mach/Makefile, incluido el kernel sender resource_notify. Headers de
sanitizers se exportan desde los fuentes reales de san; no se crean stubs.
Version.h usa la plantilla y newvers.pl oficiales. La metadata de compilación
selecciona explícitamente 25.0.0 y fecha reproducible SOURCE_DATE_EPOCH=0;
no es una lectura de un kernel ejecutándose ni de un SDK.

## Perfil y ABI

El target `arm64-apple-macos11.0` produce Mach-O y selecciona el ABI ARM64 de
los headers upstream; la CPU seleccionada es cortex-a57. No declara
compatibilidad macOS ni selecciona CPU Apple. Se usan -nostdinc, headers XNU y
recursos del compilador. El puente Linux de MIG no aparece en includes target.

El perfil es uniprocesador de laboratorio. G20 conserva un BSP separado y no
recibe esos parámetros como validación de hardware. No selecciona BSD userland,
IOKit o libkern C++; conserva Mach, VM, scheduler, bloques y coalitions.
CONFIG_PMAP_PPL selecciona la familia pmap no SPTM de upstream; no demuestra
PPL o monitor Apple funcionando. Start.s y cswitch.s están ensamblados; faltan
su enlace, pmap y ejecución integrada.

El ABI interno boot_args conserva campos upstream con CommandLine=1024. La
prueba ARM64 comprueba sizeof=1152 y offsets de vídeo, árbol, comando y flags.
AtlanticOS todavía no produce boot_args ni SecureDT; nunca se castea FDT Linux
a SecureDT. Se prueba el rechazo de PMU no implementado y de la composición
firmware con MACH_BSD o IOKIT. Eso verifica configuración, no seguridad runtime.
Las decisiones están en [PORTING_NOTES](../xnu-port/PORTING_NOTES.md).

Para VM se pasa -DVM_UNSAFE_TYPES, exigido para los .c de osfmk/vm por el
Makefile.template oficial. Activa los tipos semánticos de entrada que esperan
esas implementaciones; no se agrega para omitir errores. No se borraron
aserciones de layout ni se desactivaron errores de tipos.

## Comprobaciones y límites

| Fuente real | Símbolo comprobado |
|---|---|
| osfmk/kern/startup.c | kernel_bootstrap |
| osfmk/kern/sched_prim.c | sched_init |
| osfmk/kern/clock.c | clock_init |
| osfmk/vm/vm_init.c | vm_mem_bootstrap |
| osfmk/vm/vm_kern.c | kmem_alloc_guard |
| osfmk/arm64/start.s | start_first_cpu, __start, LowResetVectorBase |
| osfmk/arm64/cswitch.s | Switch_context, machine_load_context, Call_continuation |
| osfmk/arm64/locore.s | ExceptionVectorsBase, fleh_synchronous, fleh_irq |
| osfmk/arm64/machine_routines_asm.s | set_mmu_ttb, set_mmu_ttb_alternate |
| osfmk/arm/arm_init.c | arm_init, arm_init_cpu, arm_init_idle_cpu; const_boot_args real |
| osfmk/arm64/arm_vm_init.c | arm_vm_init; bootstrap_pagetables real |
| osfmk/arm64/machine_routines.c | machine_startup |
| osfmk/ipc/ipc_init.c | ipc_init local; registro STARTUP(MACH_IPC) real |

Se comprueban magic/tipo/arquitectura Mach-O, fuentes y objetos hasheados,
símbolos definidos y pendientes. Bootstrap debe referenciar vm_mem_bootstrap,
task_init, thread_init y sched_init: no se cuentan prototipos sin cuerpo.

Work/xnu-lab-builds/<build-id>/report.json contiene comandos, versiones,
opciones, headers generados, hashes y resultados. Los .o y fuentes completos
permanecen privados; se publica metadata y el patchset correspondiente.
Un exit 0 del driver estándar solo acredita esas trece compilaciones y los checks
descritos. El inventario agregado resta símbolos externos definidos por los
objetos a los requeridos; no es una prueba de enlace, relocaciones o reachability.
Los símbolos principales son texto externo (T), salvo ipc_init: es un
inicializador estático real (t), con su registro STARTUP exigido. Los buffers
de arranque exigidos deben tener su definición real. Cpu_ttep sigue sin proveedor
en este subconjunto: no se le agrega una definición arbitraria para cerrar el grafo.

## Offsets y ensamblador nativos

Genassym.c oficial se compila para ARM64 a assembly con -fno-integrated-as,
como exige Makefile.template. Un extractor original acepta únicamente los
marcadores decimales .ascii emitidos por ese modo; rechaza duplicados, aliases
en conflicto, valores fuera de rango, formatos desconocidos y campos faltantes.
No ejecuta un generador con ABI host ni inventa valores ante errores.

La salida contiene 137 definiciones de este perfil, cada una con alias _NUM.
Una segunda unidad C compara offsets de boot_args, thread, cpu_data y contexto
con offsetof del mismo target. Una copia con TH_KSTACKPTR desplazado un byte
debe fallar con la aserción esperada. Ocho tests del parser incluyen metadata
malformada e intentos de introducir texto en vez de constantes.

Assembler-with-cpp define __ASSEMBLER__ en Clang pero no ASSEMBLER. La receta
pasa ambos, siguiendo SFLAGS_GEN de MakeInc.def. Los primeros probes de locore
y machine_routines sin ese segundo define intentaron ensamblar declaraciones C
de headers. Se corrigió la receta; no se borraron declaraciones ni verificaciones.

La primera prueba sin -fno-integrated-as transformó .ascii de un carácter en
.byte; se rechazó esa representación. Se conserva el formato upstream adecuado
en lugar de adivinar el valor de una línea que el parser no comprende.

Patch 0004 excluye include y llamada de tunables Apple solamente bajo
ATLANTIC_ARM64_LAB. No agrega un archivo tunables vacío ni define APPLY_TUNABLES
como éxito. No aporta erratas/configuración de CPU reales para G20.

VM_KERNEL_LINK_ADDRESS=0xfffffff007004000 es un parámetro explícito de
compilación, tomado del layout small-memory de MakeInc.def. Aún no hay linker
ni imagen que satisfagan ese layout y no es una dirección física de carga.
El report deja physical_link_or_load_address=null.

Se comprueba ARM_PGSHIFT=12, granulo hardware de 4 KiB. PAGE_MAX_SHIFT=14 es un
máximo upstream diferente. PAGE_SHIFT usa PAGE_SHIFT_CONST, inicializado en
runtime por arm_init según memoria anunciada; no es constante en este perfil.
No se reemplaza esa variable por un define para forzar el test ni se reduce
artificialmente memSize para elegir otro tamaño. El mapa VM todavía debe
demostrar esa selección y el backing físico real.

Cswitch preserva registros FP/NEON; todavía no se ha ejecutado ni inicializado
un contexto válido para él. El preflight propio mantiene FP desactivado y no
salta a estos objetos. No son pruebas equivalentes ni se conectan por un cast.

Para intentar además las unidades restantes:

```sh
python3 tools/build_xnu_lab.py --probe-remaining
```

Este modo añade el probe de pageout pendiente y devuelve exit 1 si
falla, conservando resultados parciales. No es un build completo aprobado.
El modo estándar carece de las operaciones privadas de tipos requeridas;
el experimental incorpora ahora 47 unidades de Mach/VM/IPC seleccionadas.
Se consultó el builtin con target ARM64 Darwin
en Clang 19.1.7 Linux y 22.1.4 MSYS2 y ambos informaron que no estaba disponible.
Eso no demuestra que ningún otro toolchain o adaptación correcta lo resuelva.

El enlace aún necesita BSP/Platform Expert, hilos, pmap, allocator, IPC y demás
componentes requeridos. Hay símbolos pendientes como workq_init, bsd_scale_setup,
OSKextRemoveKextBootstrap y rutinas de máquina sin implementación AtlanticOS.
No se les agregaron cuerpos vacíos ni retornos de éxito.

Tamaños de objetos, BSS y mapas virtuales no son RAM residente. Xsmall conserva
CONFIG_ZONE_MAP_MIN=120586240 del upstream: hay que estudiar reserva virtual y
backing físico. No se interpreta como medición DRAM ni como cumplimiento de
menos de 100 MiB.

Evidencia histórica de cinco unidades: [xnu-lab-20261021](../evidence/xnu-lab-20261021/manifest.json).
Ampliación a siete y offsets: [xnu-arm64-entry-20261021](../evidence/xnu-arm64-entry-20261021/manifest.json).
Ampliación a once y bootstrap ARM64: [xnu-bootstrap-20261021](../evidence/xnu-bootstrap-20261021/manifest.json).

## Proveedor experimental explícito

La [integración inicial de doce unidades](XNU_THREAD_BUILD.md) añadió thread.c
con LLVM modificado por AtlanticOS y guards MACH_BSD. La
[ampliación de VM y allocators](XNU_VM_ALLOCATOR_BUILD.md) llega a diecisiete,
con parches 0007/0008. La [incorporación de pmap](XNU_PMAP_BUILD.md) llega a
dieciocho con patch 0009. La [metadata nativa de tareas](XNU_TASK_LIFETIME.md)
añade task.c, task_ref.c y dos unidades de helpers conservados: veintidós objetos.
El [cierre core](XNU_CORE_CLOSURE.md) amplía el conjunto a treinta y nueve.
La [integración IPC](XNU_IPC_BUILD.md) llega a cuarenta y siete y 50 headers
generados, con roles kernel-sender/kernel-server y precedencia nativos.
El proveedor solo se activa con --layout-compiler y su
--layout-proof correspondiente. El modo estándar de trece unidades también se
verificó. Los resultados no acreditan allocator o hilos en ejecución.
