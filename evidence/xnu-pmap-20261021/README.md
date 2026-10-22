# Dieciocho objetos XNU, incluido pmap ARM — 2026-10-21

BUILT_ARM64: el modo experimental terminó con exit 0 y 18 objetos reales.
El estándar terminó con exit 0 y 13. No hay enlace, MMU o kernel en ejecución.
Cpu_ttep tiene su definición upstream en pmap.c; no se inventó un proveedor.

Patch 0009 separa servicios Apple no seleccionados, preserva RO nativo no PPL y
el panic por compresión de páginas IOMMU. SART/UAT quedan fuera del laboratorio;
eso no implementa DMA ni certifica que el hardware esté quiescente. Las consultas
de trust caches no soportadas son unavailable, sin verificadores alternativos.

Tres pruebas API y tres de dependencia aprobaron con cada compilador. El modo
experimental comprueba además el hash y los símbolos del objeto pmap real.
El estándar declara pmap_object=null: solo comprueba headers. Esas pruebas no
ejecutan traducción, protección RO, firmas o un backend de monitor.

Los reportes incluyen comandos, hashes, 137 constantes target, ABI y diagnóstico.
1.419 nombres definidos y 857 sin proveedor, sin nombres externos repetidos, son
un inventario; no una validación del enlace. Task.c y la integración de memoria
proc/task siguen pendientes, así como BSP físico, recuperación, RAM y handoff.

Solo se normaliza la raíz local a <ROOT>. Los logs de guards PMU/BSD/IOKit/API
retienen diagnósticos de error; el preprocesado completo queda privado en work/.
No se publican objetos XNU, fuentes completas ni imágenes OEM. No hubo acceso
al teléfono ni cambios en Android.
