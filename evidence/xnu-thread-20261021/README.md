# Doce objetos XNU con proveedor C explícito — 2026-10-21

BUILT_ARM64: doce unidades reales compiladas; sin enlace ni ejecución.
El reporte experimental verifica API del compilador, macros kalloc, puntero
incompatible, ABI y offsets target. El reporte estándar vuelve a aprobar once
unidades con Clang sin extensión. Ambos usan la misma serie original y upstream.

Los dos rechazos de pruebas de compilador alteradas terminaron con exit 2.
El probe separado de vm_map.c terminó con exit 1 por TrustCache/API.h ausente.
Ninguno se cuenta como compilación aprobada. Los warnings de ucred se conservan.

Comandos y logs normalizan únicamente la raíz local a <ROOT>. Los logs de guards
PMU/BSD/IOKit/proveedor son extractos de diagnósticos; el preprocesado completo
permanece en work/. Los otros logs se conservan completos. No se publican objetos
XNU, fuentes completas, imágenes OEM o el ejecutable del compilador.

619 definiciones externas y 632 nombres sin proveedor son un inventario por
nombre, no un enlace ni una prueba de relocaciones. Tamaños de objetos no son RAM
residente. No hubo acceso al teléfono ni ejecución XNU en QEMU o hardware.
