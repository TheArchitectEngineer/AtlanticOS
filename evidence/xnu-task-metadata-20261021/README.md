# Veintidós objetos y metadata nativa de tareas — 2026-10-21

BUILT_ARM64: 22 unidades reales en el carril experimental, 13 en el estándar;
ambos exit 0. Task.c, task_ref.c y los helpers conservados de XNU tienen
definiciones externas genuinas. Los once cuerpos de funciones de los helpers
se cotejan con el commit upstream; conservan sus avisos de licencia.

HOST_TESTED: cuatro casos de ABI por carril: dos compilaciones LLVM IR ARM64
y dos rechazos de un offset alterado. Nueve valores compartidos coinciden entre
headers privados Mach y BSD. El estándar solo coteja headers; su lista de
objetos de tarea está vacía. El experimental verifica además los cuatro objetos.
Los dos carriles mantienen MACH_BSD ausente, sin BSD startup o userland.

Se conservan los diagnósticos de task.c, las llamadas nativas de zonas RO,
referencias y credenciales, y sus dependencias sin resolver. El inventario de
22 unidades tiene 1.677 nombres definidos y 987 sin proveedor; no acredita
relocations, enlace ni suficiencia del conjunto. Las consultas Apple de trust
cache siguen rechazadas y se repiten las pruebas pmap de headers/dependencias.

No hubo ejecución XNU, creación real de tareas, comprobación runtime de tokens,
backrefs o permisos RO, ni acceso al teléfono. Los tamaños ABI no son RAM
residente. No hay imagen arrancable, modificación Android ni handoff EDK2.

Los informes y logs conservan hashes y comandos; <ROOT> normaliza la raíz local
en los reportes y diagnósticos. Los logs de rechazo PMU/BSD/IOKit/API publican
solo líneas de error; su preprocesado completo permanece privado en work/ y su
hash original se registra en el manifiesto. El LLVM IR de la fixture se conserva tal como lo
emitió el compilador para mantener su hash. No se distribuyen objetos XNU,
fuentes completas upstream, imágenes OEM ni binarios del port UEFI.
