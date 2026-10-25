# Servicios comunes freestanding y política futura

fdt.c implementa validación acotada original de FDT, probada en host con
sanitizadores y ejecutada por el preflight QEMU. No es Platform Expert XNU.

macho.c valida el perfil de imagen estática ARM64 de Atlantic LLD y produce un
plan de copia/zero-fill/permisos, probado en host con sanitizadores e imágenes
LLD genuinas. No asigna, autentica, mapea o ejecuta la imagen; todavía no está
integrado en el preflight o el kernel. Contrato: docs/STATIC_IMAGE_PLAN.md.

La especificación ejecutable host de política está en atlantic_core/ (Python). El módulo C
futuro debe implementar boot-policy, eventos, memory, power, config, diagnostics
y security sobre XNU real, conservando escenarios de aceptación. Python no es
dependencia del firmware ni sustituto del kernel. No hay drivers ocultos aquí.
