# Excepciones ARM64 y ruta del reloj — 2026-10-23

Este documento conserva los resultados de la revisión de 107 unidades. La
[ampliación posterior de proveedores](XNU_BOOT_PROVIDERS.md) alcanza 123 y
registra el estado de enlace más reciente; no modifica el patch 0021.

El conjunto experimental compila **107 unidades reales derivadas de XNU** con
el compilador original v2 ya probado. El estándar conserva 13. Esta ampliación
integra sleh.c y seis unidades upstream sin modificar: arm/rtclock.c,
kern/recount.c, kern/clock_oldops.c, arm/arm_timer.c, arm/data.s y
arm/commpage/commpage.c. Todavía no hay kernel enlazado ni ejecución XNU.

SLEH aporta los handlers síncronos, SP1, IRQ, FIQ y SError, la comprobación de
stack inválido, retorno de excepciones y panic con estado de hilo nativos.
Los seis proveedores conservan la lógica de reloj, timer, contabilidad de
interrupciones y actualización de commpage, además de los stacks y RTClockData
nativos. No acreditan un timer, una interrupción o un commpage operativo en el
G20; siguen dependiendo del bootstrap, MMU, Platform Expert y BSP físicos.

## Patch 0021

El fallo anterior de SLEH no era ausencia de constantes privadas del compilador:
las definiciones BRK están en kern/trap_telemetry.h del snapshot público. Su
include quedaba condicionado por CONFIG_TELEMETRY aunque también se usa en
rutas fatales. Ahora esas declaraciones se incluyen independientemente de la
colección de telemetría. No se inventan rangos o descriptores Apple.

El header apple_arm64_cpu.h, no usado por este archivo en la placa genérica,
se excluye solo con ARM64_BOARD_CONFIG_ATLANTIC_LAB. Se conserva en otras placas.

En firmware, HAS_TELEMETRY_KERNEL_BRK requiere CONFIG_TELEMETRY además del modo
DEBUG/DEVELOPMENT. Sin ese proveedor no se selecciona la recuperación de soft
traps ni se registra su prueba SYSCTL. La llamada a panic con estado permanece;
no se avanza PC para reanudar un trap de esta ruta. MACH_ASSERT y los macros
de assertions siguen activos. Fuera de firmware y con el proveedor seleccionado
se conserva la selección nativa correspondiente.

## Comprobaciones de BRK y ABI

tools/test_xnu_brk_scope.py aprueba 15 casos por carril: seis combinaciones de
selección, dependencias de headers, cuerpo fatal intacto, cinco funciones de
encoding, registros de assertions y rechazo de un comentario de trap incorrecto.
Los contextos fuera de firmware y los habilitados se cotejan con upstream
byte a byte tras preprocesar las mismas regiones.

| Fixture compilado | Comentario BRK auditado |
|---|---|
| __builtin_trap() | 0x0001 |
| __builtin_debugtrap() | 0xF000 |
| llvm.ubsantrap(i8 25), desde IR | 0x5519, reservado en el header XNU |
| release_assert(0), macro XNU | 0xBFFC |
| mach_assert_abort3x, macro XNU | 0xBFFC |

Los valores se leen de instrucciones reales en objetos AArch64 Mach-O. Para
assert3x también se comprueban los constraints IR x8/x16/x17 y los movimientos
de argumentos a x16/x17 en el código emitido. Los headers nativos no cambian.
Se verifica el tamaño y offsets del descriptor mediante aserciones del target.

