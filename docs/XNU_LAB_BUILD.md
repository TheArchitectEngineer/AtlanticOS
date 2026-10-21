# Build incremental XNU ARM64 — 2026-10-21

El perfil original atlanticlab compila cinco unidades reales del XNU fijado:
bootstrap, scheduler, reloj, inicialización de VM y allocator kernel. Produce
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
PPL o monitor Apple funcionando. Entry y pmap aún deben construirse y ejecutarse.

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

Se comprueban magic/tipo/arquitectura Mach-O, fuentes y objetos hasheados,
símbolos definidos y pendientes. Bootstrap debe referenciar vm_mem_bootstrap,
task_init, thread_init y sched_init: no se cuentan prototipos sin cuerpo.

Work/xnu-lab-builds/<build-id>/report.json contiene comandos, versiones,
opciones, headers generados, hashes y resultados. Los .o y fuentes completos
permanecen privados; se publica metadata y el patchset correspondiente.
Un exit 0 del driver solo acredita esas cinco compilaciones.

Para intentar además las unidades restantes:

```sh
python3 tools/build_xnu_lab.py --probe-remaining
```

Este modo también compila thread.c y vm_map.c y devuelve exit 1 si alguna
falla, conservando resultados parciales. No es un build completo aprobado.
Thread.c falla por APIs BSD sin declarar y __builtin_xnu_types_compatible;
vm_map.c por TrustCache/API.h. Se consultó ese builtin con target ARM64 Darwin
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

Evidencia: [xnu-lab-20261021](../evidence/xnu-lab-20261021/manifest.json).
