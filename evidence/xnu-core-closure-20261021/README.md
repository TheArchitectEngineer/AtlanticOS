# Cierre incremental de 39 objetos — 2026-10-21

BUILT_ARM64: 39 unidades genuinas en el carril experimental y 13 en el estándar,
ambos exit 0. Se conserva la implementación Mach/VM/IPC y el contexto nativo
BSD privado de refcnt. Patch 0012 limita la selección de header Apple a la placa
de laboratorio y hace coincidir la tabla KPERF con el enum upstream.

Cuatro checks de metadata y seis de API/dependencia pmap aprobaron por carril.
El estándar solo coteja headers; el experimental verifica los objetos relevantes.
Estos checks no ejecutan tareas, allocator, pmap, locks o scheduler.

Siete probes separados fallan en pageout e IPC. El intento estricto de enlace
devuelve 1, informa 972 símbolos indefinidos, rechaza opciones sin implementar
de LLD 19.1.7 y no produce imagen. Undefined=error y warnings fatales permanecen
activos; no se usan stubs, bibliotecas falsas o dead strip para ocultar faltantes.

Los 2.593 nombres definidos y 986 sin proveedor son un inventario diferente del
diagnóstico del linker; no prueban relocations ni viabilidad de arranque. La
duplicación de dos helpers Blocks se registra como weak private external en
task_ref/locks; no se atribuye al proyecto una implementación nueva de ellos.

Reportes y logs conservan comandos/hashes. Los logs de guards PMU/BSD/IOKit/API
contienen solo errores, con hash del log completo; el preprocesado queda privado.
El LLVM IR de la fixture se conserva exactamente para mantener sus hashes.
No se publican objetos, imágenes OEM, fuentes completas ni binarios UEFI.

No hubo acceso al teléfono, ejecución XNU o medición de RAM residente. No hay
kernel enlazado, boot temporal, prueba física de recuperación ni handoff EDK2.
