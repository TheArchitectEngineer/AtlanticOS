# Soporte ARM64 y diagnóstico XNU

Evidencia de compilación, scopes y ABI del 2026-10-22. 99 unidades base
experimentales y 13 estándar; 42 probes RPC compilados por carril, 26 seleccionados
por CFILES. 30 comprobaciones de headers/ABI/scopes por carril, incluidas nueve
nuevas de dependencias ARM64, KPERF, contexto panic y ABI snprintf/vsnprintf.
78 pruebas host aprobadas. Ninguna prueba ejecuta XNU.

El intento estático experimental usa el LLD v2 ya probado y el mismo binario:
125 objetos, exit 1, 805 diagnósticos de símbolos indefinidos, cero duplicados,
sin archivo de salida. Las pruebas de 54 comandos/15 fixtures del linker se
reutilizan por hash; no se presenta una recompilación nueva del linker.
El carril estándar conserva el rechazo de opciones estáticas y 829 diagnósticos.

Cuatro probes actuales fallan al compilar: ipc_policy, mach_debug, sleh y
vm_pageout. Sus errores y comandos se publican completos; no son tests aprobados.
El código de panic y printf integrado tampoco acredita ejecución de un panic.

Se publican reportes, Makefiles oficiales, checks y logs seleccionados. No hay
objetos, fuentes RPC completas, imágenes OEM ni dumps del teléfono en este bundle.
No hay kernel enlazado o ejecutado, arranque físico AtlanticOS, handoff EDK2 ni
medición de RAM firmware. Véase docs/XNU_CORE_SUPPORT.md.