llvm.ubsantrap es un intrinsic de IR. El primer intento usó un nombre de builtin
C que este frontend no expone y falló; el fixture correcto usa la interfaz IR
documentada. Esto comprueba el encoding del backend y su correspondencia con
el comentario reservado, sin implementar ni acreditar la instrumentación de
bounds safety de Apple. Véanse [LangRef 19.1](https://releases.llvm.org/19.1.0/docs/LangRef.html#llvm-ubsantrap-intrinsic)
y el [backend AArch64 fijado](https://github.com/llvm/llvm-project/blob/cd708029e0b2869e80abe31ddb175f7c35361f90/llvm/lib/Target/AArch64/AArch64InstrInfo.td).
El caso negativo cambia el ID a 26: compila, pero el auditor debe rechazar su BRK.

En el objeto SLEH real se auditan tres descriptores fatales: clang, libcxx y
xnu_hard_traps. Sus flags no permiten recuperación ni telemetría. La relocation
ARM64_RELOC_UNSIGNED del descriptor hard apunta al handler local XNU real;
el cero del slot antes de enlazar es su addend pendiente, no una implementación.
El objeto no registra la prueba de recuperación ni referencia el backend de
telemetría. El carril estándar no compila SLEH: registra esta auditoría como ausente.

Ninguna de estas pruebas ejecuta un BRK, una assertion, IRQ, timer o kernel.
El preflight QEMU anterior ejecutó un BRK de su entry original, con XNU_NOT_LINKED;
su evidencia no se presenta como prueba de estas rutas XNU.

## Enlace y evidencia

Pasan 51 checks de alcance/ABI experimentales y 45 estándar, incluidos los
15 nuevos por carril. También pasan las 78 pruebas host; los 57 headers MIG,
42 probes RPC, selección de 26 por CFILES y 21 descriptores conservan sus checks.
Los 14 subsistemas requeridos por kobject experimental tienen proveedores.
Las 137 constantes genassym coinciden entre ambos compiladores.

El enlace estricto de 133 objetos con LLD v2 termina en exit 1: 765 diagnósticos
indefinidos, cero duplicados y ningún archivo de salida. El estándar de 39
objetos conserva el rechazo de opciones estáticas y 829 diagnósticos.
Compilador v2 y fixtures del linker se reutilizan por sus hashes actuales;
esta entrega no declara otra reconstrucción de esas herramientas.
La [evidencia local](../evidence/xnu-arm64-exceptions-20261023/manifest.json)
contiene 202 artefactos. Los probes de ipc_policy y mach_debug siguen fallando;
SLEH y pageout compilan y están seleccionados en el build experimental. Estos
cuatro probes no representan todos los proveedores que faltan para enlazar.

La [CI 39891229141](https://github.com/h0nda1337/AtlanticOS/actions/runs/39891229141)
del commit 49bbae4 terminó con success: compilador desde fuentes, API v2 con
26 checks y 100 unidades XNU. Se cotejaron inputs contra los blobs de ese commit,
fuentes, defines y 137 constantes target con la entrega local correspondiente.
Sus [52 artefactos conservados](../evidence/clang-layout-ci100-20261023/manifest.json)
no acreditan la ampliación posterior de 107 unidades. No se afirma identidad
binaria entre hosts ni una ejecución XNU remota.

Las pruebas físicas concretas de assertions y de la cadena IRQ/reloj están en
las [subpruebas T08](DEVICE_TEST_PLAN.md). Siguen pendientes una imagen XNU,
el cierre de Platform Expert/BSP y las puertas de recuperación y carga temporal.

## Reproducir

```sh
python3 tools/build_xnu_lab.py --layout-compiler <clang-v2-probado> --layout-proof <reporte-api>
python3 tools/test_xnu_brk_scope.py --build <reporte-base> --output work/brk-scope-tests
python3 tools/build_xnu_rpc.py --build <reporte-base>
python3 tools/test_xnu_rpc.py --build <reporte-base> --rpc <reporte-rpc>
```

En WSL/NTFS se agrega --windows-git a los builders. Los objetos no son una
imagen de teléfono y el tamaño de sus secciones no mide RAM residente.
La aceptación final sigue exigiendo arranque físico XNU instrumentado,
recuperación Android independiente y transferencia verificada a EDK2.
