# Proveedores XNU y linker estático ARM64 v2

Evidencia de compilación y herramientas host, 2026-10-22.
62 unidades base experimentales, 13 estándar; 42 probes RPC por carril y 26
seleccionados para enlace por CFILES del configurador oficial. La tabla
experimental requiere 14 subsistemas, con proveedores seleccionados comprobados.

LLD v2 construido desde un cache limpio: 54 comandos aprobados, 15 imágenes de
prueba auditadas y coalescing weak/strong nativo conservado. Dependencias LLVM
host por versión/hash; no se declara una toolchain completa hermética.

Enlace experimental de 88 objetos: exit 1, 1.094 diagnósticos de símbolos
indefinidos, cero duplicados, sin archivo de salida. El intento histórico que
incluía toda la lista de generación se conserva separado y tiene 24 duplicados.
Los hashes de ese intento pertenecen a su revisión anterior, no a la actual.

Se publican reportes, comandos, Makefiles de configuración, checks y logs
seleccionados. No se incluyen objetos, fuentes RPC completas o dumps OEM.
Los Makefiles de configuración se conservan byte a byte para cotejar su hash;
sus rutas de desarrollo no son una ruta de SDK usada por el build portátil.

No hay kernel enlazado o ejecutado, arranque físico AtlanticOS, handoff EDK2
ni RAM residente medida. Estas pruebas no acceden al teléfono ni a Android.
Véanse docs/XNU_RPC_PROVIDERS.md y docs/LLD_STATIC_ARM64.md.
