# Objeto genuino de hilos y proveedor explícito de layouts — 2026-10-21

El build experimental compila doce unidades XNU ARM64: las once del perfil
estándar más osfmk/kern/thread.c. Comprueba thread_init como texto externo y las
definiciones reales de kernel_thread_start y thread_terminate_self. No hay enlace
ni ejecución de esos hilos. El build estándar sigue aprobando once unidades.

## Reproducir

Primero construir el [compilador experimental](../compiler-port/README.md),
ejecutar sus 18 comprobaciones y preparar XNU/MIG como en
[XNU_LAB_BUILD](XNU_LAB_BUILD.md). Después:

```sh
python3 tools/build_xnu_lab.py \
  --layout-compiler work/clang-layout-build/build/bin/clang \
  --layout-proof work/clang-layout-build/tests/report.json
```

En el checkout Windows se puede añadir --windows-git. La prueba debe corresponder
al hash exacto del ejecutable y a los inputs actuales de la extensión y fixtures.
El driver rechaza una prueba incompleta o de otro binario. Esta comprobación de
procedencia local no es una certificación criptográfica del compilador.

La [CI manual](../.github/workflows/experimental-layout.yml) reconstruye LLVM
desde su archivo fijado y repite API, MIG y las doce unidades. El workflow normal
no construye LLVM ni activa CONFIG_ATLANTIC_C_LAYOUT. Un workflow preparado no
acredita su ejecución: los resultados se documentan por run concreto.

## Cambios sobre XNU

Patch 0005 añade KALLOC_LAYOUT_SUMMARY, SIGNATURE y COMPATIBLE. Solo selecciona
las operaciones __atlantic_layout_* con CONFIG_ATLANTIC_C_LAYOUT=1, firmware de
laboratorio y la capacidad de compilador v1. El resto conserva las operaciones
upstream. No redefine __has_builtin ni declara disponibles los builtins Apple.
Los checks de clasificación, solapamientos, punteros y emisión de metadata de
kalloc permanecen activos. Un fixture usa esas macros reales y debe rechazar
un puntero con layout incompatible; un compilador sin la API debe fallar al
seleccionar el proveedor.

Patch 0006 agrega guards MACH_BSD a las rutas de proceso BSD y workqueues
cooperativas de thread.c que antes se compilaban sin sus declaraciones. Conserva
el código Mach de creación, inicialización, terminación, contadores y scheduler.
Las funciones exclusivamente BSD se omiten cuando esa función está desactivada;
no reciben cuerpos vacíos ni resultados de éxito. Esto no elimina todas las
dependencias BSD del subconjunto: el inventario todavía contiene nombres como
bsd_getthreadname, proc_thread_qos_deallocate y workq_init.

## Evidencia y límites

[xnu-thread-20261021](../evidence/xnu-thread-20261021/manifest.json) conserva los
reportes de ambos modos, las comprobaciones y símbolos. El experimental produjo
doce objetos, 137 constantes target y sus aserciones de layout. El inventario
agregado contiene 619 definiciones externas y 632 nombres sin proveedor en ese
conjunto. Es un inventario por nombre, sin validación de relocaciones o enlace.

Thread.c conserva dos warnings de visibilidad de struct ucred en declaraciones
upstream. No se desactivaron warnings ni errores de tipos. El probe independiente
de vm_map.c con este compilador vuelve a fallar por TrustCache/API.h ausente;
su diagnóstico se incluye. Excluir ese header sin separar sus consumidores y
políticas no resolvería la integración.

El allocator aún no se ha ejecutado con esta metadata. La extensión soporta el
perfil C sin PAC descrito en su contrato; no acredita la semántica completa de
un toolchain Apple. Faltan pmap, Platform Expert/BSP, cierre de dependencias y
enlace antes de intentar ejecución instrumentada. G20, recuperación física,
handoff EDK2 y RAM residente continúan sin validar.
