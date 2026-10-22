# Cuarenta y siete objetos XNU e interfaces MIG — 2026-10-21

BUILT_ARM64: 47 unidades genuinas en el carril experimental, 13 en el estándar,
ambos exit 0. El perfil activa importancia nativa. El driver comprueba cuerpos,
bindings y los registros STARTUP originales de IPC, importancia y MIG.

MIG oficial produce 50 headers únicos: 15 sender públicos, 13 kernel-sender y
22 kernel-server, incluido device con cero RPCs al estar IOKIT ausente. Los
headers no suministran las implementaciones C RPC ni funcionalidad IOKit.

Cada carril pasa 5 casos de metadata, 3 ABI MIG y 6 API/dependencia pmap. Se
rechazan un nombre de puerto usado como objeto, una firma server antigua y
offsets RO alterados. El experimental comprueba cinco objetos de metadata;
el estándar solo sus tipos/headers y declara objetos vacíos en ese reporte.
Los 18 cuerpos de helpers nativos conservados se cotejan por hash con XNU.

Thread_RO mide 48 bytes, su propietario está en offset 0 y task en 8. Task mide
1624 bytes con importancia; la revisión sin ella tenía 1616. Los 137 valores
genassym coinciden, pero no prueban igualdad de todos los layouts. Estos valores
son ABI target y no mediciones de RAM residente.

El enlace real termina con 1, informa 1021 símbolos indefinidos y no produce
imagen. LLD sigue rechazando opciones necesarias. El inventario de 2837 nombres
definidos y 1035 sin proveedor tiene alcance distinto. Pageout conserva dos
errores de tipos y tampoco produce objeto; no se oculta con un allocator falso.

Reportes/logs conservan comandos y hashes. Los guards PMU/BSD/IOKit/API publican
solo errores, con hash del log completo; su preprocesado queda privado. El IR
de la fixture se conserva exactamente. No se distribuyen objetos, headers MIG
completos, imágenes OEM, binarios UEFI o fuentes upstream completas.

No hubo entrega de mensajes, donación de prioridad o comprobación RO runtime.
No hubo ejecución XNU ni acceso al teléfono. Arranque físico, recuperación
independiente, RAM física y handoff EDK2 siguen pendientes.
